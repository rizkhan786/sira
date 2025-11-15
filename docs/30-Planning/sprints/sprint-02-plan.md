# Sprint 2 Plan: Pattern Learning & Self-Improvement

**Sprint**: 2  
**Phase**: 1 (Foundation)  
**Duration**: 2 weeks (14 days)  
**Start Date**: TBD  
**End Date**: TBD  
**Status**: Planning Complete - Ready for Execution  

---

## Sprint Goal

**Implement core self-improvement features**: Pattern extraction, storage, retrieval, and quality scoring so SIRA learns from successful queries and improves over time.

---

## Sprint Objectives

By the end of Sprint 2, SIRA will:
1. ✅ Extract patterns from successful query→reasoning→response flows
2. ✅ Store patterns in ChromaDB with vector embeddings
3. ✅ Retrieve similar patterns for new queries
4. ✅ Score pattern quality automatically
5. ✅ Self-verify response quality
6. ✅ Have robust error handling and code quality checks

---

## Deliverables (6)

### Core Self-Improvement (4 deliverables)
- **DEL-003**: Self-Verification Module
- **DEL-004**: Pattern Extraction Engine
- **DEL-005**: Pattern Storage System (ChromaDB)
- **DEL-006**: Pattern Retrieval System

### Quality & Reliability (2 deliverables)
- **DEL-022**: Code Quality Setup
- **DEL-023**: Reliability & Error Handling

---

## Task Breakdown

### Task Group 1: Self-Verification Module (3-4 days)

#### Task 1.1: Quality Scoring Implementation
**Deliverable**: DEL-003  
**Estimated Time**: 1 day  
**Dependencies**: Sprint 1 complete  

**Subtasks**:
1. Create `src/quality/scorer.py` module
2. Implement `calculate_quality_score()` function
   - Check response completeness
   - Verify reasoning step coherence
   - Measure response relevance to query
3. Add quality thresholds to config (min: 0.7, good: 0.8, excellent: 0.9)
4. Unit tests for quality scoring

**Acceptance Criteria**:
- AC-007: Quality score calculated for every response (0.0-1.0)
- AC-008: Score considers response completeness, coherence, relevance
- AC-009: Scores stored in database with query

**Files to Create**:
- `src/quality/__init__.py`
- `src/quality/scorer.py`
- `tests/test_quality_scorer.py`

---

#### Task 1.2: Self-Verification Logic
**Deliverable**: DEL-003  
**Estimated Time**: 1.5 days  
**Dependencies**: Task 1.1  

**Subtasks**:
1. Implement verification checks:
   - Does response answer the query?
   - Are reasoning steps logical?
   - Are there contradictions?
2. Add LLM-based verification (ask LLM to verify its own response)
3. Combine rule-based + LLM verification into final score
4. Integration tests

**Acceptance Criteria**:
- AC-010: Verification runs automatically after each response
- AC-011: Low-quality responses flagged (score < 0.7)
- AC-012: Verification results logged

**Files to Modify**:
- `src/reasoning/engine.py` (add verification step)
- `src/quality/scorer.py` (add verification methods)

---

#### Task 1.3: Quality Metrics Storage
**Deliverable**: DEL-003  
**Estimated Time**: 0.5 days  
**Dependencies**: Task 1.2  

**Subtasks**:
1. Update `queries` table schema (add `quality_score` column)
2. Store verification results in `metrics` table
3. Create database migration script
4. Add quality metrics to API response

**Acceptance Criteria**:
- AC-013: Quality scores persisted to database
- AC-014: Quality visible in API response metadata
- AC-015: Historical quality queryable

**Files to Modify**:
- `ops/docker/init-db.sql` (add quality_score column)
- `src/db/repository.py` (update save_query method)
- `src/api/schemas.py` (add quality_score to response)

---

### Task Group 2: Pattern Extraction Engine (2-3 days)

#### Task 2.1: Pattern Extraction Logic
**Deliverable**: DEL-004  
**Estimated Time**: 1.5 days  
**Dependencies**: Task 1.3 (quality scoring working)  

**Subtasks**:
1. Create `src/patterns/extractor.py` module
2. Implement `extract_pattern()` function:
   - Extract query type (question, instruction, analysis)
   - Extract reasoning strategy used
   - Extract key concepts from query
   - Extract successful approach from reasoning steps
3. Define Pattern data structure (query_type, concepts, strategy, reasoning_template)
4. Only extract patterns from high-quality responses (score >= 0.8)

**Acceptance Criteria**:
- AC-016: Patterns extracted from queries with quality >= 0.8
- AC-017: Pattern includes query type, concepts, reasoning strategy
- AC-018: Pattern extraction automatic after successful query

**Files to Create**:
- `src/patterns/__init__.py`
- `src/patterns/extractor.py`
- `src/patterns/models.py` (Pattern data class)
- `tests/test_pattern_extractor.py`

---

#### Task 2.2: Pattern Template Generation
**Deliverable**: DEL-004  
**Estimated Time**: 1 day  
**Dependencies**: Task 2.1  

**Subtasks**:
1. Create reasoning templates from successful queries
2. Abstract specific details (replace entities with placeholders)
3. Generate pattern description and usage guidance
4. Add pattern validation (ensure completeness)

**Acceptance Criteria**:
- AC-019: Patterns include reusable reasoning templates
- AC-020: Specific details abstracted to placeholders
- AC-021: Pattern valid and complete before storage

**Files to Modify**:
- `src/patterns/extractor.py` (add template generation)
- `src/patterns/models.py` (add template fields)

---

### Task Group 3: Pattern Storage System (2-3 days)

#### Task 3.1: ChromaDB Integration
**Deliverable**: DEL-005  
**Estimated Time**: 1.5 days  
**Dependencies**: Task 2.2  

**Subtasks**:
1. Create `src/patterns/storage.py` module
2. Initialize ChromaDB client connection
3. Create "patterns" collection with metadata
4. Implement `store_pattern()` function
5. Generate embeddings for pattern queries (using sentence-transformers)
6. Test ChromaDB connection and storage

**Acceptance Criteria**:
- AC-022: ChromaDB connection established on startup
- AC-023: Patterns stored with vector embeddings
- AC-024: Pattern metadata includes quality, timestamp, usage_count

**Files to Create**:
- `src/patterns/storage.py`
- `tests/test_pattern_storage.py`

**Configuration**:
```yaml
# Add to .env
CHROMADB_HOST=chromadb
CHROMADB_PORT=8000
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

#### Task 3.2: Pattern Deduplication
**Deliverable**: DEL-005  
**Estimated Time**: 1 day  
**Dependencies**: Task 3.1  

**Subtasks**:
1. Check for similar patterns before storing (cosine similarity > 0.9)
2. If duplicate found, update usage_count instead of creating new
3. Merge patterns if quality improved
4. Handle edge cases (identical query, different reasoning)

**Acceptance Criteria**:
- AC-025: Duplicate patterns not stored
- AC-026: Similar patterns merged or updated
- AC-027: Pattern versioning for improvements

**Files to Modify**:
- `src/patterns/storage.py` (add deduplication logic)

---

#### Task 3.3: Pattern Metadata Management
**Deliverable**: DEL-005  
**Estimated Time**: 0.5 days  
**Dependencies**: Task 3.2  

**Subtasks**:
1. Store pattern metadata in PostgreSQL `pattern_metadata` table
2. Track: quality_score, usage_count, success_count, created_at, updated_at
3. Sync metadata between ChromaDB and PostgreSQL
4. Add pattern ID generation (UUID)

**Acceptance Criteria**:
- AC-028: Pattern metadata stored in PostgreSQL
- AC-029: Metadata queryable for analytics
- AC-030: Metadata updated on pattern reuse

**Files to Modify**:
- `src/db/repository.py` (add pattern metadata methods)
- `src/patterns/storage.py` (sync metadata)

---

### Task Group 4: Pattern Retrieval System (2-3 days)

#### Task 4.1: Similarity Search Implementation
**Deliverable**: DEL-006  
**Estimated Time**: 1.5 days  
**Dependencies**: Task 3.3  

**Subtasks**:
1. Create `src/patterns/retriever.py` module
2. Implement `retrieve_similar_patterns()` function
3. Use ChromaDB similarity search (cosine distance)
4. Return top-k most similar patterns (default k=5)
5. Filter by minimum similarity threshold (> 0.7)
6. Sort by quality * similarity score

**Acceptance Criteria**:
- AC-031: Retrieves top-5 similar patterns for any query
- AC-032: Similarity threshold configurable
- AC-033: Results ranked by quality and similarity

**Files to Create**:
- `src/patterns/retriever.py`
- `tests/test_pattern_retriever.py`

---

#### Task 4.2: Pattern Ranking Algorithm
**Deliverable**: DEL-006  
**Estimated Time**: 1 day  
**Dependencies**: Task 4.1  

**Subtasks**:
1. Implement ranking formula: `score = (similarity * 0.6) + (quality * 0.3) + (success_rate * 0.1)`
2. Consider pattern freshness (recent patterns ranked slightly higher)
3. Consider usage_count (proven patterns ranked higher)
4. Add configurable ranking weights

**Acceptance Criteria**:
- AC-034: Patterns ranked by combined score
- AC-035: Ranking considers similarity, quality, success rate
- AC-036: Recent and frequently used patterns preferred

**Files to Modify**:
- `src/patterns/retriever.py` (add ranking logic)
- `src/core/config.py` (add ranking weights config)

---

#### Task 4.3: Integration with Reasoning Engine
**Deliverable**: DEL-006  
**Estimated Time**: 0.5 days  
**Dependencies**: Task 4.2  

**Subtasks**:
1. Modify `ReasoningEngine.process_query()` to retrieve patterns before reasoning
2. Pass retrieved patterns as context to LLM
3. Log which patterns were used
4. Update pattern usage_count when applied

**Acceptance Criteria**:
- AC-037: Patterns retrieved for every query
- AC-038: Patterns passed as context to reasoning
- AC-039: Pattern usage tracked in metadata

**Files to Modify**:
- `src/reasoning/engine.py` (integrate pattern retrieval)
- `src/patterns/storage.py` (update usage tracking)

---

### Task Group 5: Code Quality Setup (1 day)

#### Task 5.1: Linting and Formatting
**Deliverable**: DEL-022  
**Estimated Time**: 0.5 days  
**Dependencies**: None (can run in parallel)  

**Subtasks**:
1. Add `ruff` for linting (Python linter)
2. Add `black` for code formatting
3. Create `pyproject.toml` with tool configurations
4. Add pre-commit hooks (optional)
5. Run linter on all code, fix issues

**Acceptance Criteria**:
- AC-064: Code linter configured and passing
- AC-065: Code formatter applied consistently
- AC-066: No critical linting errors

**Files to Create**:
- `pyproject.toml`
- `.pre-commit-config.yaml` (optional)

**Commands to Add**:
```bash
# In requirements.txt
ruff==0.1.0
black==23.0.0

# Run linting
docker exec sira-api-dev ruff check src/
docker exec sira-api-dev black --check src/
```

---

#### Task 5.2: Type Checking
**Deliverable**: DEL-022  
**Estimated Time**: 0.5 days  
**Dependencies**: Task 5.1  

**Subtasks**:
1. Add `mypy` for static type checking
2. Add type hints to all new Sprint 2 code
3. Configure mypy strictness level
4. Fix type errors

**Acceptance Criteria**:
- AC-067: Type checker configured
- AC-068: All new code has type hints
- AC-069: No type checking errors

**Files to Modify**:
- `pyproject.toml` (add mypy config)
- All Sprint 2 code files (add type hints)

---

### Task Group 6: Reliability & Error Handling (1-2 days)

#### Task 6.1: Error Handling Enhancement
**Deliverable**: DEL-023  
**Estimated Time**: 1 day  
**Dependencies**: None (can run in parallel)  

**Subtasks**:
1. Add try-except blocks to all critical functions
2. Create custom exception classes (PatternExtractionError, StorageError, etc.)
3. Log errors with context (query_id, session_id)
4. Return meaningful error messages to API
5. Add error recovery strategies (retry logic)

**Acceptance Criteria**:
- AC-070: All critical paths have error handling
- AC-071: Errors logged with full context
- AC-072: API returns clear error messages

**Files to Create**:
- `src/core/exceptions.py` (custom exceptions)

**Files to Modify**:
- All Sprint 2 modules (add error handling)

---

#### Task 6.2: Retry and Fallback Logic
**Deliverable**: DEL-023  
**Estimated Time**: 1 day  
**Dependencies**: Task 6.1  

**Subtasks**:
1. Add retry logic for LLM calls (3 retries with exponential backoff)
2. Add retry for ChromaDB operations
3. Implement fallback: if pattern retrieval fails, continue without patterns
4. Add circuit breaker for external services

**Acceptance Criteria**:
- AC-073: Transient failures retried automatically
- AC-074: System continues functioning if pattern system fails
- AC-075: Retries logged for monitoring

**Files to Modify**:
- `src/llm/client.py` (add retry logic)
- `src/patterns/storage.py` (add retry logic)
- `src/patterns/retriever.py` (add fallback logic)

---

## Sprint 2 Timeline

### Week 1 (Days 1-7)

**Day 1-2**: Task 1.1 + 1.2 (Quality Scoring + Self-Verification)
- ✅ Quality scorer implemented
- ✅ Self-verification logic working
- **Milestone**: Queries have quality scores

**Day 3-4**: Task 1.3 + 2.1 (Metrics Storage + Pattern Extraction)
- ✅ Quality scores in database
- ✅ Pattern extraction from high-quality queries
- **Milestone**: Patterns being extracted

**Day 5-6**: Task 2.2 + 3.1 (Template Generation + ChromaDB Integration)
- ✅ Pattern templates generated
- ✅ ChromaDB storing patterns
- **Milestone**: Patterns stored with embeddings

**Day 7**: Task 3.2 + 3.3 (Deduplication + Metadata)
- ✅ Duplicate patterns merged
- ✅ Pattern metadata tracked
- **Mid-Sprint Review**: Pattern storage complete

---

### Week 2 (Days 8-14)

**Day 8-9**: Task 4.1 + 4.2 (Similarity Search + Ranking)
- ✅ Pattern retrieval working
- ✅ Patterns ranked by quality + similarity
- **Milestone**: Pattern retrieval functional

**Day 10**: Task 4.3 (Integration with Reasoning Engine)
- ✅ Patterns used in reasoning
- ✅ Usage tracking working
- **Milestone**: Full pattern loop working

**Day 11**: Task 5.1 + 5.2 (Code Quality + Type Checking)
- ✅ Linting passing
- ✅ Type checking passing
- **Milestone**: Code quality validated

**Day 12-13**: Task 6.1 + 6.2 (Error Handling + Retry Logic)
- ✅ Error handling robust
- ✅ Retry logic working
- **Milestone**: System reliable

**Day 14**: Integration Testing + Sprint Review
- ✅ End-to-end pattern flow tested
- ✅ All acceptance criteria verified
- ✅ Sprint 2 complete
- **Sprint Review & Demo**

---

## Key Milestones

| Day | Milestone | Status |
|-----|-----------|--------|
| 2 | Quality scoring working | Pending |
| 4 | Pattern extraction working | Pending |
| 7 | Patterns stored in ChromaDB | Pending |
| 10 | Pattern retrieval working | Pending |
| 10 | **End-to-end pattern flow complete** | Pending |
| 14 | Sprint 2 complete | Pending |

---

## Testing Strategy

### Unit Tests (Continuous)
- Test each module independently
- Mock external dependencies (LLM, ChromaDB)
- Target: >80% code coverage on new code

### Integration Tests (Days 10, 14)
- Test full pattern flow: extract → store → retrieve → apply
- Test error scenarios and fallbacks
- Test with real LLM and ChromaDB

### End-to-End Tests (Day 14)
1. Submit query → Extract pattern → Store pattern
2. Submit similar query → Retrieve pattern → Apply pattern → Better response
3. Verify quality scores, storage, retrieval all working

---

## Acceptance Criteria Summary

**Total**: 18 Acceptance Criteria

### DEL-003: Self-Verification Module (9 ACs)
- AC-007 to AC-015: Quality scoring, verification, storage

### DEL-004: Pattern Extraction Engine (6 ACs)
- AC-016 to AC-021: Pattern extraction, templates, validation

### DEL-005: Pattern Storage System (9 ACs)
- AC-022 to AC-030: ChromaDB integration, deduplication, metadata

### DEL-006: Pattern Retrieval System (9 ACs)
- AC-031 to AC-039: Similarity search, ranking, integration

### DEL-022: Code Quality Setup (6 ACs)
- AC-064 to AC-069: Linting, formatting, type checking

### DEL-023: Reliability & Error Handling (6 ACs)
- AC-070 to AC-075: Error handling, retry logic, fallbacks

---

## Success Criteria

### Must Have (All Complete)
1. ✅ Quality scores calculated for all responses
2. ✅ Patterns extracted from high-quality queries (score >= 0.8)
3. ✅ Patterns stored in ChromaDB with embeddings
4. ✅ Similar patterns retrieved for new queries
5. ✅ Patterns applied in reasoning process
6. ✅ All 18 test cases passing
7. ✅ Code quality checks passing (lint, format, types)
8. ✅ Error handling robust with retries

### Nice to Have (If Time Permits)
- Pattern versioning and history
- Pattern analytics dashboard (API endpoint)
- Pattern export/import (defer to Sprint 3 if needed)

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Pattern extraction too slow | High | Medium | Async processing, queue patterns for extraction |
| ChromaDB performance issues | Medium | Low | Add caching layer, limit pattern count per query |
| Quality scoring inaccurate | High | Medium | Use multiple verification methods, tune thresholds |
| Pattern retrieval irrelevant | Medium | Medium | Improve ranking algorithm, add user feedback |

---

## Dependencies

### External Dependencies
- ChromaDB container running (from Sprint 1) ✅
- PostgreSQL schema updated (from Sprint 1) ✅
- LLM integration working (from Sprint 1) ✅

### Sprint 1 Dependencies
- Reasoning engine functional ✅
- Database repository working ✅
- API endpoints responding ✅

---

## Configuration Changes

### New Environment Variables
```bash
# Pattern Settings
PATTERN_MIN_QUALITY=0.8              # Min quality to extract pattern
PATTERN_RETRIEVAL_COUNT=5            # Top-k patterns to retrieve
PATTERN_SIMILARITY_THRESHOLD=0.7     # Min similarity for retrieval
PATTERN_RANKING_WEIGHTS="0.6,0.3,0.1"  # similarity, quality, success_rate

# Quality Scoring
QUALITY_MIN_THRESHOLD=0.7            # Min acceptable quality
QUALITY_GOOD_THRESHOLD=0.8           # Good quality
QUALITY_EXCELLENT_THRESHOLD=0.9      # Excellent quality

# Retry Configuration
LLM_RETRY_ATTEMPTS=3                 # Max retries for LLM calls
LLM_RETRY_DELAY=1                    # Initial delay in seconds
CHROMADB_RETRY_ATTEMPTS=3            # Max retries for ChromaDB
```

---

## Files to Create (New: 15 files)

### Pattern System
- `src/patterns/__init__.py`
- `src/patterns/models.py`
- `src/patterns/extractor.py`
- `src/patterns/storage.py`
- `src/patterns/retriever.py`

### Quality System
- `src/quality/__init__.py`
- `src/quality/scorer.py`

### Core
- `src/core/exceptions.py`

### Configuration
- `pyproject.toml`
- `.pre-commit-config.yaml` (optional)

### Tests
- `tests/test_quality_scorer.py`
- `tests/test_pattern_extractor.py`
- `tests/test_pattern_storage.py`
- `tests/test_pattern_retriever.py`
- `tests/test_pattern_flow.py` (end-to-end)

---

## Files to Modify (15+ files)

- `src/reasoning/engine.py` - Integrate pattern retrieval
- `src/db/repository.py` - Add pattern metadata methods
- `src/api/schemas.py` - Add quality score to responses
- `src/core/config.py` - Add pattern and quality settings
- `src/llm/client.py` - Add retry logic
- `ops/docker/init-db.sql` - Add quality_score column
- `requirements.txt` - Add ruff, black, mypy
- All Sprint 2 code files - Add error handling and type hints

---

## Definition of Done

Sprint 2 is complete when:

1. ✅ All 6 deliverables implemented
2. ✅ All 18 acceptance criteria passing
3. ✅ All 18 test cases passing
4. ✅ Code quality checks passing (ruff, black, mypy)
5. ✅ End-to-end pattern flow tested and working
6. ✅ Documentation updated
7. ✅ Sprint demo completed
8. ✅ Code reviewed and merged to sprint-2 branch

---

## Next Steps

### Immediate Actions
1. ✅ Review this plan with team/stakeholders
2. 🔨 Create `sprint-2` branch from main
3. 🔨 Start Task 1.1 (Quality Scoring Implementation)
4. 🔨 Set up daily standup schedule

### After Sprint 2
1. Sprint 2 retrospective
2. Update documentation with learnings
3. Sprint 3 planning (Community Learning)
4. Merge sprint-2 to main

---

**Status**: ✅ Ready for Execution  
**Prepared by**: SIRA Planning Team  
**Date**: 2025-11-15  
**Next Sprint**: Sprint 3 - Community Learning & Integration
