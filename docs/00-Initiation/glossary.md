# Glossary - SIRA

## Core Concepts

**SIRA**
Self-Improving Reasoning Agent. An AI system that learns from its own reasoning process.

**Reasoning Pattern**
A sequence of reasoning steps or strategy that led to a successful outcome, stored for future reuse.

**Self-Verification**
Process by which the agent evaluates the quality and correctness of its own reasoning.

**Iterative Refinement**
Multiple passes over a problem, improving the answer with each iteration.

**Chain-of-Thought (CoT)**
Multi-step reasoning where the agent explicitly shows intermediate steps.

**Pattern Reuse**
Applying previously successful reasoning strategies to similar problems.

**Self-Correction**
Agent identifying and fixing errors in its own reasoning without external intervention.

## Technical Terms

**Vector Database**
Database optimized for storing and querying high-dimensional embeddings (ChromaDB in this project).

**LLM**
Large Language Model. AI model used for reasoning steps, served via local runtime (e.g., Llama, Qwen, Mixtral).

**Embedding**
Vector representation of text/concepts for similarity search.

**Session**
A single query-response interaction, potentially involving multiple reasoning iterations.

**Reasoning Trace**
Complete record of all reasoning steps taken for a query.

**Quality Score**
Metric evaluating the effectiveness of a reasoning pattern or answer.

**Pattern Matching**
Finding similar past reasoning patterns for a new query using vector similarity.

## Architecture Components

**Reasoning Engine**
Core component orchestrating multi-step reasoning and self-verification.

**Learning Module**
Component responsible for extracting, storing, and retrieving reasoning patterns.

**Pattern Store**
ChromaDB database containing learned reasoning patterns as vector embeddings.

**Metrics Store**
PostgreSQL database tracking performance metrics and improvement over time.

**API Layer**
FastAPI REST interface for external interaction with SIRA.

**Web Interface**
Dashboard for monitoring reasoning, patterns, and metrics.

## Process Terms

**REQ**
Requirement (functional or non-functional) with format REQ-### or NFR-###.

**DEL**
Deliverable, mapped to one or more requirements, format DEL-###.

**AC**
Acceptance Criterion, success criteria for a deliverable, format AC-###.

**TC**
Test Case, validates one or more acceptance criteria, format TC-###.

**ADR**
Architecture Decision Record, documents significant technical decisions.

**Sprint**
Two-week development cycle with specific deliverables and testing gate.

**Phase**
Collection of sprints working toward major project milestones.

**DoR**
Definition of Ready, criteria that must be met before sprint execution.

**DoD**
Definition of Done, criteria that must be met to mark deliverable complete (tests pass).

## Metrics

**Answer Accuracy**
Percentage of correct/high-quality answers (requires evaluation criteria).

**Pattern Reuse Rate**
Percentage of queries that successfully reuse existing patterns.

**Self-Correction Rate**
Frequency of agent identifying and fixing its own reasoning errors.

**Reasoning Depth**
Number of reasoning steps taken to reach an answer.

**Improvement Rate**
Measurable increase in quality metrics over time.
