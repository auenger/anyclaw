"""Channel registry and auto-discovery."""

from __future__ import annotations

import importlib
import importlib.util
import logging
from typing import Any, Type

from anyclaw.channels.base import BaseChannel

logger = logging.getLogger(__name__)

# Built-in channel modules
BUILTIN_CHANNELS = [
    ("anyclaw.channels.cli", "CLIChannel"),
    ("anyclaw.channels.feishu", "FeishuChannel"),
    ("anyclaw.channels.discord", "DiscordChannel"),
]


def _try_import(module_name: str, class_name: str) -> Type[BaseChannel] | None:
    """Try to import a channel class, return None if not available."""
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name, None)
    except ImportError as e:
        logger.debug(f"Channel {module_name}.{class_name} not available: {e}")
        return None
    except Exception as e:
        logger.warning(f"Error loading channel {module_name}.{class_name}: {e}")
        return None


def discover_builtin() -> dict[str, Type[BaseChannel]]:
    """Discover built-in channel classes."""
    channels: dict[str, Type[BaseChannel]] = {}

    for module_name, class_name in BUILTIN_CHANNELS:
        cls = _try_import(module_name, class_name)
        if cls and issubclass(cls, BaseChannel):
            channels[cls.name] = cls

    return channels


def discover_plugins() -> dict[str, Type[BaseChannel]]:
    """Discover channel plugins via entry points."""
    channels: dict[str, Type[BaseChannel]] = {}

    try:
        # Python 3.10+ uses importlib.metadata
        import sys

        if sys.version_info >= (3, 10):
            from importlib.metadata import entry_points
        else:
            from importlib_metadata import entry_points

        eps = entry_points()
        # Try different group names
        for group in ["anyclaw.channels", "anyclaw.plugins"]:
            try:
                if hasattr(eps, "select"):
                    group_eps = eps.select(group=group)
                else:
                    group_eps = eps.get(group, [])

                for ep in group_eps:
                    try:
                        cls = ep.load()
                        if issubclass(cls, BaseChannel):
                            channels[cls.name] = cls
                    except Exception as e:
                        logger.warning(f"Failed to load plugin {ep.name}: {e}")
            except Exception:
                continue
    except ImportError:
        pass

    return channels


def discover_all() -> dict[str, Type[BaseChannel]]:
    """Discover all available channels (builtin + plugins)."""
    channels = discover_builtin()
    channels.update(discover_plugins())
    return channels


def get_channel_class(name: str) -> Type[BaseChannel] | None:
    """Get a channel class by name."""
    return discover_all().get(name)
