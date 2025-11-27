"""
Pattern Data Generator for Scalability Testing

Generates large volumes of synthetic patterns with embeddings for load testing.
Supports generating 100K+ patterns for DEL-024 scalability testing.

Usage:
    python generate_patterns.py --count 100000 --output patterns_100k.json

Requirements:
    - numpy
    - faker (for realistic content generation)
"""

import argparse
import json
import random
import time
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import numpy as np


class PatternGenerator:
    """Generates synthetic patterns with realistic structure"""
    
    DOMAINS = [
        'math', 'science', 'history', 'geography', 'coding',
        'reasoning', 'language', 'general', 'physics', 'chemistry',
        'biology', 'literature', 'philosophy', 'economics', 'psychology'
    ]
    
    PATTERN_TEMPLATES = [
        'Break down the problem into smaller steps',
        'Use {domain}-specific knowledge to analyze',
        'Consider multiple perspectives on the issue',
        'Apply systematic reasoning to solve',
        'Look for patterns and relationships',
        'Verify assumptions before proceeding',
        'Use analogies from {domain} domain',
        'Check for edge cases and exceptions',
        'Simplify the complex problem',
        'Build incrementally from basic concepts'
    ]
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility"""
        random.seed(seed)
        np.random.seed(seed)
        self.pattern_count = 0
        
    def generate_embedding(self, dimension: int = 768) -> List[float]:
        """Generate normalized random embedding vector"""
        # Generate random vector
        embedding = np.random.randn(dimension)
        # Normalize to unit length for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.tolist()
    
    def generate_pattern(self, pattern_id: int) -> Dict:
        """Generate a single synthetic pattern"""
        domain = random.choice(self.DOMAINS)
        template = random.choice(self.PATTERN_TEMPLATES)
        content = template.replace('{domain}', domain)
        
        # Generate realistic metadata
        created_days_ago = random.randint(0, 365)
        created_at = (datetime.now() - timedelta(days=created_days_ago)).isoformat()
        
        pattern = {
            'id': f'pat-{pattern_id:08d}',
            'name': f'{domain}-pattern-{pattern_id % 1000}',
            'domain': domain,
            'content': content,
            'embedding': self.generate_embedding(),
            'quality': round(random.uniform(0.5, 0.95), 3),
            'usage_count': random.randint(0, 100),
            'created_at': created_at,
            'metadata': {
                'source': 'synthetic',
                'version': '1.0',
                'validated': random.choice([True, False])
            }
        }
        
        self.pattern_count += 1
        return pattern
    
    def generate_batch(self, count: int, batch_size: int = 1000) -> List[Dict]:
        """Generate patterns in batches with progress reporting"""
        patterns = []
        
        print(f"Generating {count:,} patterns...")
        start_time = time.time()
        
        for i in range(count):
            patterns.append(self.generate_pattern(i))
            
            # Progress reporting
            if (i + 1) % batch_size == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                remaining = (count - i - 1) / rate if rate > 0 else 0
                print(f"  Generated {i + 1:,}/{count:,} patterns "
                      f"({rate:.0f} patterns/s, "
                      f"~{remaining:.0f}s remaining)")
        
        elapsed = time.time() - start_time
        print(f"✓ Generated {count:,} patterns in {elapsed:.1f}s "
              f"({count/elapsed:.0f} patterns/s)")
        
        return patterns
    
    def save_to_json(self, patterns: List[Dict], output_path: Path):
        """Save patterns to JSON file"""
        print(f"Saving patterns to {output_path}...")
        start_time = time.time()
        
        with open(output_path, 'w') as f:
            json.dump({
                'patterns': patterns,
                'metadata': {
                    'count': len(patterns),
                    'generated_at': datetime.now().isoformat(),
                    'generator_version': '1.0'
                }
            }, f, indent=2)
        
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        elapsed = time.time() - start_time
        print(f"✓ Saved to {output_path} ({file_size_mb:.1f} MB) in {elapsed:.1f}s")
    
    def save_to_jsonl(self, patterns: List[Dict], output_path: Path):
        """Save patterns to JSONL file (one pattern per line)"""
        print(f"Saving patterns to {output_path} (JSONL format)...")
        start_time = time.time()
        
        with open(output_path, 'w') as f:
            for pattern in patterns:
                f.write(json.dumps(pattern) + '\n')
        
        file_size_mb = output_path.stat().st_size / (1024 * 1024)
        elapsed = time.time() - start_time
        print(f"✓ Saved to {output_path} ({file_size_mb:.1f} MB) in {elapsed:.1f}s")
    
    def generate_summary(self, patterns: List[Dict]) -> Dict:
        """Generate summary statistics for pattern set"""
        domains = {}
        total_quality = 0
        total_usage = 0
        
        for p in patterns:
            domain = p['domain']
            domains[domain] = domains.get(domain, 0) + 1
            total_quality += p['quality']
            total_usage += p['usage_count']
        
        return {
            'total_patterns': len(patterns),
            'unique_domains': len(domains),
            'domain_distribution': domains,
            'avg_quality': round(total_quality / len(patterns), 3),
            'total_usage': total_usage,
            'avg_usage': round(total_usage / len(patterns), 1)
        }


def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic patterns for scalability testing'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=100000,
        help='Number of patterns to generate (default: 100000)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='patterns_100k.json',
        help='Output file path (default: patterns_100k.json)'
    )
    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'jsonl'],
        default='json',
        help='Output format: json or jsonl (default: json)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Print summary statistics after generation'
    )
    
    args = parser.parse_args()
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Generate patterns
    generator = PatternGenerator(seed=args.seed)
    patterns = generator.generate_batch(args.count)
    
    # Save to file
    if args.format == 'jsonl':
        generator.save_to_jsonl(patterns, output_path)
    else:
        generator.save_to_json(patterns, output_path)
    
    # Print summary if requested
    if args.summary:
        print("\nPattern Summary:")
        summary = generator.generate_summary(patterns)
        for key, value in summary.items():
            if key == 'domain_distribution':
                print(f"  {key}:")
                for domain, count in sorted(value.items()):
                    print(f"    {domain}: {count:,}")
            else:
                print(f"  {key}: {value:,}" if isinstance(value, int) else f"  {key}: {value}")
    
    print("\n✓ Pattern generation complete!")


if __name__ == '__main__':
    main()
