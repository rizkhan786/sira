"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator
import os

# Set test environment
os.environ["ENV"] = "dev"
os.environ["LOG_LEVEL"] = "INFO"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_session_id() -> str:
    """Provide a test session ID."""
    return "test-session-12345"


@pytest.fixture
async def sample_query() -> str:
    """Provide a sample query for testing."""
    return "What is 2+2?"


@pytest.fixture
async def sample_context() -> dict:
    """Provide sample context for testing."""
    return {
        "history": "Previous conversation context"
    }
