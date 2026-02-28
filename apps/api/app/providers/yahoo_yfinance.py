"""
Yahoo Finance provider implementation using yfinance library.

This provider fetches company profiles, financial statements, and price history
from Yahoo Finance. It implements all three provider interfaces (CompanyUniverseProvider,
FundamentalsProvider, PriceHistoryProvider) and includes robust error handling,
rate limiting, and retry logic via BaseProvider.

yfinance is known to be unstable with occasional throttling, outages, and incomplete
data. This implementation handles these issues gracefully.
"""

import asyncio
import logging
from datetime import date, datetime
from typing import Any, Optional

import yfinance as yf

from app.core.config import settings
from app.domain.provider_contracts import (
    CompanyListItemDTO,
    CompanyProfileDTO,
    CompanyUniverseProvider,
    FinancialStatementDTO,
    FundamentalsProvider,
    PriceDataPointDTO,
    PriceHistoryDTO,
    PriceHistoryProvider,
    ProviderError,
)
from app.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class YahooYFinanceProvider(BaseProvider, CompanyUniverseProvider, FundamentalsProvider, PriceHistoryProvider):
    """
    Yahoo Finance data provider using the yfinance library.

    Implements all provider interfaces to fetch company data, fundamentals, and price history.
    Includes automatic rate limiting (default 2000 req/hour) and retry logic with exponential backoff.

    yfinance notes:
    - Free but unstable (rate limiting, occasional outages)
    - Data completeness varies by ticker (newer companies may lack historical data)
    - Rate limiting is not well-documented but empirically ~2000 requests/hour is safe
    """

    def __init__(
        self,
        rate_limit_requests: Optional[int] = None,
        rate_limit_window_seconds: Optional[int] = None,
        retry_attempts: int = 3,
        request_timeout: Optional[int] = None,
    ):
        """
        Initialize the Yahoo Finance provider.

        Args:
            rate_limit_requests: Max requests per window (default: from settings or 2000).
            rate_limit_window_seconds: Time window for rate limiting in seconds (default: 3600).
            retry_attempts: Number of retry attempts for failed requests (default: 3).
            request_timeout: Request timeout in seconds (default: from settings or 30).
        """
        # Use settings or defaults
        rate_limit = rate_limit_requests or settings.yahoo_finance_rate_limit
        timeout = request_timeout or settings.yahoo_finance_timeout

        super().__init__(
            provider_name="yahoo_finance",
            rate_limit_requests=rate_limit,
            rate_limit_window_seconds=rate_limit_window_seconds or 3600,
            retry_attempts=retry_attempts,
            request_timeout=timeout,
        )

        self.logger.info(
            f"YahooYFinanceProvider initialized (rate_limit={rate_limit}/hour, "
            f"timeout={timeout}s, retries={retry_attempts})"
        )

    # ============================================================================
    # FundamentalsProvider Implementation
    # ============================================================================

    async def fetch_company_profile(self, ticker: str) -> Optional[CompanyProfileDTO]:
        """
        Fetch company profile data from Yahoo Finance.

        Retrieves basic company information including name, sector, industry,
        market cap, and exchange from the ticker's info dictionary.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').

        Returns:
            CompanyProfileDTO with profile data, or None if ticker is invalid or data unavailable.

        Raises:
            ProviderError: If the API request fails or returns unexpected data.
        """
        self.logger.info(f"Fetching company profile for {ticker}")

        try:
            # Apply rate limiting and execute with retry
            profile_data = await self.with_retry(
                self._fetch_company_profile_impl,
                ticker=ticker,
            )
            return profile_data

        except Exception as e:
            self.logger.error(f"Failed to fetch company profile for {ticker}: {e}")
            raise ProviderError(
                message=f"Failed to fetch company profile: {e}",
                provider_name=self.provider_name,
                ticker=ticker,
                original_exception=e,
            )

    async def _fetch_company_profile_impl(self, ticker: str) -> Optional[CompanyProfileDTO]:
        """
        Internal implementation of company profile fetching.

        This method applies rate limiting and is called via with_retry.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            CompanyProfileDTO or None if data unavailable.

        Raises:
            ProviderError: On API errors or invalid responses.
        """
        # Apply rate limiting before making the request
        await self.rate_limiter.acquire()

        try:
            # Fetch ticker info from yfinance (blocking I/O, run in thread pool)
            info = await asyncio.to_thread(self._get_ticker_info, ticker)

            if not info:
                self.logger.warning(f"No info data returned for {ticker}")
                return None

            # Log raw snapshot (in production this would save to database)
            self._log_raw_snapshot(
                entity_type="company_profile",
                entity_key=ticker,
                payload=info,
            )

            # Extract and normalize profile data
            profile = self._normalize_company_profile(ticker, info)

            if profile:
                self.logger.info(
                    f"Successfully fetched profile for {ticker}: "
                    f"{profile.name} ({profile.sector or 'N/A'}/{profile.industry or 'N/A'})"
                )
            else:
                self.logger.warning(f"Could not normalize profile data for {ticker}")

            return profile

        except Exception as e:
            self.logger.error(f"Error fetching company profile for {ticker}: {e}")
            raise ProviderError(
                message=f"Error fetching company profile: {e}",
                provider_name=self.provider_name,
                ticker=ticker,
                original_exception=e,
            )

    def _get_ticker_info(self, ticker: str) -> dict[str, Any]:
        """
        Get ticker info from yfinance (synchronous).

        This method runs in a thread pool via asyncio.to_thread to avoid blocking.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Dictionary of ticker information from yfinance.

        Raises:
            Exception: On yfinance errors.
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            info = ticker_obj.info

            # yfinance sometimes returns empty dict or dict with just 'symbol' on error
            if not info or (len(info) == 1 and 'symbol' in info):
                return {}

            return info

        except Exception as e:
            self.logger.warning(f"yfinance error for {ticker}: {e}")
            raise

    def _normalize_company_profile(
        self,
        ticker: str,
        info: dict[str, Any],
    ) -> Optional[CompanyProfileDTO]:
        """
        Normalize raw yfinance info into CompanyProfileDTO.

        Args:
            ticker: Stock ticker symbol.
            info: Raw info dictionary from yfinance.

        Returns:
            CompanyProfileDTO or None if essential fields are missing.
        """
        # yfinance field mappings (field names can vary)
        name = info.get('longName') or info.get('shortName')

        if not name:
            # Without a name, the ticker is likely invalid
            return None

        return CompanyProfileDTO(
            ticker=ticker.upper(),
            name=name,
            legal_name=info.get('longName'),
            sector=info.get('sector'),
            industry=info.get('industry'),
            country=info.get('country'),
            currency=info.get('currency') or info.get('financialCurrency'),
            market_cap=info.get('marketCap'),
            exchange=info.get('exchange'),
        )

    # ============================================================================
    # FundamentalsProvider Implementation - Financial Statements
    # ============================================================================

    async def fetch_financial_statements(
        self,
        ticker: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> list[FinancialStatementDTO]:
        """
        Fetch annual financial statements for a company.

        Retrieves income statement, balance sheet, and cash flow data from yfinance
        and normalizes it into FinancialStatementDTO objects. Returns data for all
        available fiscal years, optionally filtered by start_year and end_year.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').
            start_year: Earliest fiscal year to fetch (e.g., 2013). None = fetch all available.
            end_year: Latest fiscal year to fetch (e.g., 2023). None = fetch up to current year.

        Returns:
            List of annual financial statements, ordered by fiscal year descending (newest first).
            Empty list if no data available.

        Raises:
            ProviderError: If the API request fails or returns unexpected data.
        """
        self.logger.info(
            f"Fetching financial statements for {ticker} "
            f"(start_year={start_year}, end_year={end_year})"
        )

        try:
            # Apply rate limiting and execute with retry
            statements = await self.with_retry(
                self._fetch_financial_statements_impl,
                ticker=ticker,
                start_year=start_year,
                end_year=end_year,
            )
            return statements

        except Exception as e:
            self.logger.error(f"Failed to fetch financial statements for {ticker}: {e}")
            raise ProviderError(
                message=f"Failed to fetch financial statements: {e}",
                provider_name=self.provider_name,
                ticker=ticker,
                original_exception=e,
            )

    async def _fetch_financial_statements_impl(
        self,
        ticker: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> list[FinancialStatementDTO]:
        """
        Internal implementation of financial statements fetching.

        This method applies rate limiting and is called via with_retry.

        Args:
            ticker: Stock ticker symbol.
            start_year: Earliest fiscal year to fetch.
            end_year: Latest fiscal year to fetch.

        Returns:
            List of annual financial statements.

        Raises:
            ProviderError: On API errors or invalid responses.
        """
        # Apply rate limiting before making the request
        await self.rate_limiter.acquire()

        try:
            # Fetch all three financial statements from yfinance
            # (blocking I/O, run in thread pool)
            financials_data = await asyncio.to_thread(
                self._get_ticker_financials,
                ticker,
            )

            if not financials_data:
                self.logger.warning(f"No financial data returned for {ticker}")
                return []

            # Log raw snapshots for each statement type
            for statement_type, data in financials_data.items():
                if data is not None and not data.empty:
                    self._log_raw_snapshot(
                        entity_type=f"financial_statement_{statement_type}",
                        entity_key=ticker,
                        payload=data.to_dict(),
                    )

            # Normalize and merge the three statements into FinancialStatementDTO objects
            statements = self._normalize_financial_statements(
                ticker,
                financials_data,
                start_year,
                end_year,
            )

            if statements:
                self.logger.info(
                    f"Successfully fetched {len(statements)} annual statements for {ticker} "
                    f"(years: {[s.fiscal_year for s in statements]})"
                )
            else:
                self.logger.warning(f"No financial statements available for {ticker}")

            return statements

        except Exception as e:
            self.logger.error(f"Error fetching financial statements for {ticker}: {e}")
            raise ProviderError(
                message=f"Error fetching financial statements: {e}",
                provider_name=self.provider_name,
                ticker=ticker,
                original_exception=e,
            )

    def _get_ticker_financials(self, ticker: str) -> dict[str, Any]:
        """
        Get all financial statements from yfinance (synchronous).

        This method runs in a thread pool via asyncio.to_thread to avoid blocking.
        Fetches income statement, balance sheet, and cash flow statement.

        Args:
            ticker: Stock ticker symbol.

        Returns:
            Dictionary with keys 'income', 'balance', 'cashflow' containing pandas DataFrames.

        Raises:
            Exception: On yfinance errors.
        """
        try:
            ticker_obj = yf.Ticker(ticker)

            # Fetch all three annual financial statements
            # yfinance returns DataFrames with columns as dates and rows as line items
            income_stmt = ticker_obj.financials  # Income statement (annual)
            balance_sheet = ticker_obj.balance_sheet  # Balance sheet (annual)
            cashflow_stmt = ticker_obj.cashflow  # Cash flow statement (annual)

            return {
                'income': income_stmt,
                'balance': balance_sheet,
                'cashflow': cashflow_stmt,
            }

        except Exception as e:
            self.logger.warning(f"yfinance error fetching financials for {ticker}: {e}")
            raise

    def _normalize_financial_statements(
        self,
        ticker: str,
        financials_data: dict[str, Any],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> list[FinancialStatementDTO]:
        """
        Normalize raw yfinance financial statements into FinancialStatementDTO objects.

        Merges income statement, balance sheet, and cash flow data for each fiscal year
        into a single FinancialStatementDTO. Filters by year range if specified.

        Args:
            ticker: Stock ticker symbol.
            financials_data: Dict with 'income', 'balance', 'cashflow' DataFrames.
            start_year: Earliest fiscal year to include.
            end_year: Latest fiscal year to include.

        Returns:
            List of FinancialStatementDTO ordered by fiscal year descending (newest first).
        """
        income_df = financials_data.get('income')
        balance_df = financials_data.get('balance')
        cashflow_df = financials_data.get('cashflow')

        # Check if we have at least one non-empty statement
        if (income_df is None or income_df.empty) and \
           (balance_df is None or balance_df.empty) and \
           (cashflow_df is None or cashflow_df.empty):
            return []

        # Extract unique fiscal years from all statements
        # yfinance DataFrames have dates as columns
        fiscal_dates = set()
        if income_df is not None and not income_df.empty:
            fiscal_dates.update(income_df.columns)
        if balance_df is not None and not balance_df.empty:
            fiscal_dates.update(balance_df.columns)
        if cashflow_df is not None and not cashflow_df.empty:
            fiscal_dates.update(cashflow_df.columns)

        if not fiscal_dates:
            return []

        # Build a FinancialStatementDTO for each fiscal year
        statements = []
        for fiscal_date in fiscal_dates:
            try:
                # Convert timestamp to date
                if hasattr(fiscal_date, 'date'):
                    fiscal_year_end = fiscal_date.date()
                else:
                    fiscal_year_end = fiscal_date

                fiscal_year = fiscal_year_end.year

                # Filter by year range if specified
                if start_year and fiscal_year < start_year:
                    continue
                if end_year and fiscal_year > end_year:
                    continue

                # Extract fields from each statement for this fiscal year
                statement = FinancialStatementDTO(
                    ticker=ticker.upper(),
                    fiscal_year=fiscal_year,
                    fiscal_year_end=fiscal_year_end,
                    # Income Statement
                    revenue=self._get_financial_field(income_df, fiscal_date, 'Total Revenue'),
                    gross_profit=self._get_financial_field(income_df, fiscal_date, 'Gross Profit'),
                    operating_income=self._get_financial_field(income_df, fiscal_date, 'Operating Income'),
                    net_income=self._get_financial_field(income_df, fiscal_date, 'Net Income'),
                    eps_diluted=self._get_financial_field(income_df, fiscal_date, 'Diluted EPS'),
                    # Balance Sheet
                    total_assets=self._get_financial_field(balance_df, fiscal_date, 'Total Assets'),
                    total_liabilities=self._get_financial_field(
                        balance_df, fiscal_date, 'Total Liabilities Net Minority Interest'
                    ),
                    shareholders_equity=self._get_financial_field(
                        balance_df, fiscal_date, 'Stockholders Equity'
                    ),
                    current_assets=self._get_financial_field(balance_df, fiscal_date, 'Current Assets'),
                    current_liabilities=self._get_financial_field(
                        balance_df, fiscal_date, 'Current Liabilities'
                    ),
                    long_term_debt=self._get_financial_field(balance_df, fiscal_date, 'Long Term Debt'),
                    # Cash Flow
                    operating_cash_flow=self._get_financial_field(
                        cashflow_df, fiscal_date, 'Operating Cash Flow'
                    ),
                    capital_expenditure=self._get_financial_field(
                        cashflow_df, fiscal_date, 'Capital Expenditure'
                    ),
                    free_cash_flow=self._get_financial_field(cashflow_df, fiscal_date, 'Free Cash Flow'),
                )

                statements.append(statement)

            except Exception as e:
                self.logger.warning(
                    f"Error normalizing financial statement for {ticker} "
                    f"fiscal date {fiscal_date}: {e}"
                )
                continue

        # Sort by fiscal year descending (newest first)
        statements.sort(key=lambda s: s.fiscal_year, reverse=True)

        return statements

    def _get_financial_field(
        self,
        df: Any,
        fiscal_date: Any,
        field_name: str,
    ) -> Optional[float]:
        """
        Extract a financial field from a yfinance DataFrame.

        Handles missing fields and various yfinance field name variations gracefully.

        Args:
            df: Pandas DataFrame from yfinance (or None).
            fiscal_date: Column key (fiscal year end date).
            field_name: Row index (field name to extract).

        Returns:
            Field value as float, or None if not found or invalid.
        """
        if df is None or df.empty:
            return None

        if fiscal_date not in df.columns:
            return None

        try:
            # Try exact field name match
            if field_name in df.index:
                value = df.loc[field_name, fiscal_date]
                return float(value) if value is not None and not (hasattr(value, 'isna') and value.isna()) else None

            # yfinance field names can vary - try common alternatives
            field_alternatives = {
                'Total Revenue': ['Total Revenue', 'Revenue'],
                'Gross Profit': ['Gross Profit'],
                'Operating Income': ['Operating Income', 'EBIT'],
                'Net Income': ['Net Income', 'Net Income Common Stockholders'],
                'Diluted EPS': ['Diluted EPS', 'Basic EPS'],
                'Total Assets': ['Total Assets'],
                'Total Liabilities Net Minority Interest': [
                    'Total Liabilities Net Minority Interest',
                    'Total Liabilities',
                ],
                'Stockholders Equity': [
                    'Stockholders Equity',
                    'Total Equity Gross Minority Interest',
                    'Common Stock Equity',
                ],
                'Current Assets': ['Current Assets'],
                'Current Liabilities': ['Current Liabilities'],
                'Long Term Debt': ['Long Term Debt', 'Long Term Debt And Capital Lease Obligation'],
                'Operating Cash Flow': ['Operating Cash Flow', 'Total Cash From Operating Activities'],
                'Capital Expenditure': ['Capital Expenditure', 'Capital Expenditures'],
                'Free Cash Flow': ['Free Cash Flow'],
            }

            # Try alternatives
            for alt_name in field_alternatives.get(field_name, []):
                if alt_name in df.index:
                    value = df.loc[alt_name, fiscal_date]
                    return float(value) if value is not None and not (
                        hasattr(value, 'isna') and value.isna()
                    ) else None

            return None

        except Exception as e:
            self.logger.debug(f"Error extracting field {field_name}: {e}")
            return None

    # ============================================================================
    # PriceHistoryProvider Implementation (Stubs for future subtasks)
    # ============================================================================

    async def fetch_price_history(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[PriceHistoryDTO]:
        """
        Fetch historical daily price data for a ticker.

        NOTE: This is a stub for subtask-4-3. Full implementation coming next.

        Args:
            ticker: Stock ticker symbol.
            start_date: Start date for price history.
            end_date: End date for price history.

        Returns:
            Historical price data or None.

        Raises:
            NotImplementedError: This method is not yet implemented.
        """
        raise NotImplementedError("fetch_price_history will be implemented in subtask-4-3")

    # ============================================================================
    # CompanyUniverseProvider Implementation (Stubs for future implementation)
    # ============================================================================

    async def fetch_company_list(
        self,
        exchange: Optional[str] = None,
        country: Optional[str] = None,
        is_active_only: bool = True,
    ) -> list[CompanyListItemDTO]:
        """
        Fetch a list of companies matching the specified criteria.

        NOTE: yfinance does not provide a native company list API.
        This would require integration with another data source or scraping.

        Args:
            exchange: Filter by exchange.
            country: Filter by country.
            is_active_only: Return only active companies.

        Returns:
            List of company identifiers.

        Raises:
            NotImplementedError: yfinance does not support company list fetching.
        """
        raise NotImplementedError(
            "yfinance does not provide company list API. "
            "Use a different provider (FMP, AlphaVantage) for universe fetching."
        )

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def _log_raw_snapshot(
        self,
        entity_type: str,
        entity_key: str,
        payload: dict[str, Any],
        http_status: Optional[int] = None,
    ) -> None:
        """
        Log raw API response as a snapshot.

        In production, this would create a ProviderRawSnapshot database record.
        For now, we log it for debugging.

        Args:
            entity_type: Type of entity (e.g., 'company_profile', 'income_statement').
            entity_key: Entity identifier (e.g., ticker symbol).
            payload: Raw response payload.
            http_status: HTTP status code (if applicable).
        """
        # TODO: In subtask-4-4, this will create ProviderRawSnapshot database records
        self.logger.debug(
            f"Raw snapshot: provider={self.provider_name}, "
            f"type={entity_type}, key={entity_key}, "
            f"payload_size={len(str(payload))} chars"
        )
