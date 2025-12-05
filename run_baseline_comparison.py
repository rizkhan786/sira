#!/usr/bin/env python3
"""
Run SIRA vs Baseline LLM Comparison
===================================

This script compares SIRA (with patterns) against a baseline LLM (without patterns)
using the evaluation framework test suite.

Usage:
    python run_baseline_comparison.py --questions 10
"""
import asyncio
import argparse
from src.evaluation.test_suite import TestSuite
from src.evaluation.baseline_comparator import BaselineComparator
from src.core.reasoning_engine import ReasoningEngine
from src.llm.client import LLMClient
from src.quality.scorer import QualityScorer
from src.core.config import Config
from src.core.logging import get_logger

logger = get_logger(__name__)


async def run_comparison(num_questions: int = 10, domain: str = None):
    """Run SIRA vs baseline comparison.
    
    Args:
        num_questions: Number of test questions to compare
        domain: Optional domain filter (e.g., 'mathematics', 'coding')
    """
    print("="*60)
    print("SIRA vs Baseline LLM Comparison")
    print("="*60)
    
    # Initialize components
    print("\n1. Initializing SIRA components...")
    config = Config()
    reasoning_engine = ReasoningEngine(config)
    llm_client = LLMClient(config)
    quality_scorer = QualityScorer(config)
    
    # Load test suite
    print(f"\n2. Loading test suite from: /app/tests/evaluation/test_suites/")
    suite = TestSuite('/app/tests/evaluation/test_suites')
    total = suite.load_all_suites()
    print(f"   Loaded {total} questions across {len(suite.get_summary()['domains'])} domains")
    
    # Select test questions
    if domain:
        questions = suite.get_by_domain(domain, num_questions)
        print(f"\n3. Selected {len(questions)} questions from domain: {domain}")
    else:
        questions = suite.get_sample(num_questions)
        print(f"\n3. Selected {len(questions)} random questions")
    
    # Create comparator
    comparator = BaselineComparator(reasoning_engine, llm_client, quality_scorer)
    
    # Run comparison
    print(f"\n4. Running comparison (this may take several minutes)...")
    print(f"   Testing {len(questions)} questions...")
    
    results = await comparator.compare_batch(
        questions=questions,
        concurrent=1  # Sequential to avoid overwhelming the system
    )
    
    # Analyze results
    print(f"\n5. Analyzing results...")
    analysis = comparator.analyze_results(results)
    
    # Generate report
    print(f"\n6. Generating report...")
    report = comparator.generate_report(results, analysis)
    
    # Display results
    print("\n" + "="*60)
    print(report)
    
    # Save report to file
    report_file = f"data/comparison_report_{domain or 'all'}_{num_questions}q.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"\n📄 Report saved to: {report_file}")
    
    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS")
    print("="*60)
    
    if analysis['statistical_test']['is_significant']:
        print("✅ SIRA shows STATISTICALLY SIGNIFICANT improvement over baseline!")
        print(f"   - SIRA wins: {analysis['sira_wins']}/{analysis['sample_size']} ({analysis['win_rate']}%)")
        print(f"   - Quality improvement: {analysis['improvement_pct']}%")
        print(f"   - Statistical significance: p {analysis['statistical_test']['p_value']}")
    else:
        print("⚠️  No statistically significant difference detected")
        print(f"   - SIRA wins: {analysis['sira_wins']}/{analysis['sample_size']} ({analysis['win_rate']}%)")
        print(f"   - Quality improvement: {analysis['improvement_pct']}%")
        print("   - Consider testing with more questions for statistical power")
    
    print("\n" + "="*60)
    
    return analysis


def main():
    parser = argparse.ArgumentParser(
        description="Compare SIRA vs baseline LLM performance"
    )
    parser.add_argument(
        '--questions', '-n',
        type=int,
        default=10,
        help='Number of test questions (default: 10)'
    )
    parser.add_argument(
        '--domain', '-d',
        type=str,
        default=None,
        help='Domain filter (e.g., mathematics, coding, science)'
    )
    
    args = parser.parse_args()
    
    print(f"\n🚀 Starting SIRA vs Baseline comparison")
    print(f"   Questions: {args.questions}")
    print(f"   Domain: {args.domain or 'all domains'}")
    print(f"   Note: This will take ~30-60 seconds per question\n")
    
    asyncio.run(run_comparison(args.questions, args.domain))


if __name__ == '__main__':
    main()
