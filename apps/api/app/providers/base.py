"""
Abstract base classes for data providers.

Defines the contracts that all data provider implementations must follow.
This ensures the screening engine can work with any data source without
modification.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from app.models.company import CompanyInfo
from app.models.financial import IncomeStatement, BalanceSheet, CashFlow
from app.models.price import PriceHistory, PriceData


class CompanyUniverseProvider(ABC):
    """
    Abstract base class for company universe data providers.

    A company universe provider is responsible for:
    1. Providing a list of all available companies for screening
    2. Fetching detailed information about specific companies

    Implementations must handle:
    - Data source connectivity and error handling
    - Rate limiting and caching as appropriate
    - Mapping provider-specific data to canonical CompanyInfo models

    Example implementation:
        class YahooCompanyProvider(CompanyUniverseProvider):
            def get_company_universe(self) -> List[CompanyInfo]:
                # Fetch all companies from Yahoo Finance
                # Map to CompanyInfo objects
                return companies

            def get_company_info(self, ticker: str) -> CompanyInfo:
                # Fetch specific company from Yahoo Finance
                # Map to CompanyInfo object
                return company
    """

    @abstractmethod
    def get_company_universe(self) -> List[CompanyInfo]:
        """
        Get the complete list of companies available for screening.

        This method should return all companies that can be screened using
        this provider. The list should be comprehensive but may be filtered
        based on market cap, exchange, or other criteria relevant to the
        screening use case.

        Returns:
            List[CompanyInfo]: List of all available companies with their
                basic information (ticker, name, exchange, sector, etc.)

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            ValidationError: If the provider data cannot be mapped to CompanyInfo
        """
        pass

    @abstractmethod
    def get_company_info(self, ticker: str) -> CompanyInfo:
        """
        Get detailed information for a specific company.

        Retrieves comprehensive company information for the given ticker symbol.
        This method should be faster than filtering get_company_universe() and
        may provide more detailed or real-time information.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            CompanyInfo: Detailed company information including ticker, name,
                exchange, sector, industry, country, and currency

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            NotFoundError: If the ticker does not exist
            ValidationError: If the provider data cannot be mapped to CompanyInfo
        """
        pass


class FundamentalsProvider(ABC):
    """
    Abstract base class for fundamental financial data providers.

    A fundamentals provider is responsible for:
    1. Providing income statement data for companies
    2. Providing balance sheet data for companies
    3. Providing cash flow statement data for companies

    Implementations must handle:
    - Data source connectivity and error handling
    - Rate limiting and caching as appropriate
    - Mapping provider-specific data to canonical financial statement models
    - Supporting multiple reporting periods (annual, quarterly)

    Example implementation:
        class YahooFundamentalsProvider(FundamentalsProvider):
            def get_income_statement(self, ticker: str, period: str = "annual") -> IncomeStatement:
                # Fetch income statement from Yahoo Finance
                # Map to IncomeStatement object
                return income_statement

            def get_balance_sheet(self, ticker: str, period: str = "annual") -> BalanceSheet:
                # Fetch balance sheet from Yahoo Finance
                # Map to BalanceSheet object
                return balance_sheet

            def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
                # Fetch cash flow from Yahoo Finance
                # Map to CashFlow object
                return cash_flow
    """

    @abstractmethod
    def get_income_statement(self, ticker: str, period: str = "annual") -> IncomeStatement:
        """
        Get income statement data for a specific company.

        Retrieves the most recent income statement (profit & loss) for the given
        ticker symbol. This includes revenue, expenses, and profitability metrics.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period: Reporting period type - 'annual' for yearly statements or
                'quarterly' for quarterly statements. Defaults to 'annual'.

        Returns:
            IncomeStatement: Income statement data including revenue, cost of revenue,
                gross profit, operating expenses, operating income, net income,
                EPS, and shares outstanding

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            NotFoundError: If the ticker does not exist or has no financial data
            ValidationError: If the provider data cannot be mapped to IncomeStatement
        """
        pass

    @abstractmethod
    def get_balance_sheet(self, ticker: str, period: str = "annual") -> BalanceSheet:
        """
        Get balance sheet data for a specific company.

        Retrieves the most recent balance sheet for the given ticker symbol.
        This includes assets, liabilities, and shareholders' equity.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period: Reporting period type - 'annual' for yearly statements or
                'quarterly' for quarterly statements. Defaults to 'annual'.

        Returns:
            BalanceSheet: Balance sheet data including total assets, current assets,
                total liabilities, current liabilities, long-term debt, and
                shareholders' equity

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            NotFoundError: If the ticker does not exist or has no financial data
            ValidationError: If the provider data cannot be mapped to BalanceSheet
        """
        pass

    @abstractmethod
    def get_cash_flow(self, ticker: str, period: str = "annual") -> CashFlow:
        """
        Get cash flow statement data for a specific company.

        Retrieves the most recent cash flow statement for the given ticker symbol.
        This includes operating, investing, and financing cash flows.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            period: Reporting period type - 'annual' for yearly statements or
                'quarterly' for quarterly statements. Defaults to 'annual'.

        Returns:
            CashFlow: Cash flow statement data including operating cash flow,
                capital expenditures, free cash flow, dividends paid, and
                debt/equity financing activities

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            NotFoundError: If the ticker does not exist or has no financial data
            ValidationError: If the provider data cannot be mapped to CashFlow
        """
        pass


class PriceHistoryProvider(ABC):
    """
    Abstract base class for price history data providers.

    A price history provider is responsible for:
    1. Providing historical daily price data for securities
    2. Fetching current/latest price information
    3. Supporting flexible date ranges for historical queries

    Implementations must handle:
    - Data source connectivity and error handling
    - Rate limiting and caching as appropriate
    - Mapping provider-specific data to canonical PriceHistory and PriceData models
    - Handling trading days vs calendar days (weekends, holidays)
    - Adjusting prices for splits and dividends

    Example implementation:
        class YahooPriceHistoryProvider(PriceHistoryProvider):
            def get_price_history(self, ticker: str, start_date: date, end_date: date) -> PriceHistory:
                # Fetch historical prices from Yahoo Finance
                # Map to PriceHistory object with PriceData points
                return price_history

            def get_latest_price(self, ticker: str) -> PriceData:
                # Fetch latest price from Yahoo Finance
                # Map to PriceData object
                return price_data
    """

    @abstractmethod
    def get_price_history(
        self, ticker: str, start_date: date, end_date: date
    ) -> PriceHistory:
        """
        Get historical price data for a specific security over a date range.

        Retrieves daily OHLCV (Open, High, Low, Close, Volume) data for the given
        ticker symbol between the start and end dates (inclusive). The data should
        include adjusted closing prices to account for splits and dividends.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: First date to include in the history (inclusive)
            end_date: Last date to include in the history (inclusive)

        Returns:
            PriceHistory: Historical price data including ticker, date range,
                currency, and a chronologically ordered list of daily price points.
                Only trading days are included (weekends/holidays excluded).

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            NotFoundError: If the ticker does not exist
            ValidationError: If the provider data cannot be mapped to PriceHistory
                or if start_date is after end_date
        """
        pass

    @abstractmethod
    def get_latest_price(self, ticker: str) -> PriceData:
        """
        Get the most recent price data for a specific security.

        Retrieves the latest available trading day's price information for the
        given ticker symbol. This is typically faster than fetching full history
        and may provide more real-time data depending on the provider.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')

        Returns:
            PriceData: Latest price data including date, OHLCV values, currency,
                and adjusted close price

        Raises:
            ProviderError: If the data source is unavailable or returns an error
            NotFoundError: If the ticker does not exist
            ValidationError: If the provider data cannot be mapped to PriceData
        """
        pass
