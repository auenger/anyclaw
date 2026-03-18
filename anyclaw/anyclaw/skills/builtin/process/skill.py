"""进程管理技能

管理后台进程：启动、监控、终止。
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List
from enum import Enum

from anyclaw.skills.base import Skill


class ProcessStatus(Enum):
    """进程状态"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


@dataclass
class ProcessSession:
    """进程会话"""
    id: str
    command: str
    status: ProcessStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    exit_code: Optional[int] = None
    stdout: List[str] = field(default_factory=list)
    stderr: List[str] = field(default_factory=list)
    process: Optional[asyncio.subprocess.Process] = None


class ProcessSkill(Skill):
    """Manage background processes"""

    def __init__(self):
        super().__init__()
        self.sessions: Dict[str, ProcessSession] = {}

    async def execute(
        self,
        action: str = "list",
        command: str = "",
        session_id: str = "",
        timeout: int = 300,
        **kwargs
    ) -> str:
        """Execute process management action

        Args:
            action: Operation to perform (start, status, log, kill, list)
            command: Command to run (for start action)
            session_id: Session ID (for status/log/kill actions)
            timeout: Execution timeout in seconds

        Returns:
            Operation result
        """
        action = action.lower().strip()

        if action == "start":
            return await self._start_process(command, timeout)
        elif action == "status":
            return self._get_status(session_id)
        elif action == "log":
            return self._get_log(session_id)
        elif action == "kill":
            return await self._kill_process(session_id)
        elif action == "list":
            return self._list_processes()
        else:
            return f"Unknown action: {action}. Available: start, status, log, kill, list"

    async def _start_process(self, command: str, timeout: int) -> str:
        """启动后台进程"""
        if not command:
            return "Error: No command provided"

        session_id = str(uuid.uuid4())[:8]
        session = ProcessSession(
            id=session_id,
            command=command,
            status=ProcessStatus.RUNNING,
            started_at=datetime.now()
        )
        self.sessions[session_id] = session

        try:
            # 创建进程
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            session.process = proc

            # 启动后台任务收集输出
            asyncio.create_task(self._collect_output(session, timeout))

            return f"Process started\nSession ID: {session_id}\nCommand: {command}"

        except Exception as e:
            session.status = ProcessStatus.FAILED
            session.completed_at = datetime.now()
            return f"Error starting process: {str(e)}"

    async def _collect_output(self, session: ProcessSession, timeout: int):
        """收集进程输出"""
        proc = session.process
        if not proc:
            return

        try:
            # 等待进程完成（带超时）
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(),
                timeout=timeout
            )

            session.stdout.append(stdout.decode('utf-8', errors='replace'))
            session.stderr.append(stderr.decode('utf-8', errors='replace'))
            session.exit_code = proc.returncode
            session.status = ProcessStatus.COMPLETED if proc.returncode == 0 else ProcessStatus.FAILED

        except asyncio.TimeoutError:
            # 超时，终止进程
            try:
                proc.kill()
                await proc.wait()
            except Exception:
                pass
            session.status = ProcessStatus.KILLED
            session.stderr.append(f"\n[Process killed after {timeout}s timeout]")

        except Exception as e:
            session.status = ProcessStatus.FAILED
            session.stderr.append(f"\n[Error: {str(e)}]")

        finally:
            session.completed_at = datetime.now()
            session.process = None

    def _get_status(self, session_id: str) -> str:
        """获取进程状态"""
        if not session_id:
            return "Error: No session ID provided"

        session = self.sessions.get(session_id)
        if not session:
            return f"Error: Session {session_id} not found"

        lines = [
            f"Session: {session.id}",
            f"Command: {session.command}",
            f"Status: {session.status.value}",
            f"Started: {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        if session.completed_at:
            lines.append(f"Completed: {session.completed_at.strftime('%Y-%m-%d %H:%M:%S')}")

        if session.exit_code is not None:
            lines.append(f"Exit code: {session.exit_code}")

        return "\n".join(lines)

    def _get_log(self, session_id: str) -> str:
        """获取进程输出"""
        if not session_id:
            return "Error: No session ID provided"

        session = self.sessions.get(session_id)
        if not session:
            return f"Error: Session {session_id} not found"

        parts = [f"=== Session {session_id} ==="]

        if session.stdout:
            parts.append("\n[stdout]")
            parts.extend(session.stdout)

        if session.stderr:
            parts.append("\n[stderr]")
            parts.extend(session.stderr)

        if not session.stdout and not session.stderr:
            parts.append("(no output yet)")

        return "\n".join(parts)

    async def _kill_process(self, session_id: str) -> str:
        """终止进程"""
        if not session_id:
            return "Error: No session ID provided"

        session = self.sessions.get(session_id)
        if not session:
            return f"Error: Session {session_id} not found"

        if session.status != ProcessStatus.RUNNING:
            return f"Process is not running (status: {session.status.value})"

        proc = session.process
        if proc:
            try:
                proc.kill()
                await proc.wait()
                session.status = ProcessStatus.KILLED
                session.completed_at = datetime.now()
                return f"Process {session_id} killed"
            except Exception as e:
                return f"Error killing process: {str(e)}"
        else:
            return "Process handle not available"

    def _list_processes(self) -> str:
        """列出所有进程"""
        if not self.sessions:
            return "No processes"

        lines = ["Processes:", ""]
        for session in self.sessions.values():
            status_emoji = {
                ProcessStatus.RUNNING: "🔄",
                ProcessStatus.COMPLETED: "✅",
                ProcessStatus.FAILED: "❌",
                ProcessStatus.KILLED: "💀",
            }.get(session.status, "❓")

            lines.append(
                f"  {status_emoji} {session.id}: {session.command[:50]} "
                f"({session.status.value})"
            )

        return "\n".join(lines)

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理旧会话"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=max_age_hours)

        to_remove = [
            sid for sid, session in self.sessions.items()
            if session.completed_at and session.completed_at < cutoff
        ]

        for sid in to_remove:
            del self.sessions[sid]

        return len(to_remove)
