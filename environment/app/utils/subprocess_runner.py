"""Subprocess execution wrapper with consistent error handling."""

import subprocess
from utils.logger import get_logger

logger = get_logger(__name__)


def run_command(cmd: list[str], label: str = "") -> subprocess.CompletedProcess:
    """Run a shell command and raise with context on failure."""
    logger.debug("Running: %s", " ".join(cmd))
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        msg = f"Command failed ({label}): {e.stderr.strip()}"
        logger.error(msg)
        raise RuntimeError(msg) from e