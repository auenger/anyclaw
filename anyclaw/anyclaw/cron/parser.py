"""Cron expression parser with full 5-field syntax support."""

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

try:
    from croniter import croniter
    CRONITER_AVAILABLE = True
except ImportError:
    CRONITER_AVAILABLE = False
    croniter = None  # type: ignore

if TYPE_CHECKING:
    from croniter import croniter as CroniterType  # noqa: N812

logger = logging.getLogger(__name__)


class CronParser:
    """Full cron expression parser supporting standard 5-field syntax.

    Supports:
    - Standard expressions: "0 9 * * *"
    - Step expressions: "*/5 * * * *"
    - List expressions: "0 9,12,18 * * *"
    - Range expressions: "0 9-17 * * 1-5"
    - Timezone support via IANA timezone strings
    """

    def __init__(self, expr: str, tz: Optional[str] = None):
        """Initialize parser with cron expression.

        Args:
            expr: Standard 5-field cron expression
            tz: Optional IANA timezone string (e.g. "Asia/Shanghai")
        """
        if not CRONITER_AVAILABLE:
            raise RuntimeError("croniter library not installed. Run: poetry install")

        self.expr = expr
        self.tz = tz
        self._cron: Optional[croniter] = None

    @staticmethod
    def validate(expr: str) -> bool:
        """Validate cron expression.

        Args:
            expr: Cron expression to validate

        Returns:
            True if expression is valid, False otherwise
        """
        if not CRONITER_AVAILABLE:
            logger.warning("croniter not available, validation skipped")
            return True  # Fallback: allow if library not available

        try:
            croniter(expr)
            return True
        except (ValueError, TypeError) as e:
            logger.debug(f"Invalid cron expression '{expr}': {e}")
            return False

    def _get_cron(self, base: Optional[datetime] = None) -> "CroniterType":
        """Get or create croniter instance."""
        if self._cron is None or base is not None:
            if base is None:
                base = datetime.now(timezone.utc)
            self._cron = croniter(self.expr, base)
        return self._cron

    def get_next(self, base: Optional[datetime] = None) -> Optional[datetime]:
        """Get next execution time.

        Args:
            base: Base datetime to calculate from (default: now in UTC)

        Returns:
            Next execution datetime in UTC, or None if invalid
        """
        try:
            if base is None:
                base = datetime.now(timezone.utc)

            # If timezone specified, convert base to that timezone first
            if self.tz:
                try:
                    import zoneinfo
                    tz_info = zoneinfo.ZoneInfo(self.tz)
                    base_local = base.astimezone(tz_info)
                    cron = croniter(self.expr, base_local)
                    next_local = cron.get_next(datetime)
                    # Convert back to UTC
                    return next_local.astimezone(timezone.utc)
                except Exception as e:
                    logger.warning(f"Failed to use timezone '{self.tz}': {e}, falling back to UTC")

            cron = croniter(self.expr, base)
            return cron.get_next(datetime)
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to get next run for '{self.expr}': {e}")
            return None

    def get_next_n(self, n: int, base: Optional[datetime] = None) -> list[datetime]:
        """Get next N execution times.

        Args:
            n: Number of future times to return
            base: Base datetime to calculate from (default: now in UTC)

        Returns:
            List of next N execution datetimes in UTC
        """
        try:
            if base is None:
                base = datetime.now(timezone.utc)

            results = []

            # If timezone specified, convert base to that timezone first
            if self.tz:
                try:
                    import zoneinfo
                    tz_info = zoneinfo.ZoneInfo(self.tz)
                    base_local = base.astimezone(tz_info)
                    cron = croniter(self.expr, base_local)
                    for _ in range(n):
                        next_local = cron.get_next(datetime)
                        results.append(next_local.astimezone(timezone.utc))
                    return results
                except Exception as e:
                    logger.warning(f"Failed to use timezone '{self.tz}': {e}, falling back to UTC")

            cron = croniter(self.expr, base)
            for _ in range(n):
                results.append(cron.get_next(datetime))
            return results
        except (ValueError, TypeError) as e:
            logger.error(f"Failed to get next {n} runs for '{self.expr}': {e}")
            return []

    def get_next_ms(self, base: Optional[datetime] = None) -> Optional[int]:
        """Get next execution time as milliseconds timestamp.

        Args:
            base: Base datetime to calculate from (default: now in UTC)

        Returns:
            Next execution time in milliseconds, or None if invalid
        """
        next_dt = self.get_next(base)
        if next_dt:
            return int(next_dt.timestamp() * 1000)
        return None


def validate_cron_expr(expr: str) -> bool:
    """Validate cron expression (convenience function).

    Args:
        expr: Cron expression to validate

    Returns:
        True if expression is valid, False otherwise
    """
    return CronParser.validate(expr)


def compute_next_run_ms(
    expr: str, tz: Optional[str] = None, now_ms: Optional[int] = None
) -> Optional[int]:
    """Compute next run time in milliseconds.

    Args:
        expr: Cron expression
        tz: Optional IANA timezone
        now_ms: Current time in ms (default: now)

    Returns:
        Next run time in milliseconds, or None if invalid
    """
    try:
        if now_ms:
            base = datetime.fromtimestamp(now_ms / 1000, tz=timezone.utc)
        else:
            base = datetime.now(timezone.utc)

        parser = CronParser(expr, tz)
        return parser.get_next_ms(base)
    except Exception as e:
        logger.error(f"Failed to compute next run for '{expr}': {e}")
        return None
