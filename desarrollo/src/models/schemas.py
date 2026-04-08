"""Pydantic models for the Competitive Intelligence scraping system."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ZoneType(str, Enum):
    CENTRO = "centro"
    PREMIUM = "premium"
    RESIDENCIAL = "residencial"
    PERIFERIA = "periferia"
    CORPORATIVO = "corporativo"
    EXPANSION = "expansion"


class Platform(str, Enum):
    RAPPI = "rappi"
    UBER_EATS = "uber_eats"
    DIDI_FOOD = "didi_food"


class StoreType(str, Enum):
    RESTAURANT = "restaurant"
    CONVENIENCE = "convenience"
    PHARMACY = "pharmacy"


class ScrapeLayer(str, Enum):
    API = "api"
    DOM = "dom"
    TEXT_LLM = "text_llm"
    VISION = "vision"
    MANUAL = "manual"


class Address(BaseModel):
    """Direccion de entrega para scraping."""

    label: str = Field(..., description="Nombre descriptivo")
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    zone_type: ZoneType
    city: str = Field(default="CDMX")
    full_address: str | None = Field(default=None)


class ProductReference(BaseModel):
    """Producto de referencia para buscar en las plataformas."""

    canonical_name: str
    aliases: list[str] = Field(default_factory=list)
    category: str
    expected_price_range: dict = Field(..., description="{'min': N, 'max': N}")
    notes: str | None = Field(default=None)


class StoreGroup(BaseModel):
    """Agrupa productos por tipo de tienda."""

    store_type: StoreType
    store_name: str | None = Field(default=None)
    store_aliases: list[str] = Field(default_factory=list)
    products: list[ProductReference]
    notes: str | None = Field(default=None)


class ScrapedItem(BaseModel):
    """Un producto extraido de una plataforma."""

    name: str
    original_name: str
    price: float = Field(..., gt=0, le=10000)
    currency: str = Field(default="MXN")
    available: bool = Field(default=True)
    category: str | None = Field(default=None)


class FeeInfo(BaseModel):
    """Fees asociados a un pedido."""

    delivery_fee: float | None = Field(default=None, ge=0)
    service_fee: float | None = Field(default=None, ge=0)
    small_order_fee: float | None = Field(default=None, ge=0)
    promotions: list[str] = Field(default_factory=list)
    delivery_fee_original: str | None = Field(default=None)


class TimeEstimate(BaseModel):
    """Estimacion de tiempo de entrega."""

    min_minutes: int | None = Field(default=None, ge=0, le=180)
    max_minutes: int | None = Field(default=None, ge=0, le=180)
    original_text: str | None = Field(default=None)


class ScrapedResult(BaseModel):
    """Resultado completo de scrapear 1 tienda en 1 direccion en 1 plataforma."""

    platform: Platform
    address: Address
    store_type: StoreType
    store_name: str
    store_id: str | None = Field(default=None)
    store_url: str | None = Field(default=None)
    items: list[ScrapedItem] = Field(default_factory=list)
    fees: FeeInfo = Field(default_factory=FeeInfo)
    time_estimate: TimeEstimate = Field(default_factory=TimeEstimate)
    rating: float | None = Field(default=None, ge=0, le=5)

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.now)
    scrape_layer: ScrapeLayer
    success: bool = Field(default=True)
    error_message: str | None = Field(default=None)
    screenshot_path: str | None = Field(default=None)
    scrape_duration_seconds: float | None = Field(default=None)


class ScrapingRun(BaseModel):
    """Metadata de una ejecucion completa de scraping."""

    run_id: str
    start_time: datetime
    end_time: datetime | None = None
    platforms: list[Platform]
    addresses_count: int
    products_target: list[str]
    results: list[ScrapedResult] = Field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.success) / len(self.results)

    @property
    def layer_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for r in self.results:
            layer = r.scrape_layer.value
            dist[layer] = dist.get(layer, 0) + 1
        return dist
