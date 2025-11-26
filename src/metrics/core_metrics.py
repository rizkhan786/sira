"""Core SIRA metrics - Tier 1 (Always Tracked).

Implements 4 Tier 1 metrics that are computed for every query:
1. Learning Velocity: Quality improvement rate over time
2. Pattern Utilization Rate: % of queries using retrieved patterns
3. Average Quality Score: Mean quality across all responses
4. Domain Coverage: # domains with quality patterns / total domains
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
import asyncpg
from src.core.logging import get_logger

logger = get_logger(__name__)


class CoreMetrics:
    """Tier 1 SIRA-specific metrics computed for every query."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize core metrics calculator.
        
        Args:
            db_pool: AsyncPG connection pool
        """
        self.pool = db_pool
        logger.info("core_metrics_initialized")
    
    async def compute_learning_velocity(
        self,
        lookback_hours: int = 24
    ) -> float:
        """Compute learning velocity (quality improvement rate over time).
        
        Learning velocity = (current_avg_quality - baseline_avg_quality) / hours
        
        Args:
            lookback_hours: Hours to look back for trend calculation
            
        Returns:
            Quality improvement rate per hour (can be negative if degrading)
        """
        async with self.pool.acquire() as conn:
            # Get quality scores over time window
            rows = await conn.fetch("""
                SELECT 
                    EXTRACT(EPOCH FROM (timestamp - MIN(timestamp) OVER())) / 3600.0 as hours_elapsed,
                    quality_score
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
                ORDER BY timestamp ASC
            """, timedelta(hours=lookback_hours))
            
            if len(rows) < 2:
                logger.warning("insufficient_data_for_learning_velocity", count=len(rows))
                return 0.0
            
            # Simple linear regression for trend
            n = len(rows)
            sum_x = sum(row["hours_elapsed"] for row in rows)
            sum_y = sum(row["quality_score"] for row in rows)
            sum_xy = sum(row["hours_elapsed"] * row["quality_score"] for row in rows)
            sum_x2 = sum(row["hours_elapsed"] ** 2 for row in rows)
            
            # Slope of regression line = learning velocity
            denominator = (n * sum_x2 - sum_x ** 2)
            if denominator == 0:
                return 0.0
            
            velocity = (n * sum_xy - sum_x * sum_y) / denominator
            
            logger.info(
                "learning_velocity_computed",
                velocity=round(velocity, 6),
                data_points=n,
                lookback_hours=lookback_hours
            )
            
            return round(velocity, 6)
    
    async def compute_pattern_utilization_rate(
        self,
        lookback_hours: int = 24
    ) -> float:
        """Compute pattern utilization rate (% queries using patterns).
        
        Args:
            lookback_hours: Hours to look back
            
        Returns:
            Percentage (0.0 - 1.0) of queries that used at least one pattern
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(CASE WHEN patterns_applied > 0 THEN 1 END) as queries_with_patterns
                FROM metrics
                WHERE query_id IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(hours=lookback_hours))
            
            total = row["total_queries"] or 0
            with_patterns = row["queries_with_patterns"] or 0
            
            if total == 0:
                return 0.0
            
            rate = with_patterns / total
            
            logger.info(
                "pattern_utilization_computed",
                rate=round(rate, 3),
                queries_with_patterns=with_patterns,
                total_queries=total
            )
            
            return round(rate, 3)
    
    async def compute_average_quality(
        self,
        lookback_hours: int = 24
    ) -> float:
        """Compute average quality score across all queries.
        
        Args:
            lookback_hours: Hours to look back
            
        Returns:
            Average quality score (0.0 - 1.0)
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT AVG(quality_score) as avg_quality
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(hours=lookback_hours))
            
            avg_quality = row["avg_quality"] or 0.0
            
            logger.info(
                "average_quality_computed",
                avg_quality=round(avg_quality, 3)
            )
            
            return round(avg_quality, 3)
    
    async def compute_domain_coverage(self) -> float:
        """Compute domain coverage (ratio of domains with quality patterns).
        
        Domain coverage = # unique domains in pattern library / # total domains seen
        
        For now, we estimate domains from pattern IDs (pattern prefixes).
        
        Returns:
            Domain coverage ratio (0.0 - 1.0)
        """
        async with self.pool.acquire() as conn:
            # Count unique pattern domains (first part of pattern_id before _)
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(DISTINCT SPLIT_PART(pattern_id, '_', 1)) as covered_domains
                FROM metrics
                WHERE pattern_id IS NOT NULL
                    AND pattern_id != ''
            """)
            
            covered_domains = row["covered_domains"] or 0
            
            # Total domains is estimated - in production would track explicitly
            # For now, assume we want coverage across 10 major domains
            total_domains = 10
            
            coverage = min(covered_domains / total_domains, 1.0) if total_domains > 0 else 0.0
            
            logger.info(
                "domain_coverage_computed",
                coverage=round(coverage, 3),
                covered_domains=covered_domains,
                total_domains=total_domains
            )
            
            return round(coverage, 3)
    
    async def compute_all_tier1_metrics(
        self,
        lookback_hours: int = 24
    ) -> Dict[str, float]:
        """Compute all Tier 1 metrics at once.
        
        Args:
            lookback_hours: Hours to look back for time-based metrics
            
        Returns:
            Dictionary with all 4 Tier 1 metrics
        """
        learning_velocity = await self.compute_learning_velocity(lookback_hours)
        pattern_utilization = await self.compute_pattern_utilization_rate(lookback_hours)
        avg_quality = await self.compute_average_quality(lookback_hours)
        domain_coverage = await self.compute_domain_coverage()
        
        metrics = {
            "learning_velocity": learning_velocity,
            "pattern_utilization_rate": pattern_utilization,
            "avg_quality": avg_quality,
            "domain_coverage": domain_coverage
        }
        
        logger.info("tier1_metrics_computed", metrics=metrics)
        
        return metrics
