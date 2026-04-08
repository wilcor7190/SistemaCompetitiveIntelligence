"""Rate limiter with random delays between requests."""

import asyncio
import random

from src.utils.logger import get_logger


class RateLimiter:
    """Random delay between requests to avoid detection."""

    def __init__(
        self,
        delay_min: float = 3.0,
        delay_max: float = 7.0,
    ):
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.logger = get_logger()

    async def wait(self) -> float:
        """Wait a random delay. Returns the actual delay used."""
        delay = random.uniform(self.delay_min, self.delay_max)
        self.logger.debug(f"[rate_limiter] Waiting {delay:.1f}s")
        await asyncio.sleep(delay)
        return delay
