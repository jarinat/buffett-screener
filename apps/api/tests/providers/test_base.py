"""Tests for provider base classes and abstract interfaces."""

import inspect
from datetime import date, datetime
from decimal import Decimal
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


class TestCompanyUniverseProvider:
    """Tests for CompanyUniverseProvider abstract base class."""

    def test_is_abstract(self):
        """Test that CompanyUniverseProvider is an abstract base class."""
        assert inspect.isabstract(CompanyUniverseProvider)

    def test_cannot_instantiate_directly(self):
        """Test that CompanyUniverseProvider cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            CompanyUniverseProvider()
        assert "abstract" in str(exc_info.value).lower()

    def test_missing_get_company_universe_raises_error(self):
        """Test that missing get_company_universe implementation raises error."""

        class IncompleteProvider(CompanyUniverseProvider):
            def get_company_info(self, ticker: str) -> CompanyInfo:
                return CompanyInfo(
                    company_id=ticker,
                    name="Test Company",
                    ticker=ticker,
                    exchange="NYSE",
                    currency="USD",
                )

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_company_universe" in str(exc_info.value)

    def test_missing_get_company_info_raises_error(self):
        """Test that missing get_company_info implementation raises error."""

        class IncompleteProvider(CompanyUniverseProvider):
            def get_company_universe(self) -> List[CompanyInfo]:
                return []

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_company_info" in str(exc_info.value)

    def test_concrete_implementation_works(self):
        """Test that a complete concrete implementation can be instantiated."""

        class MockCompanyProvider(CompanyUniverseProvider):
            def get_company_universe(self) -> List[CompanyInfo]:
                return [
                    CompanyInfo(
                        company_id="AAPL",
                        name="Apple Inc.",
                        ticker="AAPL",
                        exchange="NASDAQ",
                        sector="Technology",
                        industry="Consumer Electronics",
                        country="US",
                        currency="USD",
                    ),
                    CompanyInfo(
                        company_id="MSFT",
                        name="Microsoft Corporation",
                        ticker="MSFT",
                        exchange="NASDAQ",
                        sector="Technology",
                        industry="Software",
                        country="US",
                        currency="USD",
                    ),
                ]

            def get_company_info(self, ticker: str) -> CompanyInfo:
                return CompanyInfo(
                    company_id=ticker,
                    name=f"{ticker} Company",
                    ticker=ticker,
                    exchange="NYSE",
                    currency="USD",
                )

        # Should instantiate without error
        provider = MockCompanyProvider()
        assert provider is not None

        # Should be able to call methods
        companies = provider.get_company_universe()
        assert len(companies) == 2
        assert companies[0].ticker == "AAPL"
        assert companies[1].ticker == "MSFT"

        company = provider.get_company_info("TEST")
        assert company.ticker == "TEST"
        assert company.name == "TEST Company"

    def test_interface_methods_exist(self):
        """Test that required interface methods are defined."""
        assert hasattr(CompanyUniverseProvider, "get_company_universe")
        assert hasattr(CompanyUniverseProvider, "get_company_info")
        assert callable(getattr(CompanyUniverseProvider, "get_company_universe"))
        assert callable(getattr(CompanyUniverseProvider, "get_company_info"))

    def test_get_company_universe_signature(self):
        """Test get_company_universe method signature."""
        sig = inspect.signature(CompanyUniverseProvider.get_company_universe)
        # Should have only self parameter
        params = list(sig.parameters.keys())
        assert params == ["self"]
        # Return annotation should be List[CompanyInfo]
        assert sig.return_annotation == List[CompanyInfo]

    def test_get_company_info_signature(self):
        """Test get_company_info method signature."""
        sig = inspect.signature(CompanyUniverseProvider.get_company_info)
        # Should have self and ticker parameters
        params = list(sig.parameters.keys())
        assert params == ["self", "ticker"]
        assert sig.parameters["ticker"].annotation == str
        # Return annotation should be CompanyInfo
        assert sig.return_annotation == CompanyInfo


class TestFundamentalsProvider:
    """Tests for FundamentalsProvider abstract base class."""

    def test_is_abstract(self):
        """Test that FundamentalsProvider is an abstract base class."""
        assert inspect.isabstract(FundamentalsProvider)

    def test_cannot_instantiate_directly(self):
        """Test that FundamentalsProvider cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            FundamentalsProvider()
        assert "abstract" in str(exc_info.value).lower()

    def test_missing_get_income_statement_raises_error(self):
        """Test that missing get_income_statement implementation raises error."""

        class IncompleteProvider(FundamentalsProvider):
            def get_balance_sheet(
                self, ticker: str, period: str = "annual"
            ) -> BalanceSheet:
                return BalanceSheet(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

            def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
                return CashFlow(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_income_statement" in str(exc_info.value)

    def test_missing_get_balance_sheet_raises_error(self):
        """Test that missing get_balance_sheet implementation raises error."""

        class IncompleteProvider(FundamentalsProvider):
            def get_income_statement(
                self, ticker: str, period: str = "annual"
            ) -> IncomeStatement:
                return IncomeStatement(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

            def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
                return CashFlow(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_balance_sheet" in str(exc_info.value)

    def test_missing_get_cash_flow_raises_error(self):
        """Test that missing get_cash_flow implementation raises error."""

        class IncompleteProvider(FundamentalsProvider):
            def get_income_statement(
                self, ticker: str, period: str = "annual"
            ) -> IncomeStatement:
                return IncomeStatement(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

            def get_balance_sheet(
                self, ticker: str, period: str = "annual"
            ) -> BalanceSheet:
                return BalanceSheet(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_cash_flow" in str(exc_info.value)

    def test_concrete_implementation_works(self):
        """Test that a complete concrete implementation can be instantiated."""

        class MockFundamentalsProvider(FundamentalsProvider):
            def get_income_statement(
                self, ticker: str, period: str = "annual"
            ) -> IncomeStatement:
                return IncomeStatement(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                    revenue=Decimal("100000000"),
                    cost_of_revenue=Decimal("40000000"),
                    gross_profit=Decimal("60000000"),
                    net_income=Decimal("25000000"),
                    diluted_eps=Decimal("2.50"),
                )

            def get_balance_sheet(
                self, ticker: str, period: str = "annual"
            ) -> BalanceSheet:
                return BalanceSheet(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                    total_assets=Decimal("500000000"),
                    total_liabilities=Decimal("200000000"),
                    shareholders_equity=Decimal("300000000"),
                )

            def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
                return CashFlow(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                    operating_cash_flow=Decimal("30000000"),
                    capital_expenditures=Decimal("5000000"),
                    free_cash_flow=Decimal("25000000"),
                )

        # Should instantiate without error
        provider = MockFundamentalsProvider()
        assert provider is not None

        # Should be able to call methods
        income_stmt = provider.get_income_statement("AAPL")
        assert income_stmt.ticker == "AAPL"
        assert income_stmt.period == "annual"
        assert income_stmt.revenue == Decimal("100000000")

        balance_sheet = provider.get_balance_sheet("MSFT", period="quarterly")
        assert balance_sheet.ticker == "MSFT"
        assert balance_sheet.period == "quarterly"
        assert balance_sheet.total_assets == Decimal("500000000")

        cash_flow = provider.get_cash_flow("GOOGL")
        assert cash_flow.ticker == "GOOGL"
        assert cash_flow.free_cash_flow == Decimal("25000000")

    def test_interface_methods_exist(self):
        """Test that required interface methods are defined."""
        assert hasattr(FundamentalsProvider, "get_income_statement")
        assert hasattr(FundamentalsProvider, "get_balance_sheet")
        assert hasattr(FundamentalsProvider, "get_cash_flow")
        assert callable(getattr(FundamentalsProvider, "get_income_statement"))
        assert callable(getattr(FundamentalsProvider, "get_balance_sheet"))
        assert callable(getattr(FundamentalsProvider, "get_cash_flow"))

    def test_get_income_statement_signature(self):
        """Test get_income_statement method signature."""
        sig = inspect.signature(FundamentalsProvider.get_income_statement)
        params = list(sig.parameters.keys())
        assert params == ["self", "ticker", "period"]
        assert sig.parameters["ticker"].annotation == str
        assert sig.parameters["period"].annotation == str
        assert sig.parameters["period"].default == "annual"
        assert sig.return_annotation == IncomeStatement

    def test_get_balance_sheet_signature(self):
        """Test get_balance_sheet method signature."""
        sig = inspect.signature(FundamentalsProvider.get_balance_sheet)
        params = list(sig.parameters.keys())
        assert params == ["self", "ticker", "period"]
        assert sig.parameters["ticker"].annotation == str
        assert sig.parameters["period"].annotation == str
        assert sig.parameters["period"].default == "annual"
        assert sig.return_annotation == BalanceSheet

    def test_get_cash_flow_signature(self):
        """Test get_cash_flow method signature."""
        sig = inspect.signature(FundamentalsProvider.get_cash_flow)
        params = list(sig.parameters.keys())
        assert params == ["self", "ticker", "period"]
        assert sig.parameters["ticker"].annotation == str
        assert sig.parameters["period"].annotation == str
        assert sig.parameters["period"].default == "annual"
        assert sig.return_annotation == CashFlow


class TestPriceHistoryProvider:
    """Tests for PriceHistoryProvider abstract base class."""

    def test_is_abstract(self):
        """Test that PriceHistoryProvider is an abstract base class."""
        assert inspect.isabstract(PriceHistoryProvider)

    def test_cannot_instantiate_directly(self):
        """Test that PriceHistoryProvider cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            PriceHistoryProvider()
        assert "abstract" in str(exc_info.value).lower()

    def test_missing_get_price_history_raises_error(self):
        """Test that missing get_price_history implementation raises error."""

        class IncompleteProvider(PriceHistoryProvider):
            def get_latest_price(self, ticker: str) -> PriceData:
                return PriceData(
                    ticker=ticker,
                    date=date(2024, 12, 31),
                    open=Decimal("100.00"),
                    high=Decimal("105.00"),
                    low=Decimal("99.00"),
                    close=Decimal("103.00"),
                    volume=1000000,
                    currency="USD",
                )

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_price_history" in str(exc_info.value)

    def test_missing_get_latest_price_raises_error(self):
        """Test that missing get_latest_price implementation raises error."""

        class IncompleteProvider(PriceHistoryProvider):
            def get_price_history(
                self, ticker: str, start_date: date, end_date: date
            ) -> PriceHistory:
                return PriceHistory(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    currency="USD",
                    prices=[],
                )

        with pytest.raises(TypeError) as exc_info:
            IncompleteProvider()
        assert "abstract" in str(exc_info.value).lower()
        assert "get_latest_price" in str(exc_info.value)

    def test_concrete_implementation_works(self):
        """Test that a complete concrete implementation can be instantiated."""

        class MockPriceHistoryProvider(PriceHistoryProvider):
            def get_price_history(
                self, ticker: str, start_date: date, end_date: date
            ) -> PriceHistory:
                prices = [
                    PriceData(
                        ticker=ticker,
                        date=date(2024, 1, 2),
                        open=Decimal("100.00"),
                        high=Decimal("105.00"),
                        low=Decimal("99.00"),
                        close=Decimal("103.00"),
                        volume=1000000,
                        currency="USD",
                    ),
                    PriceData(
                        ticker=ticker,
                        date=date(2024, 1, 3),
                        open=Decimal("103.00"),
                        high=Decimal("108.00"),
                        low=Decimal("102.00"),
                        close=Decimal("106.00"),
                        volume=1200000,
                        currency="USD",
                    ),
                ]
                return PriceHistory(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    currency="USD",
                    prices=prices,
                )

            def get_latest_price(self, ticker: str) -> PriceData:
                return PriceData(
                    ticker=ticker,
                    date=date(2024, 12, 31),
                    open=Decimal("150.00"),
                    high=Decimal("155.00"),
                    low=Decimal("149.00"),
                    close=Decimal("153.00"),
                    volume=2000000,
                    currency="USD",
                )

        # Should instantiate without error
        provider = MockPriceHistoryProvider()
        assert provider is not None

        # Should be able to call methods
        history = provider.get_price_history(
            "AAPL", date(2024, 1, 1), date(2024, 1, 31)
        )
        assert history.ticker == "AAPL"
        assert history.start_date == date(2024, 1, 1)
        assert history.end_date == date(2024, 1, 31)
        assert len(history.prices) == 2
        assert history.prices[0].close == Decimal("103.00")
        assert history.prices[1].close == Decimal("106.00")

        latest = provider.get_latest_price("MSFT")
        assert latest.ticker == "MSFT"
        assert latest.date == date(2024, 12, 31)
        assert latest.close == Decimal("153.00")

    def test_interface_methods_exist(self):
        """Test that required interface methods are defined."""
        assert hasattr(PriceHistoryProvider, "get_price_history")
        assert hasattr(PriceHistoryProvider, "get_latest_price")
        assert callable(getattr(PriceHistoryProvider, "get_price_history"))
        assert callable(getattr(PriceHistoryProvider, "get_latest_price"))

    def test_get_price_history_signature(self):
        """Test get_price_history method signature."""
        sig = inspect.signature(PriceHistoryProvider.get_price_history)
        params = list(sig.parameters.keys())
        assert params == ["self", "ticker", "start_date", "end_date"]
        assert sig.parameters["ticker"].annotation == str
        assert sig.parameters["start_date"].annotation == date
        assert sig.parameters["end_date"].annotation == date
        assert sig.return_annotation == PriceHistory

    def test_get_latest_price_signature(self):
        """Test get_latest_price method signature."""
        sig = inspect.signature(PriceHistoryProvider.get_latest_price)
        params = list(sig.parameters.keys())
        assert params == ["self", "ticker"]
        assert sig.parameters["ticker"].annotation == str
        assert sig.return_annotation == PriceData


class TestProviderInteroperability:
    """Tests for ensuring providers work together correctly."""

    def test_all_providers_can_be_implemented_together(self):
        """Test that a single class can implement multiple provider interfaces."""

        class UnifiedProvider(
            CompanyUniverseProvider, FundamentalsProvider, PriceHistoryProvider
        ):
            def get_company_universe(self) -> List[CompanyInfo]:
                return []

            def get_company_info(self, ticker: str) -> CompanyInfo:
                return CompanyInfo(
                    company_id=ticker,
                    name="Test",
                    ticker=ticker,
                    exchange="NYSE",
                    currency="USD",
                )

            def get_income_statement(
                self, ticker: str, period: str = "annual"
            ) -> IncomeStatement:
                return IncomeStatement(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

            def get_balance_sheet(
                self, ticker: str, period: str = "annual"
            ) -> BalanceSheet:
                return BalanceSheet(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

            def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
                return CashFlow(
                    ticker=ticker,
                    period=period,
                    end_date=date(2024, 12, 31),
                    currency="USD",
                )

            def get_price_history(
                self, ticker: str, start_date: date, end_date: date
            ) -> PriceHistory:
                return PriceHistory(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date,
                    currency="USD",
                    prices=[],
                )

            def get_latest_price(self, ticker: str) -> PriceData:
                return PriceData(
                    ticker=ticker,
                    date=date(2024, 12, 31),
                    open=Decimal("100.00"),
                    high=Decimal("105.00"),
                    low=Decimal("99.00"),
                    close=Decimal("103.00"),
                    volume=1000000,
                    currency="USD",
                )

        # Should instantiate without error
        provider = UnifiedProvider()
        assert provider is not None
        assert isinstance(provider, CompanyUniverseProvider)
        assert isinstance(provider, FundamentalsProvider)
        assert isinstance(provider, PriceHistoryProvider)

        # All methods should work
        assert provider.get_company_universe() == []
        assert provider.get_company_info("TEST").ticker == "TEST"
        assert provider.get_income_statement("TEST").ticker == "TEST"
        assert provider.get_balance_sheet("TEST").ticker == "TEST"
        assert provider.get_cash_flow("TEST").ticker == "TEST"
        assert (
            provider.get_price_history(
                "TEST", date(2024, 1, 1), date(2024, 12, 31)
            ).ticker
            == "TEST"
        )
        assert provider.get_latest_price("TEST").ticker == "TEST"
