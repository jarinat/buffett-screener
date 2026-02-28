"""
Abstract base classes for data providers.

Defines the contracts that all data provider implementations must follow.
This ensures the screening engine can work with any data source without
modification.
"""

from abc import ABC, abstractmethod
from typing import List

from app.models.company import CompanyInfo


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
