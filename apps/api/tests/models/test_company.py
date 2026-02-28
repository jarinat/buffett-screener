"""Tests for company data models."""

import pytest
from pydantic import ValidationError

from app.models.company import CompanyInfo, Listing


class TestListing:
    """Tests for Listing model."""

    def test_listing_valid_data(self):
        """Test creating a Listing with valid data."""
        listing = Listing(
            ticker="AAPL",
            exchange="NASDAQ",
            currency="USD",
        )
        assert listing.ticker == "AAPL"
        assert listing.exchange == "NASDAQ"
        assert listing.currency == "USD"

    def test_listing_serialization(self):
        """Test Listing serialization to dict."""
        listing = Listing(
            ticker="MSFT",
            exchange="NASDAQ",
            currency="USD",
        )
        data = listing.model_dump()
        assert data == {
            "ticker": "MSFT",
            "exchange": "NASDAQ",
            "currency": "USD",
        }

    def test_listing_deserialization(self):
        """Test Listing deserialization from dict."""
        data = {
            "ticker": "GOOGL",
            "exchange": "NASDAQ",
            "currency": "USD",
        }
        listing = Listing(**data)
        assert listing.ticker == "GOOGL"
        assert listing.exchange == "NASDAQ"
        assert listing.currency == "USD"

    def test_listing_json_round_trip(self):
        """Test Listing JSON serialization and deserialization."""
        original = Listing(
            ticker="TSLA",
            exchange="NASDAQ",
            currency="USD",
        )
        json_str = original.model_dump_json()
        restored = Listing.model_validate_json(json_str)
        assert restored == original

    def test_listing_missing_required_field(self):
        """Test Listing validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            Listing(
                ticker="AAPL",
                exchange="NASDAQ",
                # missing currency
            )
        assert "currency" in str(exc_info.value)


class TestCompanyInfo:
    """Tests for CompanyInfo model."""

    def test_company_info_valid_data(self):
        """Test creating CompanyInfo with valid data."""
        company = CompanyInfo(
            company_id="AAPL",
            name="Apple Inc.",
            ticker="AAPL",
            exchange="NASDAQ",
            sector="Technology",
            industry="Consumer Electronics",
            country="US",
            currency="USD",
        )
        assert company.company_id == "AAPL"
        assert company.name == "Apple Inc."
        assert company.ticker == "AAPL"
        assert company.exchange == "NASDAQ"
        assert company.sector == "Technology"
        assert company.industry == "Consumer Electronics"
        assert company.country == "US"
        assert company.currency == "USD"

    def test_company_info_minimal_data(self):
        """Test creating CompanyInfo with minimal required fields."""
        company = CompanyInfo(
            company_id="TEST",
            name="Test Company",
            ticker="TEST",
            exchange="NYSE",
            currency="USD",
        )
        assert company.company_id == "TEST"
        assert company.name == "Test Company"
        assert company.sector is None
        assert company.industry is None
        assert company.country is None

    def test_company_info_optional_fields_none(self):
        """Test CompanyInfo with optional fields explicitly set to None."""
        company = CompanyInfo(
            company_id="NOPT",
            name="No Optional Fields",
            ticker="NOPT",
            exchange="NASDAQ",
            currency="USD",
            sector=None,
            industry=None,
            country=None,
        )
        assert company.sector is None
        assert company.industry is None
        assert company.country is None

    def test_company_info_serialization(self):
        """Test CompanyInfo serialization to dict."""
        company = CompanyInfo(
            company_id="MSFT",
            name="Microsoft Corporation",
            ticker="MSFT",
            exchange="NASDAQ",
            sector="Technology",
            industry="Software",
            country="US",
            currency="USD",
        )
        data = company.model_dump()
        assert data["company_id"] == "MSFT"
        assert data["name"] == "Microsoft Corporation"
        assert data["ticker"] == "MSFT"
        assert data["exchange"] == "NASDAQ"
        assert data["sector"] == "Technology"
        assert data["industry"] == "Software"
        assert data["country"] == "US"
        assert data["currency"] == "USD"

    def test_company_info_deserialization(self):
        """Test CompanyInfo deserialization from dict."""
        data = {
            "company_id": "GOOGL",
            "name": "Alphabet Inc.",
            "ticker": "GOOGL",
            "exchange": "NASDAQ",
            "sector": "Technology",
            "industry": "Internet Services",
            "country": "US",
            "currency": "USD",
        }
        company = CompanyInfo(**data)
        assert company.company_id == "GOOGL"
        assert company.name == "Alphabet Inc."
        assert company.sector == "Technology"

    def test_company_info_json_round_trip(self):
        """Test CompanyInfo JSON serialization and deserialization."""
        original = CompanyInfo(
            company_id="AMZN",
            name="Amazon.com Inc.",
            ticker="AMZN",
            exchange="NASDAQ",
            sector="Consumer Cyclical",
            industry="Internet Retail",
            country="US",
            currency="USD",
        )
        json_str = original.model_dump_json()
        restored = CompanyInfo.model_validate_json(json_str)
        assert restored == original

    def test_company_info_missing_required_field(self):
        """Test CompanyInfo validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            CompanyInfo(
                company_id="AAPL",
                name="Apple Inc.",
                ticker="AAPL",
                # missing exchange and currency
            )
        errors = str(exc_info.value)
        assert "exchange" in errors or "currency" in errors

    def test_company_info_example_config(self):
        """Test that example from Config can be instantiated."""
        example = CompanyInfo.model_config["json_schema_extra"]["example"]
        company = CompanyInfo(**example)
        assert company.company_id == "AAPL"
        assert company.name == "Apple Inc."
        assert company.ticker == "AAPL"

    def test_company_info_with_partial_optional_fields(self):
        """Test CompanyInfo with some optional fields set and others None."""
        company = CompanyInfo(
            company_id="PART",
            name="Partial Company",
            ticker="PART",
            exchange="NYSE",
            currency="USD",
            sector="Technology",
            # industry and country not set
        )
        assert company.sector == "Technology"
        assert company.industry is None
        assert company.country is None
