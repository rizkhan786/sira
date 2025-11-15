# Acceptance Criteria Index - SIRA

**Last Updated:** 2025-11-15  
**Phase:** 1 (Foundation)

## Format
- **ID:** AC-### (unique identifier)
- **Deliverable:** Linked DEL-###
- **Requirement:** Linked REQ/NFR-###
- **Description:** What must be true for deliverable to be accepted
- **Verification Method:** How to verify (test, inspection, demo)

---

## DEL-001: Query Processing API

### AC-001
**Deliverable:** DEL-001  
**Requirement:** REQ-001  
**Description:** API endpoint POST /query accepts valid query requests with query text and returns 200 with response including answer and reasoning trace.  
**Verification:** Integration test with sample queries

### AC-002
**Deliverable:** DEL-001  
**Requirement:** REQ-001  
**Description:** API validates input (query text 1-10000 chars) and returns 400 with error message for invalid requests.  
**Verification:** Test invalid inputs (empty, too long, malformed JSON)

### AC-003
**Deliverable:** DEL-001  
**Requirement:** REQ-001  
**Description:** Query metadata (session_id, timestamp) properly associated with query and stored in database.  
**Verification:** Database inspection after query submission

---

## DEL-002: Reasoning Engine Core

### AC-004
**Deliverable:** DEL-002  
**Requirement:** REQ-002  
**Description:** Engine produces multi-step reasoning with at least 2 steps for non-trivial queries.  
**Verification:** Test with sample reasoning problems, verify step count

### AC-005
**Deliverable:** DEL-002  
**Requirement:** REQ-002  
**Description:** Each reasoning step includes step number, description, reasoning text, and dependencies on prior steps.  
**Verification:** Verify trace structure in response

### AC-006
**Deliverable:** DEL-002  
**Requirement:** NFR-001  
**Description:** Simple queries (CoT, no tools) complete in <10s, complex queries (ToT) in <30s.  
**Verification:** Performance test with timer

---

## DEL-003: Self-Verification Module

### AC-007
**Deliverable:** DEL-003  
**Requirement:** REQ-003  
**Description:** Each reasoning step assigned a quality score (0-1 float) and confidence level.  
**Verification:** Check all steps have valid scores

### AC-008
**Deliverable:** DEL-003  
**Requirement:** REQ-003  
**Description:** Low-confidence results (< threshold) trigger refinement or flagged in response.  
**Verification:** Test with deliberately weak reasoning

### AC-009
**Deliverable:** DEL-003  
**Requirement:** REQ-003  
**Description:** Verification module provides rationale for quality assessment.  
**Verification:** Inspect verification output for explanatory text

---

## DEL-004: Pattern Extraction Engine

### AC-010
**Deliverable:** DEL-004  
**Requirement:** REQ-004  
**Description:** Successful reasoning traces (confidence >0.7) trigger pattern extraction.  
**Verification:** Monitor pattern extraction on successful queries

### AC-011
**Deliverable:** DEL-004  
**Requirement:** REQ-004  
**Description:** Extracted patterns include structure, context, reasoning template, and quality score.  
**Verification:** Inspect pattern objects for required fields

### AC-012
**Deliverable:** DEL-004  
**Requirement:** REQ-004  
**Description:** Patterns with quality score <0.6 are discarded, not stored.  
**Verification:** Verify low-quality patterns not in database

---

## DEL-005: Pattern Storage System

### AC-013
**Deliverable:** DEL-005  
**Requirement:** REQ-005  
**Description:** Patterns successfully stored in ChromaDB with embeddings and metadata.  
**Verification:** Query ChromaDB directly, verify pattern count

### AC-014
**Deliverable:** DEL-005  
**Requirement:** REQ-005  
**Description:** Pattern metadata (quality, usage count, timestamps) stored in PostgreSQL.  
**Verification:** SQL query for pattern_metadata table

### AC-015
**Deliverable:** DEL-005  
**Requirement:** NFR-003  
**Description:** System handles 100K+ patterns without degradation (storage and retrieval).  
**Verification:** Load test with large pattern dataset

---

## DEL-006: Pattern Retrieval System

### AC-016
**Deliverable:** DEL-006  
**Requirement:** REQ-006  
**Description:** Vector similarity search retrieves top-k (configurable, default 5) most relevant patterns for query.  
**Verification:** Test queries return expected similar patterns

### AC-017
**Deliverable:** DEL-006  
**Requirement:** REQ-006  
**Description:** Pattern retrieval completes in <1s for typical pattern database size.  
**Verification:** Performance test with timer

### AC-018
**Deliverable:** DEL-006  
**Requirement:** REQ-006  
**Description:** When no relevant patterns exist (similarity < threshold), return empty list (no errors).  
**Verification:** Test with unique query, no patterns

---

## DEL-007: Pattern Application Logic

### AC-019
**Deliverable:** DEL-007  
**Requirement:** REQ-007  
**Description:** Retrieved patterns integrated into reasoning prompt and influence reasoning steps.  
**Verification:** Compare reasoning with/without patterns available

### AC-020
**Deliverable:** DEL-007  
**Requirement:** REQ-007  
**Description:** Pattern usage tracked: pattern_id recorded with query, usage_count incremented.  
**Verification:** Database check after pattern-assisted query

### AC-021
**Deliverable:** DEL-007  
**Requirement:** REQ-007  
**Description:** Pattern quality updated based on outcome: success_count incremented if query successful.  
**Verification:** Verify pattern quality changes over multiple uses

---

## DEL-008: Iterative Refinement System

### AC-022
**Deliverable:** DEL-008  
**Requirement:** REQ-008  
**Description:** System performs up to max_iterations (configurable, default 3) reasoning passes.  
**Verification:** Test with low initial confidence, verify iterations

### AC-023
**Deliverable:** DEL-008  
**Requirement:** REQ-008  
**Description:** Answer quality improves across iterations (confidence increases or answer changes).  
**Verification:** Compare answers from iteration 1 vs final

### AC-024
**Deliverable:** DEL-008  
**Requirement:** REQ-008  
**Description:** Iteration stops early if confidence threshold met or no improvement detected.  
**Verification:** Test convergence scenarios

---

## DEL-009: Session Management

### AC-025
**Deliverable:** DEL-009  
**Requirement:** REQ-009  
**Description:** Sessions created automatically or via explicit session_id in request.  
**Verification:** Test both auto and explicit session creation

### AC-026
**Deliverable:** DEL-009  
**Requirement:** REQ-009  
**Description:** Session data (queries, responses, timestamps) persisted in PostgreSQL.  
**Verification:** Database query for sessions and queries tables

### AC-027
**Deliverable:** DEL-009  
**Requirement:** NFR-005  
**Description:** Session data survives application restart (no data loss).  
**Verification:** Restart container, verify session data intact

---

## DEL-010: Metrics Tracking System

### AC-028
**Deliverable:** DEL-010  
**Requirement:** REQ-010  
**Description:** Metrics captured for each query: pattern_reuse_count, reasoning_depth, response_time_ms, llm_calls.  
**Verification:** Database inspection of metrics table

### AC-029
**Deliverable:** DEL-010  
**Requirement:** REQ-010  
**Description:** Metrics accessible via GET /metrics endpoint with filtering (date range, session).  
**Verification:** API test for metrics endpoint

### AC-030
**Deliverable:** DEL-010  
**Requirement:** NFR-013  
**Description:** Trend data computable: improvement over time, pattern reuse rate growth.  
**Verification:** Query multiple sessions, compute trends

---

## DEL-011: REST API Layer

### AC-031
**Deliverable:** DEL-011  
**Requirement:** REQ-011  
**Description:** All required endpoints functional: POST /query, GET /session/{id}, GET /patterns, GET /metrics.  
**Verification:** Integration tests for all endpoints

### AC-032
**Deliverable:** DEL-011  
**Requirement:** REQ-011  
**Description:** API returns proper HTTP status codes (200, 400, 404, 500) with JSON error messages.  
**Verification:** Test error scenarios, verify status codes

### AC-033
**Deliverable:** DEL-011  
**Requirement:** NFR-010  
**Description:** OpenAPI/Swagger documentation auto-generated and accessible at /docs.  
**Verification:** Navigate to /docs, verify endpoints documented

---

## DEL-012: Web Interface

### AC-034
**Deliverable:** DEL-012  
**Requirement:** REQ-012  
**Description:** Web UI accessible via browser at http://localhost:8080, displays query form and results.  
**Verification:** Manual browser test

### AC-035
**Deliverable:** DEL-012  
**Requirement:** REQ-012  
**Description:** Reasoning steps visualized clearly (expandable tree or list with step numbers).  
**Verification:** Submit query, verify visualization

### AC-036
**Deliverable:** DEL-012  
**Requirement:** NFR-011  
**Description:** UI responsive on desktop and tablet (min width 768px).  
**Verification:** Test on different screen sizes

---

## DEL-013: LLM Integration Layer

### AC-037
**Deliverable:** DEL-013  
**Requirement:** REQ-013  
**Description:** Successfully generates completions via the configured local LLM runtime (OpenAI-style HTTP API).  
**Verification:** Test query with local runtime container running

### AC-038
**Deliverable:** DEL-013  
**Requirement:** REQ-013  
**Description:** Changing LLM_BASE_URL and LLM_MODEL_GENERAL in configuration switches the runtime/model without code changes.  
**Verification:** Modify env, restart, verify responses come from new runtime/model

### AC-039
**Deliverable:** DEL-013  
**Requirement:** NFR-015  
**Description:** LLM orchestrator interface supports configuring at least two distinct local models or runtimes via configuration only.  
**Verification:** Configure two different models/backends and verify both can be used without code changes

---

## DEL-025: Local LLM Runtime Setup

### AC-067
**Deliverable:** DEL-025  
**Requirement:** REQ-013  
**Description:** Ollama container successfully starts and exposes OpenAI-style HTTP API on port 11434.  
**Verification:** curl http://localhost:11434/v1/models returns valid model list

### AC-068
**Deliverable:** DEL-025  
**Requirement:** REQ-013  
**Description:** At least one local LLM model (e.g., llama3:8b or qwen2.5:7b) downloaded and available for inference.  
**Verification:** Model appears in /v1/models endpoint and can generate completions

### AC-069
**Deliverable:** DEL-025  
**Requirement:** NFR-014  
**Description:** LLM runtime container defined in docker-compose.yml with proper networking and health checks.  
**Verification:** docker ps shows sira-llm container running and healthy

---

## DEL-014: Configuration System

### AC-040
**Deliverable:** DEL-014  
**Requirement:** REQ-014  
**Description:** All configuration loaded from .env file (API keys, DB connections, ports, limits).  
**Verification:** Change .env values, verify app uses new config

### AC-041
**Deliverable:** DEL-014  
**Requirement:** REQ-014  
**Description:** Sensible defaults provided for optional config (documented in .env.example).  
**Verification:** Run without .env, verify defaults work

### AC-042
**Deliverable:** DEL-014  
**Requirement:** NFR-006  
**Description:** Secrets never appear in logs or error messages.  
**Verification:** Grep logs for API keys, verify absent

---

## DEL-015: Docker Infrastructure

### AC-043
**Deliverable:** DEL-015  
**Requirement:** REQ-015  
**Description:** docker-compose up successfully builds and starts all services (sira-api, postgres, chromadb).  
**Verification:** Clean Docker build and startup

### AC-044
**Deliverable:** DEL-015  
**Requirement:** REQ-015  
**Description:** Dev profile (docker-compose.yml) runs with hot-reload, test profile (docker-compose.test.yml) runs pytest.  
**Verification:** Test both profiles separately

### AC-045
**Deliverable:** DEL-015  
**Requirement:** NFR-014  
**Description:** No host dependencies required (all in containers, works on clean Docker Desktop).  
**Verification:** Fresh Windows machine with only Docker

---

## DEL-016: MATLAB Analysis Integration

### AC-046
**Deliverable:** DEL-016  
**Requirement:** REQ-016  
**Description:** Episode logs written to /data/logs/run_{id}/episodes.jsonl in correct format.  
**Verification:** Inspect generated JSONL file structure

### AC-047
**Deliverable:** DEL-016  
**Requirement:** REQ-016  
**Description:** Python reads MATLAB-generated configs from /data/config/sira_tuned_*.json and applies settings.  
**Verification:** Place tuned config, verify parameters change

### AC-048
**Deliverable:** DEL-016  
**Requirement:** REQ-016  
**Description:** Config hot-reload works without restart (periodic check or file watch).  
**Verification:** Update config while running, verify applied

---

## DEL-017: Logging Infrastructure

### AC-049
**Deliverable:** DEL-017  
**Requirement:** NFR-012  
**Description:** All logs output in structured JSON format with timestamp, level, message, context.  
**Verification:** Parse log output as JSON, verify fields

### AC-050
**Deliverable:** DEL-017  
**Requirement:** NFR-012  
**Description:** Log levels (DEBUG, INFO, WARNING, ERROR) configurable via LOG_LEVEL env var.  
**Verification:** Change LOG_LEVEL, verify output filtered

### AC-051
**Deliverable:** DEL-017  
**Requirement:** NFR-012  
**Description:** No sensitive data (API keys, user PII) appears in logs.  
**Verification:** Sensitive data scan of log files

---

## DEL-018: Database Schema & Migrations

### AC-052
**Deliverable:** DEL-018  
**Requirement:** NFR-005  
**Description:** PostgreSQL schema created on first startup (sessions, queries, metrics, pattern_metadata tables).  
**Verification:** Inspect database after init

### AC-053
**Deliverable:** DEL-018  
**Requirement:** NFR-005  
**Description:** Indexes created on frequent query columns (session_id, created_at).  
**Verification:** SQL query for indexes

### AC-054
**Deliverable:** DEL-018  
**Requirement:** NFR-005  
**Description:** Alembic migrations support schema evolution without data loss.  
**Verification:** Test migration up/down

---

## DEL-019: Security Implementation

### AC-055
**Deliverable:** DEL-019  
**Requirement:** NFR-006  
**Description:** All API keys and secrets managed via .env, never hardcoded.  
**Verification:** Code review, grep for hardcoded keys

### AC-056
**Deliverable:** DEL-019  
**Requirement:** NFR-007  
**Description:** Input validation on all API endpoints (length, type, format).  
**Verification:** Fuzz testing with invalid inputs

### AC-057
**Deliverable:** DEL-019  
**Requirement:** NFR-007  
**Description:** SQL injection prevented via parameterized queries (SQLAlchemy ORM).  
**Verification:** Attempt SQL injection attacks

---

## DEL-020: Testing Framework

### AC-058
**Deliverable:** DEL-020  
**Requirement:** NFR-009  
**Description:** pytest runs successfully in Docker test profile, all tests pass.  
**Verification:** docker-compose -f docker-compose.test.yml up

### AC-059
**Deliverable:** DEL-020  
**Requirement:** NFR-009  
**Description:** Test coverage >70% for critical paths (reasoning engine, pattern learning).  
**Verification:** pytest --cov report

### AC-060
**Deliverable:** DEL-020  
**Requirement:** NFR-009  
**Description:** No mock data used in tests (real databases in test containers).  
**Verification:** Code review of test files

---

## DEL-021: Performance Optimization

### AC-061
**Deliverable:** DEL-021  
**Requirement:** NFR-001  
**Description:** 90th percentile response time <10s for simple queries, <30s for complex.  
**Verification:** Load test with percentile analysis

### AC-062
**Deliverable:** DEL-021  
**Requirement:** NFR-002  
**Description:** System handles 10+ concurrent queries with <20% response time degradation.  
**Verification:** Concurrent load test

---

## DEL-022: Code Quality Setup

### AC-063
**Deliverable:** DEL-022  
**Requirement:** NFR-008  
**Description:** Type hints present on all public functions and classes.  
**Verification:** mypy type checking passes

### AC-064
**Deliverable:** DEL-022  
**Requirement:** NFR-008  
**Description:** Docstrings present on all public functions/classes following standard format.  
**Verification:** Documentation coverage tool

---

## DEL-023: Reliability & Error Handling

### AC-065
**Deliverable:** DEL-023  
**Requirement:** NFR-004  
**Description:** Local LLM runtime HTTP failures handled with retry (3 attempts, exponential backoff).  
**Verification:** Simulate runtime HTTP failure, verify retries

### AC-066
**Deliverable:** DEL-023  
**Requirement:** NFR-004  
**Description:** Database connection failures handled with retry and logged appropriately.  
**Verification:** Disconnect DB, verify graceful handling

---

## DEL-024: Scalability Testing

### AC-067
**Deliverable:** DEL-024  
**Requirement:** NFR-003  
**Description:** Pattern retrieval remains <1s with 100K patterns in ChromaDB.  
**Verification:** Load 100K patterns, performance test

### AC-068
**Deliverable:** DEL-024  
**Requirement:** NFR-003  
**Description:** PostgreSQL query performance acceptable with 100K+ query records.  
**Verification:** Load historical data, test query times

---

## Summary

**Total Acceptance Criteria:** 68  
**By Deliverable:** Average 2.8 ACs per deliverable  
**By Sprint:**
- Sprint 1: 33 ACs (DEL-001,002,009,011,013,014,015,017,018,019,020)
- Sprint 2: 18 ACs (DEL-003,004,005,006,022,023)
- Sprint 3: 12 ACs (DEL-007,008,010,016)
- Sprint 4+: 5 ACs (DEL-012,021,024)

**Verification Methods:**
- Integration Tests: 40 ACs
- Database Inspection: 15 ACs
- Performance Tests: 8 ACs
- Code Review/Inspection: 5 ACs

---

**Next Step:** Create test cases (TC-###) for each acceptance criterion in `test-cases.md`.
