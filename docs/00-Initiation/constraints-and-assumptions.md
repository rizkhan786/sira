# Constraints & Assumptions - SIRA

## Constraints

### Technical Constraints
- **Development Environment:** All development and testing must be containerized in Docker Desktop on Windows
- **No Local Dependencies:** No builds or package installations on host machine
- **LLM Dependency:** Requires local/self-hosted LLM runtime with sufficient compute resources (optional external API fallback)
- **Vector Database:** ChromaDB for pattern storage (separate from relational data)
- **Technology Stack:** Python 3.12 (online), MATLAB R2023b+ (offline analysis), FastAPI, PostgreSQL, ChromaDB
- **MATLAB Licensing:** Requires MATLAB license for development; MATLAB Runtime (free) for production
- **Integration Pattern:** File-based communication via shared Docker volume
- **Port:** Default port 8080 (Python API)

### Process Constraints
- **Sprint Cycle:** Two-week sprints
- **Testing Gate:** No deliverable marked done until tests pass
- **No Mock Data:** All testing uses real data; errors must be visible
- **Documentation:** All work tracked in docs/ with traceability (REQ → DEL → AC → TC)
- **Version Control:** Git with sprint tags (v0N.0) and phase tags (phase-N.0)

### Resource Constraints
- **Single Instance:** Initial deployment targets single-instance architecture
- **Compute Resources:** Local LLM runtime requires sufficient CPU/GPU/memory resources
- **Response Time:** Multi-pass reasoning impacts latency
- **Storage:** Vector embeddings and reasoning history require storage planning

## Assumptions

### Technical Assumptions
- Local LLM runtime has sufficient compute resources and model availability
- ChromaDB can handle expected pattern storage volume
- Docker Desktop has sufficient resources for dev/test environments (including MATLAB and LLM runtime)
- PostgreSQL adequate for structured data (sessions, metrics, metadata)
- REST API sufficient for initial integration needs
- MATLAB toolboxes (Optimization, Statistics, Signal Processing) available
- File-based integration sufficient for Python-MATLAB communication
- MATLAB analysis doesn't need real-time responsiveness (periodic batches OK)

### User Assumptions
- Users have technical background (researchers, developers)
- Users willing to accept increased latency for improved reasoning quality
- Users value reasoning transparency over pure speed
- Users can provide feedback for learning mechanism improvement

### Business Assumptions
- Local LLM compute costs (hardware/electricity) are acceptable for research/development phase
- Open-source or internal use (licensing TBD)
- No immediate need for multi-tenant architecture
- Performance improvements measurable within reasonable timeframe

### Process Assumptions
- Two-week sprints provide sufficient delivery cadence
- Testing can validate reasoning quality improvements
- Sprint-based development suitable for research-oriented project
- Documentation overhead justified by project complexity

## Dependencies

### External Dependencies
- **LLM Runtime:** Local self-hosted runtime (Ollama, vLLM, or similar) exposing OpenAI-style HTTP API
- **Docker Desktop:** Container runtime environment
- **Python Ecosystem:** Package availability via PyPI
- **Network Access:** HTTP calls to local LLM runtime container (optional external API fallback)

### Internal Dependencies
- Reasoning quality depends on pattern learning effectiveness
- Learning effectiveness depends on sufficient query volume
- Metrics accuracy depends on evaluation criteria design
- User satisfaction depends on reasoning transparency

## Risks Related to Constraints/Assumptions
See `risks-log.md` for detailed risk analysis.
