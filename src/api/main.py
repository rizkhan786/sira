"""FastAPI application for SIRA."""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.core.logging import get_logger
from src.api.schemas import (
    QueryRequest, QueryResponse, SessionResponse,
    SessionHistoryResponse, HealthResponse
)
from src.reasoning.engine import create_reasoning_engine
from src.db.repository import get_repository
from src.llm.client import get_llm_client

logger = get_logger(__name__)

# Global instances
reasoning_engine = None
repository = None

# Create FastAPI app
app = FastAPI(
    title="SIRA API",
    description="Self-Improving Reasoning Agent",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global reasoning_engine, repository
    logger.info("Starting SIRA API", env=settings.env, port=settings.api_port)
    reasoning_engine = await create_reasoning_engine()
    repository = await get_repository()
    await repository.connect()
    logger.info("SIRA API startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down SIRA API")
    if repository:
        await repository.disconnect()
    logger.info("SIRA API shutdown complete")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with service dependencies."""
    llm_client = get_llm_client()
    llm_healthy = await llm_client.health_check()
    db_healthy = repository is not None and repository.pool is not None
    overall_status = "healthy" if (llm_healthy and db_healthy) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        service="sira-api",
        version="0.1.0",
        llm_status="healthy" if llm_healthy else "unhealthy",
        database_status="healthy" if db_healthy else "unhealthy"
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "SIRA API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "POST /query",
            "POST /session",
            "GET /session/{session_id}",
            "GET /session/{session_id}/history"
        ]
    }


@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process a user query through the reasoning engine."""
    try:
        if request.session_id:
            session = await repository.get_session(request.session_id)
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Session {request.session_id} not found"
                )
            session_id = request.session_id
            await repository.update_session_activity(session_id)
        else:
            session_id = await repository.create_session()
        
        result = await reasoning_engine.process_query(
            query=request.query,
            session_id=session_id,
            context=request.context
        )
        
        await repository.save_query(
            session_id=session_id,
            query_text=request.query,
            response_text=result["response"],
            reasoning_steps=result["reasoning_steps"],
            processing_time=result["metadata"]["processing_time_seconds"],
            token_usage=result["metadata"]["llm_usage"],
            quality_score=result["metadata"].get("quality_score"),
            quality_breakdown=result["metadata"].get("quality_breakdown")
        )
        
        return QueryResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("query_processing_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(user_id: str = None):
    """Create a new session."""
    try:
        session_id = await repository.create_session(user_id=user_id)
        session = await repository.get_session(session_id)
        return SessionResponse(**session, query_count=0)
    except Exception as e:
        logger.error("session_creation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get session information."""
    try:
        session = await repository.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        queries = await repository.get_session_queries(session_id, limit=1000)
        return SessionResponse(**session, query_count=len(queries))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_session_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@app.get("/session/{session_id}/history", response_model=SessionHistoryResponse)
async def get_session_history(session_id: str, limit: int = 10):
    """Get query history for a session."""
    try:
        session = await repository.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        queries = await repository.get_session_queries(session_id, limit=limit)
        return SessionHistoryResponse(session_id=session_id, queries=queries)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_history_error", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )
