#!/usr/bin/env python3
"""Quick test of DEL-035 evaluation framework."""
from src.evaluation.test_suite import TestSuite

# Test suite loading
suite = TestSuite('/app/tests/evaluation/test_suites')
total = suite.load_all_suites()
summary = suite.get_summary()

print('='*60)
print('DEL-035: SIRA Evaluation Framework - Test Results')
print('='*60)

print(f'\nTest Suite Summary:')
print(f'  Total questions: {summary["total_questions"]}')
print(f'  Total domains: {summary["total_domains"]}')

print('\nQuestions per domain:')
for domain, count in sorted(summary['domains'].items()):
    print(f'  {domain}: {count}')

print('\nDifficulty distribution:')
for diff, count in summary['difficulty_distribution'].items():
    print(f'  {diff}: {count}')

print(f'\nAC-079 Verification:')
print(f'  Target: 430+ questions (86% of 500)')
print(f'  Actual: {total} questions')
print(f'  Achievement: {total/430*100:.1f}% of target')
print(f'  Status: {"✅ PASSED" if total >= 430 else "⚠️  PARTIAL - " + str(total) + "/430"}')

print('\n' + '='*60)
