# Standard AI Benchmarks Integration Plan

## Goal
Run SIRA on industry-standard benchmarks (MMLU, GSM8K, HumanEval, etc.) to compare against published GPT-4, Claude, LLaMA scores.

---

## Available Standard Benchmarks

### 1. MMLU (Massive Multitask Language Understanding)
**What:** 57 subjects from elementary math to professional law  
**Size:** 15,908 multiple-choice questions  
**Format:** Question + 4 choices (A/B/C/D) + correct answer  
**Baseline Scores:**
- GPT-4: 86.4%
- GPT-3.5-Turbo: 70%
- Claude-3-Opus: 85%
- LLaMA-2-70B: 68.9%

**Source:** https://github.com/hendrycks/test
**Access:** Open dataset, freely available
**License:** MIT

### 2. GSM8K (Grade School Math)
**What:** Grade-school level math word problems  
**Size:** 8,500 problems (7,473 train, 1,319 test)  
**Format:** Word problem + numerical answer  
**Baseline Scores:**
- GPT-4: 92%
- GPT-3.5-Turbo: 57%
- Claude-3: 88%

**Source:** https://github.com/openai/grade-school-math
**Access:** Open dataset
**License:** MIT

### 3. HumanEval (Code Generation)
**What:** Python coding problems  
**Size:** 164 programming problems  
**Format:** Function signature + docstring + test cases  
**Baseline Scores:**
- GPT-4: 67%
- GPT-3.5-Turbo: 48%
- Claude-3: 71%
- Codex: 72%

**Source:** https://github.com/openai/human-eval
**Access:** Open dataset
**License:** MIT

### 4. HellaSwag (Commonsense Reasoning)
**What:** Sentence completion with commonsense reasoning  
**Size:** 10,042 questions  
**Format:** Context + 4 completions + correct answer  
**Baseline Scores:**
- GPT-4: 95.3%
- GPT-3.5: 85.5%
- Claude-3: 95.4%

**Source:** https://github.com/rowanz/hellaswag
**Access:** Open dataset
**License:** MIT

### 5. TruthfulQA
**What:** Questions testing truthfulness and avoiding falsehoods  
**Size:** 817 questions  
**Format:** Question + correct answer + common misconceptions  
**Baseline Scores:**
- GPT-4: 59%
- GPT-3.5: 47%
- Claude-3: 62%

**Source:** https://github.com/sylinrl/TruthfulQA
**Access:** Open dataset
**License:** Apache 2.0

---

## Integration Approach

### Option A: Quick Integration (Recommended)
Use existing benchmark libraries that handle dataset loading and evaluation:

**Library: lm-evaluation-harness**
- URL: https://github.com/EleutherAI/lm-evaluation-harness
- Features: Pre-integrated with 200+ benchmarks including MMLU, GSM8K, HumanEval
- Usage: Provides API to run benchmarks on any LLM
- Status: Industry standard, used by HuggingFace, OpenAI

**Implementation:**
1. Install: `pip install lm-eval`
2. Create adapter: SIRA → lm-eval API
3. Run: `lm_eval --model sira --tasks mmlu,gsm8k,humaneval`
4. Get scores comparable to published baselines

**Effort:** 1-2 days

### Option B: Manual Integration
Download datasets manually and create custom evaluation pipeline:

**Steps:**
1. Download datasets from GitHub repos
2. Parse question formats
3. Submit to SIRA
4. Compare outputs to ground truth
5. Calculate accuracy scores

**Effort:** 3-5 days per benchmark

---

## Recommended Implementation Plan

### Sprint 5 Addition: Standard Benchmark Integration

**Deliverable: DEL-036 - Standard Benchmark Evaluation**

**Scope:**
1. Integrate `lm-evaluation-harness` library
2. Create SIRA adapter for lm-eval API
3. Run benchmarks: MMLU, GSM8K, HumanEval
4. Generate comparison report vs. GPT-4, Claude, LLaMA
5. Store results in database

**Acceptance Criteria:**
- AC-091: SIRA successfully runs MMLU benchmark (all 57 subjects)
- AC-092: SIRA successfully runs GSM8K benchmark
- AC-093: Comparison report generated with baseline scores (GPT-4, Claude, etc.)

**Test Cases:**
- TC-091: Verify MMLU evaluation completes and produces accuracy score
- TC-092: Verify GSM8K evaluation completes and produces accuracy score
- TC-093: Confirm report includes baseline comparisons

**Estimated Effort:** 2-3 days

**Value Delivered:**
- Industry-standard comparison: "SIRA scores 78% on MMLU (vs GPT-4 86%, GPT-3.5 70%)"
- Credible positioning against commercial models
- Identify SIRA's strengths and weaknesses vs. established benchmarks

---

## Implementation Details

### SIRA → lm-eval Adapter

```python
from lm_eval.api.model import LM
from lm_eval.api.registry import register_model

@register_model("sira")
class SIRAEvaluator(LM):
    """Adapter to evaluate SIRA with lm-evaluation-harness."""
    
    def __init__(self, sira_api_url="http://localhost:8000"):
        self.api_url = sira_api_url
        # Initialize SIRA client
    
    def generate_until(self, requests):
        """Generate responses for benchmark questions."""
        results = []
        for context, until in requests:
            # Call SIRA API
            response = sira_query(context)
            results.append(response)
        return results
    
    def loglikelihood(self, requests):
        """Compute log-likelihood for multiple choice."""
        # SIRA returns quality scores, map to log-likelihood
        pass
```

### Running Benchmarks

```bash
# Install lm-evaluation-harness
pip install lm-eval

# Run MMLU
lm_eval --model sira --tasks mmlu --num_fewshot 5 --output_path results/

# Run GSM8K
lm_eval --model sira --tasks gsm8k --output_path results/

# Run multiple benchmarks
lm_eval --model sira --tasks mmlu,gsm8k,hellaswag --output_path results/
```

### Expected Output

```
MMLU Results:
  Overall Accuracy: 78.2%
  Breakdown by subject:
    - Mathematics: 82.1%
    - Science: 79.8%
    - History: 73.4%
    - Law: 71.2%
  
Comparison to Baselines:
  GPT-4: 86.4% (+8.2% vs SIRA)
  Claude-3: 85.0% (+6.8% vs SIRA)
  GPT-3.5: 70.0% (-8.2% vs SIRA)
  LLaMA-2: 68.9% (-9.3% vs SIRA)

Positioning: SIRA performs between GPT-3.5 and GPT-4
```

---

## Alternative: Custom Benchmark Runner

If we don't want external dependencies, we can build a custom runner:

```python
# src/evaluation/standard_benchmarks.py

class StandardBenchmarkRunner:
    """Run standard AI benchmarks on SIRA."""
    
    def run_mmlu(self, subset="all"):
        """Run MMLU benchmark."""
        # Load MMLU dataset
        dataset = load_mmlu()
        
        # Run questions through SIRA
        results = []
        for question in dataset:
            response = sira.query(question.prompt)
            correct = evaluate_answer(response, question.answer)
            results.append(correct)
        
        # Calculate accuracy
        accuracy = sum(results) / len(results)
        return {
            "benchmark": "MMLU",
            "accuracy": accuracy,
            "total_questions": len(results),
            "correct": sum(results)
        }
```

---

## Recommendation

**For Sprint 5:** Add DEL-036 to integrate `lm-evaluation-harness` and run MMLU + GSM8K.

This will give you:
- ✅ Industry-standard credibility
- ✅ Direct comparison to GPT-4, Claude, LLaMA
- ✅ Identification of strengths/weaknesses
- ✅ Publishable benchmark scores

**Timeline:** 2-3 days implementation + 1 day for running benchmarks

**Result:** You'll be able to say: "SIRA achieves 78% on MMLU (GPT-3.5: 70%, GPT-4: 86%)"
