"""Price data models."""
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field
class PriceData(BaseModel):
    """Single price data point."""
    date: date = Field(..., description="Date of the price")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: float = Field(..., description="Closing price")
    adjusted_close: Optional[float] = Field(None, description="Adjusted closing price")
    volume: Optional[int] = Field(None, description="Trading volume")
class PriceHistory(BaseModel):
    """Historical price data for a security."""
    symbol: str = Field(..., description="Stock symbol")
    prices: List[PriceData] = Field(..., description="List of price data points")
    start_date: date = Field(..., description="Start date of the price history")
    end_date: date = Field(..., description="End date of the price history")
    fetched_at: datetime = Field(default_factory=datetime.now, description="Timestamp when data was fetched")
