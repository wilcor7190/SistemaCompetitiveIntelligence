"""Async wrapper for Claude API (Anthropic).

Replaces OllamaClient. Used for:
- Insights generation (executive summary, narrative insights)
- Vision OCR fallback (Layer 3 — when DOM scraping fails)

The system works without an API key — insights fall back to stats-based
generation. Only set ANTHROPIC_API_KEY in .env to enable LLM features.
"""

import base64
import os
from pathlib import Path

from dotenv import load_dotenv

from src.utils.logger import get_logger

# Load .env file at module import (one-shot)
load_dotenv()

DEFAULT_MODEL = "claude-opus-4-6"
DEFAULT_MAX_TOKENS = 4000


class ClaudeClient:
    """Async wrapper for Anthropic Claude API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ):
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.max_tokens = max_tokens
        self.logger = get_logger()
        self._client = None

        if self.api_key and self.api_key.startswith("sk-ant-"):
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                self.logger.warning(
                    "[claude] anthropic package not installed. "
                    "Run: pip install anthropic"
                )

    def is_available(self) -> bool:
        """Check if Claude API client is configured and ready."""
        return self._client is not None

    async def chat(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> str | None:
        """Send a text message to Claude and get a text response.

        Args:
            prompt: The user message.
            system: Optional system prompt.
            max_tokens: Override default max output tokens.

        Returns:
            Response text, or None on failure.
        """
        if not self._client:
            return None

        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens or self.max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system:
                kwargs["system"] = system

            response = await self._client.messages.create(**kwargs)

            # Extract text from content blocks
            for block in response.content:
                if block.type == "text":
                    return block.text
            return None

        except Exception as e:
            self.logger.warning(f"[claude] chat failed: {e}")
            return None

    async def vision(
        self,
        image_path: str,
        prompt: str,
        system: str | None = None,
    ) -> str | None:
        """Send an image + prompt to Claude vision and get text back.

        Args:
            image_path: Path to PNG/JPEG image.
            prompt: Question about the image.
            system: Optional system prompt.

        Returns:
            Response text, or None on failure.
        """
        if not self._client:
            return None

        path = Path(image_path)
        if not path.exists():
            self.logger.warning(f"[claude] Image not found: {image_path}")
            return None

        try:
            image_data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
            media_type = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

            kwargs = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "messages": [{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }],
            }
            if system:
                kwargs["system"] = system

            response = await self._client.messages.create(**kwargs)

            for block in response.content:
                if block.type == "text":
                    return block.text
            return None

        except Exception as e:
            self.logger.warning(f"[claude] vision failed: {e}")
            return None
