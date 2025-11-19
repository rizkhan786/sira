# SIRA Quick Start Guide

## Starting SIRA

Simply run:
```powershell
.\start-sira.ps1
```

This will:
- Start all SIRA containers (API, Database, ChromaDB, LLM)
- Wait for services to be healthy
- Test the API
- Display access URLs

## Stopping SIRA

```powershell
.\stop-sira.ps1
```

## Access Points

Once SIRA is running:

- **API Documentation (Interactive)**: http://localhost:8080/docs
- **API Health Check**: http://localhost:8080/health
- **Metrics Summary**: http://localhost:8080/metrics/summary
- **Metrics Trends**: http://localhost:8080/metrics/trends?days=7
- **Complete Metrics**: http://localhost:8080/metrics?days=7

## Container Names

All SIRA containers are prefixed with `sira-`:

- `sira-api-dev` - Main API service (port 8080)
- `sira-postgres` - PostgreSQL database (port 5433)
- `sira-chromadb` - Vector database for patterns (port 8000)
- `sira-llm` - Ollama LLM service (port 11434)

## Checking Logs

```powershell
# API logs
docker logs sira-api-dev

# Database logs
docker logs sira-postgres

# Follow logs in real-time
docker logs -f sira-api-dev
```

## Troubleshooting

**API not responding?**
1. Check if containers are running:
   ```powershell
   docker ps --filter "name=sira-"
   ```

2. Check API logs:
   ```powershell
   docker logs sira-api-dev --tail 50
   ```

3. Restart everything:
   ```powershell
   .\stop-sira.ps1
   .\start-sira.ps1
   ```

**Port conflicts?**
If ports 8080, 5433, 8000, or 11434 are already in use, you'll need to stop the conflicting service or modify `ops/docker/docker-compose.yml`.

## Testing Sprint 3 Features

See [TESTING.md](./docs/testing/SPRINT3_TESTING.md) for detailed browser-based testing instructions.

Quick test:
1. Open http://localhost:8080/docs
2. Try the `POST /query` endpoint
3. Check http://localhost:8080/metrics/summary
