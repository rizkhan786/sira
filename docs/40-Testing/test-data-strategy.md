# Test Data Strategy - SIRA

**Last Updated:** 2025-11-15  
**Phase:** 1

## No Mock Data Policy

**Rule:** All tests use real data with real databases. No mocks.

**Rationale:** Errors must be visible. Mock data masks real issues.

## Test Data Categories

### 1. Sample Queries
**Purpose:** Test reasoning engine with varied input

**Examples:**
- Math: "What is 15% of 240?"
- Coding: "Write a Python function to reverse a string"
- Reasoning: "If all roses are flowers and some flowers fade quickly, what can we conclude?"
- General: "Explain why the sky is blue"

**Storage:** `tests/data/sample_queries.json`

### 2. Seed Patterns
**Purpose:** Test pattern retrieval

**Content:** Pre-generated patterns with known embeddings for similarity testing

**Storage:** `tests/data/seed_patterns.json`

### 3. Load Test Data
**Purpose:** Performance and scalability testing

**Generators:**
- `tests/data/generate_patterns.py` - Creates 100K patterns
- `tests/data/generate_queries.py` - Creates test query batches

## Test Databases

**PostgreSQL Test:** In-memory (tmpfs) for speed, clean state per run

**ChromaDB Test:** In-memory (tmpfs), ephemeral patterns

**Strategy:** Each test creates needed data, no shared state

## Test Isolation

- Tests run in isolated transactions (rolled back after test)
- Database containers reset between test suite runs
- No cross-test dependencies

## Test Data Management

**Creation:** Tests use factory functions to create test data
**Cleanup:** Automatic via container restart
**Seeding:** Minimal seed data loaded in conftest.py fixtures
