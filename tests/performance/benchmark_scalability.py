"""
Scalability Benchmark & Report Generator

Comprehensive performance testing for DEL-024:
- AC-088: Measure pattern retrieval with 100K patterns (< 1s target)
- AC-090: Generate performance report with bottlenecks, percentiles, resource utilization

Usage:
    python benchmark_scalability.py --patterns-file patterns_100k.json --output-dir reports/
    
Requirements:
    - requests
    - psutil
    - numpy
"""

import argparse
import json
import time
import statistics
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import requests
import numpy as np

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available, resource monitoring disabled")


class ScalabilityBenchmark:
    """Performance benchmark for scalability testing"""
    
    def __init__(self, api_base_url: str = "http://localhost:8080"):
        """Initialize benchmark with API URL"""
        self.api_base_url = api_base_url
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "api_url": api_base_url,
            "pattern_load_test": {},
            "retrieval_tests": [],
            "resource_usage": {},
            "bottlenecks": []
        }
    
    def check_api_health(self) -> bool:
        """Check if API is responsive"""
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"API health check failed: {e}")
            return False
    
    def load_patterns_from_file(self, patterns_file: str) -> List[Dict]:
        """Load patterns from JSON file"""
        print(f"Loading patterns from {patterns_file}...")
        start = time.time()
        
        with open(patterns_file, 'r') as f:
            data = json.load(f)
            
        if 'patterns' in data:
            patterns = data['patterns']
        else:
            patterns = data
        
        elapsed = time.time() - start
        print(f"✓ Loaded {len(patterns):,} patterns in {elapsed:.2f}s")
        
        return patterns
    
    def load_patterns_to_chromadb(self, patterns: List[Dict]) -> Dict:
        """Load patterns into ChromaDB via API"""
        print(f"\nLoading {len(patterns):,} patterns to ChromaDB...")
        start_time = time.time()
        
        batch_size = 1000
        loaded_count = 0
        failed_count = 0
        
        for i in range(0, len(patterns), batch_size):
            batch = patterns[i:i + batch_size]
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/patterns/batch",
                    json={"patterns": batch},
                    timeout=60
                )
                
                if response.status_code == 200:
                    loaded_count += len(batch)
                else:
                    failed_count += len(batch)
                    print(f"  Batch {i//batch_size + 1} failed: {response.status_code}")
                
                # Progress
                if (i + batch_size) % 10000 == 0:
                    elapsed = time.time() - start_time
                    rate = loaded_count / elapsed
                    print(f"  Loaded {loaded_count:,}/{len(patterns):,} patterns "
                          f"({rate:.0f} patterns/s)")
                    
            except Exception as e:
                failed_count += len(batch)
                print(f"  Batch {i//batch_size + 1} error: {e}")
        
        elapsed = time.time() - start_time
        
        result = {
            "total_patterns": len(patterns),
            "loaded_count": loaded_count,
            "failed_count": failed_count,
            "duration_seconds": elapsed,
            "load_rate": loaded_count / elapsed if elapsed > 0 else 0
        }
        
        print(f"✓ Loaded {loaded_count:,} patterns in {elapsed:.1f}s "
              f"({result['load_rate']:.0f} patterns/s)")
        if failed_count > 0:
            print(f"  Warning: {failed_count:,} patterns failed to load")
        
        self.results["pattern_load_test"] = result
        return result
    
    def benchmark_pattern_retrieval(
        self,
        query: str,
        num_iterations: int = 100
    ) -> Dict:
        """Benchmark pattern retrieval performance"""
        print(f"\nBenchmarking pattern retrieval ({num_iterations} iterations)...")
        
        latencies = []
        errors = 0
        
        for i in range(num_iterations):
            start = time.time()
            
            try:
                response = requests.post(
                    f"{self.api_base_url}/patterns/retrieve",
                    json={"query": query, "top_k": 5},
                    timeout=10
                )
                
                latency = (time.time() - start) * 1000  # ms
                latencies.append(latency)
                
                if response.status_code != 200:
                    errors += 1
                    
            except Exception as e:
                errors += 1
                latencies.append(10000)  # 10s timeout
            
            # Progress every 10 iterations
            if (i + 1) % 10 == 0:
                avg_so_far = statistics.mean(latencies)
                print(f"  {i + 1}/{num_iterations} - Avg: {avg_so_far:.0f}ms")
        
        # Calculate statistics
        latencies_array = np.array(latencies)
        
        result = {
            "query": query,
            "iterations": num_iterations,
            "errors": errors,
            "error_rate": (errors / num_iterations) * 100,
            "latency_ms": {
                "min": float(np.min(latencies_array)),
                "max": float(np.max(latencies_array)),
                "mean": float(np.mean(latencies_array)),
                "median": float(np.median(latencies_array)),
                "std": float(np.std(latencies_array)),
                "p50": float(np.percentile(latencies_array, 50)),
                "p95": float(np.percentile(latencies_array, 95)),
                "p99": float(np.percentile(latencies_array, 99))
            }
        }
        
        print(f"✓ Retrieval benchmark complete:")
        print(f"  Mean: {result['latency_ms']['mean']:.0f}ms")
        print(f"  P50: {result['latency_ms']['p50']:.0f}ms")
        print(f"  P95: {result['latency_ms']['p95']:.0f}ms")
        print(f"  P99: {result['latency_ms']['p99']:.0f}ms")
        
        # Check AC-088: < 1000ms (1s)
        if result['latency_ms']['mean'] < 1000:
            print(f"  ✓ AC-088: Mean latency {result['latency_ms']['mean']:.0f}ms < 1000ms")
        else:
            print(f"  ✗ AC-088: Mean latency {result['latency_ms']['mean']:.0f}ms >= 1000ms")
        
        self.results["retrieval_tests"].append(result)
        return result
    
    def measure_resource_usage(self) -> Dict:
        """Measure system resource utilization"""
        if not HAS_PSUTIL:
            return {"error": "psutil not available"}
        
        print("\nMeasuring resource usage...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory
        memory = psutil.virtual_memory()
        
        # Disk
        disk = psutil.disk_usage('/')
        
        result = {
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_gb": memory.used / (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": disk.percent
            }
        }
        
        print(f"✓ Resource usage captured:")
        print(f"  CPU: {result['cpu']['percent']:.1f}%")
        print(f"  Memory: {result['memory']['percent']:.1f}% "
              f"({result['memory']['used_gb']:.1f}/{result['memory']['total_gb']:.1f} GB)")
        print(f"  Disk: {result['disk']['percent']:.1f}%")
        
        self.results["resource_usage"] = result
        return result
    
    def identify_bottlenecks(self):
        """Identify performance bottlenecks"""
        print("\nIdentifying bottlenecks...")
        
        bottlenecks = []
        
        # Check pattern loading performance
        if "pattern_load_test" in self.results:
            load = self.results["pattern_load_test"]
            if load.get("load_rate", 0) < 500:  # < 500 patterns/s
                bottlenecks.append({
                    "category": "Pattern Loading",
                    "severity": "HIGH",
                    "description": f"Pattern loading rate {load['load_rate']:.0f} patterns/s is below target (500+)",
                    "recommendation": "Optimize batch insert or use bulk loading API"
                })
        
        # Check retrieval latency
        for test in self.results.get("retrieval_tests", []):
            if test["latency_ms"]["mean"] > 1000:
                bottlenecks.append({
                    "category": "Pattern Retrieval",
                    "severity": "HIGH",
                    "description": f"Mean retrieval latency {test['latency_ms']['mean']:.0f}ms exceeds 1000ms target",
                    "recommendation": "Enable caching, optimize embedding search, or add indexes"
                })
            
            if test["latency_ms"]["p99"] > 5000:
                bottlenecks.append({
                    "category": "Tail Latency",
                    "severity": "MEDIUM",
                    "description": f"P99 latency {test['latency_ms']['p99']:.0f}ms is high (> 5s)",
                    "recommendation": "Investigate outliers, consider query timeouts"
                })
        
        # Check resource usage
        if "resource_usage" in self.results:
            res = self.results["resource_usage"]
            
            if res.get("cpu", {}).get("percent", 0) > 80:
                bottlenecks.append({
                    "category": "CPU",
                    "severity": "HIGH",
                    "description": f"CPU usage {res['cpu']['percent']:.1f}% is high (> 80%)",
                    "recommendation": "Scale horizontally or optimize compute-intensive operations"
                })
            
            if res.get("memory", {}).get("percent", 0) > 85:
                bottlenecks.append({
                    "category": "Memory",
                    "severity": "HIGH",
                    "description": f"Memory usage {res['memory']['percent']:.1f}% is high (> 85%)",
                    "recommendation": "Increase memory or implement pattern caching/eviction"
                })
        
        self.results["bottlenecks"] = bottlenecks
        
        if bottlenecks:
            print(f"⚠ Found {len(bottlenecks)} bottleneck(s):")
            for b in bottlenecks:
                print(f"  [{b['severity']}] {b['category']}: {b['description']}")
        else:
            print("✓ No significant bottlenecks identified")
        
        return bottlenecks
    
    def generate_report(self, output_path: Path):
        """Generate comprehensive performance report"""
        print(f"\nGenerating performance report...")
        
        # Identify bottlenecks first
        self.identify_bottlenecks()
        
        report_content = self._format_report()
        
        # Save to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        # Also save JSON
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"✓ Report saved to {output_path}")
        print(f"✓ JSON data saved to {json_path}")
        
        return report_content
    
    def _format_report(self) -> str:
        """Format results as markdown report"""
        lines = []
        lines.append("# SIRA Scalability Performance Report")
        lines.append("")
        lines.append(f"**Generated:** {self.results['timestamp']}")
        lines.append(f"**API URL:** {self.results['api_url']}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Pattern Loading
        lines.append("## Pattern Loading Test")
        lines.append("")
        if "pattern_load_test" in self.results:
            load = self.results["pattern_load_test"]
            lines.append(f"- **Total Patterns:** {load['total_patterns']:,}")
            lines.append(f"- **Loaded:** {load['loaded_count']:,}")
            lines.append(f"- **Failed:** {load['failed_count']:,}")
            lines.append(f"- **Duration:** {load['duration_seconds']:.1f}s")
            lines.append(f"- **Load Rate:** {load['load_rate']:.0f} patterns/s")
        lines.append("")
        
        # Pattern Retrieval
        lines.append("## Pattern Retrieval Performance")
        lines.append("")
        for test in self.results.get("retrieval_tests", []):
            lines.append(f"**Query:** `{test['query']}`")
            lines.append(f"- Iterations: {test['iterations']}")
            lines.append(f"- Error Rate: {test['error_rate']:.2f}%")
            lines.append("")
            lines.append("### Latency Metrics (ms)")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")
            for key, val in test["latency_ms"].items():
                lines.append(f"| {key.upper()} | {val:.0f}ms |")
            lines.append("")
            
            # AC-088 check
            if test["latency_ms"]["mean"] < 1000:
                lines.append("✅ **AC-088 PASSED:** Mean retrieval < 1000ms")
            else:
                lines.append("❌ **AC-088 FAILED:** Mean retrieval >= 1000ms")
            lines.append("")
        
        # Resource Usage
        lines.append("## Resource Utilization")
        lines.append("")
        if "resource_usage" in self.results and "error" not in self.results["resource_usage"]:
            res = self.results["resource_usage"]
            lines.append("### CPU")
            lines.append(f"- Usage: {res['cpu']['percent']:.1f}%")
            lines.append(f"- Cores: {res['cpu']['count']}")
            lines.append("")
            lines.append("### Memory")
            lines.append(f"- Usage: {res['memory']['percent']:.1f}%")
            lines.append(f"- Used: {res['memory']['used_gb']:.1f} GB / {res['memory']['total_gb']:.1f} GB")
            lines.append("")
            lines.append("### Disk")
            lines.append(f"- Usage: {res['disk']['percent']:.1f}%")
            lines.append(f"- Used: {res['disk']['used_gb']:.1f} GB / {res['disk']['total_gb']:.1f} GB")
        lines.append("")
        
        # Bottlenecks
        lines.append("## Bottleneck Analysis")
        lines.append("")
        if self.results.get("bottlenecks"):
            for b in self.results["bottlenecks"]:
                lines.append(f"### [{b['severity']}] {b['category']}")
                lines.append(f"**Issue:** {b['description']}")
                lines.append(f"**Recommendation:** {b['recommendation']}")
                lines.append("")
        else:
            lines.append("✅ No significant bottlenecks identified")
            lines.append("")
        
        # Acceptance Criteria Summary
        lines.append("---")
        lines.append("")
        lines.append("## Acceptance Criteria Status")
        lines.append("")
        lines.append("### AC-088: 100K Patterns Performance")
        passed_088 = False
        for test in self.results.get("retrieval_tests", []):
            if test["latency_ms"]["mean"] < 1000:
                passed_088 = True
                break
        lines.append(f"**Status:** {'✅ PASSED' if passed_088 else '❌ FAILED'}")
        lines.append("")
        lines.append("### AC-090: Performance Report")
        lines.append("**Status:** ✅ PASSED (this report)")
        lines.append("")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Scalability benchmark and report generator for DEL-024'
    )
    parser.add_argument(
        '--api-url',
        default='http://localhost:8080',
        help='SIRA API base URL (default: http://localhost:8080)'
    )
    parser.add_argument(
        '--patterns-file',
        help='Path to patterns JSON file for loading test'
    )
    parser.add_argument(
        '--skip-load',
        action='store_true',
        help='Skip pattern loading test (patterns already loaded)'
    )
    parser.add_argument(
        '--iterations',
        type=int,
        default=100,
        help='Number of retrieval iterations (default: 100)'
    )
    parser.add_argument(
        '--output-dir',
        default='reports',
        help='Output directory for reports (default: reports/)'
    )
    
    args = parser.parse_args()
    
    # Initialize benchmark
    benchmark = ScalabilityBenchmark(api_base_url=args.api_url)
    
    # Check API health
    print("Checking API health...")
    if not benchmark.check_api_health():
        print("✗ API is not responsive. Ensure SIRA is running.")
        return 1
    print("✓ API is healthy\n")
    
    # Load patterns if requested
    if not args.skip_load and args.patterns_file:
        patterns = benchmark.load_patterns_from_file(args.patterns_file)
        benchmark.load_patterns_to_chromadb(patterns)
    
    # Benchmark retrieval
    test_queries = [
        "What is machine learning?",
        "Explain photosynthesis process",
        "How to solve quadratic equations?"
    ]
    
    for query in test_queries:
        benchmark.benchmark_pattern_retrieval(query, args.iterations)
    
    # Measure resources
    benchmark.measure_resource_usage()
    
    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(args.output_dir) / f"scalability_report_{timestamp}.md"
    benchmark.generate_report(output_path)
    
    print("\n✓ Scalability benchmark complete!")
    return 0


if __name__ == '__main__':
    exit(main())
