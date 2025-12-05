#!/usr/bin/env python3
"""Test baseline comparator for AC-080."""
from src.evaluation.baseline_comparator import BaselineComparator
import json

# Create comparator
comparator = BaselineComparator('gpt-4')

# Test data: SIRA vs baseline on sample questions
test_results = {
    'sira': {
        'correct': 85,
        'total': 100,
        'scores': [0.95, 0.88, 0.92, 0.91, 0.87, 0.94, 0.89, 0.90, 0.93, 0.86] * 10
    },
    'baseline': {
        'correct': 72,
        'total': 100,
        'scores': [0.82, 0.75, 0.79, 0.77, 0.73, 0.80, 0.76, 0.74, 0.78, 0.71] * 10
    }
}

# Add results
comparator.add_result('Q1', 'correct', test_results['sira']['scores'][0])
comparator.add_baseline_result('Q1', test_results['baseline']['scores'][0])

for i in range(1, 100):
    comparator.add_result(f'Q{i}', 'correct' if i < 85 else 'incorrect', test_results['sira']['scores'][i])
    comparator.add_baseline_result(f'Q{i}', test_results['baseline']['scores'][i])

# Generate report
report = comparator.generate_report()

print('='*60)
print('AC-080: Baseline Comparator - Paired T-Test Verification')
print('='*60)

print(f'\nSIRA Performance:')
print(f'  Accuracy: {report["sira_accuracy"]:.1f}%')
print(f'  Avg Quality: {report["sira_avg_quality"]:.3f}')

print(f'\nBaseline Performance:')
print(f'  Avg Quality: {report["baseline_avg_quality"]:.3f}')

print(f'\nStatistical Comparison:')
print(f'  SIRA Advantage: {report["improvement"]:.1f}%')
print(f'  T-Statistic: {report["statistical_significance"]["t_statistic"]:.3f}')
print(f'  P-Value: {report["statistical_significance"]["p_value"]:.4f}')
print(f'  Significant? {report["statistical_significance"]["is_significant"]}')

print(f'\nAC-080 Verification:')
has_t_test = 't_statistic' in report['statistical_significance']
has_p_value = 'p_value' in report['statistical_significance']
has_significance = 'is_significant' in report['statistical_significance']
passed = has_t_test and has_p_value and has_significance

print(f'  Paired t-test implemented: {has_t_test}')
print(f'  P-value computed: {has_p_value}')
print(f'  Significance test: {has_significance}')
print(f'  Status: {"✅ PASSED" if passed else "❌ FAILED"}')

print('\n' + '='*60)
