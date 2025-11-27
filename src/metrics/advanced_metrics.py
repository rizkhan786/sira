"""Advanced SIRA metrics - Tier 2 (Weekly) and Tier 3 (Monthly).

Tier 2 (Weekly):
5. Self-Correction Success Rate: % of refinements that improve quality
6. Pattern Transfer Efficiency: Success rate of patterns in new contexts
7. Convergence Rate: Time/queries to reach stable performance

Tier 3 (Monthly):
8. SIRA vs. Baseline: Improvement over base LLM
9. Domain-Specific Performance: Quality by domain
10. User Satisfaction: Feedback-based scoring (placeholder)
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
import asyncpg
from src.core.logging import get_logger

logger = get_logger(__name__)


class AdvancedMetrics:
    """Tier 2 and Tier 3 SIRA-specific metrics."""
    
    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize advanced metrics calculator.
        
        Args:
            db_pool: AsyncPG connection pool
        """
        self.pool = db_pool
        logger.info("advanced_metrics_initialized")
    
    # === TIER 2: WEEKLY METRICS ===
    
    async def compute_self_correction_success_rate(
        self,
        lookback_days: int = 7
    ) -> float:
        """Compute self-correction success rate (% refinements that improve quality).
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Success rate (0.0 - 1.0) of refinement iterations
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_refinements,
                    COUNT(CASE WHEN iteration_count > 1 THEN 1 END) as successful_refinements
                FROM metrics
                WHERE query_id IS NOT NULL
                    AND iteration_count IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(days=lookback_days))
            
            total = row["total_refinements"] or 0
            successful = row["successful_refinements"] or 0
            
            if total == 0:
                return 0.0
            
            # Refinement is successful if iteration_count > 1 (system refined the response)
            rate = successful / total
            
            logger.info(
                "self_correction_rate_computed",
                rate=round(rate, 3),
                successful=successful,
                total=total
            )
            
            return round(rate, 3)
    
    async def compute_pattern_transfer_efficiency(
        self,
        lookback_days: int = 7
    ) -> float:
        """Compute pattern transfer efficiency (success rate in new contexts).
        
        Transfer efficiency = quality when patterns applied in new domain / avg quality
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Transfer efficiency ratio (0.0 - 1.0+)
        """
        async with self.pool.acquire() as conn:
            # Get quality scores for queries using patterns
            row = await conn.fetchrow("""
                SELECT 
                    AVG(CASE WHEN patterns_applied > 0 THEN quality_score END) as avg_with_patterns,
                    AVG(quality_score) as overall_avg
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(days=lookback_days))
            
            avg_with_patterns = row["avg_with_patterns"] or 0.0
            overall_avg = row["overall_avg"] or 0.01  # Avoid division by zero
            
            efficiency = avg_with_patterns / overall_avg if overall_avg > 0 else 0.0
            
            logger.info(
                "pattern_transfer_efficiency_computed",
                efficiency=round(efficiency, 3),
                avg_with_patterns=round(avg_with_patterns, 3),
                overall_avg=round(overall_avg, 3)
            )
            
            return round(efficiency, 3)
    
    async def compute_convergence_rate(
        self,
        lookback_days: int = 7
    ) -> Dict[str, float]:
        """Compute convergence rate (time/queries to stable performance).
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Dictionary with queries_to_convergence and hours_to_convergence
        """
        async with self.pool.acquire() as conn:
            # Get quality scores over time
            rows = await conn.fetch("""
                SELECT 
                    ROW_NUMBER() OVER (ORDER BY timestamp) as query_num,
                    quality_score,
                    timestamp
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
                ORDER BY timestamp ASC
            """, timedelta(days=lookback_days))
            
            if len(rows) < 10:
                return {"queries_to_convergence": 0.0, "hours_to_convergence": 0.0}
            
            # Define convergence as when moving average stabilizes (variance < 0.01)
            window_size = 5
            convergence_query = 0
            convergence_time = None
            
            for i in range(window_size, len(rows)):
                window = rows[i-window_size:i]
                window_avg = sum(r["quality_score"] for r in window) / window_size
                window_var = sum((r["quality_score"] - window_avg) ** 2 for r in window) / window_size
                
                if window_var < 0.01:  # Converged
                    convergence_query = rows[i]["query_num"]
                    convergence_time = rows[i]["timestamp"]
                    break
            
            if convergence_query == 0:
                convergence_query = len(rows)  # Not yet converged
                convergence_time = rows[-1]["timestamp"]
            
            # Calculate hours from first to convergence
            start_time = rows[0]["timestamp"]
            hours_elapsed = (convergence_time - start_time).total_seconds() / 3600.0
            
            result = {
                "queries_to_convergence": float(convergence_query),
                "hours_to_convergence": round(hours_elapsed, 2)
            }
            
            logger.info("convergence_rate_computed", result=result)
            
            return result
    
    async def compute_all_tier2_metrics(
        self,
        lookback_days: int = 7
    ) -> Dict[str, any]:
        """Compute all Tier 2 metrics at once.
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Dictionary with all 3 Tier 2 metrics
        """
        self_correction = await self.compute_self_correction_success_rate(lookback_days)
        transfer_efficiency = await self.compute_pattern_transfer_efficiency(lookback_days)
        convergence = await self.compute_convergence_rate(lookback_days)
        
        metrics = {
            "self_correction_success_rate": self_correction,
            "pattern_transfer_efficiency": transfer_efficiency,
            "convergence_rate": convergence
        }
        
        logger.info("tier2_metrics_computed", metrics=metrics)
        
        return metrics
    
    # === TIER 3: MONTHLY METRICS ===
    
    async def compute_sira_vs_baseline(
        self,
        lookback_days: int = 30
    ) -> Dict[str, float]:
        """Compute SIRA improvement over baseline (base LLM without patterns).
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Dictionary with sira_avg, baseline_avg, improvement_pct
        """
        async with self.pool.acquire() as conn:
            # SIRA performance (with patterns)
            sira_row = await conn.fetchrow("""
                SELECT AVG(quality_score) as avg_quality
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND patterns_applied > 0
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(days=lookback_days))
            
            # Baseline performance (without patterns)
            baseline_row = await conn.fetchrow("""
                SELECT AVG(quality_score) as avg_quality
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND (patterns_applied = 0 OR patterns_applied IS NULL)
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(days=lookback_days))
            
            sira_avg = float(sira_row["avg_quality"]) if sira_row["avg_quality"] is not None else 0.0
            baseline_avg = float(baseline_row["avg_quality"]) if baseline_row["avg_quality"] is not None else 0.01
            
            improvement = ((sira_avg - baseline_avg) / baseline_avg * 100) if baseline_avg > 0 else 0.0
            
            result = {
                "sira_avg_quality": round(sira_avg, 3),
                "baseline_avg_quality": round(baseline_avg, 3),
                "improvement_pct": round(improvement, 2)
            }
            
            logger.info("sira_vs_baseline_computed", result=result)
            
            return result
    
    async def compute_domain_specific_performance(
        self,
        lookback_days: int = 30
    ) -> List[Dict[str, any]]:
        """Compute quality by domain (from pattern prefixes).
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            List of dictionaries with domain and avg_quality
        """
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    SPLIT_PART(pattern_id, '_', 1) as domain,
                    AVG(quality_score) as avg_quality,
                    COUNT(*) as query_count
                FROM metrics
                WHERE pattern_id IS NOT NULL
                    AND pattern_id != ''
                    AND quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
                GROUP BY domain
                ORDER BY avg_quality DESC
            """, timedelta(days=lookback_days))
            
            results = [
                {
                    "domain": row["domain"],
                    "avg_quality": round(float(row["avg_quality"]), 3),
                    "query_count": int(row["query_count"])
                }
                for row in rows
            ]
            
            logger.info(
                "domain_performance_computed",
                domain_count=len(results)
            )
            
            return results
    
    async def compute_user_satisfaction(
        self,
        lookback_days: int = 30
    ) -> float:
        """Compute user satisfaction score (placeholder - would use feedback data).
        
        For now, estimates based on quality scores and refinement success.
        In production, would use explicit user ratings.
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Satisfaction score (0.0 - 1.0)
        """
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT 
                    AVG(quality_score) as avg_quality,
                    AVG(CASE WHEN iteration_count <= 2 THEN 1.0 ELSE 0.5 END) as response_speed_factor
                FROM metrics
                WHERE quality_score IS NOT NULL
                    AND timestamp > NOW() - $1::INTERVAL
            """, timedelta(days=lookback_days))
            
            avg_quality = float(row["avg_quality"]) if row["avg_quality"] is not None else 0.0
            speed_factor = float(row["response_speed_factor"]) if row["response_speed_factor"] is not None else 0.5
            
            # Weighted satisfaction: 70% quality, 30% speed
            satisfaction = (0.7 * avg_quality) + (0.3 * speed_factor)
            
            logger.info(
                "user_satisfaction_computed",
                satisfaction=round(satisfaction, 3),
                note="estimated_from_quality_and_speed"
            )
            
            return round(satisfaction, 3)
    
    async def compute_all_tier3_metrics(
        self,
        lookback_days: int = 30
    ) -> Dict[str, any]:
        """Compute all Tier 3 metrics at once.
        
        Args:
            lookback_days: Days to look back
            
        Returns:
            Dictionary with all 3 Tier 3 metrics
        """
        sira_vs_baseline = await self.compute_sira_vs_baseline(lookback_days)
        domain_performance = await self.compute_domain_specific_performance(lookback_days)
        user_satisfaction = await self.compute_user_satisfaction(lookback_days)
        
        metrics = {
            "sira_vs_baseline": sira_vs_baseline,
            "domain_specific_performance": domain_performance,
            "user_satisfaction": user_satisfaction
        }
        
        logger.info("tier3_metrics_computed")
        
        return metrics
