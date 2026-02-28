"""Pytest fixtures for provider tests."""

import pytest
from unittest.mock import Mock, MagicMock


@pytest.fixture
def mock_yfinance_ticker():
    """Create a mock yfinance Ticker object with common attributes."""
    ticker = MagicMock()

    # Mock info property
    ticker.info = {
        'symbol': 'AAPL',
        'shortName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 3000000000000,
        'enterpriseValue': 3050000000000,
        'totalRevenue': 400000000000,
        'ebitda': 120000000000,
        'totalDebt': 120000000000,
        'totalCash': 50000000000,
        'freeCashflow': 100000000000,
        'currentPrice': 180.00,
        'bookValue': 4.50,
        'trailingPE': 28.5,
        'forwardPE': 25.0,
        'priceToBook': 40.0,
        'returnOnEquity': 1.50,
        'returnOnAssets': 0.25,
        'currentRatio': 1.05,
        'debtToEquity': 180.0,
    }

    return ticker


@pytest.fixture
def mock_yfinance_module():
    """Create a mock yfinance module."""
    mock_yf = MagicMock()
    return mock_yf


@pytest.fixture
def sample_stock_symbols():
    """Provide sample stock symbols for testing."""
    return ['AAPL', 'GOOGL', 'MSFT', 'BRK.B']


@pytest.fixture
def sample_financial_data():
    """Provide sample financial data structure."""
    return {
        'market_cap': 3000000000000,
        'enterprise_value': 3050000000000,
        'revenue': 400000000000,
        'ebitda': 120000000000,
        'total_debt': 120000000000,
        'cash': 50000000000,
        'free_cash_flow': 100000000000,
        'current_price': 180.00,
        'book_value_per_share': 4.50,
        'pe_ratio': 28.5,
        'forward_pe': 25.0,
        'price_to_book': 40.0,
        'roe': 1.50,
        'roa': 0.25,
        'current_ratio': 1.05,
        'debt_to_equity': 180.0,
    }
