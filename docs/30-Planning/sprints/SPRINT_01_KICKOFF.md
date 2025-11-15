# Sprint 1 Kickoff - SIRA

## 🎯 Sprint Goal
Set up complete infrastructure foundation for SIRA with all containers running and basic reasoning engine functional.

---

## 📊 Sprint Overview

**Duration:** 2 weeks (10 working days)  
**Deliverables:** 12  
**Acceptance Criteria:** 36  
**Test Cases:** 36  
**Status:** ✅ Ready to Execute

---

## 🚀 Quick Start

### Step 1: Create Sprint Branch
```bash
git checkout -b sprint-01
```

### Step 2: Start with Critical Task
**Task 1.1: Local LLM Runtime Setup (Day 1-2)**

This is THE most critical task - everything depends on it!

1. Create `ops/docker/` directory
2. Create docker-compose.yml with sira-llm service (Ollama)
3. Start container and download model:
```bash
cd ops/docker
docker-compose up -d sira-llm
docker exec sira-llm ollama pull llama3:8b  # ~4.7GB download
```
4. Test: `curl http://localhost:11434/v1/models`

**Expected time:** 
- Setup: 30 minutes
- Model download: 20-60 minutes (depending on internet speed)
- Total: ~2 hours

---

## 📋 Daily Plan

### **Day 1-2: Foundation** (13 hours)
- ⭐ Task 1.1: Local LLM Runtime Setup (4h) - **START HERE**
- Task 1.2: Docker Infrastructure (6h)
- Task 1.3: Database Schema (3h)

**End of Day 2 Goal:** All containers running, model downloaded

---

### **Day 3-4: Configuration & API** (12 hours)
- Task 2.1: Configuration System (4h)
- Task 2.2: Logging Infrastructure (3h)
- Task 2.3: REST API Layer (5h)

**End of Day 4 Goal:** Swagger UI accessible at http://localhost:8080/docs

---

### **Day 5-7: LLM Integration & Reasoning** (18 hours)
- Task 3.1: LLM Integration Layer (6h)
- Task 3.2: Reasoning Engine Core (8h)
- Task 3.3: Query Processing API (4h)

**End of Day 7 Goal:** End-to-end query works via Swagger UI

---

### **Day 8-9: Supporting Systems** (12 hours)
- Task 4.1: Session Management (5h)
- Task 4.2: Security Implementation (3h)
- Task 4.3: Testing Framework (4h)

**End of Day 9 Goal:** All tests passing, security in place

---

### **Day 10: Integration & Polish** (6 hours)
- Task 5.1: End-to-End Integration Test (4h)
- Task 5.2: Documentation Updates (2h)

**End of Day 10 Goal:** Sprint complete, all 36 tests passing

---

## ✅ Definition of Done

Sprint 1 is complete when:

### Functional
- [ ] All 12 deliverables complete
- [ ] 36 test cases passing
- [ ] Query → LLM → Reasoning → Response flow works end-to-end

### Technical
- [ ] `docker ps` shows 4 containers running: sira-api, postgres, chromadb, sira-llm
- [ ] Swagger UI accessible at http://localhost:8080/docs
- [ ] Can submit query via Swagger and get reasoning trace back
- [ ] Database has sessions, queries, metrics tables
- [ ] Logs show structured JSON output

### Quality
- [ ] No secrets in code or logs
- [ ] Input validation working (400 errors for invalid input)
- [ ] No errors in container logs

### Documentation
- [ ] README.md updated with setup instructions
- [ ] Quick start guide created
- [ ] Sprint 1 completion report written

---

## 🎬 Demo Script (For Sprint Review)

1. **Show Infrastructure:**
   ```bash
   docker ps  # Show all 4 containers running
   ```

2. **Show Swagger UI:**
   - Navigate to http://localhost:8080/docs
   - Show all endpoints (query, session, patterns, metrics)

3. **Submit Test Query:**
   - Click POST /query
   - Try it out with: `{"query": "Explain why the sky is blue"}`
   - Show 200 response with reasoning_trace

4. **Show Database:**
   ```bash
   docker exec -it sira-postgres psql -U sira -d sira -c "SELECT * FROM queries LIMIT 1;"
   ```

5. **Show Logs:**
   ```bash
   docker logs sira-api | tail -20  # Show structured JSON logs
   ```

6. **Run Tests:**
   ```bash
   docker-compose -f docker-compose.test.yml up
   # Show all 36 tests passing
   ```

---

## 🚨 Common Issues & Solutions

### Issue: Model download times out
**Solution:** Increase Docker timeout, use smaller model (qwen2.5:7b is ~4.4GB vs llama3:8b at ~4.7GB)

### Issue: Container out of memory
**Solution:** Allocate more RAM to Docker Desktop (recommend 8GB minimum, 16GB ideal)

### Issue: Port 8080 already in use
**Solution:** Change port in docker-compose.yml or stop conflicting service

### Issue: Containers can't talk to each other
**Solution:** All containers must be on same network (`sira_network`)

---

## 📞 Support

**Detailed Plan:** See `docs/30-Planning/sprints/sprint-01-plan.md`  
**Architecture:** See `docs/20-Solution/solution-architecture.md`  
**Requirements:** See `docs/10-Requirements/`

---

## 🎉 Success Criteria Met?

When you can do this without errors, Sprint 1 is complete:

```bash
# 1. All containers running
docker ps | grep -E "sira-api|sira-postgres|sira-chromadb|sira-llm"

# 2. API responds
curl http://localhost:8080/health

# 3. Query works
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2+2?"}'

# 4. Tests pass
docker-compose -f docker-compose.test.yml up | grep "36 passed"
```

If all 4 commands succeed → **Sprint 1 Complete!** 🎉

Tag the release: `git tag v01.0-sprint-01`

---

**Next Sprint:** Sprint 2 focuses on Pattern Learning (extraction, storage, retrieval) and Self-Verification.

**Let's build SIRA!** 🚀
