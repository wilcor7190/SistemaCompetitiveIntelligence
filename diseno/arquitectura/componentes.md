# Diagrama de Componentes y Clases

## 1. Diagrama de Clases: Scrapers

```mermaid
classDiagram
    class BaseScraper {
        <<abstract>>
        #config: ScraperConfig
        #browser: Browser
        #page: Page
        #results: list~ScrapedResult~
        #logger: Logger
        +setup() async
        +teardown() async
        +run(addresses, products) async list~ScrapedResult~
        +scrape_address(address, products) async ScrapedResult
        #try_api_interception() async dict|None
        #try_dom_parsing(selectors) async dict|None
        #try_vision_fallback(screenshot_path) async dict|None
        #take_screenshot(name) async str
        #rate_limit_delay() async
        +set_address(address)* async bool
        +search_restaurant(name)* async bool
        +extract_items(products)* async list~ScrapedItem~
        +extract_fees()* async FeeInfo
        +extract_delivery_time()* async TimeEstimate
        +get_platform_selectors()* dict~str,str~
        +get_base_url()* str
    }

    class RappiScraper {
        -BASE_URL: str = "https://rappi.com.mx"
        -SELECTORS: dict
        +set_address(address) async bool
        +search_restaurant(name) async bool
        +extract_items(products) async list~ScrapedItem~
        +extract_fees() async FeeInfo
        +extract_delivery_time() async TimeEstimate
        +get_platform_selectors() dict
        +get_base_url() str
        -_navigate_to_restaurant(restaurant_id) async
        -_parse_price_text(text) float
        -_detect_promotions() async list~str~
    }

    class UberEatsScraper {
        -BASE_URL: str = "https://ubereats.com/mx"
        -SELECTORS: dict
        +set_address(address) async bool
        +search_restaurant(name) async bool
        +extract_items(products) async list~ScrapedItem~
        +extract_fees() async FeeInfo
        +extract_delivery_time() async TimeEstimate
        +get_platform_selectors() dict
        +get_base_url() str
        -_navigate_to_store(store_slug, store_id) async
        -_parse_price_text(text) float
        -_handle_arkose_challenge() async bool
    }

    class DiDiFoodScraper {
        -BASE_URL: str = "https://didi-food.com/es-MX"
        -SELECTORS: dict
        +set_address(address) async bool
        +search_restaurant(name) async bool
        +extract_items(products) async list~ScrapedItem~
        +extract_fees() async FeeInfo
        +extract_delivery_time() async TimeEstimate
        +get_platform_selectors() dict
        +get_base_url() str
        -_set_localstorage_address(address) async
        -_wait_for_spa_load() async
    }

    BaseScraper <|-- RappiScraper
    BaseScraper <|-- UberEatsScraper
    BaseScraper <|-- DiDiFoodScraper
```

---

## 2. Diagrama de Clases: IA Components

```mermaid
classDiagram
    class OllamaClient {
        -base_url: str
        -timeout: int
        +chat(model, messages, format) async dict
        +embed(model, input) async list~float~
        +is_available() async bool
        +list_models() async list~str~
    }

    class VisionFallback {
        -client: OllamaClient
        -model: str = "qwen3-vl:8b"
        -confidence_threshold: float = 0.7
        +extract_from_screenshot(image_path) async dict
        +extract_prices(image_path) async list~ScrapedItem~
        +extract_fees(image_path) async FeeInfo
        +extract_delivery_time(image_path) async TimeEstimate
        -_build_extraction_prompt() str
        -_parse_vision_response(response) dict
        -_validate_extracted_data(data) bool
    }

    class TextParser {
        -client: OllamaClient
        -model: str = "qwen3.5:4b"
        +parse_raw_text(text) async dict
        +extract_structured_data(raw_html) async list~ScrapedItem~
        -_build_parsing_prompt(text) str
        -_validate_json_output(output) dict
    }

    class InsightGenerator {
        -client: OllamaClient
        -model: str = "qwen3.5:9b"
        +generate_insights(df, n_insights) async list~Insight~
        +generate_executive_summary(df) async str
        -_build_insight_prompt(data_summary, stats) str
        -_parse_insights_response(response) list~Insight~
        -_validate_insight(insight) bool
    }

    class Insight {
        +number: int
        +title: str
        +finding: str
        +impact: str
        +recommendation: str
    }

    class ProductMatcher {
        -client: OllamaClient
        -model: str = "nomic-embed-text"
        -threshold: float = 0.85
        -product_references: list~ProductReference~
        +match_product(name) str|None
        +get_canonical_name(original_name) str
        +compute_similarity(text1, text2) float
        -_get_embedding(text) async list~float~
        -_cosine_similarity(vec1, vec2) float
        -_load_product_references(path) list~ProductReference~
    }

    OllamaClient <-- VisionFallback : uses
    OllamaClient <-- TextParser : uses
    OllamaClient <-- InsightGenerator : uses
    OllamaClient <-- ProductMatcher : uses
    InsightGenerator --> Insight : generates
```

---

## 3. Diagrama de Clases: Procesamiento y Orquestacion

```mermaid
classDiagram
    class ScrapingOrchestrator {
        -config: Config
        -scrapers: dict~Platform, BaseScraper~
        -normalizer: DataNormalizer
        -merger: DataMerger
        -logger: Logger
        +run_all() async ScrapingRun
        +run_platform(platform, addresses, products) async list~ScrapedResult~
        -_create_scraper(platform) BaseScraper
        -_save_raw_results(platform, results)
        -_generate_run_summary(run) dict
    }

    class DataNormalizer {
        -product_matcher: ProductMatcher
        +normalize_results(results) list~NormalizedResult~
        +normalize_price(price_text) float
        +normalize_fee(fee_text) float
        +normalize_time(time_text) tuple~int,int~
        +normalize_product_name(name, platform) str
        -_parse_price_string(text) float
        -_parse_time_range(text) tuple~int,int~
    }

    class DataValidator {
        -price_range: tuple~float,float~ = (1.0, 1000.0)
        -fee_range: tuple~float,float~ = (0.0, 200.0)
        -time_range: tuple~int,int~ = (5, 120)
        +validate_result(result) ValidationResult
        +validate_batch(results) list~ValidationResult~
        +get_completeness_score(result) float
        -_check_price_range(price) bool
        -_check_required_fields(result) list~str~
    }

    class DataMerger {
        -validator: DataValidator
        +merge_to_csv(results, output_path) str
        +merge_to_dataframe(results) DataFrame
        -_flatten_result(result) dict
        -_deduplicate(df) DataFrame
    }

    class Config {
        -settings: dict
        -addresses: list~Address~
        -products: list~ProductReference~
        +load(settings_path, addresses_path, products_path)$ Config
        +get_platforms() list~Platform~
        +get_addresses() list~Address~
        +get_products() list~ProductReference~
        +get_scraping_config() ScraperConfig
        +get_ollama_config() OllamaConfig
    }

    class ScraperConfig {
        +delay_min: float
        +delay_max: float
        +max_retries: int
        +page_load_timeout: int
        +headless: bool
        +stealth: bool
        +user_agent: str
    }

    ScrapingOrchestrator --> BaseScraper : creates
    ScrapingOrchestrator --> DataNormalizer : uses
    ScrapingOrchestrator --> DataMerger : uses
    ScrapingOrchestrator --> Config : reads
    DataNormalizer --> ProductMatcher : uses
    DataMerger --> DataValidator : uses
    Config --> ScraperConfig : provides
```

---

## 4. Diagrama de Paquetes

```mermaid
graph TB
    subgraph "desarrollo/src/"
        subgraph "main.py"
            MAIN["CLI Entry Point<br/>argparse"]
        end

        subgraph "scrapers/"
            BASE["base.py<br/>BaseScraper (ABC)"]
            RAPPI["rappi.py<br/>RappiScraper"]
            UBER["uber_eats.py<br/>UberEatsScraper"]
            DIDI["didi_food.py<br/>DiDiFoodScraper"]
            ORCH["orchestrator.py<br/>ScrapingOrchestrator"]
            VIS["vision_fallback.py<br/>VisionFallback"]
            TXT["text_parser.py<br/>TextParser"]
        end

        subgraph "models/"
            SCHEMAS["schemas.py<br/>Pydantic models"]
        end

        subgraph "processors/"
            NORM["normalizer.py<br/>DataNormalizer"]
            VALID["validator.py<br/>DataValidator"]
            MERGE["merger.py<br/>DataMerger"]
            MATCH["product_matcher.py<br/>ProductMatcher"]
        end

        subgraph "analysis/"
            INSIGHT["insights.py<br/>InsightGenerator"]
            VIZMOD["visualizations.py<br/>Charts"]
            REPORT["report_generator.py<br/>HTML/Jupyter"]
        end

        subgraph "utils/"
            RATE["rate_limiter.py"]
            LOG["logger.py"]
            SCREEN["screenshot.py"]
            OLLAMA["ollama_client.py"]
        end

        subgraph "config.py"
            CFG["Config loader"]
        end
    end

    MAIN --> ORCH
    MAIN --> CFG
    ORCH --> BASE
    BASE --> RAPPI
    BASE --> UBER
    BASE --> DIDI
    BASE --> VIS
    BASE --> TXT
    VIS --> OLLAMA
    TXT --> OLLAMA
    MATCH --> OLLAMA
    INSIGHT --> OLLAMA
    ORCH --> NORM
    NORM --> MATCH
    NORM --> VALID
    NORM --> MERGE
    MERGE --> INSIGHT
    INSIGHT --> VIZMOD
    VIZMOD --> REPORT
    BASE --> SCHEMAS
    NORM --> SCHEMAS
    BASE --> RATE
    BASE --> LOG
    BASE --> SCREEN
```

---

## 5. Interfaces y Metodos Abstractos

### BaseScraper - Contrato que cada plataforma implementa

```python
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Contrato para scrapers de plataformas de delivery.
    
    Cada scraper implementa las 3 capas de recoleccion:
    - Capa 1: API interception (logica comun en base)
    - Capa 2: DOM parsing (selectores especificos por plataforma)
    - Capa 3: Vision fallback (logica comun en base con VisionFallback)
    """

    @abstractmethod
    async def set_address(self, address: Address) -> bool:
        """Configura la direccion de entrega en la plataforma.
        
        Returns:
            True si la direccion fue aceptada, False si no hay cobertura.
        """
        ...

    @abstractmethod
    async def search_restaurant(self, name: str) -> bool:
        """Navega al restaurante especificado.
        
        Returns:
            True si el restaurante fue encontrado y la pagina cargo.
        """
        ...

    @abstractmethod
    async def extract_items(self, product_names: list[str]) -> list[ScrapedItem]:
        """Extrae precios de los productos de referencia.
        
        Args:
            product_names: Lista de nombres canonicos a buscar.
        
        Returns:
            Lista de ScrapedItem con precios encontrados.
        """
        ...

    @abstractmethod
    async def extract_fees(self) -> FeeInfo:
        """Extrae delivery fee y promociones visibles.
        
        Note:
            Service fee NO es accesible sin simular compra (ver ADR-003).
        """
        ...

    @abstractmethod
    async def extract_delivery_time(self) -> TimeEstimate:
        """Extrae tiempo estimado de entrega.
        
        Note:
            Uber Eats requiere direccion configurada para mostrar tiempos.
            Rappi muestra tiempos sin direccion.
        """
        ...

    @abstractmethod
    def get_platform_selectors(self) -> dict[str, str]:
        """Retorna diccionario de selectores CSS especificos de la plataforma.
        
        Returns:
            {"product_name": "css_selector", "price": "css_selector", ...}
        """
        ...

    @abstractmethod
    def get_base_url(self) -> str:
        """URL base de la plataforma."""
        ...
```

### Conexiones entre Componentes

```
FLUJO DE DEPENDENCIAS:
═══════════════════════

main.py
  └─→ Config.load() ─────────────→ addresses.json, products.json, settings.yaml
  └─→ ScrapingOrchestrator(config)
        ├─→ RappiScraper(config)
        │     ├─→ Playwright Browser (stealth)
        │     ├─→ VisionFallback(OllamaClient) ── qwen3-vl:8b
        │     ├─→ TextParser(OllamaClient) ─────── qwen3.5:4b
        │     ├─→ RateLimiter
        │     ├─→ Screenshot
        │     └─→ Logger
        ├─→ UberEatsScraper(config)  [mismas dependencias]
        ├─→ DiDiFoodScraper(config)  [mismas dependencias]
        │
        ├─→ DataNormalizer
        │     └─→ ProductMatcher(OllamaClient) ── nomic-embed-text
        ├─→ DataValidator
        └─→ DataMerger
              └─→ comparison.csv
                    │
                    v
              InsightGenerator(OllamaClient) ──── qwen3.5:9b
                    │
                    v
              Visualizations (matplotlib/plotly)
                    │
                    v
              ReportGenerator → reports/insights.html
```
