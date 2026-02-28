"""Tests for provider registry functionality."""

from typing import List

import pytest

from app.models.company import CompanyInfo
from app.models.financial import BalanceSheet, CashFlow, IncomeStatement
from app.models.price import PriceData, PriceHistory
from app.providers.base import (
    CompanyUniverseProvider,
    FundamentalsProvider,
    PriceHistoryProvider,
)
from app.providers.registry import ProviderRegistry, get_provider_registry


# Mock provider implementations for testing
class MockCompanyProvider(CompanyUniverseProvider):
    """Mock company provider for testing."""

    def get_company_universe(self) -> List[CompanyInfo]:
        return [
            CompanyInfo(
                company_id="AAPL",
                name="Apple Inc.",
                ticker="AAPL",
                exchange="NASDAQ",
                currency="USD",
            )
        ]

    def get_company_info(self, ticker: str) -> CompanyInfo:
        return CompanyInfo(
            company_id=ticker,
            name=f"{ticker} Company",
            ticker=ticker,
            exchange="NYSE",
            currency="USD",
        )


class MockFundamentalsProvider(FundamentalsProvider):
    """Mock fundamentals provider for testing."""

    def get_income_statement(self, ticker: str, period: str = "annual") -> IncomeStatement:
        return IncomeStatement(
            company_id=ticker,
            fiscal_year=2023,
            period=period,
            source_provider="mock",
        )

    def get_balance_sheet(self, ticker: str, period: str = "annual") -> BalanceSheet:
        return BalanceSheet(
            company_id=ticker,
            fiscal_year=2023,
            period=period,
            source_provider="mock",
        )

    def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
        return CashFlow(
            company_id=ticker,
            fiscal_year=2023,
            period=period,
            source_provider="mock",
        )


class MockPriceProvider(PriceHistoryProvider):
    """Mock price provider for testing."""

    def get_price_history(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> PriceHistory:
        return PriceHistory(
            company_id=ticker,
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            currency="USD",
            source_provider="mock",
            prices=[],
        )

    def get_latest_price(self, ticker: str) -> PriceData:
        from datetime import date
        from decimal import Decimal

        return PriceData(
            ticker=ticker,
            date=date.today(),
            close=Decimal("100.00"),
            currency="USD",
            source_provider="mock",
        )


# Alternative provider implementations for multi-provider testing
class AlternativeMockCompanyProvider(CompanyUniverseProvider):
    """Alternative mock company provider for testing multi-provider scenarios."""

    def get_company_universe(self) -> List[CompanyInfo]:
        return []

    def get_company_info(self, ticker: str) -> CompanyInfo:
        return CompanyInfo(
            company_id=ticker,
            name=f"Alternative {ticker}",
            ticker=ticker,
            exchange="LSE",
            currency="GBP",
        )


class TestProviderRegistry:
    """Tests for ProviderRegistry class."""

    def test_registry_instantiation(self):
        """Test that ProviderRegistry can be instantiated."""
        registry = ProviderRegistry()
        assert registry is not None
        assert hasattr(registry, "_providers")
        assert isinstance(registry._providers, dict)
        assert len(registry._providers) == 0

    def test_register_company_provider(self):
        """Test registering a company provider."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)

        # Verify provider is registered
        key = ("company", "mock")
        assert key in registry._providers
        assert registry._providers[key] == MockCompanyProvider

    def test_register_fundamentals_provider(self):
        """Test registering a fundamentals provider."""
        registry = ProviderRegistry()
        registry.register_provider("fundamentals", "mock", MockFundamentalsProvider)

        # Verify provider is registered
        key = ("fundamentals", "mock")
        assert key in registry._providers
        assert registry._providers[key] == MockFundamentalsProvider

    def test_register_price_provider(self):
        """Test registering a price provider."""
        registry = ProviderRegistry()
        registry.register_provider("price", "mock", MockPriceProvider)

        # Verify provider is registered
        key = ("price", "mock")
        assert key in registry._providers
        assert registry._providers[key] == MockPriceProvider

    def test_register_multiple_providers_same_type(self):
        """Test registering multiple providers of the same type."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)
        registry.register_provider("company", "alternative", AlternativeMockCompanyProvider)

        # Both should be registered
        assert ("company", "mock") in registry._providers
        assert ("company", "alternative") in registry._providers
        assert registry._providers[("company", "mock")] == MockCompanyProvider
        assert registry._providers[("company", "alternative")] == AlternativeMockCompanyProvider

    def test_register_provider_replaces_existing(self):
        """Test that registering a provider with the same name replaces the existing one."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)
        registry.register_provider("company", "mock", AlternativeMockCompanyProvider)

        # Only the second provider should be registered
        key = ("company", "mock")
        assert registry._providers[key] == AlternativeMockCompanyProvider

    def test_register_provider_wrong_type_raises_error(self):
        """Test that registering a provider with wrong base class raises TypeError."""
        registry = ProviderRegistry()

        # Try to register a company provider as a fundamentals provider
        with pytest.raises(TypeError) as exc_info:
            registry.register_provider("fundamentals", "wrong", MockCompanyProvider)
        assert "must inherit from" in str(exc_info.value)
        assert "FundamentalsProvider" in str(exc_info.value)

        # Try to register a fundamentals provider as a price provider
        with pytest.raises(TypeError) as exc_info:
            registry.register_provider("price", "wrong", MockFundamentalsProvider)
        assert "must inherit from" in str(exc_info.value)
        assert "PriceHistoryProvider" in str(exc_info.value)

        # Try to register a price provider as a company provider
        with pytest.raises(TypeError) as exc_info:
            registry.register_provider("company", "wrong", MockPriceProvider)
        assert "must inherit from" in str(exc_info.value)
        assert "CompanyUniverseProvider" in str(exc_info.value)

    def test_get_provider_returns_instance(self):
        """Test that get_provider returns a provider instance."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)

        provider = registry.get_provider("company", "mock")
        assert provider is not None
        assert isinstance(provider, MockCompanyProvider)
        assert isinstance(provider, CompanyUniverseProvider)

    def test_get_provider_creates_new_instance_each_time(self):
        """Test that get_provider creates a new instance on each call."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)

        provider1 = registry.get_provider("company", "mock")
        provider2 = registry.get_provider("company", "mock")

        # Should be different instances
        assert provider1 is not provider2
        # But both should be of the same type
        assert type(provider1) == type(provider2)

    def test_get_provider_different_types(self):
        """Test getting providers of different types."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)
        registry.register_provider("fundamentals", "mock", MockFundamentalsProvider)
        registry.register_provider("price", "mock", MockPriceProvider)

        company_provider = registry.get_provider("company", "mock")
        fundamentals_provider = registry.get_provider("fundamentals", "mock")
        price_provider = registry.get_provider("price", "mock")

        assert isinstance(company_provider, CompanyUniverseProvider)
        assert isinstance(fundamentals_provider, FundamentalsProvider)
        assert isinstance(price_provider, PriceHistoryProvider)

    def test_get_provider_unregistered_raises_error(self):
        """Test that getting an unregistered provider raises KeyError."""
        registry = ProviderRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get_provider("company", "nonexistent")
        assert "No provider registered" in str(exc_info.value)
        assert "company" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_get_provider_error_message_lists_available_providers(self):
        """Test that error message includes available providers."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)
        registry.register_provider("company", "alternative", AlternativeMockCompanyProvider)

        with pytest.raises(KeyError) as exc_info:
            registry.get_provider("company", "nonexistent")
        error_msg = str(exc_info.value)
        assert "Available providers:" in error_msg
        assert "'mock'" in error_msg
        assert "'alternative'" in error_msg

    def test_get_provider_error_message_when_no_providers(self):
        """Test error message when no providers are registered for a type."""
        registry = ProviderRegistry()

        with pytest.raises(KeyError) as exc_info:
            registry.get_provider("company", "nonexistent")
        error_msg = str(exc_info.value)
        assert "Available providers: none" in error_msg

    def test_list_providers_empty(self):
        """Test listing providers when none are registered."""
        registry = ProviderRegistry()
        providers = registry.list_providers("company")
        assert providers == []

    def test_list_providers_single(self):
        """Test listing providers with a single registered provider."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)

        providers = registry.list_providers("company")
        assert providers == ["mock"]

    def test_list_providers_multiple(self):
        """Test listing providers with multiple registered providers."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)
        registry.register_provider("company", "alternative", AlternativeMockCompanyProvider)

        providers = registry.list_providers("company")
        # Should be sorted alphabetically
        assert providers == ["alternative", "mock"]

    def test_list_providers_filtered_by_type(self):
        """Test that list_providers only returns providers of the specified type."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock_company", MockCompanyProvider)
        registry.register_provider("fundamentals", "mock_fundamentals", MockFundamentalsProvider)
        registry.register_provider("price", "mock_price", MockPriceProvider)

        company_providers = registry.list_providers("company")
        fundamentals_providers = registry.list_providers("fundamentals")
        price_providers = registry.list_providers("price")

        assert company_providers == ["mock_company"]
        assert fundamentals_providers == ["mock_fundamentals"]
        assert price_providers == ["mock_price"]

    def test_provider_instance_is_functional(self):
        """Test that retrieved provider instances are fully functional."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)

        provider = registry.get_provider("company", "mock")

        # Test get_company_universe
        companies = provider.get_company_universe()
        assert len(companies) == 1
        assert companies[0].ticker == "AAPL"

        # Test get_company_info
        company = provider.get_company_info("TEST")
        assert company.ticker == "TEST"
        assert company.name == "TEST Company"

    def test_fundamentals_provider_instance_is_functional(self):
        """Test that retrieved fundamentals provider instances are fully functional."""
        registry = ProviderRegistry()
        registry.register_provider("fundamentals", "mock", MockFundamentalsProvider)

        provider = registry.get_provider("fundamentals", "mock")

        # Test get_income_statement
        income = provider.get_income_statement("AAPL")
        assert income.company_id == "AAPL"
        assert income.fiscal_year == 2023

        # Test get_balance_sheet
        balance = provider.get_balance_sheet("AAPL")
        assert balance.company_id == "AAPL"

        # Test get_cash_flow
        cash_flow = provider.get_cash_flow("AAPL")
        assert cash_flow.company_id == "AAPL"

    def test_price_provider_instance_is_functional(self):
        """Test that retrieved price provider instances are fully functional."""
        registry = ProviderRegistry()
        registry.register_provider("price", "mock", MockPriceProvider)

        provider = registry.get_provider("price", "mock")

        # Test get_price_history
        history = provider.get_price_history("AAPL", "2023-01-01", "2023-12-31")
        assert history.ticker == "AAPL"
        assert history.company_id == "AAPL"

        # Test get_latest_price
        price = provider.get_latest_price("AAPL")
        assert price.ticker == "AAPL"
        from decimal import Decimal
        assert price.close == Decimal("100.00")


class TestGetProviderRegistry:
    """Tests for get_provider_registry singleton function."""

    def test_get_provider_registry_returns_instance(self):
        """Test that get_provider_registry returns a ProviderRegistry instance."""
        registry = get_provider_registry()
        assert registry is not None
        assert isinstance(registry, ProviderRegistry)

    def test_get_provider_registry_returns_same_instance(self):
        """Test that get_provider_registry returns the same instance (singleton)."""
        # Clear the cache first to ensure clean state
        get_provider_registry.cache_clear()

        registry1 = get_provider_registry()
        registry2 = get_provider_registry()

        # Should be the exact same instance
        assert registry1 is registry2

    def test_singleton_persists_registrations(self):
        """Test that provider registrations persist across get_provider_registry calls."""
        # Clear the cache first
        get_provider_registry.cache_clear()

        # Register a provider using first reference
        registry1 = get_provider_registry()
        registry1.register_provider("company", "mock", MockCompanyProvider)

        # Get registry again
        registry2 = get_provider_registry()

        # Should still have the registered provider
        providers = registry2.list_providers("company")
        assert "mock" in providers

        # Should be able to get the provider
        provider = registry2.get_provider("company", "mock")
        assert isinstance(provider, MockCompanyProvider)


class TestProviderRegistryEdgeCases:
    """Tests for edge cases and error handling in ProviderRegistry."""

    def test_register_provider_with_empty_name(self):
        """Test registering a provider with an empty name."""
        registry = ProviderRegistry()
        # This should work - the registry doesn't enforce non-empty names
        registry.register_provider("company", "", MockCompanyProvider)
        assert ("company", "") in registry._providers

    def test_get_provider_with_empty_name(self):
        """Test getting a provider with an empty name."""
        registry = ProviderRegistry()
        registry.register_provider("company", "", MockCompanyProvider)

        provider = registry.get_provider("company", "")
        assert isinstance(provider, MockCompanyProvider)

    def test_list_providers_returns_empty_list_for_unused_type(self):
        """Test that list_providers returns empty list for types with no registrations."""
        registry = ProviderRegistry()
        registry.register_provider("company", "mock", MockCompanyProvider)

        # Query a different type
        providers = registry.list_providers("fundamentals")
        assert providers == []

    def test_multiple_provider_types_same_name(self):
        """Test registering providers with the same name but different types."""
        registry = ProviderRegistry()
        registry.register_provider("company", "yahoo", MockCompanyProvider)
        registry.register_provider("fundamentals", "yahoo", MockFundamentalsProvider)
        registry.register_provider("price", "yahoo", MockPriceProvider)

        # All should be registered independently
        assert ("company", "yahoo") in registry._providers
        assert ("fundamentals", "yahoo") in registry._providers
        assert ("price", "yahoo") in registry._providers

        # Should be able to get all of them
        company_provider = registry.get_provider("company", "yahoo")
        fundamentals_provider = registry.get_provider("fundamentals", "yahoo")
        price_provider = registry.get_provider("price", "yahoo")

        assert isinstance(company_provider, MockCompanyProvider)
        assert isinstance(fundamentals_provider, MockFundamentalsProvider)
        assert isinstance(price_provider, MockPriceProvider)

    def test_registry_isolation(self):
        """Test that separate ProviderRegistry instances are independent."""
        registry1 = ProviderRegistry()
        registry2 = ProviderRegistry()

        registry1.register_provider("company", "mock", MockCompanyProvider)

        # registry2 should not have the provider
        assert len(registry2.list_providers("company")) == 0

        with pytest.raises(KeyError):
            registry2.get_provider("company", "mock")
