# Solution Design - SIRA

## Component Design Details

### 1. Reasoning Engine

#### Core Classes

**`ReasoningEngine`**
```python
class ReasoningEngine:
    """Orchestrates multi-step reasoning process."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        learning_module: LearningModule,
        verification_module: VerificationModule,
        config: ReasoningConfig
    ):
        ...
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> ReasoningResult:
        """Process query with multi-step reasoning."""
        ...
    
    async def _generate_reasoning_steps(
        self,
        query: str,
        patterns: List[Pattern]
    ) -> List[ReasoningStep]:
        """Generate chain-of-thought reasoning steps."""
        ...
    
    async def _refine_reasoning(
        self,
        steps: List[ReasoningStep],
        verification: VerificationResult
    ) -> List[ReasoningStep]:
        """Refine reasoning based on verification feedback."""
        ...
```

**`ReasoningStep`**
```python
@dataclass
class ReasoningStep:
    step_number: int
    description: str
    reasoning: str
    confidence: float
    dependencies: List[int]  # References to prior steps
    timestamp: datetime
```

**`ReasoningResult`**
```python
@dataclass
class ReasoningResult:
    query: str
    answer: str
    reasoning_trace: List[ReasoningStep]
    confidence: float
    patterns_used: List[str]  # Pattern IDs
    iterations: int
    metrics: Dict[str, Any]
    session_id: str
```

---

### 2. Verification Module

#### Core Classes

**`VerificationModule`**
```python
class VerificationModule:
    """Evaluates reasoning quality and triggers refinement."""
    
    async def verify_reasoning(
        self,
        steps: List[ReasoningStep],
        query: str
    ) -> VerificationResult:
        """Verify reasoning steps and calculate quality metrics."""
        ...
    
    async def _calculate_step_quality(
        self,
        step: ReasoningStep,
        context: str
    ) -> float:
        """Calculate quality score for individual step."""
        ...
    
    async def _check_consistency(
        self,
        steps: List[ReasoningStep]
    ) -> ConsistencyResult:
        """Check logical consistency across steps."""
        ...
```

**`VerificationResult`**
```python
@dataclass
class VerificationResult:
    overall_quality: float
    step_scores: List[float]
    confidence: float
    issues_found: List[str]
    refinement_needed: bool
    suggestions: List[str]
```

---

### 3. Learning Module

#### Core Classes

**`LearningModule`**
```python
class LearningModule:
    """Handles pattern extraction, storage, and retrieval."""
    
    def __init__(
        self,
        chromadb_client: ChromaClient,
        postgres_session: Session,
        embedding_model: EmbeddingModel
    ):
        ...
    
    async def retrieve_patterns(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Pattern]:
        """Retrieve relevant patterns for query."""
        ...
    
    async def extract_and_store_pattern(
        self,
        reasoning_result: ReasoningResult
    ) -> Optional[str]:
        """Extract pattern from successful reasoning and store."""
        ...
    
    async def update_pattern_quality(
        self,
        pattern_id: str,
        usage_success: bool
    ):
        """Update pattern quality based on usage outcome."""
        ...
```

**`Pattern`**
```python
@dataclass
class Pattern:
    id: str
    structure: str  # Abstract pattern structure
    context: str  # When to apply
    reasoning_template: str
    quality_score: float
    usage_count: int
    success_rate: float
    embedding: Optional[List[float]] = None
```

**`PatternExtractor`**
```python
class PatternExtractor:
    """Analyzes reasoning traces to extract reusable patterns."""
    
    async def extract(
        self,
        reasoning_result: ReasoningResult
    ) -> Optional[Pattern]:
        """Extract pattern if reasoning meets quality threshold."""
        ...
    
    def _calculate_pattern_quality(
        self,
        result: ReasoningResult
    ) -> float:
        """Calculate quality score for extracted pattern."""
        ...
```

---

### 4. LLM Integration Layer

#### Core Classes

**`LLMClient` (Protocol)**
```python
from typing import Protocol

class LLMClient(Protocol):
    """Abstract interface for talking to an LLM runtime (local-first)."""
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """Generate completion from a prompt using the configured model."""
        ...
```

**`LocalRuntimeClient`**
```python
class LocalRuntimeClient:
    """HTTP client for a local/self-hosted LLM runtime (OpenAI-style API)."""
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        self._client = httpx.AsyncClient()
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = await self._client.post(f"{self.base_url}/v1/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return LLMResponse.from_chat_completion(data)
```

---

### 5. API Layer

#### FastAPI Application Structure

```
src/api/
├── main.py                 # FastAPI app initialization
├── routes/
│   ├── query.py           # POST /query
│   ├── session.py         # GET /session/{id}
│   ├── patterns.py        # GET /patterns
│   └── metrics.py         # GET /metrics
├── models/
│   ├── requests.py        # Pydantic request models
│   └── responses.py       # Pydantic response models
└── middleware/
    ├── logging.py         # Request logging
    └── error_handler.py   # Global error handling
```

**Request/Response Models**
```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    session_id: Optional[str] = None
    max_iterations: int = Field(default=3, ge=1, le=10)

class QueryResponse(BaseModel):
    query: str
    answer: str
    reasoning_steps: List[Dict]
    confidence: float
    patterns_used: List[str]
    iterations: int
    session_id: str
    metrics: Dict[str, Any]
```

---

### 6. Database Design

#### PostgreSQL Schema

```sql
-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    user_context JSONB,
    last_activity TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Queries table
CREATE TABLE queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id),
    query_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    reasoning_trace JSONB NOT NULL,
    confidence FLOAT NOT NULL,
    iterations INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_session_id (session_id),
    INDEX idx_created_at (created_at)
);

-- Metrics table
CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID NOT NULL REFERENCES queries(id),
    accuracy FLOAT,
    pattern_reuse_count INT NOT NULL DEFAULT 0,
    self_correction_count INT NOT NULL DEFAULT 0,
    reasoning_depth INT NOT NULL,
    response_time_ms INT NOT NULL,
    llm_calls INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_query_id (query_id),
    INDEX idx_created_at (created_at)
);

-- Pattern metadata table
CREATE TABLE pattern_metadata (
    id UUID PRIMARY KEY,
    quality_score FLOAT NOT NULL,
    usage_count INT NOT NULL DEFAULT 0,
    success_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_quality (quality_score DESC),
    INDEX idx_usage (usage_count DESC)
);
```

#### ChromaDB Collections

```python
# Collection configuration
collection_config = {
    "name": "reasoning_patterns",
    "metadata": {
        "hnsw:space": "cosine",  # Similarity metric
        "hnsw:construction_ef": 100,
        "hnsw:M": 16
    }
}

# Document structure
pattern_document = {
    "id": "pattern_uuid",
    "embedding": [0.1, 0.2, ...],  # 384-dim vector
    "metadata": {
        "pattern_id": "uuid",
        "context": "string",
        "quality_score": 0.85,
        "usage_count": 10,
        "created_at": "2025-11-14T..."
    },
    "document": "Pattern structure and template text"
}
```

---

### 7. Configuration Management

**`config.py`**
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API
    api_port: int = 8080
    api_host: str = "0.0.0.0"
    
# LLM
    llm_base_url: str = "http://sira-llm:11434"  # Local LLM runtime URL
    llm_model: str = "llama3:8b"  # Default local model
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    
    # Reasoning
    max_reasoning_iterations: int = 3
    min_confidence_threshold: float = 0.7
    pattern_retrieval_count: int = 5
    
    # Database
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "sira"
    postgres_user: str = "sira"
    postgres_password: str
    
    chromadb_host: str = "chromadb"
    chromadb_port: int = 8000
    
    # Embeddings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

---

### 8. Error Handling Strategy

**Error Hierarchy**
```python
class SIRAException(Exception):
    """Base exception for SIRA system."""
    pass

class LLMClientError(SIRAException):
    """LLM runtime HTTP errors."""
    pass

class PatternRetrievalError(SIRAException):
    """Pattern retrieval failures."""
    pass

class DatabaseError(SIRAException):
    """Database operation failures."""
    pass

class ValidationError(SIRAException):
    """Input validation failures."""
    pass
```

**Error Handling**
- LLM runtime HTTP errors: Retry with exponential backoff (3 attempts)
- Database errors: Log and return 500 with generic message
- Validation errors: Return 400 with specific error details
- Unexpected errors: Log full traceback, return 500

---

See also:
- `solution-architecture.md` - High-level architecture
- `decisions/` - ADRs for major design decisions
