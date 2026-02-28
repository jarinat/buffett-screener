"""
Provider contract interfaces for external data sources.

These abstract interfaces define the contracts that all data provider adapters
must implement. This ensures pluggability - the application can switch between
providers (Yahoo Finance, FMP, AlphaVantage, etc.) without changing screening logic.

All provider methods are async to support efficient I/O operations.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Data Transfer Objects (DTOs) for provider responses
# ============================================================================


class CompanyProfileDTO(BaseModel):
    """
    Company profile data returned by providers.

    Represents basic company information including name, sector, industry, and market cap.
    """

    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL')")
    name: str = Field(..., description="Company name")
    legal_name: Optional[str] = Field(None, description="Legal entity name")
    sector: Optional[str] = Field(None, description="Business sector")
    industry: Optional[str] = Field(None, description="Industry classification")
    country: Optional[str] = Field(None, description="Country of incorporation")
    currency: Optional[str] = Field(None, description="Reporting currency (e.g., 'USD')")
    market_cap: Optional[float] = Field(None, description="Market capitalization in reporting currency")
    exchange: Optional[str] = Field(None, description="Primary listing exchange")


class FinancialStatementDTO(BaseModel):
    """
    Annual financial statement data returned by providers.

    Contains normalized financial metrics from income statement, balance sheet, and cash flow.
    """

    ticker: str = Field(..., description="Stock ticker symbol")
    fiscal_year: int = Field(..., description="Fiscal year (e.g., 2023)")
    fiscal_year_end: Optional[date] = Field(None, description="Fiscal year end date")

    # Income Statement
    revenue: Optional[float] = Field(None, description="Total revenue")
    gross_profit: Optional[float] = Field(None, description="Gross profit")
    operating_income: Optional[float] = Field(None, description="Operating income (EBIT)")
    net_income: Optional[float] = Field(None, description="Net income")
    eps_diluted: Optional[float] = Field(None, description="Diluted earnings per share")

    # Balance Sheet
    total_assets: Optional[float] = Field(None, description="Total assets")
    total_liabilities: Optional[float] = Field(None, description="Total liabilities")
    shareholders_equity: Optional[float] = Field(None, description="Shareholders' equity")
    current_assets: Optional[float] = Field(None, description="Current assets")
    current_liabilities: Optional[float] = Field(None, description="Current liabilities")
    long_term_debt: Optional[float] = Field(None, description="Long-term debt")

    # Cash Flow
    operating_cash_flow: Optional[float] = Field(None, description="Operating cash flow")
    capital_expenditure: Optional[float] = Field(None, description="Capital expenditures (capex)")
    free_cash_flow: Optional[float] = Field(None, description="Free cash flow (OCF - capex)")


class PriceDataPointDTO(BaseModel):
    """
    Single price data point for a specific date.

    Represents daily OHLCV (Open, High, Low, Close, Volume) data.
    """

    ticker: str = Field(..., description="Stock ticker symbol")
    date: date = Field(..., description="Trading date")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: float = Field(..., description="Closing price (adjusted for splits)")
    volume: Optional[int] = Field(None, description="Trading volume")
    adjusted_close: Optional[float] = Field(None, description="Adjusted close (splits + dividends)")


class PriceHistoryDTO(BaseModel):
    """
    Historical price data for a ticker over a date range.

    Contains a series of daily price points.
    """

    ticker: str = Field(..., description="Stock ticker symbol")
    start_date: date = Field(..., description="Start date of the series")
    end_date: date = Field(..., description="End date of the series")
    data_points: list[PriceDataPointDTO] = Field(
        default_factory=list, description="Chronological list of price data points"
    )


class CompanyListItemDTO(BaseModel):
    """
    Single item in a company universe list.

    Minimal information needed to identify a company for bulk fetching.
    """

    ticker: str = Field(..., description="Stock ticker symbol")
    name: Optional[str] = Field(None, description="Company name")
    exchange: Optional[str] = Field(None, description="Listing exchange")
    is_active: bool = Field(default=True, description="Whether the listing is currently active")


# ============================================================================
# Provider Interfaces (Abstract Base Classes)
# ============================================================================


class CompanyUniverseProvider(ABC):
    """
    Provider interface for fetching lists of companies.

    Implementations fetch company universes from data sources (e.g., all US stocks,
    all stocks in S&P 500, etc.). Used during initial universe setup and periodic updates.
    """

    @abstractmethod
    async def fetch_company_list(
        self,
        exchange: Optional[str] = None,
        country: Optional[str] = None,
        is_active_only: bool = True,
    ) -> list[CompanyListItemDTO]:
        """
        Fetch a list of companies matching the specified criteria.

        Args:
            exchange: Filter by exchange (e.g., 'NASDAQ', 'NYSE'). None = all exchanges.
            country: Filter by country (e.g., 'US', 'CA'). None = all countries.
            is_active_only: If True, return only actively traded companies.

        Returns:
            List of company identifiers with minimal metadata.

        Raises:
            ProviderError: If the provider request fails.
        """
        pass


class FundamentalsProvider(ABC):
    """
    Provider interface for fetching company fundamentals and financial statements.

    Implementations fetch company profiles, income statements, balance sheets, and
    cash flow statements from data sources. This is the primary interface for
    obtaining financial data used in screening and metric calculations.
    """

    @abstractmethod
    async def fetch_company_profile(self, ticker: str) -> Optional[CompanyProfileDTO]:
        """
        Fetch company profile (name, sector, industry, market cap, etc.).

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').

        Returns:
            Company profile data, or None if the ticker is invalid or data unavailable.

        Raises:
            ProviderError: If the provider request fails.
        """
        pass

    @abstractmethod
    async def fetch_financial_statements(
        self,
        ticker: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> list[FinancialStatementDTO]:
        """
        Fetch annual financial statements for a company.

        Returns normalized financial data from income statement, balance sheet,
        and cash flow statement for each fiscal year in the specified range.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').
            start_year: Earliest fiscal year to fetch (e.g., 2013). None = fetch all available.
            end_year: Latest fiscal year to fetch (e.g., 2023). None = fetch up to current year.

        Returns:
            List of annual financial statements, ordered by fiscal year descending (newest first).
            Empty list if no data available.

        Raises:
            ProviderError: If the provider request fails.
        """
        pass


class PriceHistoryProvider(ABC):
    """
    Provider interface for fetching historical price data.

    Implementations fetch daily OHLCV (Open, High, Low, Close, Volume) data for stocks.
    Used for price-based metrics, charting, and backtesting screens.
    """

    @abstractmethod
    async def fetch_price_history(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[PriceHistoryDTO]:
        """
        Fetch historical daily price data for a ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').
            start_date: Start date for price history. None = fetch maximum available history.
            end_date: End date for price history. None = fetch up to most recent trading day.

        Returns:
            Historical price data, or None if the ticker is invalid or data unavailable.

        Raises:
            ProviderError: If the provider request fails.
        """
        pass


# ============================================================================
# Provider Exceptions
# ============================================================================


class ProviderError(Exception):
    """
    Base exception for provider-related errors.

    Raised when a provider encounters an error fetching or processing data.
    """

    def __init__(
        self,
        message: str,
        provider_name: str,
        ticker: Optional[str] = None,
        original_exception: Optional[Exception] = None,
    ):
        """
        Initialize a provider error.

        Args:
            message: Human-readable error message.
            provider_name: Name of the provider that raised the error.
            ticker: Stock ticker associated with the error (if applicable).
            original_exception: The underlying exception that caused this error.
        """
        self.message = message
        self.provider_name = provider_name
        self.ticker = ticker
        self.original_exception = original_exception
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.provider_name}]"]
        if self.ticker:
            parts.append(f"ticker={self.ticker}")
        parts.append(self.message)
        if self.original_exception:
            parts.append(f"(caused by: {type(self.original_exception).__name__})")
        return " ".join(parts)


class RateLimitError(ProviderError):
    """
    Exception raised when provider rate limit is exceeded.

    Implementations should raise this when receiving HTTP 429 or similar rate limit responses.
    """

    pass


class InsufficientDataError(ProviderError):
    """
    Exception raised when provider returns incomplete or missing data.

    This is NOT an error - it's an expected condition when data is unavailable
    (e.g., a new company with no historical financials).
    """

    pass
