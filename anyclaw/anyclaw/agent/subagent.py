"""Subagent manager for background task execution."""

import asyncio
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from anyclaw.tools.filesystem import ReadFileTool, WriteFileTool, ListDirTool
from anyclaw.tools.shell import ExecTool
from anyclaw.tools.registry import ToolRegistry
from anyclaw.bus.events import InboundMessage
from anyclaw.config.settings import settings
from anyclaw.agent.summary import (
    IterationSummaryCollector,
    IterationSummaryGenerator,
)


logger = logging.getLogger(__name__)


class SubagentManager:
    """Manages background subagent execution."""

    def __init__(
        self,
        provider: Any,  # LLMProvider
        workspace: Path,
        bus: Any,  # MessageBus
        model: Optional[str] = None,
        restrict_to_workspace: bool = False,
    ):
        self.provider = provider
        self.workspace = workspace
        self.bus = bus
        self.model = model or getattr(settings, 'llm_model', 'gpt-4')
        self.restrict_to_workspace = restrict_to_workspace
        self._running_tasks: dict[str, asyncio.Task[None]] = {}
        self._session_tasks: dict[str, set[str]] = {}  # session_key -> {task_id, ...}

    async def spawn(
        self,
        task: str,
        label: Optional[str] = None,
        origin_channel: str = "cli",
        origin_chat_id: str = "direct",
        session_key: Optional[str] = None,
    ) -> str:
        """Spawn a subagent to execute a task in background."""
        task_id = str(uuid.uuid4())[:8]
        display_label = label or task[:30] + ("..." if len(task) > 30 else "")
        origin = {"channel": origin_channel, "chat_id": origin_chat_id}

        bg_task = asyncio.create_task(
            self._run_subagent(task_id, task, display_label, origin)
        )
        self._running_tasks[task_id] = bg_task
        if session_key:
            self._session_tasks.setdefault(session_key, set()).add(task_id)

        def _cleanup(_: asyncio.Task) -> None:
            self._running_tasks.pop(task_id, None)
            if session_key and (ids := self._session_tasks.get(session_key)):
                ids.discard(task_id)
                if not ids:
                    del self._session_tasks[session_key]

        bg_task.add_done_callback(_cleanup)

        logger.info(f"Spawned subagent [{task_id}]: {display_label}")
        return f"Subagent [{display_label}] started (id: {task_id}). I'll notify you when it completes."

    async def _run_subagent(
        self,
        task_id: str,
        task: str,
        label: str,
        origin: dict[str, str],
    ) -> None:
        """Execute subagent task and announce result."""
        logger.info(f"Subagent [{task_id}] starting task: {label}")

        try:
            # Build subagent tools (no message tool, no spawn tool)
            tools = ToolRegistry()
            allowed_dir = self.workspace if self.restrict_to_workspace else None

            # Register tools
            tools.register(ReadFileTool(workspace=self.workspace))
            tools.register(WriteFileTool(workspace=self.workspace))
            tools.register(ListDirTool(
                workspace=self.workspace,
                timeout=getattr(settings, 'list_dir_timeout', 30),
                max_entries=getattr(settings, 'list_dir_max_entries', 200),
            ))
            tools.register(ExecTool(
                working_dir=str(self.workspace),
                timeout=getattr(settings, 'tool_timeout', 60),
            ))

            # Build system prompt
            system_prompt = self._build_subagent_prompt()

            messages: list[dict[str, Any]] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task},
            ]

            # Run agent loop (limited iterations)
            max_iterations = getattr(settings, 'subagent_max_iterations', 15)
            iteration = 0
            final_result: Optional[str] = None

            # 初始化迭代摘要收集器
            summary_collector = IterationSummaryCollector()

            while iteration < max_iterations:
                iteration += 1

                # Call LLM with tools
                try:
                    response = await self.provider.chat_with_retry(
                        messages=messages,
                        tools=tools.get_definitions(),
                        model=self.model,
                    )
                except Exception as e:
                    logger.error(f"LLM call failed: {e}")
                    final_result = f"Error: {str(e)}"
                    break

                # Check for tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    # Build tool calls
                    tool_call_dicts = []
                    for tc in response.tool_calls:
                        if hasattr(tc, 'to_dict'):
                            tool_call_dicts.append(tc.to_dict())
                        else:
                            tool_call_dicts.append({
                                "id": getattr(tc, 'id', ''),
                                "type": "function",
                                "function": {
                                    "name": getattr(tc, 'name', ''),
                                    "arguments": getattr(tc, 'arguments', {}),
                                },
                            })

                    messages.append({
                        "role": "assistant",
                        "content": response.content or "",
                        "tool_calls": tool_call_dicts,
                    })

                    # Execute tools
                    for tool_call in response.tool_calls:
                        args_str = json.dumps(tool_call.arguments, ensure_ascii=False)
                        logger.debug(f"Subagent [{task_id}] executing: {tool_call.name} with arguments: {args_str}")

                        start_time = time.time()
                        success = True
                        try:
                            result = await tools.execute(tool_call.name, tool_call.arguments)
                        except Exception as e:
                            logger.error(f"Tool execution failed: {e}")
                            result = f"Error: {str(e)}"
                            success = False
                        duration_ms = int((time.time() - start_time) * 1000)

                        # 记录到迭代摘要收集器
                        summary_collector.record_tool_call(
                            name=tool_call.name,
                            arguments=tool_call.arguments,
                            result=str(result),
                            duration_ms=duration_ms,
                            success=success,
                        )

                        messages.append({
                            "role": "tool",
                            "tool_call_id": getattr(tool_call, 'id', ''),
                            "name": tool_call.name,
                            "content": str(result),
                        })
                else:
                    final_result = response.content
                    break

            if final_result is None:
                # 达到最大迭代次数，生成智能汇报
                final_result = await self._generate_subagent_summary(
                    summary_collector, messages, max_iterations
                )

            logger.info(f"Subagent [{task_id}] completed successfully")
            await self._announce_result(task_id, label, task, final_result, origin, "ok")

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            logger.error(f"Subagent [{task_id}] failed: {e}")
            await self._announce_result(task_id, label, task, error_msg, origin, "error")

    async def _generate_subagent_summary(
        self,
        collector: IterationSummaryCollector,
        messages: list[dict[str, Any]],
        max_iterations: int,
    ) -> str:
        """生成 SubAgent 迭代限制智能汇报"""
        enabled = getattr(settings, 'iteration_summary_enabled', True)
        max_tokens = getattr(settings, 'iteration_summary_max_tokens', 1000)

        generator = IterationSummaryGenerator(enabled=enabled, max_tokens=max_tokens)
        return await generator.generate(collector, messages, max_iterations)

    async def _announce_result(
        self,
        task_id: str,
        label: str,
        task: str,
        result: str,
        origin: dict[str, str],
        status: str,
    ) -> None:
        """Announce subagent result to main agent via message bus."""
        status_text = "completed successfully" if status == "ok" else "failed"

        announce_content = f"""[Subagent '{label}' {status_text}]

Task: {task}

Result:
{result}

Summarize this naturally for the user. Keep it brief (1-2 sentences). Do not mention technical details like "subagent" or task IDs."""

        # Inject as system message to trigger main agent
        msg = InboundMessage(
            channel="system",
            sender_id="subagent",
            chat_id=f"{origin['channel']}:{origin['chat_id']}",
            content=announce_content,
        )

        try:
            await self.bus.publish_inbound(msg)
            logger.debug(f"Subagent [{task_id}] announced result to {origin['channel']}:{origin['chat_id']}")
        except Exception as e:
            logger.error(f"Failed to announce result: {e}")

    def _build_subagent_prompt(self) -> str:
        """Build a focused system prompt for subagent."""
        parts = [f"""# Subagent

You are a subagent spawned by the main agent to complete a specific task.
Stay focused on the assigned task. Your final response will be reported back to the main agent.

## Workspace
{self.workspace}"""]

        return "\n\n".join(parts)

    async def cancel_by_session(self, session_key: str) -> int:
        """Cancel all subagents for a given session. Returns count cancelled."""
        tasks = [
            self._running_tasks[tid]
            for tid in self._session_tasks.get(session_key, [])
            if tid in self._running_tasks and not self._running_tasks[tid].done()
        ]
        for t in tasks:
            t.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        return len(tasks)

    def get_running_count(self) -> int:
        """Return the number of currently running subagents."""
        return len(self._running_tasks)
