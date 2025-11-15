# Test Plan - SIRA Phase 1

**Version:** 1.0  
**Phase:** 1 (Foundation)  
**Last Updated:** 2025-11-15

## Test Strategy

**Approach:** Continuous testing with no mock data - all tests use real databases in Docker containers.

**Test Levels:**
1. **Unit Tests:** Individual functions/classes
2. **Integration Tests:** API endpoints, database operations, LLM calls
3. **E2E Tests:** Complete query→reasoning→response flows
4. **Performance Tests:** Response times, load testing

**No Mock Data Rule:** All tests use real PostgreSQL and ChromaDB running in test containers (tmpfs for speed).

## Test Environment

**Docker Test Profile:** `docker-compose.test.yml`
- sira-test container (runs pytest)
- postgres-test (in-memory tmpfs)
- chromadb-test (in-memory tmpfs)

**Execution:** `docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit`

## Test Coverage Goals

- Overall: >70%
- Critical paths (reasoning, patterns, LLM): >90%
- Measure: `pytest --cov=src --cov-report=term-missing`

## Test Execution Per Sprint

**Sprint 1:** 33 TCs (infrastructure, API, databases)  
**Sprint 2:** 18 TCs (pattern learning, quality)  
**Sprint 3:** 12 TCs (integration, MATLAB)

**Gate:** All tests pass before marking deliverable "Done"

## Test Data Strategy

See `test-data-strategy.md` for details.

**Summary:**
- Sample queries (math, coding, reasoning)
- Seed patterns for retrieval testing
- Load test generators (100K patterns/queries)
- No shared fixtures - tests create their own data

## Test Reporting

- Console output during test run
- Coverage report in terminal
- pytest HTML report (optional)
- Test status tracked in `test-cases.md`

## Definition of Done (Testing)

For each deliverable:
1. All related TCs PASS
2. Coverage targets met
3. No failing tests in full suite
4. Test status updated in `test-cases.md`
