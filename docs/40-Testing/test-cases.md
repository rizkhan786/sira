# Test Cases - SIRA

**Last Updated:** 2025-11-15  
**Phase:** 1 (Foundation)  
**Total Test Cases:** 71 (1 per AC)

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
