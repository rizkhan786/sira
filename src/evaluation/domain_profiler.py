"""Domain profiler for analyzing SIRA performance across domains.

Provides per-domain quality metrics and identifies strengths/weaknesses
across different query types (math, coding, science, etc).
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class DomainStats:
    """Statistics for a single domain."""
    domain: str
    query_count: int
    avg_quality: float
    min_quality: float
    max_quality: float
    success_rate: float  # % of queries above quality threshold
    improvement_trend: float  # slope of quality over time


class DomainProfiler:
    """Analyzes SIRA performance across different domains."""
    
    def __init__(self, db_connection, quality_threshold: float = 0.7):
        """Initialize profiler.
        
        Args:
            db_connection: Database connection for querying data
            quality_threshold: Threshold for "successful" response (default: 0.7)
        """
        self.db = db_connection
        self.quality_threshold = quality_threshold
        logger.info(
            "domain_profiler_initialized",
            quality_threshold=quality_threshold
        )
    
    async def get_domain_stats(
        self,
        domain: str,
        min_queries: int = 100
    ) -> Optional[DomainStats]:
        """Get statistics for a specific domain.
        
        Args:
            domain: Domain name
            min_queries: Minimum queries needed for analysis
            
        Returns:
            DomainStats or None if insufficient data
        """
        # Get all queries for domain with quality scores
        query = """
            SELECT 
                quality_score,
                created_at,
                ROW_NUMBER() OVER (ORDER BY created_at) as query_num
            FROM query_logs
            WHERE domain = ? AND quality_score IS NOT NULL
            ORDER BY created_at ASC
        """
        rows = await self.db.fetch_all(query, [domain])
        
        if len(rows) < min_queries:
            logger.warning(
                "insufficient_domain_data",
                domain=domain,
                found=len(rows),
                required=min_queries
            )
            return None
        
        # Extract quality scores
        qualities = [row[0] for row in rows]
        
        # Basic statistics
        avg_quality = sum(qualities) / len(qualities)
        min_quality = min(qualities)
        max_quality = max(qualities)
        
        # Success rate (queries above threshold)
        successes = sum(1 for q in qualities if q >= self.quality_threshold)
        success_rate = successes / len(qualities)
        
        # Improvement trend (linear regression slope)
        n = len(qualities)
        query_nums = list(range(1, n + 1))
        
        x_mean = sum(query_nums) / n
        y_mean = avg_quality
        
        numerator = sum((query_nums[i] - x_mean) * (qualities[i] - y_mean) for i in range(n))
        denominator = sum((query_nums[i] - x_mean) ** 2 for i in range(n))
        
        improvement_trend = numerator / denominator if denominator > 0 else 0.0
        
        stats = DomainStats(
            domain=domain,
            query_count=len(qualities),
            avg_quality=round(avg_quality, 3),
            min_quality=round(min_quality, 3),
            max_quality=round(max_quality, 3),
            success_rate=round(success_rate, 3),
            improvement_trend=round(improvement_trend, 6)
        )
        
        logger.info(
            "domain_stats_computed",
            domain=domain,
            avg_quality=stats.avg_quality,
            success_rate=stats.success_rate
        )
        
        return stats
    
    async def profile_all_domains(
        self,
        min_queries: int = 100
    ) -> List[DomainStats]:
        """Profile all domains with sufficient data.
        
        Args:
            min_queries: Minimum queries per domain
            
        Returns:
            List of DomainStats, sorted by average quality (desc)
        """
        # Get all domains
        query = """
            SELECT DISTINCT domain, COUNT(*) as count
            FROM query_logs
            WHERE domain IS NOT NULL AND quality_score IS NOT NULL
            GROUP BY domain
            HAVING count >= ?
            ORDER BY count DESC
        """
        rows = await self.db.fetch_all(query, [min_queries])
        
        domains = [row[0] for row in rows]
        
        logger.info(
            "profiling_domains",
            domain_count=len(domains),
            min_queries=min_queries
        )
        
        # Get stats for each domain
        all_stats = []
        for domain in domains:
            stats = await self.get_domain_stats(domain, min_queries)
            if stats:
                all_stats.append(stats)
        
        # Sort by average quality (descending)
        all_stats.sort(key=lambda s: s.avg_quality, reverse=True)
        
        logger.info(
            "domain_profiling_complete",
            domains_profiled=len(all_stats)
        )
        
        return all_stats
    
    def identify_strengths_weaknesses(
        self,
        domain_stats: List[DomainStats],
        top_n: int = 3
    ) -> Dict[str, List[str]]:
        """Identify SIRA's strongest and weakest domains.
        
        Args:
            domain_stats: List of domain statistics
            top_n: Number of top/bottom domains to identify
            
        Returns:
            Dictionary with 'strengths' and 'weaknesses' lists
        """
        if not domain_stats:
            return {"strengths": [], "weaknesses": []}
        
        # Already sorted by avg_quality (desc)
        strengths = [s.domain for s in domain_stats[:top_n]]
        weaknesses = [s.domain for s in domain_stats[-top_n:]]
        weaknesses.reverse()  # Show worst first
        
        logger.info(
            "strengths_weaknesses_identified",
            strengths=strengths,
            weaknesses=weaknesses
        )
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses
        }
    
    def compute_domain_coverage(
        self,
        domain_stats: List[DomainStats],
        expected_domains: List[str]
    ) -> Dict[str, any]:
        """Compute domain coverage metrics.
        
        Args:
            domain_stats: List of domain statistics
            expected_domains: List of expected/target domains
            
        Returns:
            Dictionary with coverage metrics
        """
        profiled_domains = {s.domain for s in domain_stats}
        expected_set = set(expected_domains)
        
        covered = profiled_domains & expected_set
        missing = expected_set - profiled_domains
        
        coverage_pct = len(covered) / len(expected_set) * 100 if expected_set else 0
        
        # Average quality across all domains
        avg_quality_all = sum(s.avg_quality for s in domain_stats) / len(domain_stats) if domain_stats else 0
        
        # Consistency (std deviation of avg qualities)
        if len(domain_stats) > 1:
            qualities = [s.avg_quality for s in domain_stats]
            mean = avg_quality_all
            variance = sum((q - mean) ** 2 for q in qualities) / len(qualities)
            std_dev = variance ** 0.5
        else:
            std_dev = 0.0
        
        coverage = {
            "expected_domains": len(expected_set),
            "covered_domains": len(covered),
            "missing_domains": list(missing),
            "coverage_pct": round(coverage_pct, 1),
            "avg_quality_all_domains": round(avg_quality_all, 3),
            "quality_std_dev": round(std_dev, 3),
            "consistency": "high" if std_dev < 0.1 else "medium" if std_dev < 0.2 else "low"
        }
        
        logger.info(
            "domain_coverage_computed",
            coverage_pct=coverage["coverage_pct"],
            missing_count=len(missing)
        )
        
        return coverage
    
    def generate_report(
        self,
        domain_stats: List[DomainStats],
        strengths_weaknesses: Dict[str, List[str]],
        coverage: Dict[str, any]
    ) -> str:
        """Generate comprehensive domain profiling report.
        
        Args:
            domain_stats: List of domain statistics
            strengths_weaknesses: Identified strengths/weaknesses
            coverage: Domain coverage metrics
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("Domain Performance Profile")
        report.append("=" * 60)
        report.append("")
        
        # Coverage summary
        report.append("Domain Coverage:")
        report.append(f"  Total Domains Profiled: {len(domain_stats)}")
        report.append(f"  Expected Domain Coverage: {coverage['coverage_pct']}% ({coverage['covered_domains']}/{coverage['expected_domains']})")
        if coverage['missing_domains']:
            report.append(f"  Missing Domains: {', '.join(coverage['missing_domains'])}")
        report.append(f"  Average Quality Across All Domains: {coverage['avg_quality_all_domains']}")
        report.append(f"  Quality Consistency: {coverage['consistency'].upper()} (σ = {coverage['quality_std_dev']})")
        report.append("")
        
        # Strengths and weaknesses
        report.append("Strongest Domains:")
        for i, domain in enumerate(strengths_weaknesses['strengths'], 1):
            stats = next((s for s in domain_stats if s.domain == domain), None)
            if stats:
                report.append(f"  {i}. {domain}: {stats.avg_quality} (success rate: {stats.success_rate})")
        report.append("")
        
        report.append("Weakest Domains:")
        for i, domain in enumerate(strengths_weaknesses['weaknesses'], 1):
            stats = next((s for s in domain_stats if s.domain == domain), None)
            if stats:
                report.append(f"  {i}. {domain}: {stats.avg_quality} (success rate: {stats.success_rate})")
        report.append("")
        
        # All domain details
        report.append("Detailed Domain Statistics:")
        report.append(f"{'Domain':<15} {'Queries':<10} {'Avg':<8} {'Min':<8} {'Max':<8} {'Success':<10} {'Trend':<10}")
        report.append("-" * 60)
        
        for stats in domain_stats:
            trend_str = f"+{stats.improvement_trend:.6f}" if stats.improvement_trend > 0 else f"{stats.improvement_trend:.6f}"
            report.append(
                f"{stats.domain:<15} "
                f"{stats.query_count:<10} "
                f"{stats.avg_quality:<8} "
                f"{stats.min_quality:<8} "
                f"{stats.max_quality:<8} "
                f"{stats.success_rate:<10} "
                f"{trend_str:<10}"
            )
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
