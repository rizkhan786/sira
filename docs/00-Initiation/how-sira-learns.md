# How SIRA Learns - Architecture & Limitations

**Document Version:** 1.0  
**Date:** 2025-12-03  
**Status:** Active

---

## Executive Summary

SIRA is a **self-improving reasoning agent** that learns from its own successful problem-solving patterns. However, it's crucial to understand **what SIRA can and cannot learn**.

**What SIRA Learns:**
- ✅ **How to reason better** (problem-solving strategies)
- ✅ **Which approaches work best** (pattern effectiveness)
- ✅ **Domain-specific tactics** (math vs science vs coding approaches)

**What SIRA Cannot Learn:**
- ❌ **New factual knowledge** (what happened after its training cutoff)
- ❌ **New technologies** (released after base LLM training)
- ❌ **Current events** (today's news, stock prices, etc.)
- ❌ **Personal data** (unless you explicitly provide it in queries)

---

## How SIRA's Learning Works

### 1. **Base Knowledge (Static)**

SIRA uses a Large Language Model (LLM) as its foundation. Currently:
- **Model:** llama3.2:3b (or similar)
- **Training Cutoff:** ~2023 (varies by model)
- **Knowledge:** Everything the model learned during pre-training

**This knowledge is FROZEN.** SIRA cannot update this base knowledge.

**Example:**
- ✅ Knows: "Python was created by Guido van Rossum"
- ❌ Doesn't know: "New Python 3.13 feature released yesterday"

---

### 2. **Pattern Learning (Dynamic)**

SIRA learns **HOW to solve problems**, not WHAT the facts are.

#### What is a "Pattern"?

A pattern is a reusable reasoning strategy that worked well before.

**Example Pattern:**
```
Pattern: "Breaking Down Complex Math"
Domain: Mathematics
Approach: 
1. Identify the type of problem (algebra, calculus, etc.)
2. Break into smaller sub-problems
3. Solve each sub-problem independently
4. Combine results
Quality: 95%
Used: 47 times
Success Rate: 94%
```

#### How Patterns are Created

**Step-by-Step Process:**

1. **User asks a question**
   ```
   User: "Calculate the area of a circle with radius 5"
   ```

2. **SIRA reasons through it**
   ```
   Step 1: Identify formula needed (A = πr²)
   Step 2: Plug in values (A = π × 5²)
   Step 3: Calculate (A = π × 25 ≈ 78.54)
   ```

3. **Quality scoring**
   ```
   Quality Score: 98% (answer correct, reasoning clear)
   ```

4. **Pattern extraction** (if quality > 80%)
   ```
   Extract pattern: "Circle area calculation approach"
   Store in vector database with embedding
   ```

5. **Future queries benefit**
   ```
   User: "Find area of circle with radius 10"
   SIRA retrieves pattern: "Circle area calculation"
   Applies same reasoning strategy → Faster, better answer
   ```

---

### 3. **What SIRA Actually Learns**

SIRA learns **3 types of knowledge**:

#### A. **Reasoning Strategies** ✅
- How to break down problems
- Which steps to take in what order
- How to verify answers
- When to use specific approaches

**Example:**
- Before: Takes 5 steps to solve algebra problem
- After learning: Takes 3 steps using optimized pattern
- **Improvement:** Efficiency, not new facts

#### B. **Domain-Specific Tactics** ✅
- Math problems need formulas first
- Science questions benefit from hypothesis-testing
- Coding questions should validate syntax
- History questions need context setting

**Example:**
- Query 1: "What is photosynthesis?"
- SIRA learns: Science questions benefit from step-by-step breakdown
- Query 50: Uses that pattern automatically → Better quality

#### C. **Meta-Learning** ✅
- Which patterns work in which domains
- When to refine vs accept first answer
- How to combine multiple patterns
- What quality threshold triggers refinement

**Example:**
- Learns: "Math questions with quality < 85% should be refined"
- Applies: Automatically refines when needed

---

## What SIRA Does NOT Learn

### ❌ New Factual Information

**Scenario:** New technology released tomorrow

```
Tomorrow: "Quantum Computer XYZ-5000 released with 10,000 qubits"

User asks: "Tell me about the XYZ-5000 quantum computer"

SIRA's response: 
- Will NOT know about XYZ-5000 (not in base LLM training)
- MIGHT make up plausible-sounding information (hallucination)
- CAN learn good reasoning patterns for quantum computing questions
- CANNOT learn the actual facts about XYZ-5000
```

**Why?**
- Base LLM knowledge is frozen at training time
- SIRA doesn't have internet access
- No mechanism to ingest new factual data

---

### ❌ Current Events

**Example:**
```
User: "Who won the World Cup today?"

SIRA's response:
- Will NOT know today's results
- Will only know historical World Cup data (up to training cutoff)
- Pattern learning won't help with facts it never knew
```

---

### ❌ Personal Information

**Example:**
```
User: "What's my birthday?"

SIRA's response:
- Will NOT know your personal information
- Has no access to user profiles or databases
- Each session is independent (unless you provide context)
```

**However:**
Within a session, SIRA remembers:
```
User: "My birthday is June 15"
User: "What's my birthday?"
SIRA: "June 15" ✅ (within same session)

[New session starts]
User: "What's my birthday?"
SIRA: "I don't know" ❌ (session ended, memory cleared)
```

---

## How to Work WITH SIRA's Limitations

### Strategy 1: Provide Context

If you need SIRA to know about new technology:

**Bad:**
```
User: "Explain the new React 19 feature"
SIRA: [May not know React 19 if trained before its release]
```

**Good:**
```
User: "React 19 introduced a new 'useActionState' hook for handling form state. 
       Can you explain how this works and compare it to previous approaches?"
SIRA: ✅ Can reason about it now because you provided the context
```

### Strategy 2: Focus on Reasoning

SIRA excels at **HOW**, not **WHAT**:

**Good use cases:**
- "How would I approach debugging this code?"
- "What steps should I take to learn calculus?"
- "Explain the reasoning behind X"
- "Compare these two approaches"

**Poor use cases:**
- "What happened in the news today?"
- "What's the current stock price?"
- "Who won the game yesterday?"

### Strategy 3: Treat SIRA as a Reasoning Partner

Think of SIRA as:
- ✅ A reasoning assistant (helps you think through problems)
- ✅ A pattern recognizer (finds similar problem-solving strategies)
- ✅ A self-improving tutor (gets better at explaining over time)

NOT as:
- ❌ A search engine (can't look up current facts)
- ❌ A database (doesn't store arbitrary information)
- ❌ An oracle (doesn't know everything, especially recent events)

---

## Future Enhancements (Not Currently Implemented)

### Potential Solutions for Knowledge Updates

#### Option 1: Retrieval-Augmented Generation (RAG)
**Concept:** Connect SIRA to external knowledge sources
```
User: "What's new in Python 3.13?"
SIRA: 
1. Searches documentation/web for Python 3.13
2. Retrieves relevant information
3. Reasons about it using learned patterns
4. Provides answer with citations
```
**Status:** Not implemented (would be a future deliverable)

#### Option 2: Fine-tuning
**Concept:** Periodically update base LLM with new training data
```
Every 6 months:
- Download new training data (articles, docs, etc.)
- Fine-tune the model
- Deploy updated model
```
**Status:** Not implemented (resource intensive, requires ML expertise)

#### Option 3: External Knowledge Connector
**Concept:** API integrations for specific domains
```
User: "Current Bitcoin price?"
SIRA:
1. Recognizes financial query
2. Calls CoinMarketCap API
3. Retrieves real-time price
4. Formats response
```
**Status:** Not implemented (would require DEL-038 or similar)

---

## Code Generation Capability (DEL-037)

**Status:** Planned for Sprint 6 (Phase 3)

This addresses part of your question about coding:

### What DEL-037 Will Add

1. **Code-Specialized LLM**
   - Switch to DeepSeek-Coder, CodeLlama, or similar
   - Better code generation capabilities
   - Multi-language support (Python, JavaScript, Java, etc.)

2. **Safe Execution Environment**
   - Sandboxed Docker container
   - Resource limits (CPU, memory, time)
   - Security constraints (no file system access, network isolated)

3. **Code Quality & Testing**
   - Syntax validation
   - Automated test generation
   - Code execution verification

4. **Pattern Learning for Code**
   - Extract successful coding patterns
   - Learn algorithm implementations
   - Reuse data structure patterns
   - Remember effective design patterns

### What This Means

**Before DEL-037:**
```
User: "Write a function to sort a list"
SIRA: [Provides code, but can't verify it runs]
```

**After DEL-037:**
```
User: "Write a function to sort a list"
SIRA: 
1. Generates code using code-specialized LLM
2. Validates syntax
3. Generates test cases
4. Executes code in sandbox
5. Verifies tests pass
6. Extracts pattern if successful
Result: ✅ Verified working code + pattern stored for reuse
```

**Limitations (even after DEL-037):**
- Still can't learn NEW programming languages released after training
- Can't access external APIs/libraries not in training data
- Won't know about frameworks released after LLM training cutoff

**Solution:** Provide context
```
User: "NewFramework v2.0 introduced a 'doThing()' method. 
       Write code that uses this to process data."
SIRA: ✅ Can reason about it and generate code with provided context
```

---

## Summary

### SIRA's Learning Model

| Aspect | Can Learn | Cannot Learn |
|--------|-----------|--------------|
| **Reasoning Strategies** | ✅ Yes | - |
| **Problem-Solving Patterns** | ✅ Yes | - |
| **Domain Tactics** | ✅ Yes | - |
| **New Facts** | ❌ No | ✅ Frozen at LLM training |
| **Current Events** | ❌ No | ✅ No internet access |
| **New Technologies** | ❌ No | ✅ Unless provided in context |
| **Personal Data** | ⚠️ Per-session only | ✅ No persistent user profiles |

### Key Takeaway

**SIRA learns HOW to think, not WHAT to think about.**

- It gets **better at reasoning** over time
- It does NOT get **smarter about new facts** automatically
- You must **provide context** for post-training-cutoff information

### Recommended Usage

1. **Use SIRA for reasoning tasks** (debugging, planning, explaining)
2. **Provide context for new information** (paste docs, explain features)
3. **Focus on HOW questions** (approach, strategy, method)
4. **Don't rely on factual accuracy** for very recent events
5. **Verify important information** (SIRA can hallucinate)

---

## Related Documents

- `docs/00-Initiation/scope-and-objectives.md` - What SIRA is designed to do
- `docs/20-Solution/solution-architecture.md` - Technical architecture
- `docs/30-Planning/deliverables-register.md` - DEL-037 details
- `docs/10-Requirements/functional-requirements.md` - Core capabilities

---

**Questions?**
- How does pattern extraction work technically? → See `src/patterns/extractor.py`
- How are patterns stored? → See `src/patterns/storage.py` (ChromaDB)
- How are patterns retrieved? → See `src/patterns/retrieval.py` (vector search)
- How is quality scored? → See `src/quality/scorer.py`
