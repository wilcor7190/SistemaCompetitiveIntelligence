"""Tests for DataNormalizer parsing functions (MVP 1)."""

from src.processors.normalizer import DataNormalizer


class TestParsePrice:
    def test_parse_price_with_dollar_sign(self):
        assert DataNormalizer.parse_price("$145.00") == 145.0

    def test_parse_price_no_decimals(self):
        assert DataNormalizer.parse_price("$89") == 89.0

    def test_parse_price_with_space(self):
        assert DataNormalizer.parse_price("$ 155.00") == 155.0

    def test_parse_price_mxn_prefix(self):
        assert DataNormalizer.parse_price("MXN 79.00") == 79.0

    def test_parse_price_free(self):
        assert DataNormalizer.parse_price("Gratis") == 0.0

    def test_parse_price_envio_gratis(self):
        assert DataNormalizer.parse_price("Envío Gratis") == 0.0

    def test_parse_price_empty(self):
        assert DataNormalizer.parse_price("") is None

    def test_parse_price_none(self):
        assert DataNormalizer.parse_price(None) is None

    def test_parse_price_range(self):
        """Range takes minimum price."""
        assert DataNormalizer.parse_price("$139-149") == 139.0

    def test_parse_price_two_prices_takes_min(self):
        """Two prices (discount) takes the lower one."""
        assert DataNormalizer.parse_price("$129.00 $155.00") == 129.0

    def test_parse_price_desde(self):
        assert DataNormalizer.parse_price("Desde $95.00") == 95.0

    def test_parse_price_no_disponible(self):
        assert DataNormalizer.parse_price("No disponible") is None

    def test_parse_price_agotado(self):
        assert DataNormalizer.parse_price("Agotado") is None


class TestParseFee:
    def test_parse_fee_gratis(self):
        assert DataNormalizer.parse_fee("Gratis") == 0.0

    def test_parse_fee_free(self):
        assert DataNormalizer.parse_fee("Free delivery") == 0.0

    def test_parse_fee_amount(self):
        assert DataNormalizer.parse_fee("$29.00") == 29.0

    def test_parse_fee_empty(self):
        assert DataNormalizer.parse_fee("") is None


class TestParseDeliveryTime:
    def test_parse_delivery_time_range(self):
        assert DataNormalizer.parse_delivery_time("25-35 min") == (25, 35)

    def test_parse_delivery_time_range_spaces(self):
        assert DataNormalizer.parse_delivery_time("25 - 35 min") == (25, 35)

    def test_parse_delivery_time_single(self):
        assert DataNormalizer.parse_delivery_time("35 min") == (35, 35)

    def test_parse_delivery_time_minutos(self):
        assert DataNormalizer.parse_delivery_time("20-30 minutos") == (20, 30)

    def test_parse_delivery_time_prefix(self):
        assert DataNormalizer.parse_delivery_time("Llega en 35 min") == (35, 35)

    def test_parse_delivery_time_empty(self):
        assert DataNormalizer.parse_delivery_time("") == (None, None)

    def test_parse_delivery_time_none(self):
        assert DataNormalizer.parse_delivery_time(None) == (None, None)


class TestParsePromotions:
    def test_detects_gratis(self):
        result = DataNormalizer.parse_promotions(["Envío Gratis", "Ver más"])
        assert "Envío Gratis" in result
        assert "Ver más" not in result

    def test_detects_off(self):
        result = DataNormalizer.parse_promotions(["Hasta 64% OFF imperdible"])
        assert len(result) == 1

    def test_detects_descuento(self):
        result = DataNormalizer.parse_promotions(["Descuento $30", "McDonald's"])
        assert "Descuento $30" in result
        assert "McDonald's" not in result

    def test_detects_2x1(self):
        result = DataNormalizer.parse_promotions(["2x1 en hamburguesas"])
        assert len(result) == 1

    def test_empty_list(self):
        assert DataNormalizer.parse_promotions([]) == []
