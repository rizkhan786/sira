# How AI Models Are Rated & Evaluated

**Document Version:** 1.0  
**Date:** 2025-12-03  
**Status:** Active

---

## Executive Summary

AI models (especially Large Language Models like GPT, LLaMA, Claude) are evaluated using multiple standardized benchmarks and tests. These measure different capabilities: reasoning, knowledge, coding, safety, and more.

**Quick Answer:**
- **Benchmarks:** Standardized test suites (MMLU, HumanEval, etc.)
- **Metrics:** Accuracy, perplexity, pass rate, win rate
- **Categories:** Knowledge, reasoning, coding, safety, truthfulness
- **Rankings:** Leaderboards (LMSYS, HuggingFace, etc.)

---

## Common AI Model Benchmarks

### 1. **MMLU (Massive Multitask Language Understanding)**

**What it tests:** Knowledge across 57 subjects
- Elementary math, US history, computer science
- Law, medicine, ethics, economics
- STEM subjects, humanities, social sciences

**Format:**
- Multiple choice questions (A, B, C, D)
- 5-shot learning (5 examples provided)
- 14,042 questions total

**Scoring:**
- Accuracy: % of questions answered correctly
- Per-subject breakdown

**Example:**
```
Question: What is the capital of France?
A) London
B) Paris
C) Berlin
D) Rome

Correct Answer: B
Model Score: 1.0 (100% if correct)
```

**Top Scores (as of 2023-2024):**
- GPT-4: ~86%
- Claude 3 Opus: ~86%
- Gemini Ultra: ~90%
- LLaMA 3 70B: ~82%
- LLaMA 3.2 3B: ~55-60% (smaller model)

---

### 2. **HumanEval**

**What it tests:** Python code generation ability

**Format:**
- 164 programming problems
- Function signature + docstring provided
- Model generates function body
- Automated test cases verify correctness

**Scoring:**
- pass@1: % passed on first attempt
- pass@10: % passed within 10 attempts
- pass@100: % passed within 100 attempts

**Example:**
```python
def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer 
    to each other than given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
    # Model generates code here
```

**Top Scores:**
- GPT-4: ~67% (pass@1)
- GPT-4 Turbo: ~85% (pass@1)
- Claude 3.5 Sonnet: ~92% (pass@1)
- DeepSeek-Coder: ~78% (pass@1)
- LLaMA 3.2 3B: ~20-30% (pass@1)

---

### 3. **GSM8K (Grade School Math)**

**What it tests:** Mathematical reasoning

**Format:**
- 8,500 grade school math word problems
- Requires multi-step reasoning
- Natural language solutions expected

**Scoring:**
- Accuracy: % of correct final answers
- Also evaluates reasoning steps

**Example:**
```
Question: James has 5 apples. He gives 2 to his friend and then 
buys 3 more. How many apples does he have now?

Expected Answer: 6
Expected Steps:
1. Start with 5 apples
2. Give away 2: 5 - 2 = 3
3. Buy 3 more: 3 + 3 = 6
```

**Top Scores:**
- GPT-4: ~92%
- Claude 3 Opus: ~95%
- LLaMA 3 70B: ~93%
- LLaMA 3.2 3B: ~50-60%

---

### 4. **HellaSwag**

**What it tests:** Common-sense reasoning and sentence completion

**Format:**
- Given a context, choose the most likely continuation
- Tests understanding of everyday scenarios

**Example:**
```
Context: "A woman is sitting at a piano. She..."

Options:
A) begins to play a beautiful melody
B) transforms into a butterfly
C) starts doing calculus
D) flies to the moon

Correct: A (most plausible continuation)
```

**Top Scores:**
- GPT-4: ~95%
- LLaMA 3 70B: ~89%
- LLaMA 3.2 3B: ~72-78%

---

### 5. **TruthfulQA**

**What it tests:** Truthfulness and ability to avoid misinformation

**Format:**
- Questions that humans often answer incorrectly
- Tests if model gives factually correct answers

**Example:**
```
Question: What happens if you crack your knuckles a lot?

Common False Belief: You'll get arthritis
Correct Answer: There's no evidence it causes arthritis; 
                 it may cause temporary swelling but is 
                 generally harmless
```

**Scoring:**
- % of truthful answers
- % of informative answers
- Combined truthful + informative score

**Top Scores:**
- Claude 3 Opus: ~60-70%
- GPT-4: ~60%
- LLaMA 3: ~45-50%

---

### 6. **BigBench (Beyond the Imitation Game Benchmark)**

**What it tests:** Over 200 diverse tasks

**Categories:**
- Linguistics
- Childhood development
- Math
- Common-sense reasoning
- Biology
- Physics
- Social bias
- Software development

**Scoring:**
- Average across all tasks
- Per-category breakdowns

---

### 7. **LMSYS Chatbot Arena (Elo Ratings)**

**What it tests:** Real-world conversational quality

**Format:**
- Head-to-head comparisons
- Human judges pick better response
- Blind testing (models not revealed)
- Elo rating system (like chess)

**Methodology:**
1. User submits prompt
2. Two models respond anonymously
3. User picks which response is better
4. Elo ratings updated based on results

**Current Elo Ratings (2024):**
- GPT-4 Turbo: ~1250
- Claude 3 Opus: ~1250
- GPT-4: ~1220
- Claude 3.5 Sonnet: ~1270
- Gemini 1.5 Pro: ~1210
- LLaMA 3 70B: ~1200
- LLaMA 3.2 3B: ~1000-1050

**What this measures:**
- Helpfulness
- Coherence
- Factual accuracy
- Following instructions
- Writing quality
- Creativity

---

## Evaluation Metrics Explained

### 1. **Accuracy**
```
Accuracy = (Correct Answers / Total Questions) × 100%
```
- Simple, intuitive
- Used in MMLU, GSM8K, HellaSwag

### 2. **Perplexity**
```
Perplexity = exp(cross-entropy loss)
```
- Lower is better
- Measures how "surprised" model is by correct answer
- Used for language modeling evaluation

### 3. **F1 Score**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```
- Balances precision and recall
- Used for classification tasks

### 4. **BLEU Score** (for translation)
```
Measures n-gram overlap with reference translations
Score: 0-100 (higher is better)
```

### 5. **Elo Rating** (for comparisons)
```
Based on win/loss records in head-to-head matchups
Similar to chess ratings
```

---

## Specialized Benchmarks

### Coding-Specific

**MBPP (Mostly Basic Python Problems)**
- 974 Python programming problems
- Easier than HumanEval
- Tests basic coding skills

**DS-1000 (Data Science)**
- 1,000 data science problems
- Uses libraries like Pandas, NumPy
- More realistic than simple algorithms

**CodeContests**
- Competitive programming problems
- Algorithmic complexity
- Very challenging

### Safety & Ethics

**BBQ (Bias Benchmark for QA)**
- Tests for social biases
- Gender, race, religion, etc.

**ToxiGen**
- Tests if model generates toxic content
- Hate speech detection

**BOLD (Bias in Open-Ended Language Generation)**
- Measures bias in generated text
- Demographic fairness

### Reasoning

**ARC (AI2 Reasoning Challenge)**
- Science questions requiring reasoning
- Elementary to high school level

**WinoGrande**
- Commonsense reasoning via pronoun resolution

**StrategyQA**
- Multi-hop reasoning questions
- Requires chaining facts

---

## How SIRA Could Be Evaluated

### Existing Framework (DEL-035)

SIRA's evaluation framework (Sprint 4) includes:

**Test Suites:**
1. Mathematics (100 questions)
2. Geography (100 questions)
3. Science (100 questions)
4. Coding (50 questions)
5. Reasoning (100 questions)
6. History (50 questions)
7. Language (50 questions)
8. General Knowledge (50 questions)

**Total:** 500+ questions

### SIRA-Specific Metrics (DEL-034)

**Tier 1 (Always Tracked):**
1. Learning Velocity: Quality improvement rate
2. Pattern Utilization: % queries using patterns
3. Average Quality Score: Mean quality
4. Domain Coverage: Domains with good patterns

**Tier 2 (Weekly):**
5. Self-Correction Success: % refinements that help
6. Pattern Transfer: Success in new contexts
7. Convergence Rate: Time to stable performance

**Tier 3 (Monthly):**
8. SIRA vs. Baseline: Improvement over base LLM
9. Domain-Specific: Quality by domain
10. User Satisfaction: Feedback-based

### Recommended Additional Evaluations

**For SIRA Quality:**
1. Run on standard benchmarks (MMLU, GSM8K, HumanEval)
2. Measure with and without pattern learning
3. Compare:
   - Base LLM alone
   - SIRA after 0 queries (no patterns learned)
   - SIRA after 100 queries
   - SIRA after 1000 queries

**Expected Results:**
```
MMLU Score:
- LLaMA 3.2 3B (base): 55%
- SIRA (0 queries): 55% (same as base)
- SIRA (100 queries): 56-57% (pattern learning helps)
- SIRA (1000 queries): 57-59% (more patterns)

Improvement: +2-4% from pattern learning
```

**Quality Dimensions:**
- Accuracy (correctness)
- Coherence (logical flow)
- Completeness (thorough answers)
- Efficiency (faster over time?)
- Consistency (similar quality repeated)

---

## Leaderboards & Rankings

### Public Leaderboards

**1. LMSYS Chatbot Arena**
- URL: https://chat.lmsys.org/
- Elo ratings from human preferences
- Updated continuously

**2. HuggingFace Open LLM Leaderboard**
- URL: https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
- Average across 6 benchmarks:
  - ARC, HellaSwag, MMLU, TruthfulQA, Winogrande, GSM8K

**3. Stanford HELM**
- Holistic Evaluation of Language Models
- 42 scenarios, 59 metrics
- Comprehensive but complex

**4. AlpacaEval**
- Evaluates instruction-following
- Win rate vs. GPT-4

---

## How to Interpret Scores

### Rule of Thumb

**MMLU Scores:**
- 90%+: State-of-the-art (GPT-4, Gemini Ultra)
- 80-90%: Very strong (Claude, LLaMA 3 70B)
- 70-80%: Strong (LLaMA 3 8B)
- 50-70%: Moderate (LLaMA 3.2 3B, older models)
- <50%: Weak (random guessing is 25%)

**HumanEval (Coding):**
- 80%+: Excellent coding assistant
- 60-80%: Good for coding help
- 40-60%: Basic coding capability
- <40%: Limited coding ability

**Elo Ratings:**
- 1250+: Top-tier (GPT-4, Claude 3)
- 1150-1250: Very strong
- 1050-1150: Strong
- 950-1050: Moderate
- <950: Weak

### Context Matters

**Model Size:**
- Larger models generally score higher
- LLaMA 3 70B > LLaMA 3 8B > LLaMA 3.2 3B

**Task Type:**
- Some models excel at coding (Claude 3.5 Sonnet)
- Some at general knowledge (GPT-4)
- Some at math (Gemini)

**Use Case:**
- High scores ≠ best for all tasks
- Consider: speed, cost, deployment
- Small local model might be better than expensive API

---

## Limitations of Benchmarks

### 1. **Benchmark Saturation**
- Models can "overfit" to popular benchmarks
- Test data might leak into training data
- New benchmarks needed regularly

### 2. **Limited Coverage**
- Can't test everything
- Real-world is more complex
- Novel situations not in benchmarks

### 3. **Gaming the Metrics**
- Optimizing for benchmarks ≠ better real-world performance
- Cherry-picking which benchmarks to report

### 4. **Human Evaluation Gap**
- Automated metrics miss nuance
- Helpfulness hard to quantify
- Creativity not captured

---

## SIRA's Unique Evaluation Approach

### Self-Improvement Metrics

SIRA tracks its own improvement:

**Learning Velocity:**
```
Quality at query N - Quality at query 0
-----------------------------------------
                N
```

**Pattern Effectiveness:**
```
Avg quality with patterns - Avg quality without patterns
```

**Convergence:**
```
How many queries until quality stabilizes?
```

### Why This Matters

**Standard benchmarks test static capability:**
- "How good is the model NOW?"

**SIRA tracks dynamic capability:**
- "How fast does the model IMPROVE?"
- "Does pattern learning actually help?"
- "Which domains benefit most?"

---

## Summary

### How AI Models Are Rated

**Standardized Tests:**
- MMLU (knowledge): ~14K questions
- HumanEval (coding): 164 problems
- GSM8K (math): 8.5K problems
- HellaSwag (reasoning): common-sense
- TruthfulQA (accuracy): factual correctness

**Human Evaluation:**
- LMSYS Arena: Elo ratings from preferences
- Win rate comparisons

**Metrics:**
- Accuracy (% correct)
- Pass rate (coding)
- Perplexity (language modeling)
- Elo rating (comparisons)

**Leaderboards:**
- HuggingFace Open LLM Leaderboard
- LMSYS Chatbot Arena
- Stanford HELM

### Key Takeaways

1. **Multiple benchmarks needed** - No single test captures everything
2. **Size matters** - Larger models generally score higher
3. **Specialization helps** - Code models better at coding
4. **Context is key** - Best model depends on use case
5. **Scores aren't everything** - Real-world performance matters more

### For SIRA

**Current Evaluation:**
- Internal test suites (500+ questions)
- 10 custom metrics
- Learning trajectory tracking

**Recommended:**
- Run standard benchmarks (MMLU, HumanEval)
- Compare base LLM vs SIRA after learning
- Track improvement over time
- Measure pattern learning effectiveness

---

## References

- **MMLU Paper:** https://arxiv.org/abs/2009.03300
- **HumanEval:** https://arxiv.org/abs/2107.03374
- **LMSYS Arena:** https://chat.lmsys.org/
- **HuggingFace Leaderboard:** https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
- **Stanford HELM:** https://crfm.stanford.edu/helm/

---

## Related SIRA Documents

- `docs/30-Planning/sprints/sprint-04-scope.md` - DEL-035 Evaluation Framework
- `docs/30-Planning/deliverables-register.md` - DEL-034 Core Metrics
- `docs/00-Initiation/how-sira-learns.md` - Learning mechanism
