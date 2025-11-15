# Sprint 1 Plan: Infrastructure & Core API

**Sprint:** 1  
**Duration:** 2 weeks (10 working days)  
**Start Date:** TBD  
**End Date:** TBD  
**Status:** Ready to Start

---

## Sprint Goal

Set up complete infrastructure foundation for SIRA:
- All containers running (API, PostgreSQL, ChromaDB, Local LLM Runtime)
- Basic reasoning engine functional
- End-to-end query → LLM → response flow working
- All Sprint 1 tests passing

---

## Deliverables (12 Total)

### Infrastructure (5)
- **DEL-015:** Docker Infrastructure
- **DEL-018:** Database Schema & Migrations
- **DEL-025:** Local LLM Runtime Setup ⭐ NEW
- **DEL-014:** Configuration System
- **DEL-017:** Logging Infrastructure

### Core Functionality (3)
- **DEL-011:** REST API Layer
- **DEL-001:** Query Processing API
- **DEL-002:** Reasoning Engine Core

### Integration & Support (4)
- **DEL-013:** LLM Integration Layer
- **DEL-009:** Session Management
- **DEL-019:** Security Implementation
- **DEL-020:** Testing Framework

---

## Task Breakdown

### Day 1-2: Foundation Setup

#### Task 1.1: Local LLM Runtime Setup (DEL-025)
**Owner:** TBD  
**Effort:** 4 hours  
**Priority:** CRITICAL (everything depends on this)

**Steps:**
1. Create `ops/docker/docker-compose.yml` with `sira-llm` service
2. Use Ollama image: `ollama/ollama:latest`
3. Configure port exposure: 11434
4. Add health check endpoint
5. Download initial model (llama3:8b or qwen2.5:7b)
6. Test API: `curl http://localhost:11434/v1/models`

**Acceptance Criteria:**
- AC-067: Ollama API accessible
- AC-068: Model downloaded
- AC-069: Container defined

**Test Cases:** TC-067, TC-068, TC-069

**Docker Compose Service:**
```yaml
sira-llm:
  image: ollama/ollama:latest
  container_name: sira-llm
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
  networks:
    - sira_network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:11434/v1/models"]
    interval: 30s
    timeout: 10s
    retries: 3
  command: serve
```

**Post-Start:** Run `docker exec sira-llm ollama pull llama3:8b`

---

#### Task 1.2: Docker Infrastructure (DEL-015)
**Owner:** TBD  
**Effort:** 6 hours  
**Dependencies:** None

**Steps:**
1. Create `ops/docker/Dockerfile` for SIRA API
2. Create `ops/docker/docker-compose.yml` (dev profile)
3. Create `ops/docker/docker-compose.test.yml` (test profile)
4. Add PostgreSQL service (postgres:16-alpine)
5. Add ChromaDB service (ghcr.io/chroma-core/chroma:latest)
6. Add sira-llm service (from Task 1.1)
7. Configure networks and volumes
8. Test: `docker-compose up --build`

**Acceptance Criteria:**
- AC-043: All containers build and start
- AC-044: Dev profile runs with hot-reload
- AC-045: Test profile runs pytest

**Test Cases:** TC-043, TC-044, TC-045

**Deliverables:**
- `ops/docker/Dockerfile`
- `ops/docker/docker-compose.yml`
- `ops/docker/docker-compose.test.yml`
- `ops/docker/.env.example`

---

#### Task 1.3: Database Schema (DEL-018)
**Owner:** TBD  
**Effort:** 3 hours  
**Dependencies:** Task 1.2 (PostgreSQL running)

**Steps:**
1. Create `ops/docker/init-db.sql` with:
   - sessions table
   - queries table
   - metrics table
   - pattern_metadata table
   - Indexes
2. Mount init script in docker-compose
3. Verify schema creation: Connect to PostgreSQL and list tables

**Acceptance Criteria:**
- AC-049: All tables created
- AC-050: Indexes defined
- AC-051: UUID extension enabled

**Test Cases:** TC-049, TC-050, TC-051

**SQL Script Location:** `ops/docker/init-db.sql`

---

### Day 3-4: Configuration & API Foundation

#### Task 2.1: Configuration System (DEL-014)
**Owner:** TBD  
**Effort:** 4 hours  
**Dependencies:** Task 1.2

**Steps:**
1. Create `src/core/config.py` with `Settings` class (pydantic-settings)
2. Define environment variables:
   - `LLM_BASE_URL` (default: http://sira-llm:11434)
   - `LLM_MODEL_GENERAL` (default: llama3:8b)
   - `POSTGRES_*` settings
   - `CHROMADB_*` settings
3. Add validation
4. Create `.env.example` file
5. Test config loading

**Acceptance Criteria:**
- AC-040: All config via env vars
- AC-041: Validation on startup
- AC-042: No secrets in code

**Test Cases:** TC-040, TC-041, TC-042

**Files:**
- `src/core/config.py`
- `ops/docker/.env.example`

---

#### Task 2.2: Logging Infrastructure (DEL-017)
**Owner:** TBD  
**Effort:** 3 hours  
**Dependencies:** Task 2.1

**Steps:**
1. Create `src/core/logging.py` with structlog setup
2. Configure JSON output format
3. Add context binding (request_id, session_id)
4. Set log levels via environment
5. Add logging middleware for FastAPI

**Acceptance Criteria:**
- AC-052: Structured JSON logs
- AC-053: Log levels configurable
- AC-054: No secrets in logs

**Test Cases:** TC-052, TC-053, TC-054

**File:** `src/core/logging.py`

---

#### Task 2.3: REST API Layer (DEL-011)
**Owner:** TBD  
**Effort:** 5 hours  
**Dependencies:** Tasks 2.1, 2.2

**Steps:**
1. Create `src/api/main.py` - FastAPI app initialization
2. Create request/response models in `src/api/models/`
3. Create route stubs in `src/api/routes/`:
   - `query.py` - POST /query
   - `session.py` - GET /session/{id}
   - `patterns.py` - GET /patterns
   - `metrics.py` - GET /metrics
4. Add middleware (logging, CORS)
5. Enable Swagger UI at `/docs`
6. Test: Navigate to http://localhost:8080/docs

**Acceptance Criteria:**
- AC-031: All endpoints functional
- AC-032: Proper HTTP status codes
- AC-033: Swagger docs available

**Test Cases:** TC-031, TC-032, TC-033

**Files:**
- `src/api/main.py`
- `src/api/routes/*.py`
- `src/api/models/*.py`

---

### Day 5-7: LLM Integration & Core Logic

#### Task 3.1: LLM Integration Layer (DEL-013)
**Owner:** TBD  
**Effort:** 6 hours  
**Dependencies:** Tasks 1.1, 2.1

**Steps:**
1. Create `src/llm/client.py` - LLMClient protocol
2. Create `src/llm/local_runtime.py` - LocalRuntimeClient implementation
3. Implement HTTP calls to `{LLM_BASE_URL}/v1/chat/completions`
4. Add retry logic (3 attempts, exponential backoff)
5. Add error handling (LLMClientError)
6. Test: Generate completion via Ollama

**Acceptance Criteria:**
- AC-037: Completions via local runtime
- AC-038: Config-based runtime switching
- AC-039: Multiple models supported

**Test Cases:** TC-037, TC-038, TC-039

**Files:**
- `src/llm/client.py` (protocol)
- `src/llm/local_runtime.py` (implementation)
- `src/llm/errors.py`

---

#### Task 3.2: Reasoning Engine Core (DEL-002)
**Owner:** TBD  
**Effort:** 8 hours  
**Dependencies:** Task 3.1

**Steps:**
1. Create `src/reasoning/engine.py` - ReasoningEngine class
2. Implement `process_query()` method
3. Implement `_generate_reasoning_steps()` - calls LLM
4. Create ReasoningStep and ReasoningResult dataclasses
5. Capture full reasoning trace
6. Test: Submit query, verify multi-step reasoning

**Acceptance Criteria:**
- AC-004: Multi-step reasoning (2+ steps)
- AC-005: Proper step structure
- AC-006: Response time <30s

**Test Cases:** TC-004, TC-005, TC-006

**Files:**
- `src/reasoning/engine.py`
- `src/reasoning/models.py` (dataclasses)

---

#### Task 3.3: Query Processing API (DEL-001)
**Owner:** TBD  
**Effort:** 4 hours  
**Dependencies:** Tasks 3.2, 2.3

**Steps:**
1. Implement `POST /query` route in `src/api/routes/query.py`
2. Validate query input (1-10000 chars)
3. Call ReasoningEngine.process_query()
4. Save query to database
5. Return response with reasoning trace
6. Test via Swagger UI

**Acceptance Criteria:**
- AC-001: Valid queries accepted (200)
- AC-002: Invalid queries rejected (400)
- AC-003: Metadata persisted

**Test Cases:** TC-001, TC-002, TC-003

**File:** `src/api/routes/query.py`

---

### Day 8-9: Supporting Systems

#### Task 4.1: Session Management (DEL-009)
**Owner:** TBD  
**Effort:** 5 hours  
**Dependencies:** Task 1.3

**Steps:**
1. Create `src/db/session.py` - Session management functions
2. Implement auto session creation (UUID generation)
3. Implement explicit session_id handling
4. Add `GET /session/{id}` endpoint
5. Test: Create sessions, retrieve history

**Acceptance Criteria:**
- AC-025: Auto session creation
- AC-026: Session data persisted
- AC-027: Survives restart

**Test Cases:** TC-025, TC-026, TC-027

**Files:**
- `src/db/session.py`
- `src/api/routes/session.py`

---

#### Task 4.2: Security Implementation (DEL-019)
**Owner:** TBD  
**Effort:** 3 hours  
**Dependencies:** Task 2.3

**Steps:**
1. Add input validation middleware
2. Implement size limits (query text max 10K chars)
3. Use SQLAlchemy ORM (prevents SQL injection)
4. Ensure no secrets logged
5. Add `.env` to `.gitignore`
6. Test: Submit malicious inputs, verify rejection

**Acceptance Criteria:**
- AC-055: Input validation works
- AC-056: No SQL injection possible
- AC-057: Secrets not logged

**Test Cases:** TC-055, TC-056, TC-057

**Files:**
- `src/api/middleware/validation.py`
- `.gitignore`

---

#### Task 4.3: Testing Framework (DEL-020)
**Owner:** TBD  
**Effort:** 4 hours  
**Dependencies:** All previous tasks

**Steps:**
1. Create `tests/` directory structure
2. Set up pytest configuration (`pytest.ini`)
3. Create test fixtures (`tests/conftest.py`)
4. Write integration tests for each deliverable
5. Configure test docker-compose profile
6. Run: `docker-compose -f docker-compose.test.yml up`

**Acceptance Criteria:**
- AC-058: pytest configured
- AC-059: Test structure defined
- AC-060: No mock data used

**Test Cases:** TC-058, TC-059, TC-060

**Files:**
- `pytest.ini`
- `tests/conftest.py`
- `tests/integration/test_api.py`
- `tests/integration/test_reasoning.py`
- `tests/integration/test_llm.py`

---

### Day 10: Integration & Testing

#### Task 5.1: End-to-End Integration Test
**Owner:** TBD  
**Effort:** 4 hours  
**Dependencies:** All tasks

**Steps:**
1. Start all containers: `docker-compose up`
2. Verify all services healthy
3. Run full test suite: `docker-compose -f docker-compose.test.yml up`
4. Submit test query via Swagger UI
5. Verify query → LLM → reasoning → response flow
6. Check logs for errors
7. Verify data persisted in PostgreSQL

**Success Criteria:**
- All 36 Sprint 1 test cases passing
- Query processing works end-to-end
- No errors in logs
- All containers healthy

---

#### Task 5.2: Documentation Updates
**Owner:** TBD  
**Effort:** 2 hours

**Steps:**
1. Update README.md with setup instructions
2. Document API endpoints (complement Swagger)
3. Add troubleshooting guide
4. Document environment variables
5. Add quick start guide

**Files:**
- `README.md`
- `docs/QUICKSTART.md` (new)
- `docs/TROUBLESHOOTING.md` (new)

---

## Success Criteria (Definition of Done)

### Functional
- ✅ All 12 deliverables complete
- ✅ 36 acceptance criteria met
- ✅ 36 test cases passing
- ✅ End-to-end query flow working

### Technical
- ✅ All containers build and start successfully
- ✅ Local LLM runtime serving model completions
- ✅ API accessible at http://localhost:8080
- ✅ Swagger UI functional at http://localhost:8080/docs
- ✅ Database schema created
- ✅ No errors in container logs

### Quality
- ✅ No secrets in code or logs
- ✅ Proper error handling (400, 500 status codes)
- ✅ Structured logging working
- ✅ Input validation functional

### Documentation
- ✅ README.md updated
- ✅ Quick start guide created
- ✅ All code has docstrings
- ✅ Sprint 1 completion report written

---

## Risk Management

### High Priority Risks

**Risk:** LLM model download takes too long (multi-GB)  
**Impact:** Delays Day 1-2 tasks  
**Mitigation:** Start download first thing; use smaller model (7B params); document download time

**Risk:** Sprint 1 overloaded (12 deliverables)  
**Impact:** Not all tasks complete  
**Mitigation:** Focus on MVP; defer polish; LLM setup is straightforward

**Risk:** Local LLM runtime resource constraints  
**Impact:** Slow inference, OOM errors  
**Mitigation:** Use smaller models; document minimum hardware requirements; test on target hardware

**Risk:** Docker networking issues on Windows  
**Impact:** Containers can't communicate  
**Mitigation:** Test early; use explicit network configuration; document Windows-specific setup

---

## Dependencies

### External
- Docker Desktop installed and running
- At least 16GB RAM (for local LLM)
- 20GB free disk space (for models)
- Internet connection (for model download)

### Between Tasks
```
Task 1.1 (LLM Runtime) → Task 3.1 (LLM Integration)
Task 1.2 (Docker) → Task 1.3 (Database)
Task 1.3 (Database) → Task 4.1 (Sessions)
Task 2.1 (Config) → Task 2.2 (Logging) → Task 2.3 (API)
Task 3.1 (LLM) → Task 3.2 (Reasoning) → Task 3.3 (Query)
All → Task 5.1 (Integration)
```

---

## Daily Standup Questions

1. What did you complete yesterday?
2. What will you work on today?
3. Any blockers?
4. Any risks or concerns?

---

## Sprint Review Prep

**Demo Agenda:**
1. Show all containers running (`docker ps`)
2. Navigate to Swagger UI (http://localhost:8080/docs)
3. Submit test query via Swagger
4. Show reasoning trace in response
5. Query database to show persisted data
6. Show logs with structured JSON
7. Run test suite and show all passing

---

## Next Steps After Sprint 1

Sprint 2 will focus on:
- Pattern learning (extraction, storage, retrieval)
- Self-verification
- Code quality setup
- Reliability improvements

---

**Sprint Status:** ✅ Ready to Execute  
**Branch:** Create `sprint-01` branch from main  
**Tag After Completion:** `v01.0-sprint-01`
