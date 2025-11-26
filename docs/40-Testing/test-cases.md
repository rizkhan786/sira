# Test Cases - SIRA

**Last Updated:** 2025-11-26  
**Phase:** 2 (Enhancement)  
**Total Test Cases:** 90 (1 per AC)

## Format
- **ID:** TC-### (maps 1:1 to AC-###)
- **Acceptance Criterion:** Linked AC-###
- **Test Type:** Unit / Integration / E2E / Performance
- **Steps:** Test execution steps
- **Expected Result:** What should happen
- **Status:** Not Run / Pass / Fail / Blocked

---

## Sprint 1 Test Cases (TC-001 through TC-033, TC-067 through TC-069)

### TC-001: Valid Query Accepted
**AC:** AC-001 | **Type:** Integration  
**Steps:**  
1. Start SIRA API container
2. POST to /query with `{"query": "What is 2+2?", "session_id": "test-001"}`
3. Verify 200 response
4. Check response contains `answer` and `reasoning_trace` fields

**Expected:** 200 OK with complete response structure  
**Status:** Not Run

---

### TC-002: Invalid Query Rejected
**AC:** AC-002 | **Type:** Integration  
**Steps:**  
1. POST to /query with empty query: `{"query": ""}`
2. POST with oversized query (>10000 chars)
3. POST with malformed JSON

**Expected:** 400 Bad Request with error message for each case  
**Status:** Not Run

---

### TC-003: Query Metadata Persisted
**AC:** AC-003 | **Type:** Integration  
**Steps:**  
1. POST query with session_id "test-003"
2. Query PostgreSQL: `SELECT * FROM queries WHERE session_id = 'test-003'`
3. Verify query_text, timestamp, session_id present

**Expected:** Query record in database with correct metadata  
**Status:** Not Run

---

### TC-004: Multi-Step Reasoning Generated
**AC:** AC-004 | **Type:** Integration  
**Steps:**  
1. POST query: "Explain why the sky is blue"
2. Parse reasoning_trace from response
3. Count steps

**Expected:** At least 2 reasoning steps in trace  
**Status:** Not Run

---

### TC-005: Reasoning Step Structure Valid
**AC:** AC-005 | **Type:** Integration  
**Steps:**  
1. POST query and capture reasoning_trace
2. For each step, verify fields: step_number, description, reasoning, dependencies
3. Check dependencies reference valid prior step numbers

**Expected:** All steps have required fields and valid dependencies  
**Status:** Not Run

---

### TC-006: Response Time Within Limits
**AC:** AC-006 | **Type:** Performance  
**Steps:**  
1. Configure simple CoT reasoning (no tools)
2. POST query with timer
3. Measure response time

**Expected:** Response time <10s for simple query  
**Status:** Not Run

---

*[TC-007 through TC-033 follow same pattern for Sprint 1 deliverables]*

### TC-025: Auto Session Creation
**AC:** AC-025 | **Type:** Integration  
**Steps:**  
1. POST query without session_id parameter
2. Check response for auto-generated session_id
3. Verify session created in database

**Expected:** Session auto-created with UUID  
**Status:** Not Run

---

### TC-031: All API Endpoints Functional
**AC:** AC-031 | **Type:** Integration  
**Steps:**  
1. POST /query - verify 200
2. GET /session/{id} - verify 200
3. GET /patterns - verify 200
4. GET /metrics - verify 200

**Expected:** All endpoints return successful responses  
**Status:** Not Run

---

### TC-043: Docker Compose Build Success
**AC:** AC-043 | **Type:** Integration  
**Steps:**  
1. Clean Docker environment (prune volumes, images)
2. Run: `docker-compose up --build`
3. Verify all containers start (sira-api, postgres, chromadb, sira-llm)
4. Check container logs for errors

**Expected:** All services running, no startup errors  
**Status:** Not Run

---

### TC-067: Ollama HTTP API Accessible
**AC:** AC-067 | **Type:** Integration  
**Steps:**  
1. Start docker-compose (all containers)
2. Wait for sira-llm container to be healthy
3. Run: `curl http://localhost:11434/v1/models`
4. Verify JSON response with model list

**Expected:** Valid model list returned from Ollama API  
**Status:** Not Run

---

### TC-068: LLM Model Downloaded
**AC:** AC-068 | **Type:** Integration  
**Steps:**  
1. Check /v1/models endpoint for available models
2. POST to /v1/chat/completions with test prompt
3. Verify completion generated

**Expected:** At least one model (llama3:8b or qwen2.5:7b) available and functional  
**Status:** Not Run

---

### TC-069: LLM Container Defined
**AC:** AC-069 | **Type:** Integration  
**Steps:**  
1. Inspect docker-compose.yml for sira-llm service
2. Run: `docker ps` and verify sira-llm container running
3. Check container health status
4. Verify container is on sira_network

**Expected:** sira-llm container running and healthy in correct network  
**Status:** Not Run

---

## Sprint 2 Test Cases (TC-034 through TC-051)

### TC-007: Quality Score Assignment
**AC:** AC-007 | **Type:** Integration  
**Steps:**  
1. POST query
2. Inspect each reasoning step in trace
3. Verify `quality_score` field present (float 0-1)
4. Verify `confidence` field present

**Expected:** All steps have valid quality_score and confidence  
**Status:** Not Run

---

### TC-010: Pattern Extraction Triggered
**AC:** AC-010 | **Type:** Integration  
**Steps:**  
1. POST query that succeeds with confidence >0.7
2. Monitor logs for pattern extraction message
3. Check pattern_metadata table for new entry

**Expected:** Pattern extracted and logged  
**Status:** Not Run

---

### TC-013: Pattern Stored in ChromaDB
**AC:** AC-013 | **Type:** Integration  
**Steps:**  
1. Trigger pattern extraction (successful query)
2. Query ChromaDB collection `reasoning_patterns`
3. Verify pattern count increased
4. Check pattern has embedding vector

**Expected:** Pattern in ChromaDB with embedding  
**Status:** Not Run

---

### TC-016: Pattern Retrieval Works
**AC:** AC-016 | **Type:** Integration  
**Steps:**  
1. Seed ChromaDB with 5 known patterns
2. POST query similar to one of the patterns
3. Check reasoning_trace for pattern_ids_used
4. Verify correct pattern retrieved (top-k=5)

**Expected:** Similar pattern retrieved and used  
**Status:** Not Run

---

### TC-063: Type Hints Present
**AC:** AC-063 | **Type:** Unit  
**Steps:**  
1. Run `mypy src/` in container
2. Check for type errors
3. Verify all public functions have type hints

**Expected:** mypy passes with no errors  
**Status:** Not Run

---

### TC-065: LLM Retry Logic
**AC:** AC-065 | **Type:** Integration  
**Steps:**  
1. Simulate local LLM runtime HTTP 500 errors (e.g., temporary failure handler)
2. POST query
3. Monitor logs for retry attempts (should see 3 attempts)
4. Verify exponential backoff timing

**Expected:** 3 retry attempts before final failure  
**Status:** Not Run

---

## Sprint 3 Test Cases (TC-052 through TC-063)

### TC-019: Pattern Application
**AC:** AC-019 | **Type:** Integration  
**Steps:**  
1. Store pattern for "mathematical word problems"
2. POST query: "If Alice has 5 apples..."
3. Compare reasoning with/without pattern available
4. Verify pattern influenced reasoning steps

**Expected:** Reasoning different when pattern available  
**Status:** Not Run

---

### TC-022: Multiple Iterations Performed
**AC:** AC-022 | **Type:** Integration  
**Steps:**  
1. Configure max_iterations=3
2. POST query with deliberately low initial confidence
3. Monitor logs for iteration count
4. Verify up to 3 passes attempted

**Expected:** Multiple iterations performed (up to 3)  
**Status:** Not Run

---

### TC-028: Metrics Captured
**AC:** AC-028 | **Type:** Integration  
**Steps:**  
1. POST query
2. Query metrics table: `SELECT * FROM metrics WHERE query_id = ?`
3. Verify fields: pattern_reuse_count, reasoning_depth, response_time_ms, llm_calls

**Expected:** All metric fields populated  
**Status:** Not Run

---

### TC-046: Episode Logs Written
**AC:** AC-046 | **Type:** Integration  
**Steps:**  
1. POST query
2. Check file exists: `/data/logs/run_{id}/episodes.jsonl`
3. Parse JSON, verify format matches schema
4. Verify fields: episode_id, timestamp, config, trace, result

**Expected:** JSONL file with valid episode format  
**Status:** Not Run

---

### TC-047: MATLAB Config Consumed
**AC:** AC-047 | **Type:** Integration  
**Steps:**  
1. Place tuned config file: `/data/config/sira_tuned_test.json`
2. Set config with max_depth=5 (different from default)
3. POST query
4. Verify reasoning uses max_depth=5

**Expected:** Config parameters applied from MATLAB file  
**Status:** Not Run

---

## Sprint 4+ Test Cases (TC-064 through TC-068)

### TC-034: Web UI Accessible
**AC:** AC-034 | **Type:** E2E  
**Steps:**  
1. Navigate to http://localhost:8080 in browser
2. Verify page loads
3. Verify query form present
4. Submit test query via UI
5. Verify results displayed

**Expected:** UI loads and functions correctly  
**Status:** Not Run

---

### TC-061: Performance Under Load
**AC:** AC-061 | **Type:** Performance  
**Steps:**  
1. Run load test with 100 queries
2. Calculate 90th percentile response time
3. Categorize simple vs complex queries

**Expected:** 90th percentile <10s simple, <30s complex  
**Status:** Not Run

---

### TC-067: Scalability at 100K Patterns
**AC:** AC-067 | **Type:** Performance  
**Steps:**  
1. Load 100K patterns into ChromaDB
2. POST query
3. Measure pattern retrieval time
4. Verify response time

**Expected:** Pattern retrieval <1s even with 100K patterns  
**Status:** Not Run

---

## Test Execution Strategy

### Sprint 1 Testing
- **Priority:** Infrastructure tests first (Docker, DB, API)
- **Order:** TC-043 → TC-001-003 → TC-031-033 → TC-040-042 → TC-049-051 → TC-052-054 → TC-055-057 → TC-058-060
- **Gate:** All Sprint 1 TCs pass before marking any DEL-001, DEL-002, DEL-009, DEL-011, DEL-013-020 as Done

### Sprint 2 Testing
- **Priority:** Core learning tests (pattern extraction, storage, retrieval)
- **Order:** TC-010-012 → TC-013-015 → TC-016-018 → TC-007-009 → TC-063-064 → TC-065-066
- **Gate:** Pattern flow (extract → store → retrieve) working end-to-end

### Sprint 3 Testing
- **Priority:** Integration tests (pattern application, refinement, MATLAB)
- **Order:** TC-019-021 → TC-022-024 → TC-028-030 → TC-046-048
- **Gate:** Full reasoning loop (with patterns + refinement) functional

### Sprint 4+ Testing
- **Priority:** Enhancement and optimization tests
- **Order:** TC-034-036 → TC-061-062 → TC-067-068
- **Gate:** Performance targets met, UI functional

## Test Data Strategy

**No Mock Data:** All tests use real databases (PostgreSQL, ChromaDB) running in Docker test containers.

**Test Data:**
- Sample queries: Math problems, coding questions, general reasoning
- Seed patterns: Pre-generated patterns for retrieval testing
- Load test data: Scripts to generate 100K patterns, 100K queries

**Test Isolation:**
- Test containers use tmpfs (in-memory) for speed
- Each test run starts with clean database state
- Tests create their own test data (no shared fixtures)

## Test Coverage Goals

- **Overall:** >70% code coverage
- **Critical Paths:** >90% coverage
  - Reasoning engine
  - Pattern learning (extract, store, retrieve, apply)
  - LLM integration
  - API endpoints

**Measure:** `pytest --cov=src --cov-report=term-missing`

## Continuous Testing

**During Development (Sprint Execution):**
- Run relevant TCs after each code change
- Integration tests on every commit
- Full test suite before PR (not used, but before marking DEL done)

**Definition of Done:**
- All TCs for deliverable PASS
- No failing tests in test suite
- Coverage targets met

---

## Summary

| Sprint | Test Cases | Categories |
|--------|-----------|------------|
| Sprint 1 | TC-001 to TC-033, TC-037-042, TC-049-051, TC-055-060 (33 TCs) | Infrastructure, API, DB, Security, Logging |
| Sprint 2 | TC-007-009, TC-010-012, TC-013-015, TC-016-018, TC-063-066 (18 TCs) | Pattern learning, Code quality, Reliability |
| Sprint 3 | TC-019-024, TC-028-030, TC-046-048 (12 TCs) | Integration, Refinement, MATLAB |
| Sprint 4+ | TC-034-036, TC-061-062, TC-067-068 (5 TCs) | UI, Performance, Scalability |

**Total:** 68 Test Cases  
**Status:** All "Not Run" (to be executed during sprint execution)

---

**Traceability:** REQ → DEL → AC → TC (complete chain)

Example: REQ-001 → DEL-001 → AC-001, AC-002, AC-003 → TC-001, TC-002, TC-003
## Sprint 4 Test Cases (TC-070 through TC-090) - NEW

### TC-070: MATLAB Dashboard Loads Episodes
**AC:** AC-070 | **Type:** Integration  
**Steps:**  
1. Run 20 queries to generate episodes.mat file
2. Execute matlab/sira_dashboard.m from MATLAB command window
3. Verify learning velocity calculation completes
4. Check console output for velocity metrics

**Expected:** Dashboard loads episodes successfully, computes learning velocity (quality improvement rate)  
**Status:** Not Run

---

### TC-071: Pattern Effectiveness Heatmap
**AC:** AC-071 | **Type:** Integration  
**Steps:**  
1. Load episodes with varied domains and patterns
2. Run dashboard to generate heatmap
3. Visual inspection of figure: domains on Y-axis, pattern types on X-axis
4. Verify colormap shows effectiveness scores

**Expected:** Heatmap figure generated showing quality improvement by domain/pattern  
**Status:** Not Run

---

### TC-072: PDF Report Generation
**AC:** AC-072 | **Type:** Integration  
**Steps:**  
1. Run full dashboard analysis
2. Verify PDF created in /data/matlab/reports/sira_report_YYYYMMDD.pdf
3. Open PDF and verify sections: summary, visualizations, insights, recommendations
4. Check all figures embedded correctly

**Expected:** PDF report auto-generated with all required sections and visualizations  
**Status:** Not Run

---

### TC-073: Pattern Clustering
**AC:** AC-073 | **Type:** Integration  
**Steps:**  
1. Create 100 test patterns with 10 near-duplicates (cosine similarity > 0.9)
2. Run matlab/optimization/cluster_patterns.m
3. Verify clustering output identifies similar groups
4. Check cluster sizes and similarity scores

**Expected:** Clustering identifies and groups similar patterns correctly  
**Status:** Not Run

---

### TC-074: Pattern Distillation
**AC:** AC-074 | **Type:** Integration  
**Steps:**  
1. Establish baseline quality with 100 patterns
2. Run matlab/optimization/distill_library.m with merge_threshold=0.9
3. Verify library size reduced by 20%+
4. Re-run test queries, compare quality scores (< 2% degradation acceptable)

**Expected:** Library compressed by 20%+ with quality maintained within 2%  
**Status:** Not Run

---

### TC-075: Gap Analysis
**AC:** AC-075 | **Type:** Integration  
**Steps:**  
1. Load pattern library with uneven domain coverage (e.g., 50 math, 2 geography)
2. Run matlab/optimization/gap_analysis.m
3. Verify output identifies low-coverage domains (< 5 patterns)
4. Check recommendation list prioritizes underserved domains

**Expected:** Gap analysis flags underserved domains and recommends priorities  
**Status:** Not Run

---

### TC-076: Tier 1 Metrics Computed
**AC:** AC-076 | **Type:** Integration  
**Steps:**  
1. Submit test query via API
2. Query database: SELECT * FROM core_metrics WHERE query_id = '<id>'
3. Verify all 4 Tier 1 metrics present: learning_velocity, pattern_utilization_rate, avg_quality, domain_coverage
4. Check metric values are valid (not null, within expected ranges)

**Expected:** All 4 Tier 1 metrics computed and stored for every query  
**Status:** Not Run

---

### TC-077: Metrics Persistence
**AC:** AC-077 | **Type:** Integration  
**Steps:**  
1. Submit query and capture query_id
2. Query database: SELECT * FROM core_metrics WHERE query_id = '<id>'
3. Verify timestamp, query_id, session_id foreign keys correct
4. Check metric_name and metric_value columns populated

**Expected:** Metrics persisted with correct timestamps and relationships  
**Status:** Not Run

---

### TC-078: Core Metrics API Endpoint
**AC:** AC-078 | **Type:** Integration  
**Steps:**  
1. Submit 10 queries to populate metrics
2. Call GET /metrics/core
3. Parse JSON response
4. Verify all 10 SIRA metrics present: 4 Tier 1, 3 Tier 2, 3 Tier 3
5. Validate response schema matches documentation

**Expected:** API returns all 10 SIRA-specific metrics in correct JSON format  
**Status:** Not Run

---

### TC-079: Test Suite Coverage
**AC:** AC-079 | **Type:** Inspection  
**Steps:**  
1. Count test questions in 	ests/evaluation/test_suites/*.json
2. Verify 8 domains: math, geography, science, coding, reasoning, history, language, general
3. Count questions per domain (min 50 each)
4. Total count should be 500+

**Expected:** Test suites cover 8+ domains with 50+ questions each (500+ total)  
**Status:** Not Run

---

### TC-080: Baseline Comparison Statistical Significance
**AC:** AC-080 | **Type:** Integration  
**Steps:**  
1. Select 100 test questions from suite
2. Run src/evaluation/baseline_comparator.py with base LLM and SIRA
3. Capture quality scores for both systems
4. Verify statistical analysis (t-test) performed
5. Check p-value < 0.05 for significance

**Expected:** A/B test shows statistically significant improvement (p < 0.05)  
**Status:** Not Run

---

### TC-081: Learning Trajectory Analysis
**AC:** AC-081 | **Type:** Integration  
**Steps:**  
1. Run src/evaluation/trajectory_analyzer.py with 1000 synthetic queries
2. Plot quality scores over time
3. Fit linear regression to trend
4. Verify R� > 0.7 (strong learning trend)
5. Check trajectory report generated

**Expected:** Learning curve generated with R� > 0.7 showing improvement over 1000 queries  
**Status:** Not Run

---

### TC-082: Web Interface Loads
**AC:** AC-082 | **Type:** E2E  
**Steps:**  
1. Start all containers including frontend
2. Navigate to http://localhost:3000 in browser
3. Verify page loads without console errors
4. Check query form visible with text input and submit button

**Expected:** Web interface loads successfully and displays query form  
**Status:** Not Run

---

### TC-083: Reasoning Trace Visualization
**AC:** AC-083 | **Type:** E2E  
**Steps:**  
1. Submit query \"What is 2+2?\" via web UI
2. Wait for response to render
3. Verify reasoning trace displayed as expandable steps
4. Check each step shows: step number, description, quality score
5. Test expand/collapse functionality

**Expected:** Reasoning trace rendered with expandable steps and complete information  
**Status:** Not Run

---

### TC-084: Metrics Dashboard Display
**AC:** AC-084 | **Type:** E2E  
**Steps:**  
1. Navigate to metrics dashboard page
2. Verify dashboard fetches from /metrics/summary
3. Check display shows: total_queries, avg_quality, avg_latency_ms
4. Submit query, verify metrics update (may require refresh)

**Expected:** Dashboard displays real-time metrics from API  
**Status:** Not Run

---

### TC-085: Query Latency Reduction
**AC:** AC-085 | **Type:** Performance  
**Steps:**  
1. Measure baseline: Run 20 queries, record average latency (Sprint 3 baseline: ~25s)
2. Implement performance optimizations (caching, async)
3. Run same 20 queries again
4. Calculate improvement: (baseline - optimized) / baseline * 100%
5. Verify improvement >= 30%

**Expected:** Query latency reduced by 30%+ (target: <17.5s average)  
**Status:** Not Run

---

### TC-086: Concurrent Query Handling
**AC:** AC-086 | **Type:** Performance  
**Steps:**  
1. Use load testing tool (locust or pytest-asyncio)
2. Submit 10 concurrent queries
3. Measure response times for all queries
4. Verify no requests block/timeout
5. Check response time variance < 20%

**Expected:** System handles 10 concurrent queries with consistent response times  
**Status:** Not Run

---

### TC-087: Redis Cache Hit Rate
**AC:** AC-087 | **Type:** Performance  
**Steps:**  
1. Configure Redis cache for pattern retrieval
2. Submit 100 queries (mix of similar and unique)
3. Monitor Redis metrics using INFO command
4. Calculate hit rate: cache_hits / (cache_hits + cache_misses)
5. Verify hit rate > 60%

**Expected:** Cache hit rate exceeds 60% after 100 queries  
**Status:** Not Run

---

### TC-088: 100K Pattern Scalability
**AC:** AC-088 | **Type:** Performance  
**Steps:**  
1. Generate 100K synthetic patterns using 	ests/load/generate_patterns.py
2. Load patterns into ChromaDB
3. Submit 20 test queries
4. Measure pattern retrieval time for each query
5. Verify average retrieval time < 1s

**Expected:** Pattern retrieval remains under 1 second with 100K patterns  
**Status:** Not Run

---

### TC-089: 50 Concurrent Users Load Test
**AC:** AC-089 | **Type:** Performance  
**Steps:**  
1. Configure locust with 50 concurrent users
2. Run load test for 5 minutes: locust -f tests/load/locustfile.py --users 50
3. Monitor response times, error rates, throughput
4. Verify error rate < 5%
5. Check all users can submit queries successfully

**Expected:** System handles 50 concurrent users with < 5% error rate  
**Status:** Not Run

---

### TC-090: Performance Report Generation
**AC:** AC-090 | **Type:** Integration  
**Steps:**  
1. Run full scalability test suite (TC-088, TC-089)
2. Execute report generator script
3. Verify report includes:
   - Latency percentiles (p50, p95, p99)
   - Throughput metrics (queries/sec)
   - Error rates
   - Resource utilization (CPU, memory)
   - Identified bottlenecks
4. Check report format (markdown or PDF)

**Expected:** Comprehensive performance report generated with all required metrics  
**Status:** Not Run

---

## Sprint 4 Test Summary

**Total Sprint 4 Test Cases:** 21 (TC-070 through TC-090)

**By Deliverable:**
- DEL-030 (MATLAB Dashboard): TC-070, TC-071, TC-072 (3 TCs)
- DEL-032 (Pattern Optimization): TC-073, TC-074, TC-075 (3 TCs)
- DEL-034 (Core Metrics): TC-076, TC-077, TC-078 (3 TCs)
- DEL-035 (Evaluation Framework): TC-079, TC-080, TC-081 (3 TCs)
- DEL-012 (Web Interface): TC-082, TC-083, TC-084 (3 TCs)
- DEL-021 (Performance): TC-085, TC-086, TC-087 (3 TCs)
- DEL-024 (Scalability): TC-088, TC-089, TC-090 (3 TCs)

**Test Types:**
- Integration: 15 TCs
- Performance: 5 TCs
- E2E: 3 TCs
- Inspection: 1 TC

---

## Updated Summary by Sprint

| Sprint | Test Case IDs | Count | Focus Areas |
|--------|---------------|-------|-------------|
| Sprint 1 | TC-001-033, TC-067-069 | 36 TCs | Infrastructure, API, LLM, Config |
| Sprint 2 | TC-007-012, TC-034-051, TC-063-066 | 24 TCs | Quality, Patterns, Code Quality, Reliability |
| Sprint 3 | TC-019-030 | 12 TCs | Pattern Application, Refinement, Metrics, MATLAB |
| Sprint 4 | TC-070-090 | 21 TCs | Analytics, Optimization, Evaluation, Performance |

**Total:** 90 Test Cases  
**Status:** Sprint 1-3 complete, Sprint 4 \"Not Run\"
