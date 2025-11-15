"""API models for SIRA."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    query: str = Field(..., min_length=1, max_length=5000, description="User query")
    session_id: Optional[str] = Field(None, description="Existing session ID (creates new if omitted)")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ReasoningStep(BaseModel):
    """Model for a single reasoning step."""
    step_number: int
    description: str
    timestamp: str


class QueryMetadata(BaseModel):
    """Metadata about query processing."""
    session_id: str
    timestamp: str
    processing_time_seconds: float
    llm_usage: Dict[str, int]
    confidence_score: float
    quality_score: Optional[float] = Field(None, description="Quality score (0.0-1.0)")
    quality_level: Optional[str] = Field(None, description="Quality level (poor/acceptable/good/excellent)")
    quality_breakdown: Optional[Dict[str, Any]] = Field(None, description="Detailed quality breakdown")
    pattern_extracted: Optional[bool] = Field(None, description="Whether a pattern was extracted")
    pattern_id: Optional[str] = Field(None, description="ID of extracted pattern if any")
    pattern_stored: Optional[bool] = Field(None, description="Whether the pattern was stored in ChromaDB")


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    response: str = Field(..., description="Generated response")
    reasoning_steps: List[ReasoningStep] = Field(..., description="Reasoning steps taken")
    metadata: QueryMetadata = Field(..., description="Processing metadata")


class SessionResponse(BaseModel):
    """Response model for session endpoint."""
    id: str
    user_id: Optional[str]
    created_at: str
    last_activity: str
    query_count: int = 0


class QueryHistoryItem(BaseModel):
    """Single query in history."""
    id: str
    query_text: str
    response_text: str
    reasoning_steps: List[Dict[str, Any]]
    timestamp: str
    processing_time: float
    token_usage: Dict[str, int]


class SessionHistoryResponse(BaseModel):
    """Response model for session history."""
    session_id: str
    queries: List[QueryHistoryItem]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    service: str
    version: str
    llm_status: Optional[str] = None
    database_status: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    timestamp: str
