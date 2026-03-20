"""Channel Manager - 管理多个 Channel 和后台服务"""

import asyncio
import logging
from typing import Any, Optional, Dict, List, TYPE_CHECKING

from anyclaw.cron.service import CronService
from anyclaw.cron.types import CronJob

if TYPE_CHECKING:
    from anyclaw.config.loader import Config
    from anyclaw.bus.queue import MessageBus


logger = logging.getLogger(__name__)


class ChannelManager:
    """Channel Manager - 管理所有 Channel 和后台服务"""

    def __init__(
        self,
        config: Optional["Config"] = None,
        bus: Optional["MessageBus"] = None
    ):
        self.config = config
        self.bus = bus
        self.channels: Dict[str, Any] = {}
        self.cron_service: Optional[CronService] = None

        # 从 config 初始化 channels
        if config and bus:
            self._init_channels_from_config()

    def _init_channels_from_config(self) -> None:
        """从配置初始化所有启用的 channels"""
        if not self.config or not self.bus:
            return

        # CLI Channel
        if hasattr(self.config.channels, 'cli') and self.config.channels.cli.enabled:
            from anyclaw.channels.cli import CLIChannel
            cli_channel = CLIChannel(self.config.channels.cli, self.bus)
            self.register_channel('cli', cli_channel)

        # Discord Channel
        if hasattr(self.config.channels, 'discord') and self.config.channels.discord.enabled:
            try:
                from anyclaw.channels.discord import DiscordChannel
                discord_channel = DiscordChannel(self.config.channels.discord, self.bus)
                self.register_channel('discord', discord_channel)
            except ImportError as e:
                logger.warning(f"Discord channel not available: {e}")

        # Feishu Channel
        if hasattr(self.config.channels, 'feishu') and self.config.channels.feishu.enabled:
            try:
                from anyclaw.channels.feishu import FeishuChannel
                feishu_channel = FeishuChannel(self.config.channels.feishu, self.bus)
                self.register_channel('feishu', feishu_channel)
            except ImportError as e:
                logger.warning(f"Feishu channel not available: {e}")

        logger.info(f"Initialized {len(self.channels)} channels from config")

    @property
    def enabled_channels(self) -> List[str]:
        """获取所有启用的 channel 名称"""
        return list(self.channels.keys())

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

    async def start_all(self) -> None:
        """启动所有已注册的 Channel"""
        if not self.channels:
            logger.warning("No channels to start")
            return

        tasks = []
        for name, channel in self.channels.items():
            logger.info(f"Starting channel: {name}")
            tasks.append(channel.start())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"All {len(self.channels)} channels started")

    async def stop_all(self) -> None:
        """停止所有已注册的 Channel"""
        if not self.channels:
            return

        tasks = []
        for name, channel in self.channels.items():
            logger.info(f"Stopping channel: {name}")
            tasks.append(channel.stop())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
            logger.info("All channels stopped")
