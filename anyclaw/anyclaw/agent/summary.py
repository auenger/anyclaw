"""迭代限制智能汇报生成器

当 Agent 达到最大迭代次数时，生成包含以下内容的智能汇报：
- 已执行工具摘要
- 执行状态统计
- 当前处理阶段
- 卡点诊断
- 下一步建议
"""

import json
import logging
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from litellm import acompletion

from anyclaw.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ToolCallRecord:
    """工具调用记录"""

    name: str
    arguments: Dict[str, Any]
    result_summary: str  # 结果摘要（截断）
    duration_ms: int
    success: bool
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "arguments": self.arguments,
            "result_summary": self.result_summary,
            "duration_ms": self.duration_ms,
            "success": self.success,
        }


@dataclass
class IterationStatistics:
    """迭代统计信息"""

    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_duration_ms: int = 0
    unique_tools: set = field(default_factory=set)
    repeated_calls: Dict[str, int] = field(default_factory=dict)  # tool_name -> count
    detected_loops: List[Dict[str, Any]] = field(default_factory=list)  # 检测到的循环


class IterationSummaryCollector:
    """迭代摘要收集器 - 收集工具调用数据并检测循环"""

    # 检测循环的阈值：同一工具+参数被调用超过此次数视为循环
    LOOP_DETECTION_THRESHOLD = 3

    # 结果摘要最大长度
    RESULT_SUMMARY_MAX_CHARS = 200

    def __init__(self):
        self._tool_calls: List[ToolCallRecord] = []
        self._call_signatures: Counter = Counter()  # 用于检测重复调用

    def record_tool_call(
        self,
        name: str,
        arguments: Dict[str, Any],
        result: str,
        duration_ms: int,
        success: bool = True,
    ) -> None:
        """记录一次工具调用"""
        # 截断结果摘要
        if len(result) > self.RESULT_SUMMARY_MAX_CHARS:
            result_summary = result[: self.RESULT_SUMMARY_MAX_CHARS] + "..."
        else:
            result_summary = result

        record = ToolCallRecord(
            name=name,
            arguments=arguments,
            result_summary=result_summary,
            duration_ms=duration_ms,
            success=success,
        )
        self._tool_calls.append(record)

        # 更新调用签名计数（用于循环检测）
        signature = self._make_call_signature(name, arguments)
        self._call_signatures[signature] += 1

    def _make_call_signature(self, name: str, arguments: Dict[str, Any]) -> str:
        """生成调用签名（用于检测重复调用）"""
        # 只使用工具名和参数的关键部分
        try:
            # 序列化参数，忽略可能导致误判的动态值
            stable_args: Dict[str, Any] = {}
            for k, v in arguments.items():
                if isinstance(v, str) and len(v) > 100:
                    stable_args[k] = v[:100] + "..."
                else:
                    stable_args[k] = v
            return f"{name}:{json.dumps(stable_args, sort_keys=True, default=str)}"
        except Exception:
            return f"{name}:{str(arguments)}"

    def collect_statistics(self) -> IterationStatistics:
        """收集统计信息"""
        stats = IterationStatistics()
        stats.total_calls = len(self._tool_calls)
        stats.successful_calls = sum(1 for tc in self._tool_calls if tc.success)
        stats.failed_calls = stats.total_calls - stats.successful_calls
        stats.total_duration_ms = sum(tc.duration_ms for tc in self._tool_calls)
        stats.unique_tools = {tc.name for tc in self._tool_calls}

        # 检测重复调用和循环
        for signature, count in self._call_signatures.items():
            if count >= self.LOOP_DETECTION_THRESHOLD:
                tool_name = signature.split(":", 1)[0]
                stats.repeated_calls[tool_name] = count
                stats.detected_loops.append(
                    {
                        "tool": tool_name,
                        "count": count,
                        "signature": signature,
                    }
                )

        return stats

    def get_tool_call_timeline(self) -> List[Dict[str, Any]]:
        """获取工具调用时间线"""
        return [tc.to_dict() for tc in self._tool_calls]

    def has_tool_calls(self) -> bool:
        """检查是否有工具调用"""
        return len(self._tool_calls) > 0

    def clear(self) -> None:
        """清空记录"""
        self._tool_calls.clear()
        self._call_signatures.clear()


class IterationSummaryGenerator:
    """迭代摘要生成器 - 调用 LLM 生成智能汇报"""

    # 汇报生成 Prompt 模板
    SUMMARY_PROMPT_TEMPLATE = """# 工作进度分析任务

你是一个 AI Agent 的工作进度分析器。Agent 在处理用户请求时达到了最大迭代次数限制。
请分析以下执行记录，生成一份简洁、有意义的进度汇报。

## 用户原始请求
{user_request}

## 执行统计
- 总迭代次数: {total_iterations}
- 工具调用次数: {total_calls}
- 成功: {successful_calls}, 失败: {failed_calls}
- 总耗时: {total_duration_ms}ms

## 工具调用时间线
{tool_timeline}

## 检测到的问题
{detected_issues}

## 分析要求

请生成一份包含以下内容的汇报（使用中文，简洁明了）：

1. **执行摘要** (1-2 句话): 概述 Agent 执行了什么操作
2. **当前阶段**: 分析任务执行到哪一步了
3. **卡点诊断**: 如果有循环或失败，分析可能的原因
4. **下一步建议**: 给用户具体的后续操作建议

注意：
- 汇报应该简洁，不要重复工具调用的详细内容
- 重点关注问题和解决方案
- 如果一切正常只是迭代不够，建议增加迭代次数或简化任务
"""

    def __init__(
        self,
        enabled: bool = True,
        max_tokens: int = 1000,
    ):
        self.enabled = enabled
        self.max_tokens = max_tokens

    async def generate(
        self,
        collector: IterationSummaryCollector,
        messages: List[Dict[str, Any]],
        max_iterations: int,
    ) -> str:
        """生成智能汇报

        Args:
            collector: 迭代数据收集器
            messages: 对话历史消息
            max_iterations: 最大迭代次数

        Returns:
            生成的汇报文本
        """
        if not self.enabled:
            return "达到最大迭代次数"

        # 如果没有工具调用，返回简化汇报
        if not collector.has_tool_calls():
            return self._generate_simple_summary(max_iterations, messages)

        try:
            # 收集统计数据
            stats = collector.collect_statistics()
            timeline = collector.get_tool_call_timeline()
            user_request = self._extract_user_request(messages)

            # 构建 Prompt
            prompt = self._build_prompt(
                user_request=user_request,
                total_iterations=max_iterations,
                stats=stats,
                timeline=timeline,
            )

            # 调用 LLM 生成汇报
            summary = await self._call_llm(prompt)
            return summary

        except Exception as e:
            logger.error(f"Failed to generate iteration summary: {e}")
            # 降级：返回基础汇报
            return self._generate_fallback_summary(collector, max_iterations)

    def _extract_user_request(self, messages: List[Dict[str, Any]]) -> str:
        """从消息历史中提取用户原始请求"""
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                if isinstance(content, str):
                    return content[:500]  # 限制长度
        return "未知请求"

    def _build_prompt(
        self,
        user_request: str,
        total_iterations: int,
        stats: IterationStatistics,
        timeline: List[Dict[str, Any]],
    ) -> str:
        """构建分析 Prompt"""
        # 格式化工具时间线
        timeline_str = ""
        for i, tc in enumerate(timeline[-20:], 1):  # 最多显示最近 20 条
            status = "✓" if tc["success"] else "✗"
            args_str = self._format_arguments(tc["arguments"])
            timeline_str += f"{i}. {status} {tc['name']}({args_str}) - {tc['duration_ms']}ms\n"

        # 格式化检测到的问题
        issues_str = "无"
        if stats.detected_loops:
            issues_str = "检测到重复调用循环:\n"
            for loop in stats.detected_loops:
                issues_str += f"- {loop['tool']}: 被调用 {loop['count']} 次\n"
        if stats.failed_calls > 0:
            if issues_str == "无":
                issues_str = ""
            issues_str += f"- 有 {stats.failed_calls} 次工具调用失败\n"

        return self.SUMMARY_PROMPT_TEMPLATE.format(
            user_request=user_request,
            total_iterations=total_iterations,
            total_calls=stats.total_calls,
            successful_calls=stats.successful_calls,
            failed_calls=stats.failed_calls,
            total_duration_ms=stats.total_duration_ms,
            tool_timeline=timeline_str or "无",
            detected_issues=issues_str,
        )

    def _format_arguments(self, arguments: Dict[str, Any]) -> str:
        """格式化参数为简短字符串"""
        if not arguments:
            return ""
        parts = []
        for k, v in list(arguments.items())[:3]:  # 最多显示 3 个参数
            if isinstance(v, str):
                v_str = v[:30] + "..." if len(v) > 30 else v
            else:
                v_str = str(v)[:30]
            parts.append(f"{k}={v_str}")
        return ", ".join(parts)

    async def _call_llm(self, prompt: str) -> str:
        """调用 LLM 生成汇报"""
        model = settings.llm_model

        # 规范化模型名称
        if model.startswith("zai/"):
            model = model.replace("zai/", "openai/", 1)
        elif "/" not in model:
            if settings.llm_provider == "zai":
                model = f"openai/{model}"

        kwargs: Dict[str, Any] = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,  # 低温度，更确定性的输出
            "max_tokens": self.max_tokens,
            "timeout": 30,  # 较短超时
        }

        # 添加 provider 特定参数
        if settings.llm_provider == "zai":
            from anyclaw.providers.zai import get_zai_provider

            provider = get_zai_provider()
            if provider.is_configured():
                kwargs.update(provider.get_completion_kwargs(model))

        response = await acompletion(**kwargs)
        return response.choices[0].message.content or ""

    def _generate_simple_summary(
        self, max_iterations: int, messages: List[Dict[str, Any]]
    ) -> str:
        """生成简化汇报（无工具调用时）"""
        return f"""## 工作进度汇报

**执行摘要**: Agent 处理您的请求时达到了 {max_iterations} 次迭代限制，期间没有执行任何工具操作。

**当前阶段**: 可能正在进行纯文本推理或需要更多信息。

**下一步建议**:
- 如果任务复杂，可以尝试增加迭代次数
- 考虑将任务拆分为更小的步骤
- 提供更明确的指令或上下文"""

    def _generate_fallback_summary(
        self, collector: IterationSummaryCollector, max_iterations: int
    ) -> str:
        """生成降级汇报（LLM 调用失败时）"""
        stats = collector.collect_statistics()
        timeline = collector.get_tool_call_timeline()

        # 构建基础汇报
        parts = [
            "## 工作进度汇报",
            "",
            (f"**执行摘要**: 达到 {max_iterations} 次迭代限制，"
             f"执行了 {stats.total_calls} 次工具调用。"),
            "",
            (f"**统计**: 成功 {stats.successful_calls} 次, "
             f"失败 {stats.failed_calls} 次, 耗时 {stats.total_duration_ms}ms"),
        ]

        # 添加循环检测信息
        if stats.detected_loops:
            parts.append("")
            parts.append("**检测到的问题**:")
            for loop in stats.detected_loops:
                parts.append(f"- {loop['tool']} 被重复调用 {loop['count']} 次")

        # 添加最近工具调用
        if timeline:
            parts.append("")
            parts.append("**最近的工具调用**:")
            for tc in timeline[-5:]:
                status = "✓" if tc["success"] else "✗"
                parts.append(f"- {status} {tc['name']}")

        parts.append("")
        parts.append("**下一步建议**: 检查任务进度，可能需要增加迭代次数或调整策略。")

        return "\n".join(parts)


# 便捷函数：创建全局实例
_collector: Optional[IterationSummaryCollector] = None


def get_summary_collector() -> IterationSummaryCollector:
    """获取全局摘要收集器实例"""
    global _collector
    if _collector is None:
        _collector = IterationSummaryCollector()
    return _collector


def reset_summary_collector() -> None:
    """重置全局摘要收集器"""
    global _collector
    if _collector:
        _collector.clear()
    _collector = IterationSummaryCollector()
