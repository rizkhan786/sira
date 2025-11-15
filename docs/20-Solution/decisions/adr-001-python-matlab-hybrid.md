# ADR-001: Python + MATLAB Hybrid Architecture

**Date:** 2025-11-15  
**Status:** Accepted  
**Decision Makers:** Product Owner, Architecture Team

## Context

SIRA (Self-Improving Reasoning Agent) requires both:
1. **Real-time agent execution** - LLM calls, reasoning orchestration, tool use, API serving
2. **Offline quantitative analysis** - Deep statistical modeling, optimization, pattern analysis

Most similar systems use only Python. This creates an opportunity for competitive differentiation.

## Decision

**Adopt a hybrid Python + MATLAB architecture with clear separation of concerns:**

### Python Responsibilities (Online/Real-time)
- Core agent logic (CoT, ToT, ReAct, Reflexion)
- LLM integration via local/self-hosted LLM runtime (serving open models; optional external providers later if needed)
- Tool execution and orchestration
- REST API serving
- Database operations (PostgreSQL, ChromaDB)
- Episode logging and trace capture
- Configuration consumption
- Web interface serving

### MATLAB Responsibilities (Offline/Analysis)
- Quantitative analysis of reasoning episodes
- Statistical modeling of improvement patterns
- Hyperparameter optimization
- Signal processing of reasoning traces
- Pattern similarity analysis (DTW, cross-correlation)
- Learning curve modeling and prediction
- Strategy selection optimization
- Data visualization and reporting
- Configuration generation (tuned hyperparameters)

### Integration Pattern: File-Based Communication
- **Python → MATLAB:** Write episode logs, traces, embeddings to shared volume
- **MATLAB → Python:** Write tuned configs, insights, reports to shared volume
- **No direct API calls between systems** (clean separation, Docker-friendly)

## Rationale

### Why This Works

1. **Best Tool for Each Job:**
   - Python excels at: async I/O, LLM APIs, web serving, general-purpose programming
   - MATLAB excels at: numerical optimization, statistical modeling, signal processing, matrix operations

2. **Competitive Differentiation:**
   - Others use only Python or Node.js for LLM agents
   - MATLAB's optimization and analysis capabilities are world-class but underutilized in AI agent space
   - This hybrid gives SIRA a quantitative edge in self-improvement

3. **Clean Architecture:**
   - File-based integration keeps systems decoupled
   - Easy to run MATLAB analysis offline/batch without blocking agent
   - Simple to test and develop each component independently
   - Docker-friendly (separate containers)

4. **Scalability:**
   - Python agent handles real-time traffic
   - MATLAB analysis runs periodically (hourly, daily) without impacting latency
   - Can scale Python horizontally, MATLAB vertically

5. **Development Efficiency:**
   - Python team: Focus on agent logic, API, integrations
   - MATLAB team: Focus on quant analysis, optimization, modeling
   - Minimal coordination needed (file contracts)

### MATLAB's Specific Value-Add

**1. Advanced Numerical Analysis**
- Per-episode performance metrics (success rate, token usage, latency)
- Time-series analysis of improvement over training runs
- Convergence and stability detection
- Sensitivity analysis (hyperparameter marginal effects)

**2. Statistical Modeling**
- Regression models predicting success from hyperparameters
- Learning curve fitting (power laws, exponentials)
- Strategy selection meta-models (which policy for which task type)
- Probabilistic models of reasoning flows (Markov chains)

**3. Signal Processing**
- Reasoning traces as multivariate time series
- Dynamic Time Warping for trace similarity
- Pattern detection (healthy vs problematic reasoning patterns)
- Cross-correlation between successful and failed episodes

**4. Optimization**
- Hyperparameter tuning (depth, branching, temperature)
- Reward shaping (optimize composite scoring functions)
- Multi-objective optimization (accuracy vs cost vs latency)
- Portfolio optimization for strategy selection

**5. Visualization**
- Learning curves and performance dashboards
- Sankey diagrams of reasoning flows
- Heatmaps of tool usage and branching patterns
- Model comparison visualizations

**6. Custom Mathematical Models**
- Risk models for high-stakes reasoning
- Meta-policy evaluation and simulation
- Predictive models for expected performance

## Implementation Details

### Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Python Container                      │
│  ┌────────────────────────────────────────────────┐    │
│  │  SIRA Agent (FastAPI)                           │    │
│  │  - Execute reasoning episodes                   │    │
│  │  - Log traces to /data/logs/                    │    │
│  │  - Read configs from /data/config/              │    │
│  └────────────────────────────────────────────────┘    │
└───────────────────────┬──────────────────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   Shared Volume     │
              │   /data/            │
              │  ├── logs/          │
              │  │   └── episodes/  │
              │  ├── config/        │
              │  └── reports/       │
              └─────────────────────┘
                        │
                        ▼
┌───────────────────────┴──────────────────────────────────┐
│                   MATLAB Container                        │
│  ┌────────────────────────────────────────────────┐    │
│  │  Analysis Engine                                │    │
│  │  - Read episodes from /data/logs/               │    │
│  │  - Analyze, optimize, model                     │    │
│  │  - Write tuned configs to /data/config/         │    │
│  │  - Generate reports to /data/reports/           │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### File Formats

**Python Writes:**
```
/data/logs/run_{run_id}/
├── episodes.jsonl          # Detailed episode logs (one JSON per line)
├── episodes_summary.csv    # Aggregated metrics per episode
├── traces/                 # Individual reasoning traces
│   ├── episode_001.json
│   └── episode_002.json
└── embeddings.npy          # Optional: pattern embeddings
```

**MATLAB Writes:**
```
/data/config/
├── sira_tuned_{timestamp}.json   # Optimized hyperparameters
└── strategy_policy.json          # Task-specific strategy rules

/data/reports/
├── learning_curves_{timestamp}.png
├── sensitivity_analysis.pdf
└── optimization_summary.json
```

### Episode Log Schema (episodes.jsonl)
```json
{
  "episode_id": "uuid",
  "timestamp": "2025-11-15T00:00:00Z",
  "task_type": "math_problem",
  "difficulty": "hard",
  "config": {
    "max_depth": 3,
    "branching_factor": 2,
    "temperature": 0.7,
    "use_tools": true,
    "use_reflexion": false
  },
  "trace": [
    {"step": 1, "type": "thought", "content": "...", "confidence": 0.8},
    {"step": 2, "type": "tool_call", "tool": "calculator", "input": "..."},
    {"step": 3, "type": "tool_result", "output": "..."}
  ],
  "result": {
    "success": true,
    "answer": "...",
    "confidence": 0.85,
    "reasoning_depth": 5,
    "branches_explored": 3,
    "tools_used": ["calculator"],
    "tokens_used": 1250,
    "latency_ms": 3400
  }
}
```

### Tuned Config Schema (sira_tuned_*.json)
```json
{
  "version": "1.0",
  "timestamp": "2025-11-15T00:00:00Z",
  "optimization_run": "opt_001",
  "hyperparameters": {
    "max_depth": 4,
    "branching_factor": 3,
    "temperature": 0.65,
    "top_p": 0.9,
    "tool_threshold": 0.7
  },
  "strategy_policy": {
    "math_easy": "CoT",
    "math_hard": "ToT_tools",
    "coding": "ToT_tools_reflexion",
    "general": "CoT"
  },
  "scoring_weights": {
    "correctness": 1.0,
    "tokens": -0.001,
    "latency": -0.0005,
    "tool_use": 0.1
  },
  "metadata": {
    "episodes_analyzed": 1000,
    "objective_value": 0.85,
    "convergence": true
  }
}
```

## Alternatives Considered

### Alt 1: Python-Only with scipy/scikit-learn
**Pros:** Single language, simpler deployment  
**Cons:** Python's optimization/modeling less mature than MATLAB for our use cases  
**Rejected:** Missing MATLAB's specialized toolboxes and competitive edge

### Alt 2: Python + R
**Pros:** R excellent for statistics  
**Cons:** R not as strong for optimization; less familiar to team  
**Rejected:** MATLAB better fit for our specific needs

### Alt 3: Python with direct MATLAB API calls
**Pros:** Tighter integration  
**Cons:** Complex Docker setup, tight coupling, latency in API path  
**Rejected:** File-based cleaner and doesn't block agent performance

### Alt 4: All-in-One Container
**Pros:** Simpler initial setup  
**Cons:** Heavy image, poor separation of concerns, harder to scale independently  
**Rejected:** Separate containers cleaner architecture

## Consequences

### Positive
- ✅ World-class optimization and analysis capabilities
- ✅ Competitive differentiation (unique architecture in AI agent space)
- ✅ Clean separation of concerns
- ✅ Parallel development (Python and MATLAB teams independent)
- ✅ MATLAB analysis doesn't impact agent latency
- ✅ Easy to disable MATLAB component if needed

### Negative
- ⚠️ Two languages to maintain (team needs both Python and MATLAB skills)
- ⚠️ MATLAB licensing costs (can use MATLAB Runtime for deployment)
- ⚠️ Docker complexity (two containers vs one)
- ⚠️ File-based integration has slight delay (not real-time)

### Neutral
- 📊 Learning curve for Python devs unfamiliar with MATLAB
- 📊 Need clear file format contracts
- 📊 MATLAB container larger than pure Python

## Mitigation Strategies

**Licensing:** Use MATLAB Runtime for production (free), full MATLAB for development  
**Team Skills:** Python team owns agent, MATLAB specialist owns analysis  
**Testing:** Each system tested independently; integration tests via file contracts  
**Documentation:** Clear schemas for all shared file formats  

## Success Metrics

- MATLAB-optimized hyperparameters improve SIRA performance by 15%+
- Analysis turnaround time <1 hour for 1000 episodes
- Zero runtime failures due to Python-MATLAB integration
- Development velocity maintained (no coordination bottlenecks)

## References

- Python official documentation
- MATLAB Optimization Toolbox
- MATLAB Signal Processing Toolbox
- Docker multi-container best practices

---

**Approved By:** [Names]  
**Implementation Start:** Sprint 2 (after core Python agent functional)
