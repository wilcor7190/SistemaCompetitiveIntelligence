"""DataMerger: flatten ScrapedResults into a comparison CSV."""

import time
from pathlib import Path

import pandas as pd

from src.models.schemas import ScrapedResult
from src.processors.validator import DataValidator
from src.utils.logger import get_logger


class DataMerger:
    """Merges ScrapedResults into a unified DataFrame/CSV."""

    def __init__(self, validator: DataValidator | None = None):
        self.validator = validator or DataValidator()
        self.logger = get_logger()

    def merge_to_dataframe(self, results: list[ScrapedResult]) -> pd.DataFrame:
        """Flatten results into a DataFrame with one row per item."""
        rows = []

        for result in results:
            if not result.success:
                continue

            base = {
                "timestamp": result.timestamp.isoformat(),
                "run_id": None,
                "platform": result.platform.value,
                "address_label": result.address.label,
                "lat": result.address.lat,
                "lng": result.address.lng,
                "zone_type": result.address.zone_type.value,
                "city": result.address.city,
                "store_type": result.store_type.value,
                "store_name": result.store_name,
                "store_id": result.store_id,
                "delivery_fee_mxn": result.fees.delivery_fee,
                "service_fee_mxn": result.fees.service_fee,
                "delivery_time_min": result.time_estimate.min_minutes,
                "delivery_time_max": result.time_estimate.max_minutes,
                "promotions": ";".join(result.fees.promotions) if result.fees.promotions else None,
                "rating": result.rating,
                "scrape_layer": result.scrape_layer.value,
                "screenshot_path": result.screenshot_path,
            }

            if result.items:
                for item in result.items:
                    row = {
                        **base,
                        "canonical_product": item.name,
                        "product_category": item.category,
                        "original_product_name": item.original_name,
                        "price_mxn": item.price,
                        "available": item.available,
                    }
                    rows.append(row)
            else:
                # Include result even with no items (for tracking)
                row = {
                    **base,
                    "canonical_product": None,
                    "product_category": None,
                    "original_product_name": None,
                    "price_mxn": None,
                    "available": None,
                }
                rows.append(row)

        df = pd.DataFrame(rows)

        # Deduplicate: same (platform, address, store_name, canonical_product)
        if not df.empty and "canonical_product" in df.columns:
            dedup_cols = ["platform", "address_label", "store_name", "canonical_product"]
            existing = [c for c in dedup_cols if c in df.columns]
            before = len(df)
            df = df.drop_duplicates(subset=existing, keep="first")
            after = len(df)
            if before != after:
                self.logger.info(
                    f"[merger] Deduplicated: {before} -> {after} rows"
                )

        self.logger.info(f"[merger] DataFrame created: {len(df)} rows")
        return df

    def merge_to_csv(
        self,
        results: list[ScrapedResult],
        output_dir: str = "data/merged",
    ) -> str:
        """Merge results and save to CSV."""
        df = self.merge_to_dataframe(results)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        ts = time.strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{ts}.csv"
        filepath = output_path / filename

        df.to_csv(filepath, index=False, encoding="utf-8")
        self.logger.info(f"[merger] CSV saved: {filepath} ({len(df)} rows)")

        return str(filepath)
