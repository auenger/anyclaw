"""Channel Manager - 管理多个 Channel 和后台服务"""

import asyncio
import logging
from typing import Any, Optional, Dict

from anyclaw.cron.service import CronService
from anyclaw.cron.types import CronJob


logger = logging.getLogger(__name__)


class ChannelManager:
    """Channel Manager - 管理所有 Channel 和后台服务"""

    def __init__(self):
        self.channels: Dict[str, Any] = {}
        self.cron_service: Optional[CronService] = None

    def register_channel(self, name: str, channel: Any) -> None:
        """注册一个 Channel"""
        self.channels[name] = channel
        logger.info(f"Registered channel: {name}")

    def get_channel(self, name: str) -> Optional[Any]:
        """获取已注册的 Channel"""
        return self.channels.get(name)

    def set_cron_service(self, cron_service: CronService) -> None:
        """设置 Cron 服务"""
        self.cron_service = cron_service
        logger.info("CronService set in ChannelManager")

    async def start_cron(self) -> None:
        """启动 Cron 服务"""
        if self.cron_service:
            await self.cron_service.start()
            logger.info("CronService started")

    async def stop_cron(self) -> None:
        """停止 Cron 服务"""
        if self.cron_service:
            self.cron_service.stop()
            logger.info("CronService stopped")

    async def cron_job_callback(self, job: CronJob) -> Optional[str]:
        """Cron 任务执行回调（由 Channel 调用）"""
        if self.cron_service:
            return await self.cron_service.on_job(job)
        return None

    def get_cron_service(self) -> Optional[CronService]:
        """获取 Cron 服务实例"""
        return self.cron_service
