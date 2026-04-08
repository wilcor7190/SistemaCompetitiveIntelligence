"""Config loader: reads settings.yaml, addresses.json, products.json."""

import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from src.models.schemas import (
    Address,
    Platform,
    ProductReference,
    StoreGroup,
    StoreType,
)


@dataclass
class ScraperConfig:
    delay_min: float
    delay_max: float
    delay_addresses_min: float
    delay_addresses_max: float
    max_retries: int
    retry_delay: float
    page_load_timeout: int
    selector_timeout: int
    screenshot_timeout: int
    network_idle_timeout: int
    headless: bool
    stealth: bool
    user_agent: str
    viewport_width: int
    viewport_height: int
    locale: str
    timezone: str
    geolocation: bool
    circuit_breaker_window: int
    circuit_breaker_threshold: float


@dataclass
class OllamaConfig:
    base_url: str
    timeout: int
    model_vision: str
    model_text_parser: str
    model_insights: str
    model_embeddings: str
    embedding_similarity_threshold: float
    vision_confidence_threshold: float
    max_llm_retries: int


class Config:
    """Central configuration loaded from YAML + JSON files."""

    def __init__(
        self,
        settings: dict,
        addresses: list[Address],
        store_groups: list[StoreGroup],
    ):
        self._settings = settings
        self._addresses = addresses
        self._store_groups = store_groups

    @staticmethod
    def load(
        settings_path: str = "config/settings.yaml",
        addresses_path: str = "config/addresses.json",
        products_path: str = "config/products.json",
    ) -> "Config":
        base = Path(__file__).parent.parent  # desarrollo/

        # Load settings
        with open(base / settings_path, encoding="utf-8") as f:
            settings = yaml.safe_load(f)

        # Load addresses
        with open(base / addresses_path, encoding="utf-8") as f:
            addr_data = json.load(f)
        addresses = [Address(**a) for a in addr_data["addresses"]]

        # Load products (store_groups format)
        with open(base / products_path, encoding="utf-8") as f:
            prod_data = json.load(f)
        store_groups = []
        for sg in prod_data["store_groups"]:
            products = [ProductReference(**p) for p in sg["products"]]
            store_groups.append(
                StoreGroup(
                    store_type=StoreType(sg["store_type"]),
                    store_name=sg.get("store_name"),
                    store_aliases=sg.get("store_aliases", []),
                    products=products,
                    notes=sg.get("notes"),
                )
            )

        return Config(settings, addresses, store_groups)

    def get_platforms(self) -> list[Platform]:
        return [Platform(p) for p in self._settings["scraping"]["platforms"]]

    def get_addresses(self) -> list[Address]:
        return self._addresses

    def get_store_groups(self) -> list[StoreGroup]:
        return self._store_groups

    def get_products(self) -> list[ProductReference]:
        products = []
        for sg in self._store_groups:
            products.extend(sg.products)
        return products

    def get_scraper_config(self) -> ScraperConfig:
        s = self._settings["scraping"]
        b = self._settings["browser"]
        vp = b.get("viewport", {})
        return ScraperConfig(
            delay_min=s["delay_between_requests_min"],
            delay_max=s["delay_between_requests_max"],
            delay_addresses_min=s["delay_between_addresses_min"],
            delay_addresses_max=s["delay_between_addresses_max"],
            max_retries=s["max_retries_per_address"],
            retry_delay=s["retry_delay"],
            page_load_timeout=s["page_load_timeout"],
            selector_timeout=s["selector_timeout"],
            screenshot_timeout=s.get("screenshot_timeout", 5000),
            network_idle_timeout=s.get("network_idle_timeout", 15000),
            headless=b["headless"],
            stealth=b["stealth"],
            user_agent=b["user_agent"],
            viewport_width=vp.get("width", 1920),
            viewport_height=vp.get("height", 1080),
            locale=b["locale"],
            timezone=b["timezone"],
            geolocation=b["geolocation"],
            circuit_breaker_window=s.get("circuit_breaker_window", 10),
            circuit_breaker_threshold=s.get("circuit_breaker_threshold", 0.6),
        )

    def get_ollama_config(self) -> OllamaConfig:
        o = self._settings["ollama"]
        m = o["models"]
        return OllamaConfig(
            base_url=o["base_url"],
            timeout=o["timeout"],
            model_vision=m["vision"],
            model_text_parser=m["text_parser"],
            model_insights=m["insights"],
            model_embeddings=m["embeddings"],
            embedding_similarity_threshold=o["embedding_similarity_threshold"],
            vision_confidence_threshold=o["vision_confidence_threshold"],
            max_llm_retries=o.get("max_llm_retries", 2),
        )

    def get_paths(self) -> dict[str, str]:
        return self._settings["paths"]

    def get_logging_config(self) -> dict:
        return self._settings["logging"]

    def get_screenshot_config(self) -> dict:
        return self._settings.get("screenshots", {})

    @property
    def settings(self) -> dict:
        return self._settings
