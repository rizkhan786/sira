"""Baseline comparator for A/B testing SIRA vs base LLM.

Compares SIRA performance against baseline (no patterns/refinement)
to demonstrate measurable improvement with statistical significance.
"""
from typing import List, Dict, Tuple
import asyncio
from dataclasses import dataclass
from src.evaluation.test_suite import TestQuestion
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ComparisonResult:
    """Result of comparing SIRA vs baseline on one question."""
    question_id: str
    question: str
    sira_response: str
    baseline_response: str
    sira_quality: float
    baseline_quality: float
    improvement: float


class BaselineComparator:
    """Compares SIRA performance vs baseline LLM."""
    
    def __init__(self, reasoning_engine, llm_client, quality_scorer):
        """Initialize comparator.
        
        Args:
            reasoning_engine: SIRA reasoning engine
            llm_client: Direct LLM client for baseline
            quality_scorer: Quality scoring module
        """
        self.reasoning_engine = reasoning_engine
        self.llm_client = llm_client
        self.quality_scorer = quality_scorer
        logger.info("baseline_comparator_initialized")
    
    async def compare_single(
        self,
        question: TestQuestion
    ) -> ComparisonResult:
        """Compare SIRA vs baseline on a single question.
        
        Args:
            question: Test question to evaluate
            
        Returns:
            ComparisonResult with both responses and scores
        """
        # Get SIRA response (with patterns and refinement)
        sira_result = await self.reasoning_engine.process_query(
            query=question.question,
            session_id="baseline_comparison"
        )
        sira_response = sira_result["response"]
        sira_quality = sira_result["quality_score"]
        
        # Get baseline response (direct LLM, no patterns/refinement)
        baseline_prompt = f"Answer the following question concisely:\n\n{question.question}"
        baseline_result = await self.llm_client.generate(
            prompt=baseline_prompt,
            max_tokens=500
        )
        baseline_response = baseline_result["content"]
        
        # Score baseline response
        baseline_quality_result = await self.quality_scorer.score_response(
            query=question.question,
            response=baseline_response
        )
        baseline_quality = baseline_quality_result["total_score"]
        
        improvement = sira_quality - baseline_quality
        
        result = ComparisonResult(
            question_id=question.id,
            question=question.question,
            sira_response=sira_response,
            baseline_response=baseline_response,
            sira_quality=sira_quality,
            baseline_quality=baseline_quality,
            improvement=improvement
        )
        
        logger.info(
            "comparison_complete",
            question_id=question.id,
            sira_quality=round(sira_quality, 3),
            baseline_quality=round(baseline_quality, 3),
            improvement=round(improvement, 3)
        )
        
        return result
    
    async def compare_batch(
        self,
        questions: List[TestQuestion],
        concurrent: int = 1
    ) -> List[ComparisonResult]:
        """Compare SIRA vs baseline on a batch of questions.
        
        Args:
            questions: List of test questions
            concurrent: Number of concurrent comparisons (default: 1 for sequential)
            
        Returns:
            List of comparison results
        """
        logger.info(
            "batch_comparison_started",
            question_count=len(questions),
            concurrent=concurrent
        )
        
        if concurrent == 1:
            # Sequential processing
            results = []
            for i, question in enumerate(questions):
                logger.info(f"processing_question {i+1}/{len(questions)}")
                result = await self.compare_single(question)
                results.append(result)
        else:
            # Concurrent processing with semaphore
            semaphore = asyncio.Semaphore(concurrent)
            
            async def compare_with_limit(q):
                async with semaphore:
                    return await self.compare_single(q)
            
            results = await asyncio.gather(*[compare_with_limit(q) for q in questions])
        
        logger.info("batch_comparison_complete", total=len(results))
        
        return results
    
    def analyze_results(
        self,
        results: List[ComparisonResult]
    ) -> Dict[str, any]:
        """Analyze comparison results with statistical tests.
        
        Args:
            results: List of comparison results
            
        Returns:
            Dictionary with statistical analysis
        """
        if not results:
            return {"error": "No results to analyze"}
        
        sira_scores = [r.sira_quality for r in results]
        baseline_scores = [r.baseline_quality for r in results]
        improvements = [r.improvement for r in results]
        
        # Basic statistics
        n = len(results)
        avg_sira = sum(sira_scores) / n
        avg_baseline = sum(baseline_scores) / n
        avg_improvement = sum(improvements) / n
        
        # Count wins/losses
        sira_wins = sum(1 for i in improvements if i > 0)
        baseline_wins = sum(1 for i in improvements if i < 0)
        ties = sum(1 for i in improvements if i == 0)
        
        # Paired t-test for statistical significance
        import math
        
        # Calculate standard deviation of improvements
        variance = sum((i - avg_improvement) ** 2 for i in improvements) / (n - 1)
        std_dev = math.sqrt(variance)
        
        # t-statistic for paired samples
        if std_dev > 0:
            t_statistic = (avg_improvement * math.sqrt(n)) / std_dev
            
            # Approximate p-value (two-tailed)
            # For simplicity, using rule of thumb: |t| > 2 implies p < 0.05
            degrees_of_freedom = n - 1
            is_significant = abs(t_statistic) > 2.0  # Rough approximation
            p_value_estimate = "< 0.05" if is_significant else "> 0.05"
        else:
            t_statistic = 0.0
            is_significant = False
            p_value_estimate = "N/A"
        
        analysis = {
            "sample_size": n,
            "sira_avg_quality": round(avg_sira, 3),
            "baseline_avg_quality": round(avg_baseline, 3),
            "avg_improvement": round(avg_improvement, 3),
            "improvement_pct": round((avg_improvement / avg_baseline * 100) if avg_baseline > 0 else 0, 2),
            "sira_wins": sira_wins,
            "baseline_wins": baseline_wins,
            "ties": ties,
            "win_rate": round(sira_wins / n * 100, 1),
            "statistical_test": {
                "test_type": "paired_t_test",
                "t_statistic": round(t_statistic, 3),
                "degrees_of_freedom": degrees_of_freedom,
                "p_value": p_value_estimate,
                "is_significant": is_significant,
                "confidence": "95%"
            }
        }
        
        logger.info(
            "statistical_analysis_complete",
            avg_improvement=analysis["avg_improvement"],
            win_rate=analysis["win_rate"],
            is_significant=is_significant
        )
        
        return analysis
    
    def generate_report(
        self,
        results: List[ComparisonResult],
        analysis: Dict[str, any]
    ) -> str:
        """Generate a text report of the comparison.
        
        Args:
            results: List of comparison results
            analysis: Statistical analysis
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("SIRA vs Baseline LLM Comparison Report")
        report.append("=" * 60)
        report.append("")
        
        report.append(f"Sample Size: {analysis['sample_size']} questions")
        report.append("")
        
        report.append("Performance Metrics:")
        report.append(f"  SIRA Average Quality:     {analysis['sira_avg_quality']}")
        report.append(f"  Baseline Average Quality: {analysis['baseline_avg_quality']}")
        report.append(f"  Average Improvement:      {analysis['avg_improvement']}")
        report.append(f"  Improvement Percentage:   {analysis['improvement_pct']}%")
        report.append("")
        
        report.append("Head-to-Head Results:")
        report.append(f"  SIRA Wins:     {analysis['sira_wins']} ({analysis['win_rate']}%)")
        report.append(f"  Baseline Wins: {analysis['baseline_wins']}")
        report.append(f"  Ties:          {analysis['ties']}")
        report.append("")
        
        stats = analysis['statistical_test']
        report.append("Statistical Significance:")
        report.append(f"  Test: {stats['test_type']}")
        report.append(f"  t-statistic: {stats['t_statistic']}")
        report.append(f"  p-value: {stats['p_value']}")
        report.append(f"  Significant at {stats['confidence']}: {'YES' if stats['is_significant'] else 'NO'}")
        report.append("")
        
        if stats['is_significant']:
            report.append("✅ CONCLUSION: SIRA shows statistically significant improvement")
            report.append("   over baseline LLM (p < 0.05)")
        else:
            report.append("⚠️  CONCLUSION: No statistically significant difference detected")
            report.append("   (more data may be needed)")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)
