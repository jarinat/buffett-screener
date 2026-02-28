"""
Company data models.

Defines canonical company and listing information models that all providers
must return. These models are independent of any specific data source.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Listing(BaseModel):
    """Stock exchange listing information."""

    ticker: str = Field(description="Stock ticker symbol (e.g., 'AAPL')")
    exchange: str = Field(
        description="Primary stock exchange where the security is listed (e.g., 'NASDAQ', 'NYSE')"
    )
    currency: str = Field(
        description="Currency in which the stock is traded (ISO 4217 code, e.g., 'USD')"
    )


class CompanyInfo(BaseModel):
    """Canonical company information model."""

    company_id: str = Field(
        description="Unique identifier for the company (provider-agnostic)"
    )
    name: str = Field(description="Official company name")
    ticker: str = Field(description="Primary stock ticker symbol")
    exchange: str = Field(description="Primary stock exchange")
    sector: Optional[str] = Field(
        default=None, description="Business sector (e.g., 'Technology', 'Healthcare')"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Specific industry classification (e.g., 'Software', 'Pharmaceuticals')",
    )
    country: Optional[str] = Field(
        default=None,
        description="Country of incorporation or headquarters (ISO 3166-1 alpha-2 code)",
    )
    currency: str = Field(
        description="Primary trading currency (ISO 4217 code, e.g., 'USD')"
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "company_id": "AAPL",
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "exchange": "NASDAQ",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "country": "US",
                "currency": "USD",
            }
        }
