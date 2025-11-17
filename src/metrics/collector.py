"""Metrics collection for SIRA performance tracking."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a single query."""
    query_id: str
    timestamp: datetime
    query_latency_ms: int
    quality_score: float
    iteration_count: int
    patterns_retrieved: int
    patterns_applied: int
    improvement_over_baseline: Optional[float] = None
    

@dataclass
class PatternMetrics:
    """Metrics for pattern performance."""
    pattern_id: str
    timestamp: datetime
    usage_count: int
    effectiveness_score: float  # Average quality improvement
    retrieval_rate: float  # % of queries retrieving this pattern
    success_rate: float  # % of queries where pattern helped


@dataclass
class SystemMetrics:
    """System-level aggregate metrics."""
    timestamp: datetime
    total_queries: int
    avg_quality: float
    avg_latency_ms: int
    pattern_library_size: int
    domain_coverage: int
    quality_trend: List[float] = field(default_factory=list)
    pattern_usage_trend: List[float] = field(default_factory=list)


class MetricsCollector:
    """Collects and aggregates metrics from query processing."""
    
    def __init__(self, storage=None):
        """Initialize metrics collector.
        
        Args:
            storage: MetricsStorage instance for persistence
        """
        self.storage = storage
        self._batch_buffer: List[Dict[str, Any]] = []
        self._batch_size = 10
        logger.info("metrics_collector_initialized", batch_size=self._batch_size)
    
    async def collect_query_metrics(
        self,
        query_id: str,
        processing_time: float,
        quality_score: float,
        iteration_count: int,
        patterns_retrieved: int,
        patterns_applied: int,
        improvement_over_baseline: Optional[float] = None
    ) -> QueryMetrics:
        """Collect metrics for a single query.
        
        Args:
            query_id: Unique query identifier
            processing_time: Total processing time in seconds
            quality_score: Final quality score (0.0-1.0)
            iteration_count: Number of refinement iterations
            patterns_retrieved: Count of patterns retrieved
            patterns_applied: Count of patterns actually applied
            improvement_over_baseline: Quality improvement vs baseline
            
        Returns:
            QueryMetrics object
        """
        metrics = QueryMetrics(
            query_id=query_id,
            timestamp=datetime.now(timezone.utc),
            query_latency_ms=int(processing_time * 1000),
            quality_score=quality_score,
            iteration_count=iteration_count,
            patterns_retrieved=patterns_retrieved,
            patterns_applied=patterns_applied,
            improvement_over_baseline=improvement_over_baseline
        )
        
        logger.info(
            "query_metrics_collected",
            query_id=query_id,
            latency_ms=metrics.query_latency_ms,
            quality=quality_score,
            iterations=iteration_count
        )
        
        # Add to batch buffer for storage
        if self.storage:
            await self._add_to_batch({
                "type": "query",
                "data": metrics
            })
        
        return metrics
    
    async def collect_pattern_metrics(
        self,
        pattern_id: str,
        usage_count: int,
        effectiveness_score: float,
        retrieval_rate: float,
        success_rate: float
    ) -> PatternMetrics:
        """Collect metrics for a pattern.
        
        Args:
            pattern_id: Pattern identifier
            usage_count: Total times pattern used
            effectiveness_score: Average quality improvement
            retrieval_rate: Percentage of queries retrieving pattern
            success_rate: Percentage where pattern improved quality
            
        Returns:
            PatternMetrics object
        """
        metrics = PatternMetrics(
            pattern_id=pattern_id,
            timestamp=datetime.now(timezone.utc),
            usage_count=usage_count,
            effectiveness_score=effectiveness_score,
            retrieval_rate=retrieval_rate,
            success_rate=success_rate
        )
        
        logger.info(
            "pattern_metrics_collected",
            pattern_id=pattern_id,
            usage_count=usage_count,
            effectiveness=effectiveness_score
        )
        
        if self.storage:
            await self._add_to_batch({
                "type": "pattern",
                "data": metrics
            })
        
        return metrics
    
    async def collect_system_metrics(
        self,
        total_queries: int,
        avg_quality: float,
        avg_latency_ms: int,
        pattern_library_size: int,
        domain_coverage: int,
        quality_trend: List[float],
        pattern_usage_trend: List[float]
    ) -> SystemMetrics:
        """Collect system-level aggregate metrics.
        
        Args:
            total_queries: Total queries processed
            avg_quality: Average quality score
            avg_latency_ms: Average latency in milliseconds
            pattern_library_size: Number of patterns in library
            domain_coverage: Number of unique domains covered
            quality_trend: Historical quality scores
            pattern_usage_trend: Historical pattern usage rates
            
        Returns:
            SystemMetrics object
        """
        metrics = SystemMetrics(
            timestamp=datetime.now(timezone.utc),
            total_queries=total_queries,
            avg_quality=avg_quality,
            avg_latency_ms=avg_latency_ms,
            pattern_library_size=pattern_library_size,
            domain_coverage=domain_coverage,
            quality_trend=quality_trend,
            pattern_usage_trend=pattern_usage_trend
        )
        
        logger.info(
            "system_metrics_collected",
            total_queries=total_queries,
            avg_quality=avg_quality,
            pattern_count=pattern_library_size
        )
        
        if self.storage:
            await self._add_to_batch({
                "type": "system",
                "data": metrics
            })
        
        return metrics
    
    async def _add_to_batch(self, metric: Dict[str, Any]):
        """Add metric to batch buffer and flush if needed.
        
        Args:
            metric: Metric data to add to batch
        """
        self._batch_buffer.append(metric)
        
        if len(self._batch_buffer) >= self._batch_size:
            await self._flush_batch()
    
    async def _flush_batch(self):
        """Flush batch buffer to storage."""
        if not self._batch_buffer:
            return
        
        try:
            await self.storage.store_metrics_batch(self._batch_buffer)
            logger.info(
                "metrics_batch_flushed",
                count=len(self._batch_buffer)
            )
            self._batch_buffer.clear()
        except Exception as e:
            logger.error(
                "metrics_batch_flush_failed",
                error=str(e),
                count=len(self._batch_buffer)
            )
    
    async def flush(self):
        """Manually flush any pending metrics."""
        await self._flush_batch()
    
    def calculate_improvement(
        self,
        quality_with_patterns: float,
        quality_without_patterns: Optional[float]
    ) -> Optional[float]:
        """Calculate quality improvement from pattern usage.
        
        Args:
            quality_with_patterns: Quality score with patterns
            quality_without_patterns: Quality score without patterns (if available)
            
        Returns:
            Improvement score or None if baseline unavailable
        """
        if quality_without_patterns is None:
            return None
        
        improvement = quality_with_patterns - quality_without_patterns
        return round(improvement, 3)
    
    async def get_current_stats(self) -> Dict[str, Any]:
        """Get current metrics statistics.
        
        Returns:
            Dictionary with current stats
        """
        if not self.storage:
            return {
                "status": "no_storage",
                "buffered_metrics": len(self._batch_buffer)
            }
        
        try:
            return await self.storage.get_summary_stats()
        except Exception as e:
            logger.error("get_stats_failed", error=str(e))
            return {
                "status": "error",
                "error": str(e)
            }
