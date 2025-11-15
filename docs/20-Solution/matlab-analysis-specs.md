# MATLAB Analysis Specifications - SIRA

## Overview

MATLAB serves as SIRA's "offline quant/research lab," analyzing reasoning episodes to optimize hyperparameters, model learning patterns, and generate insights that feed back into the Python agent.

## Responsibilities

### 1. Episode Analysis
- Read episode logs from `/data/logs/run_{id}/episodes.jsonl`
- Compute per-episode metrics (success rate, token usage, latency)
- Aggregate across episodes for trend analysis
- Identify patterns in successful vs failed episodes

### 2. Statistical Modeling
- Build regression models predicting success from hyperparameters
- Fit learning curves (power laws, exponentials)
- Perform sensitivity analysis on configuration parameters
- Create meta-models for strategy selection

### 3. Hyperparameter Optimization
- Optimize: `max_depth`, `branching_factor`, `temperature`, `top_p`, `tool_threshold`
- Objective: Maximize success rate subject to cost constraints
- Methods: `fmincon`, `ga` (genetic algorithm), `bayesopt`
- Output: Tuned configuration JSON files

### 4. Signal Processing & Pattern Analysis
- Treat reasoning traces as multivariate time series
- Apply Dynamic Time Warping (DTW) for trace similarity
- Identify "healthy" vs "problematic" reasoning patterns
- Cross-correlation between successful and failed patterns

### 5. Reward Shaping
- Optimize composite scoring functions:
  ```
  score = α * correctness - β * tokens - γ * latency + δ * tool_use
  ```
- Tune weights (α, β, γ, δ) to balance objectives

### 6. Visualization & Reporting
- Learning curves (episode vs reward)
- Heatmaps (depth vs success, tool usage frequency)
- Sankey diagrams (reasoning flow visualizations)
- Strategy comparison plots

## File I/O Specifications

### Input Files (Python → MATLAB)

#### 1. Episode Logs (`episodes.jsonl`)
**Location:** `/data/logs/run_{run_id}/episodes.jsonl`  
**Format:** JSON Lines (one JSON object per line)

**Schema:**
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

#### 2. Episode Summary (`episodes_summary.csv`)
**Location:** `/data/logs/run_{run_id}/episodes_summary.csv`  
**Format:** CSV with header

**Columns:**
```
episode_id,timestamp,task_type,difficulty,success,confidence,reasoning_depth,branches_explored,tokens_used,latency_ms,max_depth,branching_factor,temperature,use_tools,use_reflexion
```

#### 3. Reasoning Traces (Individual Files)
**Location:** `/data/logs/run_{run_id}/traces/episode_{nnn}.json`  
**Format:** JSON (detailed trace for specific episode)

#### 4. Embeddings (Optional)
**Location:** `/data/logs/run_{run_id}/embeddings.npy`  
**Format:** NumPy array (N x D, where N = episodes, D = embedding dimension)

### Output Files (MATLAB → Python)

#### 1. Tuned Configuration (`sira_tuned_{timestamp}.json`)
**Location:** `/data/config/sira_tuned_{timestamp}.json`  
**Format:** JSON

**Schema:**
```json
{
  "version": "1.0",
  "timestamp": "2025-11-15T12:00:00Z",
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
    "convergence": true,
    "optimization_method": "bayesopt",
    "constraints": "tokens < 2000, latency < 5000ms"
  }
}
```

#### 2. Strategy Policy (`strategy_policy.json`)
**Location:** `/data/config/strategy_policy.json`  
**Format:** JSON

**Schema:**
```json
{
  "version": "1.0",
  "timestamp": "2025-11-15T12:00:00Z",
  "policies": {
    "math_easy": {
      "strategy": "CoT",
      "max_depth": 2,
      "use_tools": false
    },
    "math_hard": {
      "strategy": "ToT_tools",
      "max_depth": 4,
      "branching_factor": 3,
      "use_tools": true
    },
    "coding": {
      "strategy": "ToT_tools_reflexion",
      "max_depth": 5,
      "use_reflexion": true
    }
  }
}
```

#### 3. Analysis Reports
**Location:** `/data/reports/`  
**Formats:** PDF, PNG, JSON

**Files:**
- `learning_curves_{timestamp}.png` - Plots of improvement over time
- `sensitivity_analysis_{timestamp}.pdf` - Hyperparameter sensitivity
- `pattern_analysis_{timestamp}.json` - Pattern quality and usage stats
- `optimization_summary_{timestamp}.json` - Optimization results

## MATLAB Analysis Functions

### Main Entry Point
```matlab
% run_analysis.m - Main script executed by Docker container
function run_analysis()
    % 1. Load episode data
    [episodes, summary] = load_episode_data('/data/logs');
    
    % 2. Perform analyses
    metrics = compute_metrics(episodes);
    learning_curves = analyze_learning_curves(summary);
    patterns = analyze_patterns(episodes);
    
    % 3. Optimize hyperparameters
    tuned_config = optimize_hyperparameters(summary, metrics);
    
    % 4. Generate reports
    generate_visualizations(metrics, learning_curves, '/data/reports');
    
    % 5. Write outputs
    write_tuned_config(tuned_config, '/data/config');
    write_analysis_report(metrics, '/data/reports');
    
    fprintf('Analysis complete at %s\n', datestr(now));
end
```

### Core Functions

#### 1. Metrics Computation
```matlab
function metrics = compute_metrics(episodes)
    % Compute success rate by task type
    % Compute token efficiency (success / tokens)
    % Compute latency distributions
    % Identify high-performing configurations
end
```

#### 2. Learning Curve Analysis
```matlab
function curves = analyze_learning_curves(summary)
    % Fit power law or exponential to learning curve
    % Detect convergence or plateaus
    % Predict future performance
end
```

#### 3. Hyperparameter Optimization
```matlab
function tuned_config = optimize_hyperparameters(data, metrics)
    % Define objective function
    objective = @(x) -compute_score(x, data);
    
    % Define constraints
    lb = [2, 1, 0.1, 0.5];  % min: depth, branching, temp, tool_threshold
    ub = [10, 5, 1.0, 0.95]; % max
    
    % Run Bayesian optimization
    results = bayesopt(objective, [lb, ub], ...
        'MaxObjectiveEvaluations', 100, ...
        'IsObjectiveDeterministic', false);
    
    tuned_config = format_config(results.XAtMinObjective);
end
```

#### 4. Pattern Similarity Analysis
```matlab
function similarities = analyze_pattern_similarity(traces)
    % Convert traces to time series
    % Compute DTW distance matrix
    % Cluster similar patterns
    % Identify canonical successful patterns
end
```

#### 5. Reward Shaping Optimization
```matlab
function weights = optimize_reward_weights(episodes)
    % Define composite score function
    score = @(w) w(1)*correct - w(2)*tokens - w(3)*latency + w(4)*tools;
    
    % Optimize weights to maximize separation between good/bad episodes
    % Use fmincon or genetic algorithm
end
```

## Execution Modes

### Mode 1: Periodic Batch Analysis (Default)
- Runs every N hours (configurable via `MATLAB_ANALYSIS_INTERVAL`)
- Docker container loops: analyze → sleep → repeat
- Suitable for continuous improvement

**Docker Command:**
```yaml
command: |
  bash -c '
    while true; do
      cd /app/matlab && matlab -batch "run_analysis"
      sleep ${MATLAB_ANALYSIS_INTERVAL:-3600}
    done
  '
```

### Mode 2: On-Demand Execution
- Container stays alive but idle
- Manual trigger when needed
- Suitable for development and debugging

**Docker Command:**
```yaml
command: tail -f /dev/null
```

**Manual Trigger:**
```bash
docker exec -it sira-matlab matlab -batch "run_analysis"
```

### Mode 3: Event-Driven (Future)
- Python signals MATLAB when sufficient new data available
- MATLAB runs analysis and returns quickly
- Requires inter-container communication (future enhancement)

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Analysis Time | <1 hour | For 1000 episodes |
| Config Generation | <5 minutes | Optimization converged |
| Memory Usage | <8 GB | Typical analysis run |
| Pattern Retrieval | <10s | DTW on 10K patterns |

## Testing Strategy

### Unit Tests
- Test each MATLAB function independently
- Use MATLAB Test Framework
- Mock data for reproducibility

### Integration Tests
- Test full `run_analysis` pipeline
- Use real episode logs (subset)
- Verify output file formats

### Validation Tests
- Compare MATLAB-optimized configs vs baselines
- Verify configs improve Python agent performance
- A/B testing in production

## Development Workflow

1. **Local Development:**
   - Full MATLAB installation with toolboxes
   - Interactive development and debugging
   - Test with sample episode data

2. **Docker Testing:**
   - Build MATLAB container
   - Mount local MATLAB code
   - Test full integration with Python logs

3. **Production Deployment:**
   - Compile MATLAB code to standalone
   - Use MATLAB Runtime (free)
   - Deploy via Docker Compose

## Troubleshooting

### Issue: MATLAB container fails to start
**Check:**
- License configuration (`MATLAB_LICENSE_FILE`)
- Image availability (MathWorks account required)
- Memory allocation (MATLAB needs significant RAM)

### Issue: No output files generated
**Check:**
- Permissions on `/data` volume
- MATLAB script errors (check logs)
- Input data availability

### Issue: Optimization not converging
**Check:**
- Sufficient episode data (100+ recommended)
- Constraint bounds (too tight?)
- Objective function validity

## Future Enhancements

- **Real-time Analysis:** Incremental updates as episodes arrive
- **Multi-objective Optimization:** Pareto frontiers for accuracy vs cost
- **Distributed Computing:** Use Parallel Computing Toolbox for speed
- **Database Integration:** Direct PostgreSQL access (alternative to files)
- **Advanced Models:** Deep learning for pattern prediction

---

See also:
- `adr-001-python-matlab-hybrid.md` - Architecture decision rationale
- `tech-stack-and-language.md` - MATLAB toolbox details
- `deployment-topology.md` - Docker configuration
