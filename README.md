# SIRA - Self-Improving Reasoning Agent

A local, cost-free reasoning AI system that learns from usage and optionally benefits from community patterns.

## 🎯 Overview

SIRA (Self-Improving Reasoning Agent) is an AI reasoning system that:
- Uses a **local LLM** (no external API costs)
- Shows **explicit reasoning steps** before answering
- **Learns from usage** to improve over time
- Supports **community pattern sharing** (opt-in, privacy-preserving)

## ✨ Current Status: Sprint 1 Complete ✅

All 12 Sprint 1 deliverables implemented and tested:

### Infrastructure
- ✅ Local LLM Runtime (Ollama with llama3:8b)
- ✅ Docker Infrastructure (4 containers)
- ✅ Database Schema (PostgreSQL + ChromaDB)
- ✅ Configuration System
- ✅ Structured Logging
- ✅ Security Implementation

### Application
- ✅ REST API (FastAPI with 5 endpoints)
- ✅ Query Processing with Reasoning Steps
- ✅ Reasoning Engine (2-phase processing)
- ✅ LLM Integration Layer
- ✅ Session Management
- ✅ Testing Framework

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- 8GB+ RAM available
- Windows/Linux/Mac

### Run SIRA

```bash
# Clone repository
git clone https://github.com/rizkhan786/sira.git
cd sira/ops/docker

# Copy environment file
cp .env.example .env

# Start all services
docker compose up -d

# Download LLM model (one-time, ~4.7GB)
docker exec sira-llm ollama pull llama3:8b

# Wait for all containers to be healthy (~30 seconds)
docker ps
```

### Test It Out

Open browser: **http://localhost:8080/docs**

Try this query in Swagger UI:
```json
{
  "query": "What is 2+2?"
}
```

You'll see:
- **Response**: The answer
- **Reasoning Steps**: 3-5 steps showing how SIRA arrived at the answer
- **Metadata**: Processing time, token usage, session ID

## 📊 Example Response

```json
{
  "response": "2+2 equals 4...",
  "reasoning_steps": [
    {
      "step_number": 1,
      "description": "Define what we mean by '2+2'...",
      "timestamp": "2025-11-15T12:00:00Z"
    },
    {
      "step_number": 2,
      "description": "Recall basic arithmetic rules...",
      "timestamp": "2025-11-15T12:00:01Z"
    },
    {
      "step_number": 3,
      "description": "Apply the addition rule...",
      "timestamp": "2025-11-15T12:00:02Z"
    }
  ],
  "metadata": {
    "session_id": "abc-123-def",
    "processing_time_seconds": 45.2,
    "llm_usage": {
      "prompt_tokens": 199,
      "completion_tokens": 115,
      "total_tokens": 314
    }
  }
}
```

## 📡 API Endpoints

- `GET /` - API information
- `GET /health` - Health check (LLM + Database status)
- `POST /query` - Process a query (returns reasoning steps)
- `POST /session` - Create new session
- `GET /session/{id}` - Get session info
- `GET /session/{id}/history` - Get query history

Full documentation: http://localhost:8080/docs

## 🏗️ Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│  FastAPI    │ (Port 8080)
│  sira-api   │
└──────┬──────┘
       │
   ┌───┴────┬────────┬─────────┐
   │        │        │         │
   ▼        ▼        ▼         ▼
┌──────┐ ┌──────┐ ┌─────┐ ┌────────┐
│Ollama│ │Postgres│ │Chroma│ │  Data  │
│:11434│ │ :5433 │ │:8000│ │Volumes │
└──────┘ └──────┘ └─────┘ └────────┘
```

## 📈 Roadmap

### ✅ Phase 1 - Sprint 1 (Complete)
Foundation infrastructure and core API

### 🔨 Phase 1 - Sprint 2 (Next)
Self-improvement features:
- Pattern extraction from successful queries
- Pattern storage and retrieval
- Quality scoring
- Feedback loop

### 🔮 Phase 1 - Sprint 3 (Planned)
Community learning:
- Pattern export/import
- Privacy-preserving sharing
- Community pattern repository
- Federated learning

## 🔒 Privacy & Cost

### Privacy
- **All data stays local** by default
- Community learning is **opt-in**
- Patterns anonymized before sharing
- No external API calls (unless you enable community features)

### Cost
- **$0 per query** (runs on your hardware)
- One-time model download (~4.7GB)
- Compare to:
  - GPT-4: ~$0.03-0.06 per query
  - GPT-3.5: ~$0.002 per query

## 💻 Development

### Project Structure
```
sira/
├── src/
│   ├── api/          # FastAPI application
│   ├── reasoning/    # Reasoning engine
│   ├── llm/          # LLM client
│   ├── db/           # Database access
│   └── core/         # Config & logging
├── tests/            # Integration tests
├── ops/docker/       # Docker setup
└── docs/             # Documentation
```

### Run Tests
```bash
docker exec sira-api-dev pytest
```

### View Logs
```bash
docker compose logs -f sira-api-dev
```

## 📚 Documentation

- [Project Plan](PROJECT_PLAN.md)
- [Sprint 1 Completion Report](docs/testing/sprint1-completion-report.md)
- [Infrastructure Test Report](docs/testing/sprint1-infrastructure-test-report.md)
- [Requirements](docs/10-Requirements/)
- [Architecture](docs/20-Solution/)
- [Sprint Planning](docs/30-Planning/)

## 🤝 Contributing

This project follows sprint-based development:
- Each sprint has its own branch (`sprint-1`, `sprint-2`, etc.)
- All work happens in sprints (see [warp.md](warp.md))
- No work outside sprints

## 📝 License

[To be added]

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Ollama](https://ollama.ai/)
- [LLaMA 3](https://ai.meta.com/llama/)
- [PostgreSQL](https://www.postgresql.org/)
- [ChromaDB](https://www.trychroma.com/)

---

**Current Version**: 0.1.0 (Sprint 1)  
**Status**: ✅ Fully Functional  
**Last Updated**: 2025-11-15
