"""Weather 技能

使用 wttr.in 查询天气信息。
"""

import asyncio
import shutil
from anyclaw.skills.base import Skill


class WeatherSkill(Skill):
    """Query weather information using wttr.in"""

    async def execute(self, location: str = "", **kwargs) -> str:
        """Query weather for a location

        Args:
            location: 城市名称或位置（如：Beijing, Shanghai, London）

        Returns:
            天气信息字符串
        """
        if not location:
            location = "Beijing"  # 默认北京

        # 检查 curl 是否可用
        if not shutil.which("curl"):
            return "Weather skill requires 'curl' command. Please install curl first."

        try:
            # 使用 wttr.in 查询天气
            process = await asyncio.create_subprocess_exec(
                "curl", "-s", f"wttr.in/{location}?format=3&lang=zh",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                result = stdout.decode("utf-8").strip()
                if result:
                    return f"Weather for {location}: {result}"
                else:
                    return f"Unable to get weather for {location}"
            else:
                return f"Failed to query weather: {stderr.decode('utf-8')}"

        except Exception as e:
            return f"Error querying weather: {str(e)}"
