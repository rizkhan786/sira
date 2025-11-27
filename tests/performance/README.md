# Performance & Scalability Testing

Performance testing tools for DEL-024 (Scalability Testing) and DEL-021 (Performance Optimization).

## Test Components

### 1. Pattern Data Generator (`generate_patterns.py`)

Generates synthetic patterns with embeddings for scalability testing.

```bash
# Generate 100K patterns
python generate_patterns.py --count 100000 --output patterns_100k.json --summary

# Generate smaller test set
python generate_patterns.py --count 1000 --output patterns_1k.json

# Generate in JSONL format
python generate_patterns.py --count 10000 --output patterns_10k.jsonl --format jsonl
```

**Features:**
- Generates realistic patterns across 15 domains
- 768-dimensional normalized embeddings
- Reproducible (fixed random seed)
- Progress reporting
- Summary statistics

### 2. Locust Load Test (`load_test.py`)

Tests concurrent user performance with realistic API load.

```bash
# Install dependencies
pip install locust

# Run with web UI
locust -f load_test.py --host=http://localhost:8080

# Run headless (for CI/CD)
locust -f load_test.py --host=http://localhost:8080 \
  --users 50 --spawn-rate 5 --run-time 5m --headless

# Light load test
locust -f load_test.py --host=http://localhost:8080 \
  --users 10 --spawn-rate 2 --run-time 2m --headless

# Stress test
locust -f load_test.py --host=http://localhost:8080 \
  --users 100 --spawn-rate 10 --run-time 5m --headless
```

**Test Scenarios:**
- **Light Load:** 10 users, 2m
- **Medium Load:** 25 users, 3m
- **Heavy Load:** 50 users, 5m (AC-089 requirement)
- **Stress Test:** 100 users, 5m

**Tasks:**
- Submit queries (70% of requests)
- Get metrics summary (20%)
- Get core metrics (10%)

**AC-089 Validation:**
- Error rate must be < 5% with 50 concurrent users

### 3. Scalability Benchmark (`benchmark_scalability.py`)

Comprehensive performance testing and report generation.

```bash
# Install dependencies
pip install requests psutil numpy

# Full benchmark with pattern loading
python benchmark_scalability.py \
  --api-url http://localhost:8080 \
  --patterns-file patterns_100k.json \
  --iterations 100 \
  --output-dir reports/

# Skip pattern loading (if already loaded)
python benchmark_scalability.py \
  --api-url http://localhost:8080 \
  --skip-load \
  --iterations 100 \
  --output-dir reports/

# Quick test
python benchmark_scalability.py \
  --patterns-file patterns_1k.json \
  --iterations 20
```

**Features:**
- Pattern loading performance measurement
- Retrieval latency benchmarking with percentiles (P50, P95, P99)
- Resource utilization monitoring (CPU, Memory, Disk)
- Bottleneck identification
- Automated AC validation (AC-088, AC-090)
- Markdown + JSON report generation

## Acceptance Criteria Testing

### AC-088: 100K Patterns Performance
**Requirement:** System handles 100K patterns with retrieval < 1s per query

**Test:**
```bash
# Generate 100K patterns
python generate_patterns.py --count 100000 --output patterns_100k.json

# Load and benchmark
python benchmark_scalability.py \
  --patterns-file patterns_100k.json \
  --iterations 100 \
  --output-dir reports/
```

**Pass Criteria:**
- Mean retrieval latency < 1000ms
- Reported in benchmark output and report

### AC-089: Concurrent Users
**Requirement:** 50 concurrent users submit queries with < 5% error rate

**Test:**
```bash
# Run load test with 50 users
locust -f load_test.py --host=http://localhost:8080 \
  --users 50 --spawn-rate 5 --run-time 5m --headless
```

**Pass Criteria:**
- Error rate < 5%
- Test summary shows AC-089 PASSED

### AC-090: Performance Report
**Requirement:** Report documents bottlenecks, latency percentiles, resource utilization

**Test:**
```bash
# Generate report
python benchmark_scalability.py --skip-load --iterations 100 --output-dir reports/
```

**Pass Criteria:**
- Report contains:
  - Pattern loading metrics
  - Latency percentiles (P50, P95, P99)
  - Resource utilization (CPU, Memory, Disk)
  - Bottleneck analysis with recommendations
  - AC validation status

## Output Files

### Benchmark Reports
- `reports/scalability_report_YYYYMMDD_HHMMSS.md` - Human-readable markdown report
- `reports/scalability_report_YYYYMMDD_HHMMSS.json` - Machine-readable data

### Locust Reports
- Console output with summary statistics
- Optional CSV export (if using `--csv` flag)

## Testing Workflow

### Full Scalability Test Suite

```bash
# 1. Generate test data
python generate_patterns.py --count 100000 --output data/patterns_100k.json --summary

# 2. Run scalability benchmark (AC-088, AC-090)
python benchmark_scalability.py \
  --patterns-file data/patterns_100k.json \
  --iterations 100 \
  --output-dir reports/

# 3. Run concurrent load test (AC-089)
locust -f load_test.py --host=http://localhost:8080 \
  --users 50 --spawn-rate 5 --run-time 5m --headless

# 4. Review reports
cat reports/scalability_report_*.md
```

### Quick Smoke Test

```bash
# Generate small test set
python generate_patterns.py --count 1000 --output data/patterns_1k.json

# Quick benchmark
python benchmark_scalability.py \
  --patterns-file data/patterns_1k.json \
  --iterations 20 \
  --output-dir reports/

# Quick load test
locust -f load_test.py --host=http://localhost:8080 \
  --users 10 --spawn-rate 2 --run-time 1m --headless
```

## Troubleshooting

### API Not Responsive
```bash
# Check if SIRA is running
curl http://localhost:8080/health

# Check Docker containers
docker-compose ps

# Restart if needed
docker-compose restart sira-api
```

### Pattern Loading Fails
- Check API batch endpoint exists: `/patterns/batch`
- Reduce batch size in `benchmark_scalability.py` (default: 1000)
- Check available memory (100K patterns ~800MB)

### High Error Rates
- Check API logs for errors
- Verify database connections
- Monitor resource usage (may need more CPU/memory)
- Reduce concurrent users

### Slow Performance
- Enable Redis caching (DEL-021)
- Check ChromaDB configuration
- Monitor disk I/O
- Review bottleneck analysis in report

## Performance Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Pattern Retrieval (100K patterns) | < 1s | TBD | AC-088 |
| Concurrent Users (50 users) | < 5% error | TBD | AC-089 |
| Load Rate | > 500 patterns/s | TBD | - |
| CPU Usage | < 80% | TBD | - |
| Memory Usage | < 85% | TBD | - |

## Dependencies

```bash
pip install locust requests psutil numpy
```

## CI/CD Integration

```yaml
# Example GitHub Actions workflow
- name: Scalability Tests
  run: |
    # Generate test data
    python tests/performance/generate_patterns.py --count 10000 --output patterns.json
    
    # Run benchmark
    python tests/performance/benchmark_scalability.py --patterns-file patterns.json
    
    # Run load test
    locust -f tests/performance/load_test.py --host=http://localhost:8080 \
      --users 25 --spawn-rate 5 --run-time 2m --headless
```

## References

- DEL-024: Scalability Testing
- DEL-021: Performance Optimization
- AC-088, AC-089, AC-090: Acceptance Criteria
- Sprint 4 Scope Document
