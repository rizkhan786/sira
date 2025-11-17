"""Metrics storage and retrieval from PostgreSQL."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import uuid
import asyncpg
from src.core.logging import get_logger

logger = get_logger(__name__)


class MetricsStorage:
    """Handles metrics persistence in PostgreSQL."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize metrics storage.
        
        Args:
            db_pool: AsyncPG connection pool
        """
        self.pool = db_pool
        logger.info("metrics_storage_initialized")
    
    async def store_metrics_batch(self, metrics_batch: List[Dict[str, Any]]):
        """Store a batch of metrics in the database.
        
        Args:
            metrics_batch: List of metric dictionaries
        """
        if not metrics_batch:
            return
        
        async with self.pool.acquire() as conn:
            for metric in metrics_batch:
                metric_type = metric["type"]
                data = metric["data"]
                
                if metric_type == "query":
                    await self._store_query_metrics(conn, data)
                elif metric_type == "pattern":
                    await self._store_pattern_metrics(conn, data)
                elif metric_type == "system":
                    await self._store_system_metrics(conn, data)
        
        logger.info("metrics_batch_stored", count=len(metrics_batch))
    
    async def _store_query_metrics(self, conn, metrics):
        """Store query-level metrics."""
        await conn.execute("""
            INSERT INTO metrics (
                id, timestamp, query_id, query_latency_ms, quality_score,
                iteration_count, patterns_retrieved, patterns_applied
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, 
            uuid.uuid4(),
            metrics.timestamp,
            uuid.UUID(metrics.query_id),
            metrics.query_latency_ms,
            metrics.quality_score,
            metrics.iteration_count,
            metrics.patterns_retrieved,
            metrics.patterns_applied
        )
    
    async def _store_pattern_metrics(self, conn, metrics):
        """Store pattern-level metrics."""
        await conn.execute("""
            INSERT INTO metrics (
                id, timestamp, pattern_id, pattern_effectiveness
            ) VALUES ($1, $2, $3, $4)
        """,
            uuid.uuid4(),
            metrics.timestamp,
            metrics.pattern_id,
            metrics.effectiveness_score
        )
    
    async def _store_system_metrics(self, conn, metrics):
        """Store system-level metrics."""
        await conn.execute("""
            INSERT INTO metrics (
                id, timestamp, total_queries, avg_quality,
                avg_latency_ms, pattern_library_size, domain_coverage
            ) VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
            uuid.uuid4(),
            metrics.timestamp,
            metrics.total_queries,
            metrics.avg_quality,
            metrics.avg_latency_ms,
            metrics.pattern_library_size,
            metrics.domain_coverage
        )
    
    async def get_summary_stats(self) -> Dict[str, Any]:
        """Get current summary statistics.
        
        Returns:
            Dictionary with summary stats
        """
        async with self.pool.acquire() as conn:
            # Query recent metrics
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(DISTINCT query_id) as total_queries,
                    AVG(quality_score) as avg_quality,
                    AVG(query_latency_ms) as avg_latency,
                    SUM(patterns_retrieved) as total_patterns_retrieved
                FROM metrics
                WHERE query_id IS NOT NULL
                    AND timestamp > NOW() - INTERVAL '30 days'
            """)
            
            # Get pattern library size from ChromaDB metadata
            pattern_count_row = await conn.fetchrow("""
                SELECT COUNT(DISTINCT pattern_id) as pattern_count
                FROM metrics
                WHERE pattern_id IS NOT NULL
            """)
            
            return {
                "total_queries": row["total_queries"] or 0,
                "avg_quality": round(row["avg_quality"], 3) if row["avg_quality"] else 0.0,
                "avg_latency_ms": int(row["avg_latency"]) if row["avg_latency"] else 0,
                "pattern_library_size": pattern_count_row["pattern_count"] or 0,
                "domain_coverage": 0  # Placeholder - would need domain tracking
            }
    
    async def get_quality_trends(
        self,
        days: int = 7,
        bucket_hours: int = 24
    ) -> List[float]:
        """Get quality score trends over time.
        
        Args:
            days: Number of days to look back
            bucket_hours: Hours per bucket for aggregation
            
        Returns:
            List of average quality scores per time bucket
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('hour', timestamp) as hour_bucket,
                    AVG(quality_score) as avg_quality
                FROM metrics
                WHERE query_id IS NOT NULL
                    AND quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
                GROUP BY hour_bucket
                ORDER BY hour_bucket ASC
            """, timedelta(days=days))
            
            return [round(row["avg_quality"], 3) for row in rows]
    
    async def get_pattern_usage_trends(
        self,
        days: int = 7
    ) -> List[float]:
        """Get pattern usage rate trends.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of pattern usage rates per day
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    DATE(timestamp) as day,
                    AVG(CASE WHEN patterns_applied > 0 THEN 1.0 ELSE 0.0 END) as usage_rate
                FROM metrics
                WHERE query_id IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
                GROUP BY day
                ORDER BY day ASC
            """, timedelta(days=days))
            
            return [round(row["usage_rate"], 3) for row in rows]
    
    async def get_pattern_effectiveness(
        self,
        pattern_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get effectiveness metrics for a specific pattern.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Pattern effectiveness metrics or None
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as usage_count,
                    AVG(pattern_effectiveness) as avg_effectiveness
                FROM metrics
                WHERE pattern_id = $1
            """, pattern_id)
            
            if not row or row["usage_count"] == 0:
                return None
            
            return {
                "pattern_id": pattern_id,
                "usage_count": row["usage_count"],
                "effectiveness_score": round(row["avg_effectiveness"], 3) if row["avg_effectiveness"] else 0.0
            }
    
    async def cleanup_old_metrics(self, retention_days: int = 90):
        """Remove metrics older than retention period.
        
        Args:
            retention_days: Number of days to retain metrics
        """
        async with self.pool.acquire() as conn:
            result = await conn.execute("""
                DELETE FROM metrics
                WHERE timestamp < NOW() - $1::INTERVAL
            """, timedelta(days=retention_days))
            
            # Parse result like "DELETE 42"
            deleted_count = int(result.split()[-1]) if result.split() else 0
            logger.info(
                "old_metrics_cleaned",
                retention_days=retention_days,
                deleted=deleted_count
            )
            
            return deleted_count
