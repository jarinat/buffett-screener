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
from sqlalchemy.orm import Session

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
from app.models.provider import ProviderRawSnapshot
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
        db_session: Optional[Session] = None,
    ):
        """
        Initialize the Yahoo Finance provider.

        Args:
            rate_limit_requests: Max requests per window (default: from settings or 2000).
            rate_limit_window_seconds: Time window for rate limiting in seconds (default: 3600).
            retry_attempts: Number of retry attempts for failed requests (default: 3).
            request_timeout: Request timeout in seconds (default: from settings or 30).
            db_session: Optional database session for persisting raw snapshots.
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

        self.db_session = db_session

        self.logger.info(
            f"YahooYFinanceProvider initialized (rate_limit={rate_limit}/hour, "
            f"timeout={timeout}s, retries={retry_attempts}, "
            f"db_session={'configured' if db_session else 'not configured'})"
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

            # Log raw snapshot with timestamp and payload
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

        Extracts company profile fields from the raw yfinance info dictionary
        and creates a standardized CompanyProfileDTO. Returns None if the
        ticker appears invalid (no company name found).

        Args:
            ticker: Stock ticker symbol.
            info: Raw info dictionary from yfinance.

        Returns:
            CompanyProfileDTO or None if essential fields are missing.

        Raises:
            No exceptions raised - returns None on normalization failures.
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
        Handles missing or incomplete data gracefully by logging warnings and continuing.

        Args:
            ticker: Stock ticker symbol.
            financials_data: Dict with 'income', 'balance', 'cashflow' DataFrames.
            start_year: Earliest fiscal year to include.
            end_year: Latest fiscal year to include.

        Returns:
            List of FinancialStatementDTO ordered by fiscal year descending (newest first).

        Raises:
            No exceptions raised - errors during normalization are logged and skipped.
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
    # PriceHistoryProvider Implementation
    # ============================================================================

    async def fetch_price_history(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[PriceHistoryDTO]:
        """
        Fetch historical daily price data for a ticker.

        Retrieves daily OHLCV (Open, High, Low, Close, Volume) data from Yahoo Finance
        for the specified date range. If no dates are specified, fetches maximum available history.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL').
            start_date: Start date for price history. None = fetch maximum available history.
            end_date: End date for price history. None = fetch up to most recent trading day.

        Returns:
            PriceHistoryDTO with historical price data, or None if ticker is invalid or data unavailable.

        Raises:
            ProviderError: If the API request fails or returns unexpected data.
        """
        self.logger.info(
            f"Fetching price history for {ticker} "
            f"(start_date={start_date}, end_date={end_date})"
        )

        try:
            # Apply rate limiting and execute with retry
            price_history = await self.with_retry(
                self._fetch_price_history_impl,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
            )
            return price_history

        except Exception as e:
            self.logger.error(f"Failed to fetch price history for {ticker}: {e}")
            raise ProviderError(
                message=f"Failed to fetch price history: {e}",
                provider_name=self.provider_name,
                ticker=ticker,
                original_exception=e,
            )

    async def _fetch_price_history_impl(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[PriceHistoryDTO]:
        """
        Internal implementation of price history fetching.

        This method applies rate limiting and is called via with_retry.

        Args:
            ticker: Stock ticker symbol.
            start_date: Start date for price history.
            end_date: End date for price history.

        Returns:
            PriceHistoryDTO or None if data unavailable.

        Raises:
            ProviderError: On API errors or invalid responses.
        """
        # Apply rate limiting before making the request
        await self.rate_limiter.acquire()

        try:
            # Fetch price history from yfinance (blocking I/O, run in thread pool)
            history_df = await asyncio.to_thread(
                self._get_ticker_history,
                ticker,
                start_date,
                end_date,
            )

            if history_df is None or history_df.empty:
                self.logger.warning(f"No price history data returned for {ticker}")
                return None

            # Log raw snapshot with timestamp and payload
            self._log_raw_snapshot(
                entity_type="price_history",
                entity_key=ticker,
                payload=history_df.to_dict(),
            )

            # Normalize price history into PriceHistoryDTO
            price_history = self._normalize_price_history(
                ticker,
                history_df,
                start_date,
                end_date,
            )

            if price_history:
                self.logger.info(
                    f"Successfully fetched {len(price_history.data_points)} price data points for {ticker} "
                    f"(date range: {price_history.start_date} to {price_history.end_date})"
                )
            else:
                self.logger.warning(f"Could not normalize price history data for {ticker}")

            return price_history

        except Exception as e:
            self.logger.error(f"Error fetching price history for {ticker}: {e}")
            raise ProviderError(
                message=f"Error fetching price history: {e}",
                provider_name=self.provider_name,
                ticker=ticker,
                original_exception=e,
            )

    def _get_ticker_history(
        self,
        ticker: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Any:
        """
        Get historical price data from yfinance (synchronous).

        This method runs in a thread pool via asyncio.to_thread to avoid blocking.

        Args:
            ticker: Stock ticker symbol.
            start_date: Start date for price history.
            end_date: End date for price history.

        Returns:
            Pandas DataFrame with columns: Open, High, Low, Close, Volume, Adj Close.

        Raises:
            Exception: On yfinance errors.
        """
        try:
            ticker_obj = yf.Ticker(ticker)

            # Fetch historical price data
            # yfinance returns DataFrame with date index and OHLCV columns
            if start_date or end_date:
                # Convert date objects to strings for yfinance
                start_str = start_date.strftime('%Y-%m-%d') if start_date else None
                end_str = end_date.strftime('%Y-%m-%d') if end_date else None
                history = ticker_obj.history(start=start_str, end=end_str)
            else:
                # Fetch maximum available history
                history = ticker_obj.history(period='max')

            # yfinance sometimes returns empty DataFrame on error
            if history.empty:
                return None

            return history

        except Exception as e:
            self.logger.warning(f"yfinance error fetching history for {ticker}: {e}")
            raise

    def _normalize_price_history(
        self,
        ticker: str,
        history_df: Any,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[PriceHistoryDTO]:
        """
        Normalize raw yfinance price history into PriceHistoryDTO.

        Converts DataFrame rows into PriceDataPointDTO objects and determines
        the actual date range of the returned data. Handles missing OHLCV values
        gracefully by setting them to None.

        Args:
            ticker: Stock ticker symbol.
            history_df: Pandas DataFrame from yfinance with price data.
            start_date: Requested start date (for validation).
            end_date: Requested end date (for validation).

        Returns:
            PriceHistoryDTO with normalized price data, or None if data is invalid.

        Raises:
            No exceptions raised - errors during normalization are logged and skipped.
        """
        if history_df is None or history_df.empty:
            return None

        data_points = []

        # Iterate through DataFrame rows (index is date)
        for date_idx, row in history_df.iterrows():
            try:
                # Convert timestamp to date
                if hasattr(date_idx, 'date'):
                    price_date = date_idx.date()
                else:
                    price_date = date_idx

                # Extract OHLCV data (handle missing values gracefully)
                data_point = PriceDataPointDTO(
                    ticker=ticker.upper(),
                    date=price_date,
                    open=float(row['Open']) if 'Open' in row and row['Open'] is not None else None,
                    high=float(row['High']) if 'High' in row and row['High'] is not None else None,
                    low=float(row['Low']) if 'Low' in row and row['Low'] is not None else None,
                    close=float(row['Close']) if 'Close' in row and row['Close'] is not None else None,
                    volume=int(row['Volume']) if 'Volume' in row and row['Volume'] is not None else None,
                    adjusted_close=float(row['Adj Close']) if 'Adj Close' in row and row['Adj Close'] is not None else None,
                )

                data_points.append(data_point)

            except Exception as e:
                self.logger.warning(
                    f"Error normalizing price data point for {ticker} on {date_idx}: {e}"
                )
                continue

        if not data_points:
            return None

        # Sort by date ascending (chronological order)
        data_points.sort(key=lambda dp: dp.date)

        # Determine actual date range from the data
        actual_start_date = data_points[0].date
        actual_end_date = data_points[-1].date

        return PriceHistoryDTO(
            ticker=ticker.upper(),
            start_date=actual_start_date,
            end_date=actual_end_date,
            data_points=data_points,
        )

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
    # Batch Fetching Methods
    # ============================================================================

    async def fetch_batch_company_profiles(
        self,
        tickers: list[str],
    ) -> dict[str, Optional[CompanyProfileDTO]]:
        """
        Fetch company profiles for multiple tickers sequentially.

        Processes tickers one at a time to respect rate limits. Continues on errors
        and returns partial results with None for failed tickers.

        Args:
            tickers: List of stock ticker symbols to fetch.

        Returns:
            Dictionary mapping ticker -> CompanyProfileDTO (or None if failed/unavailable).
        """
        self.logger.info(f"Starting batch fetch for {len(tickers)} company profiles")

        results: dict[str, Optional[CompanyProfileDTO]] = {}

        for ticker in tickers:
            try:
                profile = await self.fetch_company_profile(ticker)
                results[ticker] = profile

                if profile:
                    self.logger.debug(f"Batch: Successfully fetched profile for {ticker}")
                else:
                    self.logger.debug(f"Batch: No profile data for {ticker}")

            except Exception as e:
                self.logger.warning(f"Batch: Failed to fetch profile for {ticker}: {e}")
                results[ticker] = None

        successful_count = sum(1 for v in results.values() if v is not None)
        self.logger.info(
            f"Batch fetch complete: {successful_count}/{len(tickers)} profiles fetched successfully"
        )

        return results

    async def fetch_batch_financial_statements(
        self,
        tickers: list[str],
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> dict[str, list[FinancialStatementDTO]]:
        """
        Fetch financial statements for multiple tickers sequentially.

        Processes tickers one at a time to respect rate limits. Continues on errors
        and returns partial results with empty list for failed tickers.

        Args:
            tickers: List of stock ticker symbols to fetch.
            start_year: Earliest fiscal year to fetch. None = fetch all available.
            end_year: Latest fiscal year to fetch. None = fetch up to current year.

        Returns:
            Dictionary mapping ticker -> list of FinancialStatementDTO (empty list if failed/unavailable).
        """
        self.logger.info(
            f"Starting batch fetch for {len(tickers)} financial statements "
            f"(start_year={start_year}, end_year={end_year})"
        )

        results: dict[str, list[FinancialStatementDTO]] = {}

        for ticker in tickers:
            try:
                statements = await self.fetch_financial_statements(ticker, start_year, end_year)
                results[ticker] = statements

                if statements:
                    self.logger.debug(
                        f"Batch: Successfully fetched {len(statements)} statements for {ticker}"
                    )
                else:
                    self.logger.debug(f"Batch: No financial statements for {ticker}")

            except Exception as e:
                self.logger.warning(f"Batch: Failed to fetch statements for {ticker}: {e}")
                results[ticker] = []

        successful_count = sum(1 for v in results.values() if v)
        self.logger.info(
            f"Batch fetch complete: {successful_count}/{len(tickers)} tickers with financial data"
        )

        return results

    async def fetch_batch_price_history(
        self,
        tickers: list[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict[str, Optional[PriceHistoryDTO]]:
        """
        Fetch price history for multiple tickers sequentially.

        Processes tickers one at a time to respect rate limits. Continues on errors
        and returns partial results with None for failed tickers.

        Args:
            tickers: List of stock ticker symbols to fetch.
            start_date: Start date for price history. None = fetch maximum available.
            end_date: End date for price history. None = fetch up to most recent.

        Returns:
            Dictionary mapping ticker -> PriceHistoryDTO (or None if failed/unavailable).
        """
        self.logger.info(
            f"Starting batch fetch for {len(tickers)} price histories "
            f"(start_date={start_date}, end_date={end_date})"
        )

        results: dict[str, Optional[PriceHistoryDTO]] = {}

        for ticker in tickers:
            try:
                history = await self.fetch_price_history(ticker, start_date, end_date)
                results[ticker] = history

                if history:
                    self.logger.debug(
                        f"Batch: Successfully fetched {len(history.data_points)} price points for {ticker}"
                    )
                else:
                    self.logger.debug(f"Batch: No price history for {ticker}")

            except Exception as e:
                self.logger.warning(f"Batch: Failed to fetch price history for {ticker}: {e}")
                results[ticker] = None

        successful_count = sum(1 for v in results.values() if v is not None)
        self.logger.info(
            f"Batch fetch complete: {successful_count}/{len(tickers)} price histories fetched successfully"
        )

        return results

    # ============================================================================
    # Utility Methods
    # ============================================================================

    def _log_raw_snapshot(
        self,
        entity_type: str,
        entity_key: str,
        payload: dict[str, Any],
        http_status: Optional[int] = None,
        ingestion_run_id: Optional[str] = None,
    ) -> ProviderRawSnapshot:
        """
        Log raw API response as a snapshot.

        Creates a ProviderRawSnapshot record with the complete raw response.
        If a database session is configured, the snapshot is persisted to the database.
        Otherwise, it's created in-memory and logged for debugging.

        Args:
            entity_type: Type of entity (e.g., 'company_profile', 'income_statement').
            entity_key: Entity identifier (e.g., ticker symbol).
            payload: Raw response payload (must be JSON-serializable).
            http_status: HTTP status code (if applicable).
            ingestion_run_id: Optional ID of the ingestion run that created this snapshot.

        Returns:
            ProviderRawSnapshot instance (persisted to DB if session available).
        """
        # Create ProviderRawSnapshot instance
        snapshot = ProviderRawSnapshot(
            provider_name=self.provider_name,
            provider_entity_type=entity_type,
            provider_entity_key=entity_key,
            fetched_at=datetime.utcnow(),
            payload_json=payload,
            http_status=http_status,
            ingestion_run_id=ingestion_run_id,
        )

        # Persist to database if session is configured
        if self.db_session:
            try:
                self.db_session.add(snapshot)
                self.db_session.commit()
                self.logger.debug(
                    f"Saved raw snapshot: provider={self.provider_name}, "
                    f"type={entity_type}, key={entity_key}, "
                    f"snapshot_id={snapshot.snapshot_id}"
                )
            except Exception as e:
                self.logger.error(
                    f"Failed to persist raw snapshot for {entity_key}: {e}",
                    exc_info=True,
                )
                self.db_session.rollback()
        else:
            # No database session configured - log for debugging
            self.logger.debug(
                f"Raw snapshot (not persisted): provider={self.provider_name}, "
                f"type={entity_type}, key={entity_key}, "
                f"payload_size={len(str(payload))} chars, "
                f"snapshot_id={snapshot.snapshot_id}"
            )

        return snapshot
