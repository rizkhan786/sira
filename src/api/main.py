"""FastAPI application for SIRA."""
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from src.core.config import settings
from src.core.logging import get_logger
from src.core.exceptions import SIRAException
from src.api.schemas import (
    QueryRequest, QueryResponse, SessionResponse,
    SessionHistoryResponse, HealthResponse
)
from src.reasoning.engine import create_reasoning_engine
from src.db.repository import get_repository
from src.llm.client import get_llm_client
from src.metrics.collector import MetricsCollector
from src.metrics.storage import MetricsStorage
from src.api import metrics as metrics_api
from src.matlab.episode_logger import EpisodeLogger
from src.matlab.config_reader import ConfigReader

logger = get_logger(__name__)

# Global instances
reasoning_engine = None
repository = None
metrics_collector = None
metrics_storage = None
episode_logger = None
config_reader = None

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

# Include metrics router
app.include_router(metrics_api.router)


# Global exception handlers
@app.exception_handler(SIRAException)
async def sira_exception_handler(request: Request, exc: SIRAException):
    """Handle SIRA custom exceptions."""
    logger.error(
        "sira_exception",
        extra={
            "error": exc.message,
            "details": exc.details,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(
        "unexpected_exception",
        extra={
            "error": str(exc),
            "error_type": type(exc).__name__,
            "path": request.url.path
        }
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    global reasoning_engine, repository, metrics_collector, metrics_storage, episode_logger, config_reader
    logger.info("Starting SIRA API", env=settings.env, port=settings.api_port)
    reasoning_engine = await create_reasoning_engine()
    repository = await get_repository()
    await repository.connect()
    
    # Initialize metrics system
    metrics_storage = MetricsStorage(repository.pool)
    metrics_collector = MetricsCollector(storage=metrics_storage)
    metrics_api.set_metrics_storage(metrics_storage)
    
    # Initialize MATLAB integration
    episode_logger = EpisodeLogger(
        log_path="./data/matlab/episodes.mat",
        batch_size=10,
        export_interval_seconds=3600
    )
    config_reader = ConfigReader(
        config_path="./data/matlab/optimized_config.json",
        reload_interval=60
    )
    
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
        
        query_id = await repository.save_query(
            session_id=session_id,
            query_text=request.query,
            response_text=result["response"],
            reasoning_steps=result["reasoning_steps"],
            processing_time=result["metadata"]["processing_time_seconds"],
            token_usage=result["metadata"]["llm_usage"],
            quality_score=result["metadata"].get("quality_score"),
            quality_breakdown=result["metadata"].get("quality_breakdown")
        )
        
        # Record pattern usage now that query is saved
        if result["metadata"].get("pattern_metadata"):
            try:
                from src.patterns.usage_tracker import PatternUsageTracker
                usage_tracker = PatternUsageTracker()
                await usage_tracker.record_pattern_usage(
                    query_id=query_id,
                    patterns=result["metadata"]["pattern_metadata"],
                    final_quality=result["metadata"].get("quality_score")
                )
                logger.info("pattern_usage_recorded", query_id=query_id)
            except Exception as e:
                logger.error("pattern_usage_recording_failed", error=str(e), query_id=query_id)
        
        # Collect metrics
        if metrics_collector:
            try:
                iteration_count = 1
                if result["metadata"].get("refinement", {}).get("performed"):
                    iteration_count = result["metadata"]["refinement"]["iterations"]
                
                await metrics_collector.collect_query_metrics(
                    query_id=query_id,
                    processing_time=result["metadata"]["processing_time_seconds"],
                    quality_score=result["metadata"]["quality_score"],
                    iteration_count=iteration_count,
                    patterns_retrieved=result["metadata"]["patterns_retrieved_count"],
                    patterns_applied=result["metadata"]["patterns_applied_count"]
                )
            except Exception as e:
                logger.error("metrics_collection_failed", error=str(e), query_id=query_id)
        
        # Log episode for MATLAB analysis
        if episode_logger:
            try:
                # Extract quality scores from refinement or single score
                quality_scores = [result["metadata"]["quality_score"]]
                if result["metadata"].get("refinement", {}).get("performed"):
                    quality_scores = result["metadata"]["refinement"]["quality_progression"]
                
                episode_logger.log_episode(
                    query_id=query_id,
                    session_id=session_id,
                    query=request.query,
                    response=result["response"],
                    reasoning_steps=result["reasoning_steps"],
                    patterns_retrieved=result["metadata"].get("pattern_metadata", []),
                    quality_scores=quality_scores,
                    iteration_count=result["metadata"].get("refinement", {}).get("iterations", 1),
                    timing_ms={"total": result["metadata"]["processing_time_seconds"] * 1000}
                )
            except Exception as e:
                logger.error("episode_logging_failed", error=str(e), query_id=query_id)
        
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
