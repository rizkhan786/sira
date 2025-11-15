# Reliability & Error Handling

This document outlines SIRA's reliability patterns, error handling strategies, and fault tolerance mechanisms.

## Exception Hierarchy

### Custom Exceptions

All SIRA exceptions inherit from `SIRAException`:

```python
from src.core.exceptions import (
    SIRAException,           # Base exception
    LLMServiceError,         # LLM service failures
    DatabaseError,           # Database operation failures
    PatternStorageError,     # Pattern storage failures
    PatternRetrievalError,   # Pattern retrieval failures
    QualityScoreError,       # Quality scoring failures
    PatternExtractionError,  # Pattern extraction failures
    ConfigurationError,      # Configuration issues
    ValidationError          # Input validation failures
)
```

### Exception Details

All custom exceptions support detailed error information:

```python
raise LLMServiceError(
    message="Failed to generate response",
    details={
        "model": "llama3:8b",
        "timeout": 120,
        "attempt": 3
    }
)
```

## Retry Logic

### Async Retry Decorator

Automatically retry async functions with exponential backoff:

```python
from src.core.reliability import retry_async
import httpx

@retry_async(
    max_attempts=3,
    delay=1.0,
    backoff=2.0,
    exceptions=(httpx.HTTPError, httpx.TimeoutException)
)
async def call_external_api():
    async with httpx.AsyncClient() as client:
        return await client.get("https://api.example.com/data")
```

**Configuration**:
- `max_attempts`: Number of retries (default: 3)
- `delay`: Initial delay between retries in seconds (default: 1.0)
- `backoff`: Multiplier for delay after each retry (default: 2.0)
- `exceptions`: Tuple of exceptions to catch and retry
- `on_retry`: Optional callback function for retry events

**Retry Schedule**:
- Attempt 1: Immediate
- Attempt 2: After 1.0s
- Attempt 3: After 2.0s
- Attempt 4: After 4.0s
- ...

### Sync Retry Decorator

For synchronous functions:

```python
from src.core.reliability import retry_sync

@retry_sync(max_attempts=3, delay=1.0)
def read_config_file(path: str):
    with open(path, 'r') as f:
        return f.read()
```

## Circuit Breaker

### Purpose

Prevent cascading failures by failing fast when a service is unhealthy.

### States

1. **CLOSED**: Normal operation, requests pass through
2. **OPEN**: Too many failures, requests fail immediately
3. **HALF_OPEN**: Testing if service recovered

### Usage

```python
from src.core.reliability import CircuitBreaker

# Create circuit breaker
llm_breaker = CircuitBreaker(
    failure_threshold=5,      # Open after 5 failures
    timeout=60.0,             # Wait 60s before HALF_OPEN
    half_open_max_calls=1     # Allow 1 test call in HALF_OPEN
)

async def call_llm_service():
    # Check if requests are allowed
    if not llm_breaker.allow_request():
        raise LLMServiceError("Circuit breaker is OPEN")
    
    try:
        result = await llm_client.generate(prompt)
        llm_breaker.record_success()
        return result
    except Exception as e:
        llm_breaker.record_failure()
        raise
```

### State Transitions

```
CLOSED --[failures >= threshold]--> OPEN
OPEN --[timeout expired]--> HALF_OPEN
HALF_OPEN --[success]--> CLOSED
HALF_OPEN --[failure]--> OPEN
```

## Timeouts

### Async Timeout Wrapper

Prevent operations from hanging indefinitely:

```python
from src.core.reliability import with_timeout

async def fetch_data():
    return await with_timeout(
        slow_operation(),
        timeout_seconds=30.0,
        operation_name="slow_operation"
    )
```

### LLM Client Timeout

The LLM client has built-in timeout (120 seconds):

```python
# Configured in src/llm/client.py
self.timeout = 120.0
```

## Global Error Handlers

### API Error Handlers

The FastAPI app includes global exception handlers:

```python
# Custom SIRA exceptions
@app.exception_handler(SIRAException)
async def sira_exception_handler(request, exc):
    # Returns 500 with error details

# All other exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # Returns 500 with generic error message
```

### Error Response Format

```json
{
    "error": "Error message",
    "details": {},
    "timestamp": "2025-11-15T12:00:00Z"
}
```

## Logging

All errors are logged with structured context:

```python
logger.error(
    "operation_failed",
    extra={
        "error": str(e),
        "error_type": type(e).__name__,
        "function": "process_query",
        "session_id": session_id
    }
)
```

## Safe Operations

### Safe Division

Prevent division by zero errors:

```python
from src.core.reliability import safe_divide

# Returns 0.0 if denominator is 0
score = safe_divide(correct_count, total_count, default=0.0)
```

## Best Practices

### 1. Use Specific Exceptions

```python
# Good
raise LLMServiceError("Model not found", details={"model": "llama3"})

# Bad
raise Exception("Error occurred")
```

### 2. Add Retry for Transient Failures

```python
# Network calls, external APIs
@retry_async(max_attempts=3, exceptions=(httpx.HTTPError,))
async def fetch_remote_data():
    pass

# File I/O
@retry_sync(max_attempts=2, exceptions=(OSError,))
def read_config():
    pass
```

### 3. Use Circuit Breakers for External Services

```python
# LLM service, vector DB, external APIs
llm_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)
```

### 4. Set Appropriate Timeouts

```python
# Short operations
await with_timeout(quick_op(), timeout_seconds=5.0)

# Long operations
await with_timeout(llm_generate(), timeout_seconds=120.0)
```

### 5. Log Contextual Information

```python
logger.error(
    "pattern_extraction_failed",
    extra={
        "query_id": query_id,
        "quality_score": quality_score,
        "error": str(e)
    }
)
```

## Error Recovery Strategies

### Graceful Degradation

```python
try:
    patterns = retriever.retrieve_patterns(query)
except PatternRetrievalError as e:
    logger.warning("pattern_retrieval_failed", error=str(e))
    patterns = []  # Continue without patterns
```

### Fallback Values

```python
try:
    config = load_config()
except ConfigurationError:
    config = get_default_config()
```

### Partial Success

```python
results = []
for item in items:
    try:
        result = process_item(item)
        results.append(result)
    except ProcessingError as e:
        logger.warning("item_processing_failed", item=item, error=str(e))
        # Continue with next item
```

## Health Checks

### API Health Endpoint

```bash
GET /health
```

Response:
```json
{
    "status": "healthy",
    "service": "sira-api",
    "version": "0.1.0",
    "llm_status": "healthy",
    "database_status": "healthy"
}
```

### Component Health Checks

```python
# LLM service
llm_healthy = await llm_client.health_check()

# Pattern storage
storage_healthy = pattern_storage.health_check()

# Database
db_healthy = repository.pool is not None
```

## Monitoring & Observability

### Structured Logging

All operations log structured JSON:

```json
{
    "event": "pattern_extraction_failed",
    "level": "error",
    "timestamp": "2025-11-15T12:00:00Z",
    "query_id": "abc123",
    "error": "Invalid JSON response"
}
```

### Key Metrics to Monitor

1. **Error Rates**: Count of exceptions by type
2. **Retry Attempts**: How often retries are triggered
3. **Circuit Breaker State**: Time spent in each state
4. **Timeout Occurrences**: Operations that time out
5. **Response Times**: P50, P95, P99 latencies

## Sprint 2 Deliverable

**DEL-023: Reliability & Error Handling** ✅

### Components Delivered

1. **Custom Exception Hierarchy**
   - Base `SIRAException` class
   - 8 specific exception types
   - Support for error details

2. **Retry Logic**
   - Async retry decorator
   - Sync retry decorator
   - Exponential backoff
   - Configurable attempts and delays

3. **Circuit Breaker**
   - State machine (CLOSED/OPEN/HALF_OPEN)
   - Configurable failure threshold
   - Automatic recovery testing

4. **Timeout Handling**
   - Async timeout wrapper
   - Operation-level timeouts
   - Timeout logging

5. **Global Error Handlers**
   - API-level exception handling
   - Structured error responses
   - Detailed error logging

6. **Safe Operations**
   - Safe division utility
   - Graceful degradation patterns
   - Fallback mechanisms

### Files Created

- `src/core/exceptions.py` (58 lines)
- `src/core/reliability.py` (297 lines)
- `docs/60-Development/reliability.md` (this file)

### API Improvements

- Global exception handlers
- Structured error responses
- Improved logging context

All reliability patterns are ready for use across the codebase.
