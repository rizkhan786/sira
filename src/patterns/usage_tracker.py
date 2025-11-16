"""Track pattern usage and effectiveness."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import asyncpg
from src.core.config import get_settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class PatternUsageTracker:
    """Tracks when patterns are applied and their effectiveness."""
    
    def __init__(self):
        self.settings = get_settings()
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """Initialize database connection pool."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(
                host=self.settings.postgres_host,
                port=self.settings.postgres_port,
                user=self.settings.postgres_user,
                password=self.settings.postgres_password,
                database=self.settings.postgres_db,
                min_size=1,
                max_size=5
            )
    
    async def record_pattern_usage(
        self,
        query_id: str,
        patterns: List[Dict[str, Any]],
        baseline_quality: Optional[float] = None,
        final_quality: Optional[float] = None
    ) -> List[str]:
        """Record that patterns were applied to a query.
        
        Args:
            query_id: UUID of the query
            patterns: List of pattern metadata that were applied
            baseline_quality: Quality score without patterns (if available)
            final_quality: Final quality score with patterns
            
        Returns:
            List of usage record IDs
        """
        await self.initialize()
        
        if not patterns:
            return []
        
        usage_ids = []
        
        for pattern in patterns:
            pattern_id = pattern.get("pattern_id")
            if not pattern_id:
                continue
            
            usage_id = str(uuid.uuid4())
            similarity_score = pattern.get("similarity", 0.0)
            
            # Calculate effectiveness if we have both baseline and final quality
            effectiveness_score = None
            improved_quality = None
            
            if baseline_quality is not None and final_quality is not None:
                effectiveness_score = final_quality - baseline_quality
                improved_quality = final_quality > baseline_quality
            
            try:
                sql = """
                    INSERT INTO pattern_usage (
                        id, query_id, pattern_id, similarity_score,
                        applied_at, effectiveness_score, improved_quality
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """
                
                async with self.pool.acquire() as conn:
                    await conn.execute(
                        sql,
                        usage_id,
                        query_id,
                        pattern_id,
                        similarity_score,
                        datetime.now(timezone.utc),
                        effectiveness_score,
                        improved_quality
                    )
                
                usage_ids.append(usage_id)
                
                logger.info(
                    "pattern_usage_recorded",
                    pattern_id=pattern_id,
                    query_id=query_id,
                    similarity=similarity_score,
                    effectiveness=effectiveness_score
                )
                
            except Exception as e:
                logger.error(
                    "pattern_usage_record_failed",
                    pattern_id=pattern_id,
                    error=str(e)
                )
        
        return usage_ids
    
    async def update_pattern_effectiveness(
        self,
        usage_id: str,
        effectiveness_score: float,
        improved_quality: bool
    ):
        """Update effectiveness score after quality calculation.
        
        Args:
            usage_id: Usage record ID
            effectiveness_score: Quality improvement from pattern
            improved_quality: Whether quality improved
        """
        await self.initialize()
        
        try:
            sql = """
                UPDATE pattern_usage
                SET effectiveness_score = $1,
                    improved_quality = $2
                WHERE id = $3
            """
            
            async with self.pool.acquire() as conn:
                await conn.execute(
                    sql,
                    effectiveness_score,
                    improved_quality,
                    usage_id
                )
            
            logger.info(
                "pattern_effectiveness_updated",
                usage_id=usage_id,
                effectiveness=effectiveness_score
            )
            
        except Exception as e:
            logger.error(
                "pattern_effectiveness_update_failed",
                usage_id=usage_id,
                error=str(e)
            )
    
    async def get_pattern_usage_stats(
        self,
        pattern_id: str
    ) -> Dict[str, Any]:
        """Get usage statistics for a pattern.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Dict with usage statistics
        """
        await self.initialize()
        
        try:
            sql = """
                SELECT 
                    COUNT(*) as usage_count,
                    AVG(similarity_score) as avg_similarity,
                    AVG(effectiveness_score) as avg_effectiveness,
                    SUM(CASE WHEN improved_quality = true THEN 1 ELSE 0 END) as success_count
                FROM pattern_usage
                WHERE pattern_id = $1
                    AND effectiveness_score IS NOT NULL
            """
            
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(sql, pattern_id)
            
            usage_count = row['usage_count'] if row else 0
            success_count = row['success_count'] if row else 0
            
            return {
                "pattern_id": pattern_id,
                "usage_count": usage_count,
                "avg_similarity": float(row['avg_similarity']) if row and row['avg_similarity'] else 0.0,
                "avg_effectiveness": float(row['avg_effectiveness']) if row and row['avg_effectiveness'] else 0.0,
                "success_rate": success_count / usage_count if usage_count > 0 else 0.0,
                "success_count": success_count
            }
            
        except Exception as e:
            logger.error(
                "get_pattern_stats_failed",
                pattern_id=pattern_id,
                error=str(e)
            )
            return {
                "pattern_id": pattern_id,
                "usage_count": 0,
                "avg_similarity": 0.0,
                "avg_effectiveness": 0.0,
                "success_rate": 0.0,
                "success_count": 0
            }
    
    async def get_query_pattern_usage(
        self,
        query_id: str
    ) -> List[Dict[str, Any]]:
        """Get patterns used for a specific query.
        
        Args:
            query_id: Query identifier
            
        Returns:
            List of pattern usage records
        """
        await self.initialize()
        
        try:
            sql = """
                SELECT 
                    id, pattern_id, similarity_score,
                    applied_at, effectiveness_score, improved_quality
                FROM pattern_usage
                WHERE query_id = $1
                ORDER BY similarity_score DESC
            """
            
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(sql, query_id)
            
            usage_records = []
            for row in rows:
                usage_records.append({
                    "id": str(row['id']),
                    "pattern_id": row['pattern_id'],
                    "similarity_score": float(row['similarity_score']),
                    "applied_at": row['applied_at'].isoformat(),
                    "effectiveness_score": float(row['effectiveness_score']) if row['effectiveness_score'] else None,
                    "improved_quality": row['improved_quality']
                })
            
            return usage_records
            
        except Exception as e:
            logger.error(
                "get_query_patterns_failed",
                query_id=query_id,
                error=str(e)
            )
            return []
    
    async def close(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
