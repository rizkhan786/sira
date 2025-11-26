# SIRA Project Plan
## Self-Improving Reasoning Agent

**Version:** 1.3  
**Date:** 2025-11-19  
**Status:** Phase 1 Complete - Sprint 4 Ready

---

## Project Overview

**Vision:** An AI agent that continuously improves its reasoning capabilities through self-reflection and learning from its own problem-solving patterns.

**Problem:** Current LLMs don't learn from their reasoning process or improve their problem-solving strategies over time.

**Solution:** SIRA builds a knowledge base of successful reasoning patterns and applies them to future problems, with self-verification and iterative refinement.

**Competitive Edge:** Hybrid Python + MATLAB architecture. While others use only Python, SIRA leverages MATLAB's world-class optimization, statistical modeling, and signal processing capabilities for offline analysis and hyperparameter tuning. This gives SIRA a quantitative advantage in self-improvement.

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language (Online) | Python 3.12 |
| Language (Offline Analysis) | MATLAB R2023b+ |
| API Framework | FastAPI |
| Relational DB | PostgreSQL |
| Vector DB | ChromaDB |
|| LLM Runtime | Local/self-hosted LLM service (OpenAI-style HTTP API, serving open models) |
| Containerization | Docker + Docker Compose |
| Integration | File-based (shared volume) |
| Port (API) | 8080 |

---

## Requirements Summary

### Functional Requirements: 16 Total
- **Must Have:** 15 (REQ-001 through REQ-016, except REQ-012)
- **Should Have:** 1 (REQ-012: Web Interface)

**Categories:**
- Core Reasoning: REQ-001, REQ-002, REQ-003, REQ-008
- Pattern Learning: REQ-004, REQ-005, REQ-006, REQ-007
- Infrastructure: REQ-009, REQ-013, REQ-014, REQ-015
- API/Interface: REQ-011, REQ-012
- Observability: REQ-010
- Analysis Integration: REQ-016 (Python-MATLAB)

### Non-Functional Requirements: 15 Total
- **Must Have:** 11
- **Should Have:** 4

**Categories:**
- Performance: NFR-001, NFR-002
- Scalability: NFR-003
- Reliability: NFR-004, NFR-005
- Security: NFR-006, NFR-007
- Maintainability: NFR-008, NFR-009
- Usability: NFR-010, NFR-011
- Observability: NFR-012, NFR-013
- Portability: NFR-014
- Extensibility: NFR-015

---

## Project Phases

### Phase 1: Foundation ✅ COMPLETE
**Goal:** Core reasoning engine with basic pattern learning
**Status:** ✅ Complete (2025-11-19)
**Actual Duration:** 3 sprints (5 weeks)

**Key Deliverables:**
- ✅ Multi-step reasoning engine (REQ-002) - Sprint 1
- ✅ Self-verification system (REQ-003) - Sprint 2
- ✅ Pattern extraction and storage (REQ-004, REQ-005) - Sprint 2
- ✅ Pattern retrieval (REQ-006) - Sprint 2
- ✅ Pattern application (REQ-007) - Sprint 3
- ✅ Iterative refinement (REQ-008) - Sprint 3
- ✅ Metrics tracking (REQ-010) - Sprint 3
- ✅ MATLAB integration (REQ-016) - Sprint 3
- ✅ Basic REST API (REQ-011) - Sprint 1
- ✅ PostgreSQL + ChromaDB setup (REQ-015) - Sprint 1
- ✅ LLM integration with local runtime (REQ-013) - Sprint 1

**Completed Sprints:**
- Sprint 1 (2025-11-15 to 2025-11-15): Infrastructure & Foundation (12 deliverables)
- Sprint 2 (2025-11-15 to 2025-11-16): Pattern Learning (6 deliverables)
- Sprint 3 (2025-11-16 to 2025-11-19): Pattern Application & Integration (4 deliverables)

### Phase 2: Enhancement
**Goal:** Advanced features and observability

**Key Deliverables:**
- Pattern application and quality updates (REQ-007)
- Iterative refinement (REQ-008)
- Session management (REQ-009)
- Metrics tracking (REQ-010)
- Web interface (REQ-012)
- Multiple LLM runtime/model support (NFR-015)

**Target Duration:** 3-4 sprints (6-8 weeks)

### Phase 3: Optimization
**Goal:** Performance, quality, and polish

**Key Deliverables:**
- Performance tuning (NFR-001, NFR-002)
- Pattern quality improvements
- Comprehensive testing (NFR-009)
- Documentation and examples
- UI/UX polish

**Target Duration:** 2-3 sprints (4-6 weeks)

---

## Success Metrics

### Quantitative
- Answer accuracy improves 20%+ over 100 queries
- Pattern reuse rate reaches 40%+ by session 10
- Self-correction rate increases over time
- Response time <30s for multi-pass reasoning
- Test coverage >70% for critical paths

### Qualitative
- Users rate reasoning transparency >4/5
- Developers find API intuitive
- Reasoning patterns demonstrate actual learning
- System shows measurable improvement

---

## Current Status

**Project Stage:** Phase 1 Complete - Sprint 4 Planning

**Completed:**
- ✅ Project discovery and scope definition
- ✅ Requirements analysis (16 FRs, 15 NFRs)
- ✅ Solution architecture and design (Python + MATLAB hybrid)
- ✅ Technology stack selection
- ✅ Deployment topology defined
- ✅ Risk identification and mitigation planning
- ✅ **Phase Planning Complete:**
  - ✅ 25 Deliverables created and mapped (added DEL-025: Local LLM Runtime)
  - ✅ 71 Acceptance Criteria defined
  - ✅ 71 Test Cases authored
  - ✅ Sprint assignments (3 sprints × 2 weeks)
  - ✅ Consistency check passed
  - ✅ Traceability validated (REQ → DEL → AC → TC)
- ✅ **Sprint 1 Complete (2025-11-15):**
  - ✅ 12 deliverables: Infrastructure, API, LLM integration, database setup
  - ✅ Docker containerized development environment operational
  - ✅ Local LLM runtime (Ollama) with llama3.2:3b
  - ✅ Core reasoning engine with multi-step prompts
  - ✅ Session management and logging infrastructure
- ✅ **Sprint 2 Complete (2025-11-16):**
  - ✅ 6 deliverables: Pattern extraction, storage, retrieval, quality scoring
  - ✅ ChromaDB integration with pattern embeddings
  - ✅ Self-verification module with rule-based and LLM-based scoring
  - ✅ Code quality setup (Ruff, Black, MyPy)
  - ✅ Reliability and error handling
- ✅ **Sprint 3 Complete (2025-11-19):**
  - ✅ 4 deliverables: Pattern application, iterative refinement, metrics tracking, MATLAB integration
  - ✅ All 12 acceptance criteria met and validated
  - ✅ Pattern application actively improving response quality
  - ✅ Refinement loop with convergence detection
  - ✅ Comprehensive metrics collection and API
  - ✅ Episode logging for MATLAB analysis
  - ✅ Config hot-reload from MATLAB output
- ✅ **Phase 1 (Foundation) COMPLETE:**
  - ✅ Complete self-improvement loop operational
  - ✅ 22 deliverables completed across 3 sprints
  - ✅ All core requirements implemented (REQ-002, 003, 004, 005, 006, 007, 008, 010, 011, 013, 015, 016)

**Next Steps:**
1. Complete Sprint 3 completion protocol:
   - ✅ Documentation updates
   - ⏳ Project plan update (in progress)
   - Sprint completion report
   - Release notes
   - Merge and tag v03.0
2. Sprint 4 Planning (Phase 2 start):
   - Review sprint-04-scope.md
   - Define deliverables for analytics dashboard and optimization
   - Create task breakdown
   - Set up sprint-04 branch
3. Begin Sprint 4 execution focus:
   - DEL-012: Web Interface
   - DEL-030: MATLAB Advanced Analytics Dashboard
   - DEL-032: MATLAB Pattern Optimization Engine
   - DEL-034: SIRA Core Metrics System
   - DEL-035: SIRA Evaluation Framework

---

## Documentation Structure

```
docs/
├── 00-Initiation/
│   ├── discovery-questionnaire.md
│   ├── scope-and-objectives.md
│   ├── stakeholders-and-roles.md
│   ├── constraints-and-assumptions.md
│   ├── risks-log.md
│   └── glossary.md
├── 10-Requirements/
│   ├── PRD.md
│   ├── functional-requirements.md (15 REQs)
│   └── non-functional-requirements.md (15 NFRs)
├── 20-Solution/
│   ├── solution-architecture.md
│   ├── solution-design.md
│   ├── tech-stack-and-language.md
│   ├── deployment-topology.md
│   └── decisions/ (ADRs)
├── 30-Planning/
│   ├── phase-plan.md (TBD)
│   ├── deliverables-register.md (TBD)
│   └── sprints/ (TBD)
├── 40-Testing/
│   ├── test-plan.md (TBD)
│   ├── acceptance-criteria-index.md (TBD)
│   ├── test-cases.md (TBD)
│   └── test-data-strategy.md (TBD)
├── 50-Completion/
│   └── (Sprint release notes, phase outcomes)
└── 60-Quality/
    └── (Consistency reports, debug logs)
```

---

## Key Risks

| Risk ID | Description | Impact | Mitigation |
|---------|-------------|--------|-----------|
| R-001 | Local LLM runtime resource/hardware costs exceed expectations | High | Monitor compute usage, optimize model selection, efficient batching |
| R-003 | Pattern learning ineffective | High | Quality scoring, validation, review |
| R-006 | Difficulty measuring improvements | High | Clear metrics early, A/B testing, feedback |
| R-011 | Testing self-improving behavior | High | Deterministic scenarios, snapshot testing |

See `docs/00-Initiation/risks-log.md` for complete risk register.

---

## Process & Workflow

### Sprint Cycle
- **Duration:** 2 weeks
- **Planning:** Define goal, deliverables, ACs, TCs
- **Execution:** Implement, test continuously, maintain traceability
- **Completion:** All tests pass, documentation updated, merge & tag

### Quality Gates
- **Definition of Ready (DoR):** DEL with REQ/NFR, ACs defined, TCs authored, environment ready
- **Definition of Done (DoD):** Tests pass, ACs met, documentation updated, no mock data used

### Traceability
- REQ-### → DEL-### → AC-### → TC-###
- Consistency checks at planning and completion
- Traceability maintained in registers/indexes

---

## Team & Roles

- **Development Team:** Build, test, deploy, document
- **Product Owner:** Requirements, priorities, validation
- **Users:** AI researchers, developers, power users

---

## Repository Setup

**Recommended:**
1. Initialize Git repository
2. Create `.gitignore` (exclude `.env`, `__pycache__`, `.pytest_cache`, etc.)
3. Set up remote (GitHub, GitLab, etc.)
4. Tag initial state: `git tag v00.0-intake`

---

## Next Command

**Ready for Phase Planning:**
```
Tell Agent: Do Phase Planning
```

This will:
- Run consistency check across REQ ⇄ DEL ⇄ AC ⇄ TC
- Create deliverables register
- Define acceptance criteria
- Create test cases
- Assign deliverables to sprints
- Update phase plan document

---

**Last Updated:** 2025-11-19  
**Updated By:** Sprint 3 Completion Protocol
