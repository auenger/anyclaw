"""Tool 注册表 - 管理和执行工具"""

from typing import Any, Dict, List, Optional

from .base import Tool


class ToolRegistry:
    """
    Tool 注册表

    管理所有注册的工具，提供执行接口
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册工具"""
        self._tools[tool.name] = tool

    def unregister(self, name: str) -> None:
        """注销工具"""
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self._tools.get(name)

    def has(self, name: str) -> bool:
        """检查工具是否存在"""
        return name in self._tools

    def get_definitions(self) -> List[Dict[str, Any]]:
        """获取所有工具的 OpenAI 格式定义"""
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute(self, name: str, params: Dict[str, Any]) -> str:
        """
        执行工具

        Args:
            name: 工具名称
            params: 工具参数

        Returns:
            执行结果
        """
        _HINT = "\n\n[分析上面的错误，尝试不同的方法。]"

        tool = self._tools.get(name)
        if not tool:
            available = ", ".join(self.tool_names) if self.tool_names else "无"
            return f"错误: 工具 '{name}' 不存在。可用工具: {available}"

        try:
            # 类型转换
            if hasattr(tool, 'cast_params'):
                params = tool.cast_params(params)

            # 参数验证
            if hasattr(tool, 'validate_params'):
                errors = tool.validate_params(params)
                if errors:
                    return f"错误: 工具 '{name}' 参数无效: " + "; ".join(errors) + _HINT

            # 执行
            result = await tool.execute(**params)

            # 检查错误结果
            if isinstance(result, str) and result.startswith("错误"):
                return result + _HINT

            return result

        except Exception as e:
            return f"执行 {name} 时出错: {str(e)}" + _HINT

    @property
    def tool_names(self) -> List[str]:
        """获取所有工具名称"""
        return list(self._tools.keys())

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
