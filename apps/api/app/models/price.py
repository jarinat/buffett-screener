"""
Price data models.

Defines canonical price and price history models that all providers must return.
These models are independent of any specific data source and represent historical
and current price information for securities.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """Single day's price data for a security."""

    ticker: str = Field(description="Stock ticker symbol (e.g., 'AAPL')")
    date: date = Field(description="Trading date for this price data")
    open: Optional[Decimal] = Field(
        default=None,
        description="Opening price for the trading day",
    )
    high: Optional[Decimal] = Field(
        default=None,
        description="Highest price during the trading day",
    )
    low: Optional[Decimal] = Field(
        default=None,
        description="Lowest price during the trading day",
    )
    close: Optional[Decimal] = Field(
        default=None,
        description="Closing price for the trading day",
    )
    adjusted_close: Optional[Decimal] = Field(
        default=None,
        description="Closing price adjusted for splits and dividends",
    )
    volume: Optional[int] = Field(
        default=None,
        description="Trading volume (number of shares traded)",
    )
    currency: str = Field(
        description="Currency of price values (ISO 4217 code, e.g., 'USD')"
    )
    source_provider: str = Field(
        description="Data provider that supplied this price data (e.g., 'yahoo', 'alpha_vantage')"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "date": "2024-01-15",
                "open": "185.50",
                "high": "188.25",
                "low": "184.75",
                "close": "187.45",
                "adjusted_close": "187.45",
                "volume": 52847500,
                "currency": "USD",
                "source_provider": "yahoo",
            }
        }


class PriceHistory(BaseModel):
    """Historical price data for a security over a time period."""

    company_id: str = Field(
        description="Unique identifier for the company (matches CompanyInfo.company_id)"
    )
    ticker: str = Field(description="Stock ticker symbol (e.g., 'AAPL')")
    start_date: date = Field(description="Start date of the price history period")
    end_date: date = Field(description="End date of the price history period")
    currency: str = Field(
        description="Currency of price values (ISO 4217 code, e.g., 'USD')"
    )
    source_provider: str = Field(
        description="Data provider that supplied this price history (e.g., 'yahoo', 'alpha_vantage')"
    )
    data: list[PriceData] = Field(
        description="List of daily price data points, ordered chronologically"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "company_id": "AAPL",
                "ticker": "AAPL",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "currency": "USD",
                "source_provider": "yahoo",
                "data": [
                    {
                        "ticker": "AAPL",
                        "date": "2024-01-02",
                        "open": "185.00",
                        "high": "186.50",
                        "low": "184.25",
                        "close": "185.75",
                        "adjusted_close": "185.75",
                        "volume": 45678900,
                        "currency": "USD",
                        "source_provider": "yahoo",
                    },
                    {
                        "ticker": "AAPL",
                        "date": "2024-01-03",
                        "open": "186.00",
                        "high": "188.00",
                        "low": "185.50",
                        "close": "187.50",
                        "adjusted_close": "187.50",
                        "volume": 52847500,
                        "currency": "USD",
                        "source_provider": "yahoo",
                    },
                ],
            }
        }
