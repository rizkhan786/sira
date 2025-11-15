"""Integration tests for SIRA API."""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "SIRA API"
    assert data["version"] == "0.1.0"
    assert "endpoints" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["service"] == "sira-api"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_create_session():
    """Test session creation."""
    response = client.post("/session")
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["query_count"] == 0


@pytest.mark.asyncio
async def test_process_query_new_session():
    """Test query processing with automatic session creation."""
    response = client.post("/query", json={
        "query": "What is 2+2?"
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "reasoning_steps" in data
    assert "metadata" in data
    assert len(data["reasoning_steps"]) > 0


@pytest.mark.asyncio
async def test_process_query_existing_session():
    """Test query processing with existing session."""
    # Create session first
    session_response = client.post("/session")
    session_id = session_response.json()["id"]
    
    # Process query
    response = client.post("/query", json={
        "query": "What is the capital of France?",
        "session_id": session_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["session_id"] == session_id


@pytest.mark.asyncio
async def test_get_session():
    """Test retrieving session information."""
    # Create session
    session_response = client.post("/session")
    session_id = session_response.json()["id"]
    
    # Get session
    response = client.get(f"/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id


@pytest.mark.asyncio
async def test_get_session_history():
    """Test retrieving session history."""
    # Create session and process query
    session_response = client.post("/session")
    session_id = session_response.json()["id"]
    
    client.post("/query", json={
        "query": "Test query",
        "session_id": session_id
    })
    
    # Get history
    response = client.get(f"/session/{session_id}/history")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert len(data["queries"]) > 0


@pytest.mark.asyncio
async def test_query_with_context():
    """Test query processing with context."""
    response = client.post("/query", json={
        "query": "Continue the conversation",
        "context": {"history": "We were discussing AI"}
    })
    assert response.status_code == 200
    data = response.json()
    assert "response" in data


def test_invalid_session_id():
    """Test handling of invalid session ID."""
    response = client.post("/query", json={
        "query": "Test",
        "session_id": "invalid-uuid"
    })
    assert response.status_code == 404


def test_query_validation():
    """Test query validation."""
    # Empty query
    response = client.post("/query", json={
        "query": ""
    })
    assert response.status_code == 422  # Validation error
    
    # Too long query
    long_query = "x" * 10000
    response = client.post("/query", json={
        "query": long_query
    })
    assert response.status_code == 422


def test_openapi_docs():
    """Test that OpenAPI documentation is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/redoc")
    assert response.status_code == 200
