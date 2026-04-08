"""DataValidator: validate scraped data ranges and completeness."""

from dataclasses import dataclass, field

from src.models.schemas import ScrapedResult
from src.utils.logger import get_logger


@dataclass
class ValidationResult:
    """Result of validating a ScrapedResult."""

    valid: bool = True
    completeness_score: float = 0.0
    warnings: list[str] = field(default_factory=list)
    suspect_fields: list[str] = field(default_factory=list)


class DataValidator:
    """Validates scraped data against expected ranges."""

    PRICE_RANGE = (1.0, 1000.0)
    FEE_RANGE = (0.0, 200.0)
    TIME_RANGE = (5, 120)
    RATING_RANGE = (0.0, 5.0)

    def __init__(self):
        self.logger = get_logger()

    def validate_result(self, result: ScrapedResult) -> ValidationResult:
        """Validate a single ScrapedResult."""
        vr = ValidationResult()

        if not result.success:
            vr.valid = False
            vr.completeness_score = 0.0
            return vr

        # Validate item prices
        for item in result.items:
            if not (self.PRICE_RANGE[0] <= item.price <= self.PRICE_RANGE[1]):
                vr.suspect_fields.append(f"price:{item.original_name}={item.price}")
                vr.warnings.append(
                    f"Suspect price {item.price} for '{item.original_name}'"
                )

        # Validate delivery fee
        if result.fees.delivery_fee is not None:
            if not (self.FEE_RANGE[0] <= result.fees.delivery_fee <= self.FEE_RANGE[1]):
                vr.suspect_fields.append(f"delivery_fee={result.fees.delivery_fee}")

        # Validate delivery time
        if result.time_estimate.min_minutes is not None:
            if not (
                self.TIME_RANGE[0]
                <= result.time_estimate.min_minutes
                <= self.TIME_RANGE[1]
            ):
                vr.suspect_fields.append(
                    f"delivery_time_min={result.time_estimate.min_minutes}"
                )

        # Validate rating
        if result.rating is not None:
            if not (self.RATING_RANGE[0] <= result.rating <= self.RATING_RANGE[1]):
                vr.suspect_fields.append(f"rating={result.rating}")

        # Completeness score
        vr.completeness_score = self.get_completeness_score(result)
        vr.valid = len(vr.suspect_fields) == 0

        if vr.warnings:
            for w in vr.warnings:
                self.logger.warning(f"[validator] {w}")

        return vr

    def validate_batch(self, results: list[ScrapedResult]) -> list[ValidationResult]:
        """Validate a batch of results."""
        return [self.validate_result(r) for r in results]

    @staticmethod
    def get_completeness_score(result: ScrapedResult) -> float:
        """Calculate completeness score (0.0 to 1.0).

        Fields: items, delivery_fee, delivery_time, rating, promotions.
        """
        if not result.success:
            return 0.0

        total_fields = 5
        filled = 0

        if result.items:
            filled += 1
        if result.fees.delivery_fee is not None:
            filled += 1
        if result.time_estimate.min_minutes is not None:
            filled += 1
        if result.rating is not None:
            filled += 1
        if result.fees.promotions:
            filled += 1

        return filled / total_fields
