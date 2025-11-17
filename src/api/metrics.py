"""Metrics API endpoints for SIRA."""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
from src.core.logging import get_logger

logger = get_logger(__name__)

# Router will be included in main.py
router = APIRouter(prefix="/metrics", tags=["metrics"])


class MetricsSummary(BaseModel):
    """Summary statistics response model."""
    total_queries: int = Field(..., description="Total queries processed")
    avg_quality: float = Field(..., description="Average quality score")
    avg_latency_ms: int = Field(..., description="Average latency in milliseconds")
    pattern_library_size: int = Field(..., description="Number of patterns in library")
    domain_coverage: int = Field(..., description="Number of unique domains")


class MetricsTrends(BaseModel):
    """Historical trends response model."""
    quality: list[float] = Field(..., description="Quality score trends")
    pattern_usage_rate: list[float] = Field(..., description="Pattern usage rate trends")


class MetricsResponse(BaseModel):
    """Complete metrics response."""
    summary: MetricsSummary
    trends: MetricsTrends


class PatternMetricsResponse(BaseModel):
    """Pattern-specific metrics response."""
    pattern_id: str
    usage_count: int
    effectiveness_score: float
    retrieval_rate: Optional[float] = None
    success_rate: Optional[float] = None


# Global metrics storage instance (set in main.py)
_metrics_storage = None


def set_metrics_storage(storage):
    """Set the global metrics storage instance.
    
    Args:
        storage: MetricsStorage instance
    """
    global _metrics_storage
    _metrics_storage = storage
    logger.info("metrics_storage_set_for_api")


@router.get("/summary", response_model=MetricsSummary)
async def get_metrics_summary():
    """Get current summary statistics.
    
    Returns:
        MetricsSummary with current stats
    """
    if not _metrics_storage:
        raise HTTPException(status_code=503, detail="Metrics storage not available")
    
    try:
        stats = await _metrics_storage.get_summary_stats()
        return MetricsSummary(**stats)
    except Exception as e:
        logger.error("get_metrics_summary_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/trends", response_model=MetricsTrends)
async def get_metrics_trends(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back")
):
    """Get historical trends.
    
    Args:
        days: Number of days to look back (1-90)
        
    Returns:
        MetricsTrends with historical data
    """
    if not _metrics_storage:
        raise HTTPException(status_code=503, detail="Metrics storage not available")
    
    try:
        quality_trends = await _metrics_storage.get_quality_trends(days=days)
        pattern_usage_trends = await _metrics_storage.get_pattern_usage_trends(days=days)
        
        return MetricsTrends(
            quality=quality_trends,
            pattern_usage_rate=pattern_usage_trends
        )
    except Exception as e:
        logger.error("get_metrics_trends_failed", error=str(e), days=days)
        raise HTTPException(status_code=500, detail=f"Failed to get trends: {str(e)}")


@router.get("", response_model=MetricsResponse)
async def get_metrics(
    days: int = Query(7, ge=1, le=90, description="Number of days for trends")
):
    """Get complete metrics (summary + trends).
    
    Args:
        days: Number of days to look back for trends
        
    Returns:
        MetricsResponse with summary and trends
    """
    summary = await get_metrics_summary()
    trends = await get_metrics_trends(days=days)
    
    return MetricsResponse(
        summary=summary,
        trends=trends
    )


@router.get("/patterns/{pattern_id}", response_model=PatternMetricsResponse)
async def get_pattern_metrics(pattern_id: str):
    """Get metrics for a specific pattern.
    
    Args:
        pattern_id: Pattern identifier
        
    Returns:
        PatternMetricsResponse with pattern stats
    """
    if not _metrics_storage:
        raise HTTPException(status_code=503, detail="Metrics storage not available")
    
    try:
        metrics = await _metrics_storage.get_pattern_effectiveness(pattern_id)
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for pattern {pattern_id}"
            )
        
        return PatternMetricsResponse(**metrics)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_pattern_metrics_failed", error=str(e), pattern_id=pattern_id)
        raise HTTPException(status_code=500, detail=f"Failed to get pattern metrics: {str(e)}")
