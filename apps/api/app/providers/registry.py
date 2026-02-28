"""
Provider registry for managing and selecting data providers at runtime.

The registry enables the application to dynamically select between different
data provider implementations without code changes. This supports the core
architectural goal of provider independence.
"""

from functools import lru_cache
from typing import Dict, List, Literal, Optional, Type, Union

from app.providers.base import (
    CompanyUniverseProvider,
    FundamentalsProvider,
    PriceHistoryProvider,
)


# Type alias for supported provider types
ProviderType = Literal["company", "fundamentals", "price"]

# Type alias for all provider base classes
ProviderClass = Union[
    Type[CompanyUniverseProvider],
    Type[FundamentalsProvider],
    Type[PriceHistoryProvider],
]


class ProviderRegistry:
    """
    Registry for managing data provider implementations.

    The registry maintains a mapping of provider types and names to their
    implementations. This allows the application to:
    1. Register multiple providers for each type (e.g., Yahoo, Alpha Vantage)
    2. Select providers at runtime based on configuration
    3. List available providers for each type

    The registry is implemented as a singleton to ensure consistent provider
    state across the application.

    Example usage:
        # Get the registry instance
        registry = get_provider_registry()

        # Register providers
        registry.register_provider("company", "yahoo", YahooCompanyProvider)
        registry.register_provider("fundamentals", "yahoo", YahooFundamentalsProvider)
        registry.register_provider("price", "yahoo", YahooPriceProvider)

        # Retrieve a provider instance
        company_provider = registry.get_provider("company", "yahoo")
        companies = company_provider.get_company_universe()

        # List available providers
        available = registry.list_providers("company")
        # Returns: ["yahoo"]
    """

    def __init__(self) -> None:
        """Initialize the provider registry with an empty provider map."""
        self._providers: Dict[tuple[ProviderType, str], ProviderClass] = {}

    def register_provider(
        self,
        provider_type: ProviderType,
        name: str,
        provider_class: ProviderClass,
    ) -> None:
        """
        Register a provider implementation.

        Adds a provider class to the registry under the specified type and name.
        If a provider with the same type and name already exists, it will be
        replaced with the new implementation.

        Args:
            provider_type: Type of provider ("company", "fundamentals", or "price")
            name: Unique name for this provider implementation (e.g., "yahoo", "alpha_vantage")
            provider_class: The provider class to register (must inherit from the
                appropriate base class for the provider_type)

        Raises:
            TypeError: If provider_class does not inherit from the correct base class
                for the specified provider_type

        Example:
            registry.register_provider("company", "yahoo", YahooCompanyProvider)
        """
        # Validate that provider_class matches the provider_type
        expected_base_class = self._get_base_class_for_type(provider_type)
        if not issubclass(provider_class, expected_base_class):
            raise TypeError(
                f"Provider class {provider_class.__name__} must inherit from "
                f"{expected_base_class.__name__} for provider_type '{provider_type}'"
            )

        key = (provider_type, name)
        self._providers[key] = provider_class

    def get_provider(
        self,
        provider_type: ProviderType,
        name: str,
    ) -> Union[CompanyUniverseProvider, FundamentalsProvider, PriceHistoryProvider]:
        """
        Get a provider instance by type and name.

        Retrieves the registered provider class for the specified type and name,
        then instantiates and returns it. Each call creates a new instance.

        Args:
            provider_type: Type of provider ("company", "fundamentals", or "price")
            name: Name of the provider implementation (e.g., "yahoo")

        Returns:
            An instance of the requested provider. The specific type depends on
            provider_type:
            - "company" -> CompanyUniverseProvider instance
            - "fundamentals" -> FundamentalsProvider instance
            - "price" -> PriceHistoryProvider instance

        Raises:
            KeyError: If no provider is registered with the specified type and name

        Example:
            company_provider = registry.get_provider("company", "yahoo")
            companies = company_provider.get_company_universe()
        """
        key = (provider_type, name)
        if key not in self._providers:
            available = self.list_providers(provider_type)
            available_str = ", ".join(f"'{p}'" for p in available) if available else "none"
            raise KeyError(
                f"No provider registered for type '{provider_type}' with name '{name}'. "
                f"Available providers: {available_str}"
            )

        provider_class = self._providers[key]
        return provider_class()

    def list_providers(self, provider_type: ProviderType) -> List[str]:
        """
        List all registered provider names for a given type.

        Returns the names of all providers registered for the specified provider
        type, sorted alphabetically.

        Args:
            provider_type: Type of provider ("company", "fundamentals", or "price")

        Returns:
            Sorted list of provider names registered for this type. Returns an
            empty list if no providers are registered for the type.

        Example:
            # After registering yahoo and alpha_vantage providers
            names = registry.list_providers("company")
            # Returns: ["alpha_vantage", "yahoo"]
        """
        provider_names = [
            name for (p_type, name) in self._providers.keys() if p_type == provider_type
        ]
        return sorted(provider_names)

    def _get_base_class_for_type(
        self, provider_type: ProviderType
    ) -> Union[
        Type[CompanyUniverseProvider],
        Type[FundamentalsProvider],
        Type[PriceHistoryProvider],
    ]:
        """
        Get the expected base class for a given provider type.

        Internal helper method to map provider type strings to their corresponding
        abstract base classes.

        Args:
            provider_type: Type of provider ("company", "fundamentals", or "price")

        Returns:
            The abstract base class corresponding to the provider type

        Raises:
            ValueError: If provider_type is not recognized (should not happen with
                Literal type enforcement)
        """
        type_map = {
            "company": CompanyUniverseProvider,
            "fundamentals": FundamentalsProvider,
            "price": PriceHistoryProvider,
        }
        if provider_type not in type_map:
            raise ValueError(f"Unknown provider type: {provider_type}")
        return type_map[provider_type]


@lru_cache
def get_provider_registry() -> ProviderRegistry:
    """
    Get the singleton provider registry instance.

    Uses lru_cache to ensure the registry is instantiated only once and shared
    across the application. This is the recommended way to access the registry.

    Returns:
        The global ProviderRegistry instance

    Example:
        registry = get_provider_registry()
        registry.register_provider("company", "yahoo", YahooCompanyProvider)
    """
    return ProviderRegistry()
