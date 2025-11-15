# Tech Stack & Language - SIRA

## Technology Decisions & Rationale

### Programming Languages: Python 3.12 + MATLAB

**Decision:** Hybrid Python + MATLAB architecture

**Python 3.12 - Online/Real-time System**

**Rationale:**
- **AI/ML Ecosystem:** Best-in-class libraries for LLM integration, embeddings, and NLP
- **Async Support:** Mature async/await for non-blocking I/O (critical for LLM API calls)
- **Type Safety:** Type hints and mypy for static analysis
- **Web/API:** FastAPI for REST endpoints, excellent async performance
- **Community:** Large ecosystem of AI/ML practitioners and libraries

**MATLAB - Offline Analysis & Optimization**

**Rationale:**
- **Numerical Optimization:** World-class optimization toolbox (fmincon, GA, Bayesian optimization)
- **Statistical Modeling:** Advanced regression, time-series, and predictive modeling
- **Signal Processing:** Unmatched for time-series analysis (DTW, cross-correlation)
- **Competitive Edge:** Underutilized in AI agent space - gives SIRA unique advantage
- **Visualization:** Superior plotting and dashboard capabilities
- **Matrix Operations:** Optimized for large-scale numerical computations

**Why Hybrid (Not Python-Only)?**
- **Best Tool for Job:** Python excels at I/O, APIs, general programming; MATLAB excels at quant analysis
- **Competitive Differentiation:** Others use only Python - MATLAB gives us an edge
- **Clean Separation:** File-based integration keeps systems decoupled
- **No Performance Impact:** MATLAB runs offline/batch, doesn't affect agent latency

**Alternatives Considered:**
- Python-only with scipy/scikit-learn: Less mature optimization than MATLAB, no competitive edge
- Python + R: R weaker for optimization, less familiar to team
- TypeScript/Node.js: Less mature AI/ML ecosystem, no quant advantage
- Go: Excellent performance but limited AI/ML libraries and no quant tools
- Rust: Overkill for research/prototype phase, steeper learning curve

---

### API Framework: FastAPI

**Decision:** FastAPI for REST API

**Rationale:**
- **Async Native:** Built on Starlette, fully async-capable
- **Type Safety:** Leverages Python type hints for automatic validation
- **Auto Documentation:** OpenAPI/Swagger docs generated automatically
- **Performance:** Among fastest Python frameworks
- **Developer Experience:** Intuitive, well-documented, modern

**Alternatives Considered:**
- Flask: Lacks native async support, more boilerplate
- Django: Too heavyweight for API-focused application
- Django REST Framework: Overkill, includes ORM we don't need full features of

---

### Relational Database: PostgreSQL

**Decision:** PostgreSQL for structured data

**Rationale:**
- **Reliability:** Industry-standard, ACID-compliant
- **JSON Support:** JSONB for flexible schema (reasoning traces)
- **Performance:** Excellent query performance with proper indexing
- **Extensions:** Rich ecosystem (could add pgvector later if needed)
- **Docker Support:** Official images, easy containerization

**Alternatives Considered:**
- MySQL: Less robust JSON support
- SQLite: Not suitable for concurrent access patterns
- MongoDB: Overkill for our structured data needs

**Data Stored:**
- Sessions (ID, timestamps, user context)
- Queries and responses
- Metrics (performance, accuracy, reuse rates)
- Pattern metadata (quality scores, usage counts)

---

### Vector Database: ChromaDB

**Decision:** ChromaDB for pattern embeddings

**Rationale:**
- **Simplicity:** Easy to set up and use, minimal configuration
- **Python-Native:** Excellent Python client library
- **Embeddings:** Built-in support for embedding generation
- **Performance:** Fast similarity search for our scale (<100K patterns)
- **Local-First:** Can run embedded or as server
- **Open Source:** Active development, good documentation

**Alternatives Considered:**
- Pinecone: Cloud-only, cost concerns, overkill for our scale
- Weaviate: More complex setup, feature-heavy
- Qdrant: Good option, but ChromaDB simpler for our needs
- pgvector: Considered but separate vector DB cleaner separation

**Data Stored:**
- Reasoning pattern embeddings (384-dimensional vectors)
- Pattern metadata and context
- Usage statistics per pattern

---

### LLM Integration

**Decision:** Local-first LLM runtime (self-hosted open models) behind a provider-agnostic interface.

**Rationale:**
- **Cost Control:** No per-query API fees; inference runs on owned hardware
- **Privacy:** Reasoning data stays local, no external LLM providers by default
- **Flexibility:** Swap open models (Llama, Qwen, Mixtral, etc.) without changing application code
- **Abstraction:** Orchestrator interface enables multiple runtimes/models in future

**Primary Approach (Phase 1):**
- Single local LLM runtime exposing an OpenAI-style HTTP API
- One or more open models configured via environment variables

**Future Options (Phase 2+):**
- Multiple local runtimes/models (e.g., general_reasoner vs critic)
- Optional external providers as rare fallbacks (not required for normal SIRA usage)

---

### Embeddings: sentence-transformers

**Decision:** sentence-transformers library for pattern embeddings

**Rationale:**
- **Quality:** High-quality semantic embeddings
- **Performance:** Fast inference, can run locally
- **Model Selection:** Many pre-trained models available
- **No API Dependency:** Runs in-process, no external calls
- **Cost:** Free, unlike OpenAI embeddings API

**Model:** `all-MiniLM-L6-v2`
- 384 dimensions (good balance of size/quality)
- Fast inference (<50ms per embedding)
- Proven effectiveness for semantic similarity

---

### Containerization: Docker & Docker Compose

**Decision:** Docker for all environments, Docker Compose for orchestration

**Rationale:**
- **Isolation:** No host dependencies, consistent environments
- **Reproducibility:** Same environment in dev/test/prod
- **Multi-Service:** Easily orchestrate API, PostgreSQL, ChromaDB
- **Environment Profiles:** Separate compose files for dev vs test
- **Standard Practice:** Industry standard, well-documented

**Container Strategy:**
- `sira-api`: Main application container
- `postgres`: Official PostgreSQL image
- `chromadb`: Official ChromaDB server image
- Separate networks for isolation
- Volume mounts for data persistence

---

### Testing: pytest

**Decision:** pytest for all testing

**Rationale:**
- **Python Standard:** De facto standard for Python testing
- **Fixtures:** Excellent fixture system for setup/teardown
- **Async Support:** pytest-asyncio for async test functions
- **Parametrization:** Easy to test multiple scenarios
- **Coverage:** pytest-cov for coverage reports

**Test Structure:**
- Unit tests: `tests/unit/` (reasoning, learning, verification)
- Integration tests: `tests/integration/` (API endpoints, database)
- No mocks: Real databases in Docker test profile

---

### Logging: structlog

**Decision:** structlog for structured logging

**Rationale:**
- **Structured:** JSON output for easy parsing
- **Context:** Bind context (request_id, session_id) to log entries
- **Performance:** Minimal overhead
- **Integration:** Works well with Python logging

**Log Levels:**
- DEBUG: Detailed reasoning steps, LLM prompts/responses
- INFO: Query processing, pattern retrieval
- WARNING: Low confidence results, pattern quality issues
- ERROR: API failures, database errors

---

### ORM: SQLAlchemy (async)

**Decision:** SQLAlchemy with async support

**Rationale:**
- **Async Native:** SQLAlchemy 2.0+ with asyncpg driver
- **Type Safety:** Compatible with Python type hints
- **Migrations:** Alembic for schema migrations
- **Query Building:** Expressive query API
- **Connection Pooling:** Built-in pool management

---

### Code Quality Tools

**Linting & Formatting:**
- **black:** Code formatting (opinionated, consistent)
- **ruff:** Fast linting (replaces flake8, isort, etc.)
- **mypy:** Static type checking

**Pre-commit Hooks (future):**
- Format with black
- Lint with ruff
- Type-check with mypy
- Run fast unit tests

---

### Development Environment

**Editor/IDE Support:**
- VS Code with Python extension
- PyCharm Professional
- Type hints enable excellent autocomplete

**Virtual Environment:**
- All dependencies in Docker containers
- No local Python dependencies required
- Development via Docker Compose dev profile

---

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language (Online) | Python | 3.12 | Agent, API, databases |
| Language (Offline) | MATLAB | R2023b+ | Analysis, optimization |
| API Framework | FastAPI | 0.100+ | REST API |
| Relational DB | PostgreSQL | 16 | Structured data |
| Vector DB | ChromaDB | 0.4+ | Pattern embeddings |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Async Driver | asyncpg | 0.29+ | PostgreSQL async |
| Embeddings | sentence-transformers | 2.2+ | Pattern vectors |
| LLM Runtime | Ollama / vLLM / similar | Latest | Local LLM serving |
| LLM Models | Llama 3 / Qwen 2.5 / Mixtral | Latest | Reasoning & verification |
| Testing (Python) | pytest | 8.0+ | Unit/integration tests |
| Testing (MATLAB) | MATLAB Test Framework | Built-in | MATLAB unit tests |
| Logging | structlog | 24.0+ | Structured logging |
| Validation | Pydantic | 2.0+ | Data validation |
| HTTP Client | httpx | 0.27+ | Async HTTP |
| Container | Docker | 24+ | Containerization |
| Orchestration | Docker Compose | 2.20+ | Multi-container |

---

## Dependencies Management

**requirements.txt Structure:**
```
# Core
fastapi>=0.100.0
uvicorn[standard]>=0.23.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# Database
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.12.0

# Vector DB
chromadb>=0.4.0

# LLM Integration
httpx>=0.27.0

# Embeddings
sentence-transformers>=2.2.0

# Logging
structlog>=24.0.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0

# Code Quality
black>=24.0.0
ruff>=0.1.0
mypy>=1.7.0
```

---

## Python-MATLAB Integration

### Communication Pattern: File-Based

**Python → MATLAB:**
- Episode logs: `/data/logs/run_{id}/episodes.jsonl`
- Summary metrics: `/data/logs/run_{id}/episodes_summary.csv`
- Reasoning traces: `/data/logs/run_{id}/traces/*.json`
- Embeddings (optional): `/data/logs/run_{id}/embeddings.npy`

**MATLAB → Python:**
- Tuned configs: `/data/config/sira_tuned_{timestamp}.json`
- Strategy policies: `/data/config/strategy_policy.json`
- Analysis reports: `/data/reports/*.pdf`, `*.png`, `*.json`

**Why File-Based (Not API)?**
- Clean decoupling (no tight coupling)
- Docker-friendly (shared volume)
- No latency impact on Python agent
- Simple to test and debug
- MATLAB can run offline/batch

### MATLAB Toolboxes Required

**Essential:**
- **Optimization Toolbox:** Hyperparameter tuning, reward shaping
- **Statistics and Machine Learning Toolbox:** Regression, classification, learning curves
- **Signal Processing Toolbox:** DTW, cross-correlation, pattern analysis

**Optional:**
- **Deep Learning Toolbox:** If training custom models
- **Parallel Computing Toolbox:** Speed up batch analysis
- **Database Toolbox:** Direct PostgreSQL access (alternative to files)

### MATLAB Deployment Options

**Development:**
- Full MATLAB installation with all toolboxes
- Interactive development and visualization

**Production:**
- **MATLAB Runtime (Free):** Run compiled MATLAB code without license
- **MATLAB Production Server:** Enterprise-scale deployment (future)
- **Docker:** Use official `mathworks/matlab` or `mathworks/matlab-runtime` images

**Licensing Strategy:**
- Dev: Full MATLAB license (1-2 seats)
- Test/Prod: MATLAB Runtime (no cost)
- Compile MATLAB code to standalone executables for deployment

---

## Port Assignments

| Service | Port | Purpose |
|---------|------|---------|
| SIRA API (Python) | 8080 | REST API, Web UI |
| PostgreSQL | 5432 | Database (internal) |
| ChromaDB | 8000 | Vector DB (internal) |
| MATLAB (optional) | 9090 | MATLAB web server (if used) |

---

See also:
- `solution-architecture.md` - Architecture overview
- `deployment-topology.md` - Docker configuration details
- `decisions/adr-001-python-matlab-hybrid.md` - Hybrid architecture ADR
