"""
Base provider class with rate limiting and retry logic.

All provider implementations should inherit from BaseProvider to gain:
- Automatic rate limiting to prevent API throttling
- Exponential backoff retry logic for transient failures
- Structured logging for debugging and monitoring
- Consistent error handling patterns
"""

import asyncio
import logging
import time
from collections import deque
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from app.domain.provider_contracts import ProviderError, RateLimitError

# Type variable for generic decorator return types
T = TypeVar("T")

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter for API requests.

    Implements a sliding window rate limiter that tracks request timestamps
    and enforces a maximum number of requests per time window.
    """

    def __init__(self, max_requests: int, time_window_seconds: int):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window.
            time_window_seconds: Time window in seconds (e.g., 3600 for 1 hour).
        """
        self.max_requests = max_requests
        self.time_window_seconds = time_window_seconds
        self.request_times: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        Blocks if rate limit would be exceeded, waiting until a slot becomes available.
        Removes expired timestamps from the sliding window.
        """
        async with self._lock:
            current_time = time.time()

            # Remove timestamps outside the time window
            while self.request_times and current_time - self.request_times[0] > self.time_window_seconds:
                self.request_times.popleft()

            # If at capacity, wait until oldest request expires
            if len(self.request_times) >= self.max_requests:
                sleep_time = self.time_window_seconds - (current_time - self.request_times[0]) + 0.1
                logger.debug(
                    f"Rate limit reached ({self.max_requests}/{self.time_window_seconds}s). "
                    f"Waiting {sleep_time:.2f}s"
                )
                await asyncio.sleep(sleep_time)

                # After waiting, remove expired timestamps again
                current_time = time.time()
                while self.request_times and current_time - self.request_times[0] > self.time_window_seconds:
                    self.request_times.popleft()

            # Record this request
            self.request_times.append(current_time)

    def get_remaining_requests(self) -> int:
        """
        Get the number of requests remaining in the current window.

        Returns:
            Number of requests that can be made without waiting.
        """
        current_time = time.time()
        # Remove expired timestamps
        while self.request_times and current_time - self.request_times[0] > self.time_window_seconds:
            self.request_times.popleft()

        return max(0, self.max_requests - len(self.request_times))


class BaseProvider:
    """
    Base class for all data provider adapters.

    Provides common functionality for rate limiting, retries, and error handling.
    Subclasses should implement specific provider methods while utilizing these utilities.
    """

    def __init__(
        self,
        provider_name: str,
        rate_limit_requests: int = 2000,
        rate_limit_window_seconds: int = 3600,
        retry_attempts: int = 3,
        retry_base_delay: float = 1.0,
        retry_max_delay: float = 60.0,
        request_timeout: int = 30,
    ):
        """
        Initialize the base provider.

        Args:
            provider_name: Name of the provider (e.g., 'yahoo_finance').
            rate_limit_requests: Maximum requests allowed in the time window.
            rate_limit_window_seconds: Time window for rate limiting in seconds.
            retry_attempts: Number of retry attempts for failed requests.
            retry_base_delay: Base delay in seconds for exponential backoff.
            retry_max_delay: Maximum delay in seconds between retries.
            request_timeout: Request timeout in seconds.
        """
        self.provider_name = provider_name
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window_seconds)
        self.retry_attempts = retry_attempts
        self.retry_base_delay = retry_base_delay
        self.retry_max_delay = retry_max_delay
        self.request_timeout = request_timeout

        self.logger = logging.getLogger(f"{__name__}.{provider_name}")
        self.logger.info(
            f"Initialized {provider_name} provider "
            f"(rate_limit={rate_limit_requests}/{rate_limit_window_seconds}s, "
            f"retry_attempts={retry_attempts}, timeout={request_timeout}s)"
        )

    def with_rate_limit(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to apply rate limiting to a function.

        Args:
            func: The async function to wrap with rate limiting.

        Returns:
            Wrapped function that enforces rate limits before execution.
        """
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            await self.rate_limiter.acquire()
            return await func(*args, **kwargs)

        return wrapper

    async def with_retry(
        self,
        func: Callable[..., T],
        *args: Any,
        ticker: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """
        Execute a function with exponential backoff retry logic.

        Retries on transient errors. Does NOT retry on rate limit errors
        (those should be handled by rate limiting) or on permanent errors
        (invalid ticker, insufficient data).

        Args:
            func: The async function to execute with retries.
            *args: Positional arguments to pass to the function.
            ticker: Optional ticker symbol for error context.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The result of the function call.

        Raises:
            ProviderError: If all retry attempts fail.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(1, self.retry_attempts + 1):
            try:
                return await func(*args, **kwargs)

            except RateLimitError:
                # Don't retry rate limit errors - they should be prevented by rate limiter
                raise

            except ProviderError as e:
                # Don't retry if it's a permanent error (invalid ticker, no data)
                if "invalid" in str(e).lower() or "not found" in str(e).lower():
                    raise
                last_exception = e
                self.logger.warning(
                    f"Provider error on attempt {attempt}/{self.retry_attempts} "
                    f"for {ticker or 'unknown'}: {e}"
                )

            except Exception as e:
                # Retry on unexpected errors (network issues, timeouts, etc.)
                last_exception = e
                self.logger.warning(
                    f"Unexpected error on attempt {attempt}/{self.retry_attempts} "
                    f"for {ticker or 'unknown'}: {type(e).__name__}: {e}"
                )

            # Don't sleep after the last attempt
            if attempt < self.retry_attempts:
                # Exponential backoff: base_delay * 2^(attempt-1)
                delay = min(
                    self.retry_base_delay * (2 ** (attempt - 1)),
                    self.retry_max_delay
                )
                self.logger.debug(f"Retrying in {delay:.2f}s...")
                await asyncio.sleep(delay)

        # All retries exhausted
        error_msg = f"Failed after {self.retry_attempts} attempts"
        if ticker:
            error_msg += f" for ticker {ticker}"

        raise ProviderError(
            message=error_msg,
            provider_name=self.provider_name,
            ticker=ticker,
            original_exception=last_exception,
        )

    async def execute_with_retry_and_rate_limit(
        self,
        func: Callable[..., T],
        *args: Any,
        ticker: Optional[str] = None,
        **kwargs: Any,
    ) -> T:
        """
        Execute a function with both rate limiting and retry logic.

        This is a convenience method that combines rate limiting and retries.
        Use this for provider API calls that need both protections.

        Args:
            func: The async function to execute.
            *args: Positional arguments to pass to the function.
            ticker: Optional ticker symbol for error context.
            **kwargs: Keyword arguments to pass to the function.

        Returns:
            The result of the function call.

        Raises:
            ProviderError: If the operation fails after all retries.
        """
        # Apply rate limiting wrapper
        rate_limited_func = self.with_rate_limit(func)

        # Execute with retry logic
        return await self.with_retry(rate_limited_func, *args, ticker=ticker, **kwargs)

    def log_fetch_start(self, operation: str, ticker: Optional[str] = None, **context: Any) -> None:
        """
        Log the start of a fetch operation.

        Args:
            operation: Description of the operation (e.g., 'fetch_company_profile').
            ticker: Optional ticker symbol.
            **context: Additional context to log.
        """
        msg_parts = [f"Starting {operation}"]
        if ticker:
            msg_parts.append(f"for ticker={ticker}")
        if context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in context.items())
            msg_parts.append(f"({ctx_str})")

        self.logger.info(" ".join(msg_parts))

    def log_fetch_success(
        self,
        operation: str,
        ticker: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        **context: Any,
    ) -> None:
        """
        Log successful completion of a fetch operation.

        Args:
            operation: Description of the operation.
            ticker: Optional ticker symbol.
            duration_seconds: Time taken for the operation.
            **context: Additional context to log (e.g., records_fetched=10).
        """
        msg_parts = [f"Completed {operation}"]
        if ticker:
            msg_parts.append(f"for ticker={ticker}")
        if duration_seconds is not None:
            msg_parts.append(f"in {duration_seconds:.2f}s")
        if context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in context.items())
            msg_parts.append(f"({ctx_str})")

        self.logger.info(" ".join(msg_parts))

    def log_fetch_error(
        self,
        operation: str,
        error: Exception,
        ticker: Optional[str] = None,
        **context: Any,
    ) -> None:
        """
        Log a failed fetch operation.

        Args:
            operation: Description of the operation.
            error: The exception that occurred.
            ticker: Optional ticker symbol.
            **context: Additional context to log.
        """
        msg_parts = [f"Failed {operation}"]
        if ticker:
            msg_parts.append(f"for ticker={ticker}")
        msg_parts.append(f"- {type(error).__name__}: {error}")
        if context:
            ctx_str = ", ".join(f"{k}={v}" for k, v in context.items())
            msg_parts.append(f"({ctx_str})")

        self.logger.error(" ".join(msg_parts))
