"""Echo 技能"""
from anyclaw.skills.base import Skill


class EchoSkill(Skill):
    """Echo back the input message"""

    async def execute(self, message: str = "", **kwargs) -> str:
        """Echo the input message"""
        if not message:
            return "Please provide a message to echo"
        return f"Echo: {message}"
