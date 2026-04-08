"""Async wrapper for Ollama local LLM."""

import os

import aiohttp

from src.utils.logger import get_logger


class OllamaClient:
    """Async client for Ollama API."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 60000,
    ):
        self.base_url = (
            base_url
            or os.environ.get("OLLAMA_BASE_URL")
            or "http://localhost:11434"
        )
        self.timeout = aiohttp.ClientTimeout(total=timeout / 1000)
        self.logger = get_logger()

    async def is_available(self) -> bool:
        """Check if Ollama server is reachable."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """List available models."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status != 200:
                        return []
                    data = await resp.json()
                    return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            self.logger.warning(f"Failed to list Ollama models: {e}")
            return []

    async def chat(
        self,
        model: str,
        messages: list[dict],
        format: str | None = None,
    ) -> dict | None:
        """Send a chat request to Ollama.

        Args:
            model: Model name (e.g. 'qwen3-vl:8b').
            messages: List of message dicts with 'role' and 'content'.
            format: Optional response format ('json').

        Returns:
            Response dict or None on failure.
        """
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if format:
            payload["format"] = format

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/chat", json=payload
                ) as resp:
                    if resp.status != 200:
                        self.logger.warning(
                            f"Ollama chat error: HTTP {resp.status}"
                        )
                        return None
                    data = await resp.json()
                    return data.get("message", {})
        except Exception as e:
            self.logger.warning(f"Ollama chat failed: {e}")
            return None

    async def embed(
        self,
        model: str,
        input_text: str,
    ) -> list[float] | None:
        """Get embedding vector for text.

        Args:
            model: Embedding model name (e.g. 'nomic-embed-text').
            input_text: Text to embed.

        Returns:
            Embedding vector or None on failure.
        """
        payload = {
            "model": model,
            "input": input_text,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/embed", json=payload
                ) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    embeddings = data.get("embeddings", [])
                    return embeddings[0] if embeddings else None
        except Exception as e:
            self.logger.warning(f"Ollama embed failed: {e}")
            return None
