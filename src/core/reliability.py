"""Reliability utilities for SIRA - retry logic, circuit breakers, timeouts."""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Optional, Type, Tuple

logger = logging.getLogger(__name__)


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """Decorator to retry async functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
        
    Example:
        @retry_async(max_attempts=3, delay=1.0, exceptions=(httpx.HTTPError,))
        async def fetch_data():
            return await client.get("/api/data")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            "retry_exhausted",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "error": str(e),
                            },
                        )
                        raise

                    logger.warning(
                        "retry_attempt",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "delay": current_delay,
                            "error": str(e),
                        },
                    )

                    if on_retry:
                        on_retry(attempt, e)

                    await asyncio.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_sync(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """Decorator to retry synchronous functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback function called on each retry
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            "retry_exhausted",
                            extra={
                                "function": func.__name__,
                                "attempts": attempt,
                                "error": str(e),
                            },
                        )
                        raise

                    logger.warning(
                        "retry_attempt",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "max_attempts": max_attempts,
                            "delay": current_delay,
                            "error": str(e),
                        },
                    )

                    if on_retry:
                        on_retry(attempt, e)

                    time.sleep(current_delay)
                    current_delay *= backoff

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker pattern implementation for fault tolerance.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failures exceeded threshold, requests fail immediately
    - HALF_OPEN: Testing if service recovered, limited requests allowed
    
    Example:
        breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
        
        async def call_external_service():
            if not breaker.allow_request():
                raise Exception("Circuit breaker is OPEN")
            
            try:
                result = await service.call()
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        half_open_max_calls: int = 1,
    ):
        """Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (OPEN -> HALF_OPEN)
            half_open_max_calls: Max requests allowed in HALF_OPEN state
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.half_open_calls = 0

    def allow_request(self) -> bool:
        """Check if request should be allowed through.
        
        Returns:
            True if request can proceed, False otherwise
        """
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if self.last_failure_time and time.time() - self.last_failure_time >= self.timeout:
                logger.info("circuit_breaker_half_open")
                self.state = "HALF_OPEN"
                self.half_open_calls = 0
                return True
            return False

        if self.state == "HALF_OPEN":
            if self.half_open_calls < self.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False

        return False

    def record_success(self):
        """Record a successful request."""
        if self.state == "HALF_OPEN":
            logger.info("circuit_breaker_closed")
            self.state = "CLOSED"
            self.failure_count = 0
            self.half_open_calls = 0
        elif self.state == "CLOSED":
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record a failed request."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "HALF_OPEN":
            logger.warning("circuit_breaker_opened_from_half_open")
            self.state = "OPEN"
        elif self.state == "CLOSED" and self.failure_count >= self.failure_threshold:
            logger.warning(
                "circuit_breaker_opened",
                extra={"failure_count": self.failure_count},
            )
            self.state = "OPEN"

    def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        logger.info("circuit_breaker_reset")
        self.state = "CLOSED"
        self.failure_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None


async def with_timeout(coro, timeout_seconds: float, operation_name: str = "operation"):
    """Execute coroutine with timeout.
    
    Args:
        coro: Coroutine to execute
        timeout_seconds: Timeout in seconds
        operation_name: Name for logging
        
    Returns:
        Result of coroutine
        
    Raises:
        asyncio.TimeoutError: If operation times out
    """
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.error(
            "operation_timeout",
            extra={
                "operation": operation_name,
                "timeout_seconds": timeout_seconds,
            },
        )
        raise


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default on division by zero.
    
    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return if denominator is zero
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError):
        return default
