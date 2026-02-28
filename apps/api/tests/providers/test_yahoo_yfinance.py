"""Unit tests for Yahoo Finance provider implementation."""

import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch
import pandas as pd

from app.providers.yahoo_yfinance import YahooYFinanceProvider
from app.domain.provider_contracts import (
    CompanyProfileDTO,
    FinancialStatementDTO,
    PriceDataPointDTO,
    PriceHistoryDTO,
    ProviderError,
)


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def provider():
    """Create a YahooYFinanceProvider instance for testing."""
    return YahooYFinanceProvider(
        rate_limit_requests=10,
        rate_limit_window_seconds=1,
        retry_attempts=2,
        request_timeout=5,
        db_session=None,
    )


@pytest.fixture
def mock_ticker_info():
    """Mock yfinance ticker info dictionary."""
    return {
        'symbol': 'AAPL',
        'longName': 'Apple Inc.',
        'shortName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'country': 'US',
        'currency': 'USD',
        'marketCap': 3000000000000,
        'exchange': 'NASDAQ',
    }


@pytest.fixture
def mock_ticker_info_minimal():
    """Mock yfinance ticker info with minimal data."""
    return {
        'symbol': 'TEST',
        'shortName': 'Test Company',
    }


@pytest.fixture
def mock_financials_dataframes():
    """Mock yfinance financial statement DataFrames."""
    # Create sample DataFrames with fiscal year columns
    dates = [pd.Timestamp('2023-12-31'), pd.Timestamp('2022-12-31')]

    income_df = pd.DataFrame({
        dates[0]: {
            'Total Revenue': 400000000000,
            'Gross Profit': 200000000000,
            'Operating Income': 120000000000,
            'Net Income': 100000000000,
            'Diluted EPS': 6.50,
        },
        dates[1]: {
            'Total Revenue': 380000000000,
            'Gross Profit': 190000000000,
            'Operating Income': 110000000000,
            'Net Income': 95000000000,
            'Diluted EPS': 6.20,
        },
    })

    balance_df = pd.DataFrame({
        dates[0]: {
            'Total Assets': 350000000000,
            'Total Liabilities Net Minority Interest': 280000000000,
            'Stockholders Equity': 70000000000,
            'Current Assets': 120000000000,
            'Current Liabilities': 100000000000,
            'Long Term Debt': 110000000000,
        },
        dates[1]: {
            'Total Assets': 340000000000,
            'Total Liabilities Net Minority Interest': 270000000000,
            'Stockholders Equity': 70000000000,
            'Current Assets': 115000000000,
            'Current Liabilities': 95000000000,
            'Long Term Debt': 105000000000,
        },
    })

    cashflow_df = pd.DataFrame({
        dates[0]: {
            'Operating Cash Flow': 110000000000,
            'Capital Expenditure': -10000000000,
            'Free Cash Flow': 100000000000,
        },
        dates[1]: {
            'Operating Cash Flow': 105000000000,
            'Capital Expenditure': -9000000000,
            'Free Cash Flow': 96000000000,
        },
    })

    return {
        'income': income_df,
        'balance': balance_df,
        'cashflow': cashflow_df,
    }


@pytest.fixture
def mock_price_history_dataframe():
    """Mock yfinance price history DataFrame."""
    dates = pd.date_range('2024-01-01', '2024-01-05', freq='D')

    return pd.DataFrame({
        'Open': [180.0, 181.0, 182.0, 181.5, 183.0],
        'High': [182.0, 183.0, 184.0, 183.5, 185.0],
        'Low': [179.0, 180.0, 181.0, 180.5, 182.0],
        'Close': [181.0, 182.0, 183.0, 182.5, 184.0],
        'Volume': [50000000, 51000000, 52000000, 51500000, 53000000],
        'Adj Close': [181.0, 182.0, 183.0, 182.5, 184.0],
    }, index=dates)


# ============================================================================
# Tests - Company Profile Fetching
# ============================================================================


@pytest.mark.asyncio
async def test_fetch_company_profile_success(provider, mock_ticker_info):
    """Test successful company profile fetch."""
    with patch.object(provider, '_get_ticker_info', return_value=mock_ticker_info):
        profile = await provider.fetch_company_profile('AAPL')

        assert profile is not None
        assert isinstance(profile, CompanyProfileDTO)
        assert profile.ticker == 'AAPL'
        assert profile.name == 'Apple Inc.'
        assert profile.legal_name == 'Apple Inc.'
        assert profile.sector == 'Technology'
        assert profile.industry == 'Consumer Electronics'
        assert profile.country == 'US'
        assert profile.currency == 'USD'
        assert profile.market_cap == 3000000000000
        assert profile.exchange == 'NASDAQ'


@pytest.mark.asyncio
async def test_fetch_company_profile_minimal_data(provider, mock_ticker_info_minimal):
    """Test company profile fetch with minimal data."""
    with patch.object(provider, '_get_ticker_info', return_value=mock_ticker_info_minimal):
        profile = await provider.fetch_company_profile('TEST')

        assert profile is not None
        assert profile.ticker == 'TEST'
        assert profile.name == 'Test Company'
        assert profile.sector is None
        assert profile.industry is None


@pytest.mark.asyncio
async def test_fetch_company_profile_no_name(provider):
    """Test company profile fetch with missing name returns None."""
    mock_info = {'symbol': 'INVALID'}

    with patch.object(provider, '_get_ticker_info', return_value=mock_info):
        profile = await provider.fetch_company_profile('INVALID')

        assert profile is None


@pytest.mark.asyncio
async def test_fetch_company_profile_empty_info(provider):
    """Test company profile fetch with empty info returns None."""
    with patch.object(provider, '_get_ticker_info', return_value={}):
        profile = await provider.fetch_company_profile('INVALID')

        assert profile is None


@pytest.mark.asyncio
async def test_fetch_company_profile_yfinance_error(provider):
    """Test company profile fetch handles yfinance errors."""
    with patch.object(provider, '_get_ticker_info', side_effect=Exception('yfinance error')):
        with pytest.raises(ProviderError) as exc_info:
            await provider.fetch_company_profile('AAPL')

        assert 'Failed to fetch company profile' in str(exc_info.value)
        assert exc_info.value.provider_name == 'yahoo_finance'
        assert exc_info.value.ticker == 'AAPL'


# ============================================================================
# Tests - Financial Statements Fetching
# ============================================================================


@pytest.mark.asyncio
async def test_fetch_financial_statements_success(provider, mock_financials_dataframes):
    """Test successful financial statements fetch."""
    with patch.object(provider, '_get_ticker_financials', return_value=mock_financials_dataframes):
        statements = await provider.fetch_financial_statements('AAPL')

        assert len(statements) == 2
        assert all(isinstance(s, FinancialStatementDTO) for s in statements)

        # Check statements are sorted by fiscal year descending
        assert statements[0].fiscal_year > statements[1].fiscal_year

        # Check first statement (2023)
        stmt_2023 = statements[0]
        assert stmt_2023.ticker == 'AAPL'
        assert stmt_2023.fiscal_year == 2023
        assert stmt_2023.revenue == 400000000000
        assert stmt_2023.gross_profit == 200000000000
        assert stmt_2023.operating_income == 120000000000
        assert stmt_2023.net_income == 100000000000
        assert stmt_2023.eps_diluted == 6.50
        assert stmt_2023.total_assets == 350000000000
        assert stmt_2023.total_liabilities == 280000000000
        assert stmt_2023.shareholders_equity == 70000000000
        assert stmt_2023.operating_cash_flow == 110000000000
        assert stmt_2023.capital_expenditure == -10000000000
        assert stmt_2023.free_cash_flow == 100000000000


@pytest.mark.asyncio
async def test_fetch_financial_statements_year_filtering(provider, mock_financials_dataframes):
    """Test financial statements fetch with year filtering."""
    with patch.object(provider, '_get_ticker_financials', return_value=mock_financials_dataframes):
        # Fetch only 2023
        statements = await provider.fetch_financial_statements('AAPL', start_year=2023, end_year=2023)

        assert len(statements) == 1
        assert statements[0].fiscal_year == 2023


@pytest.mark.asyncio
async def test_fetch_financial_statements_empty_data(provider):
    """Test financial statements fetch with empty DataFrames."""
    empty_data = {
        'income': pd.DataFrame(),
        'balance': pd.DataFrame(),
        'cashflow': pd.DataFrame(),
    }

    with patch.object(provider, '_get_ticker_financials', return_value=empty_data):
        statements = await provider.fetch_financial_statements('AAPL')

        assert statements == []


@pytest.mark.asyncio
async def test_fetch_financial_statements_partial_data(provider):
    """Test financial statements fetch with some missing DataFrames."""
    dates = [pd.Timestamp('2023-12-31')]
    partial_data = {
        'income': pd.DataFrame({
            dates[0]: {
                'Total Revenue': 400000000000,
            }
        }),
        'balance': pd.DataFrame(),
        'cashflow': pd.DataFrame(),
    }

    with patch.object(provider, '_get_ticker_financials', return_value=partial_data):
        statements = await provider.fetch_financial_statements('AAPL')

        assert len(statements) == 1
        assert statements[0].revenue == 400000000000
        # Balance sheet and cash flow fields should be None
        assert statements[0].total_assets is None
        assert statements[0].operating_cash_flow is None


@pytest.mark.asyncio
async def test_fetch_financial_statements_yfinance_error(provider):
    """Test financial statements fetch handles yfinance errors."""
    with patch.object(provider, '_get_ticker_financials', side_effect=Exception('yfinance error')):
        with pytest.raises(ProviderError) as exc_info:
            await provider.fetch_financial_statements('AAPL')

        assert 'Failed to fetch financial statements' in str(exc_info.value)
        assert exc_info.value.provider_name == 'yahoo_finance'
        assert exc_info.value.ticker == 'AAPL'


# ============================================================================
# Tests - Price History Fetching
# ============================================================================


@pytest.mark.asyncio
async def test_fetch_price_history_success(provider, mock_price_history_dataframe):
    """Test successful price history fetch."""
    with patch.object(provider, '_get_ticker_history', return_value=mock_price_history_dataframe):
        history = await provider.fetch_price_history(
            'AAPL',
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5)
        )

        assert history is not None
        assert isinstance(history, PriceHistoryDTO)
        assert history.ticker == 'AAPL'
        assert history.start_date == date(2024, 1, 1)
        assert history.end_date == date(2024, 1, 5)
        assert len(history.data_points) == 5

        # Check first data point
        first_point = history.data_points[0]
        assert isinstance(first_point, PriceDataPointDTO)
        assert first_point.ticker == 'AAPL'
        assert first_point.date == date(2024, 1, 1)
        assert first_point.open == 180.0
        assert first_point.high == 182.0
        assert first_point.low == 179.0
        assert first_point.close == 181.0
        assert first_point.volume == 50000000
        assert first_point.adjusted_close == 181.0


@pytest.mark.asyncio
async def test_fetch_price_history_no_date_range(provider, mock_price_history_dataframe):
    """Test price history fetch without date range (max history)."""
    with patch.object(provider, '_get_ticker_history', return_value=mock_price_history_dataframe):
        history = await provider.fetch_price_history('AAPL')

        assert history is not None
        assert len(history.data_points) == 5


@pytest.mark.asyncio
async def test_fetch_price_history_empty_data(provider):
    """Test price history fetch with empty DataFrame."""
    with patch.object(provider, '_get_ticker_history', return_value=None):
        history = await provider.fetch_price_history('AAPL')

        assert history is None


@pytest.mark.asyncio
async def test_fetch_price_history_yfinance_error(provider):
    """Test price history fetch handles yfinance errors."""
    with patch.object(provider, '_get_ticker_history', side_effect=Exception('yfinance error')):
        with pytest.raises(ProviderError) as exc_info:
            await provider.fetch_price_history('AAPL')

        assert 'Failed to fetch price history' in str(exc_info.value)
        assert exc_info.value.provider_name == 'yahoo_finance'
        assert exc_info.value.ticker == 'AAPL'


# ============================================================================
# Tests - Batch Operations
# ============================================================================


@pytest.mark.asyncio
async def test_fetch_batch_company_profiles_success(provider, mock_ticker_info):
    """Test batch company profile fetch."""
    tickers = ['AAPL', 'GOOGL', 'MSFT']

    with patch.object(provider, '_get_ticker_info', return_value=mock_ticker_info):
        results = await provider.fetch_batch_company_profiles(tickers)

        assert len(results) == 3
        assert all(ticker in results for ticker in tickers)
        assert all(isinstance(results[ticker], CompanyProfileDTO) for ticker in tickers)


@pytest.mark.asyncio
async def test_fetch_batch_company_profiles_partial_failure(provider, mock_ticker_info):
    """Test batch company profile fetch with partial failures."""
    tickers = ['AAPL', 'INVALID', 'MSFT']

    def mock_get_info(ticker):
        if ticker == 'INVALID':
            raise Exception('yfinance error')
        return mock_ticker_info

    with patch.object(provider, '_get_ticker_info', side_effect=mock_get_info):
        results = await provider.fetch_batch_company_profiles(tickers)

        assert len(results) == 3
        assert results['AAPL'] is not None
        assert results['INVALID'] is None  # Failed ticker
        assert results['MSFT'] is not None


@pytest.mark.asyncio
async def test_fetch_batch_financial_statements_success(provider, mock_financials_dataframes):
    """Test batch financial statements fetch."""
    tickers = ['AAPL', 'GOOGL']

    with patch.object(provider, '_get_ticker_financials', return_value=mock_financials_dataframes):
        results = await provider.fetch_batch_financial_statements(tickers)

        assert len(results) == 2
        assert all(ticker in results for ticker in tickers)
        assert all(isinstance(results[ticker], list) for ticker in tickers)
        assert all(len(results[ticker]) == 2 for ticker in tickers)


@pytest.mark.asyncio
async def test_fetch_batch_price_history_success(provider, mock_price_history_dataframe):
    """Test batch price history fetch."""
    tickers = ['AAPL', 'GOOGL']

    with patch.object(provider, '_get_ticker_history', return_value=mock_price_history_dataframe):
        results = await provider.fetch_batch_price_history(tickers)

        assert len(results) == 2
        assert all(ticker in results for ticker in tickers)
        assert all(isinstance(results[ticker], PriceHistoryDTO) for ticker in tickers)


# ============================================================================
# Tests - Company List (Not Implemented)
# ============================================================================


@pytest.mark.asyncio
async def test_fetch_company_list_not_implemented(provider):
    """Test that fetch_company_list raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as exc_info:
        await provider.fetch_company_list()

    assert 'yfinance does not provide company list API' in str(exc_info.value)


# ============================================================================
# Tests - Helper Methods
# ============================================================================


def test_normalize_company_profile(provider):
    """Test company profile normalization."""
    info = {
        'longName': 'Apple Inc.',
        'shortName': 'Apple',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'country': 'US',
        'currency': 'USD',
        'marketCap': 3000000000000,
        'exchange': 'NASDAQ',
    }

    profile = provider._normalize_company_profile('AAPL', info)

    assert profile is not None
    assert profile.ticker == 'AAPL'
    assert profile.name == 'Apple Inc.'
    assert profile.sector == 'Technology'


def test_normalize_company_profile_missing_name(provider):
    """Test company profile normalization with missing name."""
    info = {'symbol': 'TEST'}

    profile = provider._normalize_company_profile('TEST', info)

    assert profile is None


def test_get_financial_field(provider, mock_financials_dataframes):
    """Test financial field extraction."""
    income_df = mock_financials_dataframes['income']
    fiscal_date = pd.Timestamp('2023-12-31')

    revenue = provider._get_financial_field(income_df, fiscal_date, 'Total Revenue')

    assert revenue == 400000000000


def test_get_financial_field_missing(provider, mock_financials_dataframes):
    """Test financial field extraction with missing field."""
    income_df = mock_financials_dataframes['income']
    fiscal_date = pd.Timestamp('2023-12-31')

    result = provider._get_financial_field(income_df, fiscal_date, 'Nonexistent Field')

    assert result is None


def test_get_financial_field_none_dataframe(provider):
    """Test financial field extraction with None DataFrame."""
    fiscal_date = pd.Timestamp('2023-12-31')

    result = provider._get_financial_field(None, fiscal_date, 'Total Revenue')

    assert result is None


def test_normalize_price_history(provider, mock_price_history_dataframe):
    """Test price history normalization."""
    history = provider._normalize_price_history(
        'AAPL',
        mock_price_history_dataframe,
        date(2024, 1, 1),
        date(2024, 1, 5)
    )

    assert history is not None
    assert history.ticker == 'AAPL'
    assert len(history.data_points) == 5
    assert history.start_date == date(2024, 1, 1)
    assert history.end_date == date(2024, 1, 5)


def test_normalize_price_history_empty(provider):
    """Test price history normalization with empty DataFrame."""
    history = provider._normalize_price_history(
        'AAPL',
        pd.DataFrame(),
        date(2024, 1, 1),
        date(2024, 1, 5)
    )

    assert history is None


# ============================================================================
# Tests - Raw Snapshot Logging
# ============================================================================


def test_log_raw_snapshot_without_db_session(provider):
    """Test raw snapshot logging without database session."""
    payload = {'test': 'data'}

    snapshot = provider._log_raw_snapshot(
        entity_type='test_entity',
        entity_key='TEST',
        payload=payload
    )

    assert snapshot is not None
    assert snapshot.provider_name == 'yahoo_finance'
    assert snapshot.provider_entity_type == 'test_entity'
    assert snapshot.provider_entity_key == 'TEST'
    assert snapshot.payload_json == payload


def test_log_raw_snapshot_with_db_session(provider):
    """Test raw snapshot logging with database session."""
    mock_db_session = MagicMock()
    provider.db_session = mock_db_session

    payload = {'test': 'data'}

    snapshot = provider._log_raw_snapshot(
        entity_type='test_entity',
        entity_key='TEST',
        payload=payload
    )

    assert snapshot is not None
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


# ============================================================================
# Tests - Initialization
# ============================================================================


def test_provider_initialization():
    """Test provider initialization with custom parameters."""
    provider = YahooYFinanceProvider(
        rate_limit_requests=100,
        rate_limit_window_seconds=60,
        retry_attempts=5,
        request_timeout=10,
    )

    assert provider.provider_name == 'yahoo_finance'
    assert provider.retry_attempts == 5
    assert provider.request_timeout == 10
    assert provider.rate_limiter.max_requests == 100
    assert provider.rate_limiter.time_window_seconds == 60


def test_provider_initialization_with_defaults():
    """Test provider initialization with default parameters."""
    with patch('app.providers.yahoo_yfinance.settings') as mock_settings:
        mock_settings.yahoo_finance_rate_limit = 2000
        mock_settings.yahoo_finance_timeout = 30

        provider = YahooYFinanceProvider()

        assert provider.provider_name == 'yahoo_finance'
        assert provider.retry_attempts == 3
        assert provider.request_timeout == 30
        assert provider.rate_limiter.max_requests == 2000
