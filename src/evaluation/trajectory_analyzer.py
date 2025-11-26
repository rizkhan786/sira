"""Learning trajectory analyzer for SIRA.

Tracks quality improvements over time and analyzes learning curves
to demonstrate continuous improvement through pattern refinement.
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import math
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class TrajectoryPoint:
    """Single data point in learning trajectory."""
    query_number: int
    timestamp: datetime
    quality_score: float
    domain: Optional[str] = None
    session_id: Optional[str] = None


class TrajectoryAnalyzer:
    """Analyzes learning trajectories and improvement curves."""
    
    def __init__(self, db_connection):
        """Initialize analyzer.
        
        Args:
            db_connection: Database connection for querying historical data
        """
        self.db = db_connection
        logger.info("trajectory_analyzer_initialized")
    
    async def get_trajectory(
        self,
        min_queries: int = 1000,
        domain: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> List[TrajectoryPoint]:
        """Get quality trajectory over queries.
        
        Args:
            min_queries: Minimum number of queries to fetch
            domain: Optional domain filter
            session_id: Optional session filter
            
        Returns:
            List of trajectory points ordered by time
        """
        query = """
            SELECT 
                ROW_NUMBER() OVER (ORDER BY created_at) as query_num,
                created_at,
                quality_score,
                domain,
                session_id
            FROM query_logs
            WHERE quality_score IS NOT NULL
        """
        params = []
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        
        query += " ORDER BY created_at ASC LIMIT ?"
        params.append(min_queries)
        
        rows = await self.db.fetch_all(query, params)
        
        trajectory = [
            TrajectoryPoint(
                query_number=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                quality_score=row[2],
                domain=row[3],
                session_id=row[4]
            )
            for row in rows
        ]
        
        logger.info(
            "trajectory_fetched",
            point_count=len(trajectory),
            domain=domain,
            session_id=session_id
        )
        
        return trajectory
    
    def compute_linear_regression(
        self,
        trajectory: List[TrajectoryPoint]
    ) -> Dict[str, float]:
        """Compute linear regression for quality over query number.
        
        Uses least squares method to fit y = mx + b where:
        - x is query number
        - y is quality score
        
        Args:
            trajectory: List of trajectory points
            
        Returns:
            Dictionary with slope, intercept, R²
        """
        if len(trajectory) < 2:
            return {
                "slope": 0.0,
                "intercept": 0.0,
                "r_squared": 0.0,
                "error": "Insufficient data points"
            }
        
        n = len(trajectory)
        x = [p.query_number for p in trajectory]
        y = [p.quality_score for p in trajectory]
        
        # Calculate means
        x_mean = sum(x) / n
        y_mean = sum(y) / n
        
        # Calculate slope (m) and intercept (b)
        numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            slope = 0.0
        else:
            slope = numerator / denominator
        
        intercept = y_mean - slope * x_mean
        
        # Calculate R² (coefficient of determination)
        # R² = 1 - (SS_res / SS_tot)
        y_pred = [slope * x[i] + intercept for i in range(n)]
        ss_res = sum((y[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        
        if ss_tot == 0:
            r_squared = 0.0
        else:
            r_squared = 1 - (ss_res / ss_tot)
        
        return {
            "slope": round(slope, 6),
            "intercept": round(intercept, 3),
            "r_squared": round(r_squared, 3),
            "sample_size": n
        }
    
    def compute_moving_average(
        self,
        trajectory: List[TrajectoryPoint],
        window_size: int = 100
    ) -> List[Tuple[int, float]]:
        """Compute moving average of quality scores.
        
        Args:
            trajectory: List of trajectory points
            window_size: Size of moving average window
            
        Returns:
            List of (query_number, moving_avg) tuples
        """
        if len(trajectory) < window_size:
            window_size = len(trajectory)
        
        moving_avgs = []
        
        for i in range(window_size - 1, len(trajectory)):
            window = trajectory[i - window_size + 1 : i + 1]
            avg_quality = sum(p.quality_score for p in window) / window_size
            moving_avgs.append((trajectory[i].query_number, avg_quality))
        
        return moving_avgs
    
    def detect_improvement_phases(
        self,
        trajectory: List[TrajectoryPoint],
        segment_size: int = 250
    ) -> List[Dict[str, any]]:
        """Detect phases of improvement by analyzing trajectory segments.
        
        Divides trajectory into segments and computes regression for each
        to identify periods of rapid improvement vs plateaus.
        
        Args:
            trajectory: List of trajectory points
            segment_size: Size of each segment
            
        Returns:
            List of phase dictionaries with segment analysis
        """
        if len(trajectory) < segment_size:
            segment_size = len(trajectory)
        
        phases = []
        
        for i in range(0, len(trajectory), segment_size):
            segment = trajectory[i : i + segment_size]
            if len(segment) < 10:  # Skip tiny segments
                continue
            
            regression = self.compute_linear_regression(segment)
            
            # Classify phase
            if regression["slope"] > 0.0001:
                phase_type = "improvement"
            elif regression["slope"] < -0.0001:
                phase_type = "decline"
            else:
                phase_type = "plateau"
            
            avg_quality = sum(p.quality_score for p in segment) / len(segment)
            
            phase = {
                "segment_number": len(phases) + 1,
                "query_range": (segment[0].query_number, segment[-1].query_number),
                "query_count": len(segment),
                "phase_type": phase_type,
                "slope": regression["slope"],
                "r_squared": regression["r_squared"],
                "avg_quality": round(avg_quality, 3)
            }
            
            phases.append(phase)
        
        logger.info(
            "improvement_phases_detected",
            phase_count=len(phases),
            improvement_phases=sum(1 for p in phases if p["phase_type"] == "improvement")
        )
        
        return phases
    
    def analyze_trajectory(
        self,
        trajectory: List[TrajectoryPoint]
    ) -> Dict[str, any]:
        """Comprehensive trajectory analysis.
        
        Args:
            trajectory: List of trajectory points
            
        Returns:
            Dictionary with complete trajectory analysis
        """
        if not trajectory:
            return {"error": "No trajectory data"}
        
        # Overall regression
        regression = self.compute_linear_regression(trajectory)
        
        # Moving average
        moving_avg = self.compute_moving_average(trajectory, window_size=100)
        
        # Improvement phases
        phases = self.detect_improvement_phases(trajectory, segment_size=250)
        
        # Quality statistics
        qualities = [p.quality_score for p in trajectory]
        initial_quality = sum(qualities[:100]) / min(100, len(qualities))
        final_quality = sum(qualities[-100:]) / min(100, len(qualities))
        improvement = final_quality - initial_quality
        
        # Learning rate (slope interpretation)
        queries_to_improve_10pct = abs(0.1 / regression["slope"]) if regression["slope"] != 0 else float('inf')
        
        analysis = {
            "sample_size": len(trajectory),
            "query_range": (trajectory[0].query_number, trajectory[-1].query_number),
            "linear_regression": regression,
            "learning_curve": {
                "initial_avg_quality": round(initial_quality, 3),
                "final_avg_quality": round(final_quality, 3),
                "total_improvement": round(improvement, 3),
                "improvement_pct": round((improvement / initial_quality * 100) if initial_quality > 0 else 0, 2)
            },
            "learning_rate": {
                "slope": regression["slope"],
                "queries_for_10pct_improvement": round(queries_to_improve_10pct) if queries_to_improve_10pct != float('inf') else "N/A"
            },
            "phases": phases,
            "model_fit": {
                "r_squared": regression["r_squared"],
                "fit_quality": "excellent" if regression["r_squared"] > 0.7 else "good" if regression["r_squared"] > 0.5 else "moderate" if regression["r_squared"] > 0.3 else "poor"
            }
        }
        
        logger.info(
            "trajectory_analysis_complete",
            total_improvement=analysis["learning_curve"]["total_improvement"],
            r_squared=analysis["model_fit"]["r_squared"],
            fit_quality=analysis["model_fit"]["fit_quality"]
        )
        
        return analysis
    
    def generate_report(
        self,
        analysis: Dict[str, any]
    ) -> str:
        """Generate text report of trajectory analysis.
        
        Args:
            analysis: Trajectory analysis dictionary
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("Learning Trajectory Analysis Report")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Sample Size: {analysis['sample_size']} queries")
        report.append(f"Query Range: {analysis['query_range'][0]} - {analysis['query_range'][1]}")
        report.append("")
        
        curve = analysis['learning_curve']
        report.append("Learning Curve:")
        report.append(f"  Initial Average Quality: {curve['initial_avg_quality']}")
        report.append(f"  Final Average Quality:   {curve['final_avg_quality']}")
        report.append(f"  Total Improvement:       {curve['total_improvement']}")
        report.append(f"  Improvement Percentage:  {curve['improvement_pct']}%")
        report.append("")
        
        regression = analysis['linear_regression']
        report.append("Linear Regression (y = mx + b):")
        report.append(f"  Slope (m):     {regression['slope']}")
        report.append(f"  Intercept (b): {regression['intercept']}")
        report.append(f"  R² Score:      {regression['r_squared']}")
        report.append("")
        
        fit = analysis['model_fit']
        report.append(f"Model Fit Quality: {fit['fit_quality'].upper()} (R² = {fit['r_squared']})")
        
        if fit['r_squared'] > 0.7:
            report.append("✅ Strong linear learning trend detected (R² > 0.7)")
        elif fit['r_squared'] > 0.5:
            report.append("✅ Moderate learning trend detected (R² > 0.5)")
        else:
            report.append("⚠️  Weak linear trend - learning may be non-linear or noisy")
        
        report.append("")
        
        rate = analysis['learning_rate']
        report.append("Learning Rate:")
        report.append(f"  Slope: {rate['slope']} quality points per query")
        if rate['queries_for_10pct_improvement'] != "N/A":
            report.append(f"  Queries for 10% improvement: ~{rate['queries_for_10pct_improvement']}")
        report.append("")
        
        phases = analysis['phases']
        report.append(f"Improvement Phases: {len(phases)} detected")
        improvement_phases = [p for p in phases if p['phase_type'] == 'improvement']
        plateau_phases = [p for p in phases if p['phase_type'] == 'plateau']
        decline_phases = [p for p in phases if p['phase_type'] == 'decline']
        
        report.append(f"  Improvement: {len(improvement_phases)}")
        report.append(f"  Plateau:     {len(plateau_phases)}")
        report.append(f"  Decline:     {len(decline_phases)}")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
