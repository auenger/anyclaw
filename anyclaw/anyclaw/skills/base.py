"""技能基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class Skill(ABC):
    """技能基类"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.description = self.__doc__ or "No description"

    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """执行技能"""
        pass

    def get_info(self) -> Dict[str, str]:
        """获取技能信息"""
        return {
            "name": self.name,
            "description": self.description
        }
