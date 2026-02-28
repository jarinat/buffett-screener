"""Tests for price data models."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.price import PriceData, PriceHistory


class TestPriceData:
    """Tests for PriceData model."""

    def test_price_data_valid_data(self):
        """Test creating PriceData with valid data."""
        price = PriceData(
            ticker="AAPL",
            date=date(2024, 1, 15),
            open=Decimal("185.50"),
            high=Decimal("188.25"),
            low=Decimal("184.75"),
            close=Decimal("187.45"),
            adjusted_close=Decimal("187.45"),
            volume=52847500,
            currency="USD",
            source_provider="yahoo",
        )
        assert price.ticker == "AAPL"
        assert price.date == date(2024, 1, 15)
        assert price.open == Decimal("185.50")
        assert price.close == Decimal("187.45")
        assert price.volume == 52847500

    def test_price_data_minimal_data(self):
        """Test creating PriceData with minimal required fields."""
        price = PriceData(
            ticker="TEST",
            date=date(2024, 1, 1),
            currency="USD",
            source_provider="test_provider",
        )
        assert price.ticker == "TEST"
        assert price.open is None
        assert price.high is None
        assert price.low is None
        assert price.close is None
        assert price.adjusted_close is None
        assert price.volume is None

    def test_price_data_serialization(self):
        """Test PriceData serialization to dict."""
        price = PriceData(
            ticker="MSFT",
            date=date(2024, 1, 10),
            open=Decimal("370.00"),
            high=Decimal("375.50"),
            low=Decimal("369.25"),
            close=Decimal("374.20"),
            adjusted_close=Decimal("374.20"),
            volume=25678900,
            currency="USD",
            source_provider="yahoo",
        )
        data = price.model_dump()
        assert data["ticker"] == "MSFT"
        assert data["open"] == Decimal("370.00")
        assert data["volume"] == 25678900

    def test_price_data_deserialization(self):
        """Test PriceData deserialization from dict."""
        data = {
            "ticker": "GOOGL",
            "date": "2024-01-10",
            "open": "140.50",
            "high": "142.75",
            "low": "140.00",
            "close": "142.30",
            "adjusted_close": "142.30",
            "volume": 18234567,
            "currency": "USD",
            "source_provider": "yahoo",
        }
        price = PriceData(**data)
        assert price.ticker == "GOOGL"
        assert price.close == Decimal("142.30")

    def test_price_data_json_round_trip(self):
        """Test PriceData JSON serialization and deserialization."""
        original = PriceData(
            ticker="TSLA",
            date=date(2024, 1, 15),
            open=Decimal("215.30"),
            high=Decimal("220.80"),
            low=Decimal("214.50"),
            close=Decimal("219.45"),
            adjusted_close=Decimal("219.45"),
            volume=98765432,
            currency="USD",
            source_provider="yahoo",
        )
        json_str = original.model_dump_json()
        restored = PriceData.model_validate_json(json_str)
        assert restored.ticker == original.ticker
        assert restored.date == original.date
        assert restored.close == original.close

    def test_price_data_example_config(self):
        """Test that example from Config can be instantiated."""
        example = PriceData.model_config["json_schema_extra"]["example"]
        price = PriceData(**example)
        assert price.ticker == "AAPL"
        assert price.close == Decimal("187.45")

    def test_price_data_missing_required_field(self):
        """Test PriceData validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            PriceData(
                ticker="AAPL",
                date=date(2024, 1, 1),
                # missing currency and source_provider
            )
        errors = str(exc_info.value)
        assert "currency" in errors or "source_provider" in errors

    def test_price_data_decimal_precision(self):
        """Test PriceData handles decimal precision correctly."""
        price = PriceData(
            ticker="PREC",
            date=date(2024, 1, 1),
            open=Decimal("123.456789"),
            high=Decimal("124.987654"),
            low=Decimal("122.123456"),
            close=Decimal("123.789012"),
            adjusted_close=Decimal("123.789012"),
            currency="USD",
            source_provider="test",
        )
        assert price.open == Decimal("123.456789")
        assert price.adjusted_close == Decimal("123.789012")

    def test_price_data_with_split_adjustment(self):
        """Test PriceData with different close and adjusted_close (e.g., after split)."""
        price = PriceData(
            ticker="SPLIT",
            date=date(2020, 8, 31),
            open=Decimal("500.00"),
            high=Decimal("510.00"),
            low=Decimal("495.00"),
            close=Decimal("505.00"),
            adjusted_close=Decimal("126.25"),  # 4:1 split adjusted
            volume=100000000,
            currency="USD",
            source_provider="yahoo",
        )
        assert price.close == Decimal("505.00")
        assert price.adjusted_close == Decimal("126.25")

    def test_price_data_zero_volume(self):
        """Test PriceData with zero volume (e.g., holiday or no trading)."""
        price = PriceData(
            ticker="ZERO",
            date=date(2024, 1, 1),
            open=Decimal("100.00"),
            high=Decimal("100.00"),
            low=Decimal("100.00"),
            close=Decimal("100.00"),
            adjusted_close=Decimal("100.00"),
            volume=0,
            currency="USD",
            source_provider="test",
        )
        assert price.volume == 0


class TestPriceHistory:
    """Tests for PriceHistory model."""

    def test_price_history_valid_data(self):
        """Test creating PriceHistory with valid data."""
        price_data = [
            PriceData(
                ticker="AAPL",
                date=date(2024, 1, 2),
                open=Decimal("185.00"),
                high=Decimal("186.50"),
                low=Decimal("184.25"),
                close=Decimal("185.75"),
                adjusted_close=Decimal("185.75"),
                volume=45678900,
                currency="USD",
                source_provider="yahoo",
            ),
            PriceData(
                ticker="AAPL",
                date=date(2024, 1, 3),
                open=Decimal("186.00"),
                high=Decimal("188.00"),
                low=Decimal("185.50"),
                close=Decimal("187.50"),
                adjusted_close=Decimal("187.50"),
                volume=52847500,
                currency="USD",
                source_provider="yahoo",
            ),
        ]
        history = PriceHistory(
            company_id="AAPL",
            ticker="AAPL",
            start_date=date(2024, 1, 2),
            end_date=date(2024, 1, 3),
            currency="USD",
            source_provider="yahoo",
            data=price_data,
        )
        assert history.company_id == "AAPL"
        assert history.ticker == "AAPL"
        assert len(history.data) == 2
        assert history.data[0].close == Decimal("185.75")
        assert history.data[1].close == Decimal("187.50")

    def test_price_history_empty_data(self):
        """Test creating PriceHistory with empty data list."""
        history = PriceHistory(
            company_id="EMPTY",
            ticker="EMPTY",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            currency="USD",
            source_provider="test",
            data=[],
        )
        assert len(history.data) == 0

    def test_price_history_serialization(self):
        """Test PriceHistory serialization to dict."""
        price_data = [
            PriceData(
                ticker="MSFT",
                date=date(2024, 1, 5),
                open=Decimal("370.00"),
                close=Decimal("374.20"),
                currency="USD",
                source_provider="yahoo",
            ),
        ]
        history = PriceHistory(
            company_id="MSFT",
            ticker="MSFT",
            start_date=date(2024, 1, 5),
            end_date=date(2024, 1, 5),
            currency="USD",
            source_provider="yahoo",
            data=price_data,
        )
        data = history.model_dump()
        assert data["company_id"] == "MSFT"
        assert len(data["data"]) == 1
        assert data["data"][0]["close"] == Decimal("374.20")

    def test_price_history_deserialization(self):
        """Test PriceHistory deserialization from dict."""
        data = {
            "company_id": "GOOGL",
            "ticker": "GOOGL",
            "start_date": "2024-01-01",
            "end_date": "2024-01-02",
            "currency": "USD",
            "source_provider": "yahoo",
            "data": [
                {
                    "ticker": "GOOGL",
                    "date": "2024-01-01",
                    "open": "140.00",
                    "close": "141.50",
                    "currency": "USD",
                    "source_provider": "yahoo",
                },
                {
                    "ticker": "GOOGL",
                    "date": "2024-01-02",
                    "open": "141.75",
                    "close": "142.30",
                    "currency": "USD",
                    "source_provider": "yahoo",
                },
            ],
        }
        history = PriceHistory(**data)
        assert history.company_id == "GOOGL"
        assert len(history.data) == 2

    def test_price_history_json_round_trip(self):
        """Test PriceHistory JSON serialization and deserialization."""
        price_data = [
            PriceData(
                ticker="AMZN",
                date=date(2024, 1, 10),
                open=Decimal("150.00"),
                close=Decimal("152.50"),
                currency="USD",
                source_provider="yahoo",
            ),
        ]
        original = PriceHistory(
            company_id="AMZN",
            ticker="AMZN",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 1, 10),
            currency="USD",
            source_provider="yahoo",
            data=price_data,
        )
        json_str = original.model_dump_json()
        restored = PriceHistory.model_validate_json(json_str)
        assert restored.company_id == original.company_id
        assert len(restored.data) == len(original.data)

    def test_price_history_example_config(self):
        """Test that example from Config can be instantiated."""
        example = PriceHistory.model_config["json_schema_extra"]["example"]
        history = PriceHistory(**example)
        assert history.company_id == "AAPL"
        assert len(history.data) == 2

    def test_price_history_missing_required_field(self):
        """Test PriceHistory validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            PriceHistory(
                company_id="AAPL",
                ticker="AAPL",
                start_date=date(2024, 1, 1),
                # missing end_date, currency, source_provider, data
            )
        errors = str(exc_info.value)
        assert any(
            field in errors
            for field in ["end_date", "currency", "source_provider", "data"]
        )

    def test_price_history_single_day(self):
        """Test PriceHistory for a single day."""
        price_data = [
            PriceData(
                ticker="ONE",
                date=date(2024, 1, 15),
                open=Decimal("100.00"),
                close=Decimal("102.00"),
                currency="USD",
                source_provider="test",
            ),
        ]
        history = PriceHistory(
            company_id="ONE",
            ticker="ONE",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 15),
            currency="USD",
            source_provider="test",
            data=price_data,
        )
        assert history.start_date == history.end_date
        assert len(history.data) == 1

    def test_price_history_multi_year(self):
        """Test PriceHistory spanning multiple years."""
        price_data = [
            PriceData(
                ticker="LONG",
                date=date(2020, 1, 1),
                close=Decimal("100.00"),
                currency="USD",
                source_provider="test",
            ),
            PriceData(
                ticker="LONG",
                date=date(2024, 12, 31),
                close=Decimal("200.00"),
                currency="USD",
                source_provider="test",
            ),
        ]
        history = PriceHistory(
            company_id="LONG",
            ticker="LONG",
            start_date=date(2020, 1, 1),
            end_date=date(2024, 12, 31),
            currency="USD",
            source_provider="test",
            data=price_data,
        )
        assert (history.end_date - history.start_date).days > 1000
        assert len(history.data) == 2

    def test_price_history_chronological_data(self):
        """Test PriceHistory with chronologically ordered data."""
        price_data = [
            PriceData(
                ticker="CHRONO",
                date=date(2024, 1, 1),
                close=Decimal("100.00"),
                currency="USD",
                source_provider="test",
            ),
            PriceData(
                ticker="CHRONO",
                date=date(2024, 1, 2),
                close=Decimal("101.00"),
                currency="USD",
                source_provider="test",
            ),
            PriceData(
                ticker="CHRONO",
                date=date(2024, 1, 3),
                close=Decimal("102.00"),
                currency="USD",
                source_provider="test",
            ),
        ]
        history = PriceHistory(
            company_id="CHRONO",
            ticker="CHRONO",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 3),
            currency="USD",
            source_provider="test",
            data=price_data,
        )
        # Verify chronological order
        for i in range(len(history.data) - 1):
            assert history.data[i].date < history.data[i + 1].date
