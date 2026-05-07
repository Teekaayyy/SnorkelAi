"""Simple progress reporting for pipeline stages."""

from utils.logger import get_logger

logger = get_logger(__name__)


def report_progress(stage: str, current: int, total: int) -> None:
    """Log progress of a stage as current/total."""
    pct = int((current / total) * 100) if total > 0 else 0
    logger.info("[%s] %d/%d (%d%%)", stage, current, total, pct)