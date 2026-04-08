"""Screenshot capture and naming utility."""

import re
import time
from pathlib import Path

from src.utils.logger import get_logger


def make_screenshot_path(
    platform: str,
    address_label: str,
    output_dir: str = "data/screenshots",
) -> str:
    """Generate a screenshot file path with standardized naming.

    Format: {platform}_{address_slug}_{YYYYMMDD}_{HHMMSS}.png
    """
    slug = re.sub(r"[^a-zA-Z0-9]", "-", address_label).strip("-")[:40]
    slug = re.sub(r"-+", "-", slug).lower()
    ts = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{platform}_{slug}_{ts}.png"

    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)

    return str(path / filename)


async def capture_screenshot(
    page,
    platform: str,
    address_label: str,
    output_dir: str = "data/screenshots",
) -> str | None:
    """Capture a screenshot with standardized naming."""
    logger = get_logger()
    filepath = make_screenshot_path(platform, address_label, output_dir)

    try:
        await page.screenshot(path=filepath, full_page=False)
        logger.debug(f"Screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.warning(f"Screenshot failed: {e}")
        return None
