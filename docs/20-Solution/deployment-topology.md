# Deployment Topology - SIRA

## Overview

SIRA uses Docker Desktop with Docker Compose for consistent deployment across all environments. Two profiles are defined:
- **Dev Profile:** Interactive development with hot-reload
- **Test Profile:** Automated test execution

## Container Architecture

```
┌──────────────────────────────────────────────────┐
│         Docker Desktop (Windows)                  │
│                                                   │
│  ┌─────────────────────────────────────────────┐ │
│  │   Docker Network: sira_network              │ │
│  │                                             │ │
│  │  ┌──────────────┐                          │ │
│  │  │  sira-api    │                          │ │
│  │  │  Port: 8080  │◄─────────────────────────┼─┼─── Host: http://localhost:8080
│  │  └───────┬──────┘                          │ │
│  │          │                                  │ │
│  │          ├─────────────┬──────────────┐    │ │
│  │          │             │              │    │ │
│  │  ┌───────▼──────┐ ┌────▼────────┐    │    │ │
│  │  │  postgres    │ │  chromadb   │    │    │ │
│  │  │  Port: 5432  │ │  Port: 8000 │    │    │ │
│  │  └──────────────┘ └─────────────┘    │    │ │
│  │                                       │    │ │
│  │                                       │    │ │
│  │  ┌────────────────────────────────────▼──┐ │ │
│  │  │         Shared Volume: /data         │ │ │
│  │  │  ┌─────────┬─────────┬──────────┐   │ │ │
│  │  │  │  logs/  │ config/ │ reports/ │   │ │ │
│  │  │  └─────────┴─────────┴──────────┘   │ │ │
│  │  └─────────────┬──────────────────────┘ │ │
│  │                │                          │ │
│  │  ┌─────────────▼──────────────┐          │ │
│  │  │  sira-matlab               │          │ │
│  │  │  (Analysis Engine)         │          │ │
│  │  │  Runs periodically/on-demand│         │ │
│  │  └────────────────────────────┘          │ │
│  │                                           │ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Volumes:                                       │
│  - postgres_data (persistent)                   │
│  - chromadb_data (persistent)                   │
│  - sira_data (shared /data volume)              │
│  - ./src (dev: bind mount)                      │
│  - ./matlab (dev: bind mount for MATLAB code)  │
└──────────────────────────────────────────────────┘
```

## Docker Compose Configuration

### Dev Profile (docker-compose.yml)

**Location:** `ops/docker/docker-compose.yml`

```yaml
version: '3.8'

services:
  sira-api:
    build:
      context: ../..
      dockerfile: ops/docker/Dockerfile
    container_name: sira-api-dev
    ports:
      - "8080:8080"
    volumes:
      - ../../src:/app/src  # Hot-reload in dev
    environment:
      - ENV=development
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
      - POSTGRES_DB=sira
      - POSTGRES_USER=sira
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - CHROMADB_HOST=chromadb
      - CHROMADB_PORT=8000
      - LLM_BASE_URL=${LLM_BASE_URL:-http://sira-llm:11434}
      - LLM_MODEL_GENERAL=${LLM_MODEL_GENERAL:-llama3:8b}
      - LOG_LEVEL=DEBUG
    depends_on:
      postgres:
        condition: service_healthy
      chromadb:
        condition: service_started
    networks:
      - sira_network
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8080 --reload

  postgres:
    image: postgres:16-alpine
    container_name: sira-postgres
    environment:
      - POSTGRES_DB=sira
      - POSTGRES_USER=sira
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ../../ops/docker/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"  # Exposed for debugging only
    networks:
      - sira_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sira"]
      interval: 5s
      timeout: 5s
      retries: 5

  chromadb:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: sira-chromadb
    volumes:
      - chromadb_data:/chroma/chroma
    environment:
      - IS_PERSISTENT=TRUE
      - ANONYMIZED_TELEMETRY=FALSE
    ports:
      - "8000:8000"  # Exposed for debugging only
    networks:
      - sira_network

  sira-matlab:
    image: mathworks/matlab:r2023b
    # Alternative for production: mathworks/matlab-runtime:r2023b
    container_name: sira-matlab
    volumes:
      - sira_data:/data  # Shared volume for logs, configs, reports
      - ../../matlab:/app/matlab  # MATLAB code (dev only)
    environment:
      - MLM_LICENSE_FILE=${MATLAB_LICENSE_FILE}  # License server or file
    networks:
      - sira_network
    command: |
      bash -c '
        # Run analysis script periodically (every hour)
        while true; do
          cd /app/matlab && matlab -batch "run_analysis"
          sleep 3600
        done
      '
    # For on-demand execution, use:
    # command: tail -f /dev/null  # Keep container running
    # Then manually trigger: docker exec -it sira-matlab matlab -batch "run_analysis"

networks:
  sira_network:
    driver: bridge

volumes:
  postgres_data:
  chromadb_data:
  sira_data:  # Shared data volume for Python-MATLAB integration
```

### Test Profile (docker-compose.test.yml)

**Location:** `ops/docker/docker-compose.test.yml`

```yaml
version: '3.8'

services:
  sira-test:
    build:
      context: ../..
      dockerfile: ops/docker/Dockerfile
    container_name: sira-test
    environment:
      - ENV=test
      - POSTGRES_HOST=postgres-test
      - POSTGRES_PORT=5432
      - POSTGRES_DB=sira_test
      - POSTGRES_USER=sira_test
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - CHROMADB_HOST=chromadb-test
      - CHROMADB_PORT=8000
      - LLM_BASE_URL=${LLM_BASE_URL:-http://sira-llm:11434}
      - LLM_MODEL_GENERAL=${LLM_MODEL_GENERAL:-llama3:8b}
      - LOG_LEVEL=INFO
    depends_on:
      postgres-test:
        condition: service_healthy
      chromadb-test:
        condition: service_started
    networks:
      - sira_test_network
    command: pytest tests/ -v --cov=src --cov-report=term-missing
    volumes:
      - ../../tests:/app/tests  # Test code
      - ../../src:/app/src      # Source code for coverage

  postgres-test:
    image: postgres:16-alpine
    container_name: sira-postgres-test
    environment:
      - POSTGRES_DB=sira_test
      - POSTGRES_USER=sira_test
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    tmpfs:
      - /var/lib/postgresql/data  # In-memory for speed
    networks:
      - sira_test_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sira_test"]
      interval: 2s
      timeout: 3s
      retries: 5

  chromadb-test:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: sira-chromadb-test
    tmpfs:
      - /chroma/chroma  # In-memory for speed
    environment:
      - IS_PERSISTENT=FALSE
      - ANONYMIZED_TELEMETRY=FALSE
    networks:
      - sira_test_network

networks:
  sira_test_network:
    driver: bridge
```

## Dockerfile

**Location:** `ops/docker/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/

# Create non-root user
RUN useradd -m -u 1000 sira && chown -R sira:sira /app
USER sira

# Expose port
EXPOSE 8080

# Default command (overridden in compose files)
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

## Environment Configuration

**Location:** `ops/docker/.env.example`

```bash
# PostgreSQL
POSTGRES_PASSWORD=sira_dev_password_change_me

# Local LLM Runtime Configuration
LLM_BASE_URL=http://sira-llm:11434
LLM_MODEL_GENERAL=llama3:8b
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# (Optional) External LLM API Keys for rare fallback use
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Reasoning Configuration
MAX_REASONING_ITERATIONS=3
MIN_CONFIDENCE_THRESHOLD=0.7
PATTERN_RETRIEVAL_COUNT=5

# MATLAB Configuration
MATLAB_LICENSE_FILE=27000@license.example.com
# Or for license file: MATLAB_LICENSE_FILE=/path/to/license.lic
# For MATLAB Runtime (free), leave empty or comment out

# MATLAB Analysis Configuration
MATLAB_ANALYSIS_INTERVAL=3600  # Run analysis every hour (in seconds)
MATLAB_ENABLE=true  # Set to false to disable MATLAB analysis

# Logging
LOG_LEVEL=INFO
```

**Instructions:**
1. Copy `.env.example` to `.env`
2. Update PostgreSQL password and local LLM runtime settings (base URL, model)
3. Only set external LLM API keys if you explicitly want a paid fallback
4. Never commit `.env` to version control

## Database Initialization

**Location:** `ops/docker/init-db.sql`

```sql
-- Database initialization script
-- Runs automatically on first PostgreSQL container start

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_context JSONB,
    last_activity TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create queries table
CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    reasoning_trace JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    iterations INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create metrics table
CREATE TABLE IF NOT EXISTS metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_id UUID NOT NULL REFERENCES queries(id) ON DELETE CASCADE,
    accuracy FLOAT,
    pattern_reuse_count INT NOT NULL DEFAULT 0,
    self_correction_count INT NOT NULL DEFAULT 0,
    reasoning_depth INT NOT NULL,
    response_time_ms INT NOT NULL,
    llm_calls INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create pattern_metadata table
CREATE TABLE IF NOT EXISTS pattern_metadata (
    id UUID PRIMARY KEY,
    quality_score FLOAT NOT NULL,
    usage_count INT NOT NULL DEFAULT 0,
    success_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_queries_session_id ON queries(session_id);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);
CREATE INDEX IF NOT EXISTS idx_metrics_query_id ON metrics(query_id);
CREATE INDEX IF NOT EXISTS idx_metrics_created_at ON metrics(created_at);
CREATE INDEX IF NOT EXISTS idx_pattern_metadata_quality ON pattern_metadata(quality_score DESC);
CREATE INDEX IF NOT EXISTS idx_pattern_metadata_usage ON pattern_metadata(usage_count DESC);
```

## Usage Commands

### Development

```powershell
# Start dev environment
cd ops/docker
docker-compose up --build

# Stop dev environment
docker-compose down

# View logs
docker-compose logs -f sira-api

# Restart API only
docker-compose restart sira-api

# Clean up (including volumes)
docker-compose down -v
```

### Testing

```powershell
# Run tests
cd ops/docker
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# View test output
docker-compose -f docker-compose.test.yml logs sira-test

# Clean up test environment
docker-compose -f docker-compose.test.yml down
```

### Database Access

```powershell
# Connect to PostgreSQL (dev)
docker exec -it sira-postgres psql -U sira -d sira

# Run migrations (future)
docker exec -it sira-api-dev alembic upgrade head
```

## Network Configuration

**Internal Network:** `sira_network` (dev) / `sira_test_network` (test)
- All containers communicate via container names
- Isolated from host network except exposed ports

**Service Discovery:**
- API references databases by hostname: `postgres`, `chromadb`
- No hardcoded IPs required

## Volume Strategy

### Development (Persistent)
- `postgres_data`: Database persists across restarts
- `chromadb_data`: Patterns persist across restarts
- `./src`: Bind mount for hot-reload

### Test (Ephemeral)
- `tmpfs` for databases (in-memory, fast)
- No persistence needed (clean state per run)

## Port Mapping

| Service | Internal Port | External Port (Dev) | Purpose |
|---------|---------------|---------------------|---------|
| SIRA API | 8080 | 8080 | Application access |
| PostgreSQL | 5432 | 5432 (debug only) | Database |
| ChromaDB | 8000 | 8000 (debug only) | Vector DB |

**Note:** In production, only expose 8080 (API). Database ports for debugging only.

## Resource Requirements

**Minimum (Dev):**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB

**Recommended (Dev):**
- CPU: 4 cores
- RAM: 8 GB
- Disk: 20 GB

**Test Profile:**
- Similar to dev but uses in-memory databases (faster, less disk)

## Health Checks

**PostgreSQL:**
- Command: `pg_isready -U sira`
- Interval: 5s (dev) / 2s (test)
- Retries: 5

**SIRA API (future):**
- Endpoint: `GET /health`
- Returns: `{"status": "healthy", "version": "x.y.z"}`

**ChromaDB:**
- No health check (starts quickly)
- API depends on it via Docker Compose

## Troubleshooting

**Container won't start:**
```powershell
docker-compose logs [service-name]
docker ps -a  # Check exit codes
```

**Database connection issues:**
```powershell
# Check network
docker network inspect sira_network

# Test connection
docker exec -it sira-api-dev ping postgres
```

**Port already in use:**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Change port in docker-compose.yml
ports:
  - "8081:8080"  # Host:Container
```

**Volumes not updating:**
```powershell
# Rebuild without cache
docker-compose build --no-cache

# Remove volumes
docker-compose down -v
```

---

See also:
- `solution-architecture.md` - Architecture overview
- `tech-stack-and-language.md` - Technology choices
