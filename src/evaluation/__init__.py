"""Evaluation module for SIRA.

Provides test suites, baseline comparison, trajectory analysis,
and domain profiling for comprehensive SIRA performance evaluation.
"""
from src.evaluation.test_suite import TestSuite, TestQuestion
from src.evaluation.baseline_comparator import BaselineComparator, ComparisonResult
from src.evaluation.trajectory_analyzer import TrajectoryAnalyzer, TrajectoryPoint
from src.evaluation.domain_profiler import DomainProfiler, DomainStats

__all__ = [
    "TestSuite",
    "TestQuestion",
    "BaselineComparator",
    "ComparisonResult",
    "TrajectoryAnalyzer",
    "TrajectoryPoint",
    "DomainProfiler",
    "DomainStats",
]
