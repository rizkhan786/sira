# Sprint 2 Kickoff: Pattern Learning & Self-Improvement

**Date**: 2025-11-15  
**Sprint Duration**: 2 weeks (14 days)  
**Status**: Ready to Start  

---

## 🎯 Sprint Goal

**Make SIRA learn from its own usage** by implementing pattern extraction, storage, and retrieval so it improves over time.

---

## 📦 What We're Building

### The Big Picture

Currently (Sprint 1):
```
User Query → Reasoning Engine → LLM (2 calls) → Response
```

After Sprint 2:
```
User Query → Retrieve Similar Patterns → Reasoning Engine (with patterns) → LLM → Response
                                              ↓
                                    Extract Pattern (if high quality)
                                              ↓
                                        Store in ChromaDB
```

### Key Features

1. **Quality Scoring** - Every response gets a quality score (0.0-1.0)
2. **Pattern Extraction** - High-quality responses (≥0.8) become patterns
3. **Pattern Storage** - Patterns stored in ChromaDB with vector embeddings
4. **Pattern Retrieval** - Similar patterns retrieved for new queries
5. **Self-Improvement** - System learns from successful reasoning approaches

---

## 📋 Deliverables (6)

| # | Deliverable | Description | Days |
|---|-------------|-------------|------|
| DEL-003 | Self-Verification Module | Quality scoring & verification | 3-4 |
| DEL-004 | Pattern Extraction Engine | Extract patterns from successes | 2-3 |
| DEL-005 | Pattern Storage System | Store in ChromaDB | 2-3 |
| DEL-006 | Pattern Retrieval System | Retrieve & rank similar patterns | 2-3 |
| DEL-022 | Code Quality Setup | Linting, formatting, type checking | 1 |
| DEL-023 | Reliability & Error Handling | Robust error handling & retries | 1-2 |

---

## 📅 Timeline

### Week 1: Pattern Creation
- **Days 1-2**: Quality scoring
- **Days 3-4**: Pattern extraction
- **Days 5-6**: Pattern storage
- **Day 7**: Mid-sprint review

### Week 2: Pattern Usage
- **Days 8-9**: Pattern retrieval
- **Day 10**: Integration with reasoning
- **Day 11**: Code quality
- **Days 12-13**: Error handling
- **Day 14**: Testing & sprint review

---

## ✅ Success Criteria

Sprint 2 succeeds when:

1. ✅ Submit query "What is 2+2?" → Quality score: 0.92 → Pattern extracted
2. ✅ Submit query "What is 3+3?" → Similar pattern retrieved → Uses pattern in reasoning
3. ✅ Pattern visible in database and ChromaDB
4. ✅ Response quality improves with pattern usage
5. ✅ All 18 test cases passing
6. ✅ Code quality checks passing

---

## 🧪 How to Test

### Manual Test Flow

```bash
# 1. Start Sprint 2 development
git checkout -b sprint-2

# 2. After implementing quality scoring (Day 2):
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'

# Response should include quality_score in metadata

# 3. After pattern storage (Day 7):
# Check ChromaDB has patterns
docker exec sira-chromadb chromadb-cli list-collections

# Check PostgreSQL has pattern metadata
docker exec sira-postgres psql -U sira -d sira \
  -c "SELECT COUNT(*) FROM pattern_metadata;"

# 4. After pattern retrieval (Day 10):
# Submit similar query
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of Spain?"}'

# Response metadata should show patterns_used > 0
```

---

## 📁 New Code Structure

After Sprint 2:
```
sira/
├── src/
│   ├── patterns/          # NEW
│   │   ├── __init__.py
│   │   ├── models.py      # Pattern data structures
│   │   ├── extractor.py   # Extract patterns
│   │   ├── storage.py     # Store in ChromaDB
│   │   └── retriever.py   # Retrieve similar patterns
│   ├── quality/           # NEW
│   │   ├── __init__.py
│   │   └── scorer.py      # Quality scoring
│   └── core/
│       └── exceptions.py  # NEW - Custom errors
└── tests/
    ├── test_quality_scorer.py
    ├── test_pattern_extractor.py
    ├── test_pattern_storage.py
    ├── test_pattern_retriever.py
    └── test_pattern_flow.py
```

---

## ⚙️ Configuration

New environment variables to add:

```bash
# .env additions for Sprint 2
PATTERN_MIN_QUALITY=0.8
PATTERN_RETRIEVAL_COUNT=5
PATTERN_SIMILARITY_THRESHOLD=0.7
PATTERN_RANKING_WEIGHTS="0.6,0.3,0.1"

QUALITY_MIN_THRESHOLD=0.7
QUALITY_GOOD_THRESHOLD=0.8
QUALITY_EXCELLENT_THRESHOLD=0.9

LLM_RETRY_ATTEMPTS=3
LLM_RETRY_DELAY=1
CHROMADB_RETRY_ATTEMPTS=3
```

---

## 🎓 Learning Path

### What is a "Pattern"?

A pattern is a reusable reasoning approach extracted from a successful query. Example:

**Query**: "What is the capital of France?"

**Pattern Extracted**:
```json
{
  "id": "uuid-123",
  "query_type": "factual_question",
  "concepts": ["geography", "capital", "country"],
  "reasoning_strategy": "recall_and_verify",
  "reasoning_template": [
    "1. Identify the subject (country)",
    "2. Recall known fact (capital city)",
    "3. State the answer clearly"
  ],
  "quality_score": 0.95,
  "usage_count": 0
}
```

**When Similar Query Asked**: "What is the capital of Spain?"

The pattern is retrieved and used as guidance:
- "Oh, this is similar to the France query"
- "I should use the same reasoning approach"
- Result: Better, more consistent response

---

## 🚀 Getting Started

### Immediate Next Steps

1. **Review the plan**: Read `sprint-02-plan.md` in detail
2. **Create branch**: `git checkout -b sprint-2`
3. **Start Task 1.1**: Create `src/quality/scorer.py`
4. **Run tests frequently**: `docker exec sira-api-dev pytest`

### First Day Checklist

- [ ] Sprint 2 branch created
- [ ] Reviewed full sprint plan
- [ ] Understanding of pattern concept
- [ ] Environment variables planned
- [ ] Started Task 1.1 (Quality Scoring)

---

## 📊 Progress Tracking

Track progress in `SPRINT_02_PROGRESS.md` (create as you go):

```markdown
# Sprint 2 Progress

## Day 1
- [x] Created sprint-2 branch
- [x] Started quality scorer implementation
- [ ] Quality scorer tests

## Day 2
- [ ] Quality scorer complete
- [ ] Self-verification logic
...
```

---

## 🤝 Daily Standup Questions

1. What did I complete yesterday?
2. What will I work on today?
3. Any blockers or questions?
4. Is the sprint on track for the milestones?

---

## 🎯 Definition of Done

Each task is "done" when:
- ✅ Code written and works
- ✅ Tests written and passing
- ✅ Type hints added
- ✅ No linting errors
- ✅ Acceptance criteria met
- ✅ Committed to sprint-2 branch

---

## 📚 Key Concepts

### Quality Score Components
1. **Completeness** - Did it fully answer the question?
2. **Coherence** - Are reasoning steps logical?
3. **Relevance** - Is the response on-topic?
4. **Verification** - Does self-check pass?

### Pattern Ranking Formula
```
score = (similarity × 0.6) + (quality × 0.3) + (success_rate × 0.1)
```

### Why These Weights?
- **Similarity (60%)**: Most important - pattern must match query
- **Quality (30%)**: Use high-quality patterns
- **Success Rate (10%)**: Proven patterns preferred

---

## 🔍 Monitoring

Watch these metrics during Sprint 2:

- **Quality scores**: Should range 0.7-1.0 for most queries
- **Pattern count**: Should grow as we process queries
- **Pattern usage**: Should increase as patterns accumulate
- **Response time**: Should not increase significantly

---

## ⚠️ Known Risks

1. **Pattern extraction too slow**
   - Mitigation: Extract async, don't block response

2. **Quality scoring inaccurate**
   - Mitigation: Tune thresholds, use multiple verification methods

3. **ChromaDB performance**
   - Mitigation: Limit patterns per query, add caching

---

## 💡 Tips

- **Test early, test often** - Don't wait until Day 14
- **Keep it simple** - Minimal viable version first
- **Log everything** - You'll need visibility
- **Ask questions** - No blockers should last > 1 day

---

## 📖 Reference Documents

- [Full Sprint Plan](sprint-02-plan.md)
- [Deliverables Register](../deliverables-register.md)
- [Acceptance Criteria](../../40-Testing/acceptance-criteria-index.md)
- [Test Cases](../../40-Testing/test-cases.md)

---

**Ready to start?** Create the sprint-2 branch and begin with Task 1.1!

```bash
git checkout -b sprint-2
mkdir -p src/quality src/patterns
touch src/quality/__init__.py src/quality/scorer.py
```

Let's build self-improvement! 🚀
