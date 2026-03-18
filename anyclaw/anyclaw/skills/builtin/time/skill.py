"""时间技能"""
from datetime import datetime
from anyclaw.skills.base import Skill


class TimeSkill(Skill):
    """Get current time"""

    async def execute(self, **kwargs) -> str:
        """Get current time"""
        now = datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"
