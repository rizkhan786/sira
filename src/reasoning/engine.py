"""Reasoning engine for SIRA."""
from typing import Dict, Any, List
from datetime import datetime, timezone
from src.llm.client import get_llm_client
from src.quality.scorer import QualityScorer
from src.patterns.extractor import PatternExtractor
from src.patterns.storage import PatternStorage
from src.patterns.retrieval import PatternRetriever
from src.reasoning.pattern_prompt import PatternPromptFormatter
from src.patterns.usage_tracker import PatternUsageTracker
from src.core.logging import get_logger

logger = get_logger(__name__)


class ReasoningEngine:
    """Core reasoning engine with self-improvement capabilities."""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.quality_scorer = QualityScorer()
        self.pattern_extractor = PatternExtractor(
            llm_service=self.llm_client,
            config={}
        )
        self.pattern_storage = PatternStorage()
        self.pattern_retriever = PatternRetriever(self.pattern_storage)
        self.pattern_formatter = PatternPromptFormatter()
        self.usage_tracker = PatternUsageTracker()
        
    async def process_query(
        self,
        query: str,
        session_id: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Process a user query through the reasoning pipeline.
        
        Args:
            query: User's input query
            session_id: Session identifier for context
            context: Optional additional context
            
        Returns:
            Dict with 'response', 'reasoning_steps', 'metadata' keys
        """
        logger.info("reasoning_process_start", session_id=session_id, query_length=len(query))
        
        start_time = datetime.now(timezone.utc)
        
        try:
            # Retrieve similar patterns before reasoning
            retrieved_patterns = self.pattern_retriever.retrieve_patterns(
                query=query,
                n_results=3,
                min_quality=0.7,
                min_similarity=0.2  # Lowered from 0.5 to 0.2 for better matching
            )
            
            # Format patterns for prompt using new formatter
            pattern_metadata = []
            if retrieved_patterns:
                if context is None:
                    context = {}
                context['retrieved_patterns'] = retrieved_patterns
                context['pattern_guidance'] = self.pattern_formatter.format_patterns_for_prompt(retrieved_patterns)
                pattern_metadata = self.pattern_formatter.extract_pattern_metadata(retrieved_patterns)
                
                logger.info(
                    "patterns_applied",
                    pattern_count=len(retrieved_patterns),
                    pattern_ids=self.pattern_formatter.format_pattern_ids_summary(retrieved_patterns)
                )
            
            # Generate reasoning steps
            reasoning_steps = await self._generate_reasoning_steps(query, context)
            
            # Generate final response
            response = await self._generate_response(query, reasoning_steps, context)
            
            # Calculate metrics
            end_time = datetime.now(timezone.utc)
            processing_time = (end_time - start_time).total_seconds()
            
            # Calculate quality score
            quality_result = await self.quality_scorer.calculate_quality_score(
                query=query,
                response=response["text"],
                reasoning_steps=reasoning_steps
            )
            
            # Pattern usage will be recorded in API layer after query is saved
            # (Removed inline tracking to avoid foreign key constraint issues)
            
            # Extract pattern if quality is high enough
            pattern = None
            pattern_stored = False
            if quality_result["quality_score"] >= self.pattern_extractor.QUALITY_THRESHOLD:
                pattern = await self.pattern_extractor.extract_pattern(
                    query=query,
                    response=response["text"],
                    quality_score=quality_result["quality_score"],
                    quality_breakdown={
                        "rule_based": quality_result["rule_based"],
                        "llm_based": quality_result["llm_based"]
                    }
                )
                
                # Store pattern in ChromaDB if extraction succeeded
                if pattern:
                    pattern_stored = self.pattern_storage.store_pattern(pattern)
            
            result = {
                "response": response["text"],
                "reasoning_steps": reasoning_steps,
                "metadata": {
                    "session_id": session_id,
                    "timestamp": end_time.isoformat(),
                    "processing_time_seconds": processing_time,
                    "llm_usage": response["usage"],
                    "confidence_score": response.get("confidence", 0.85),
                    "quality_score": quality_result["quality_score"],
                    "quality_level": quality_result["quality_level"],
                    "quality_breakdown": {
                        "rule_based": quality_result["rule_based"],
                        "llm_based": quality_result["llm_based"]
                    },
                    "pattern_extracted": pattern is not None,
                    "pattern_id": pattern["pattern_id"] if pattern else None,
                    "pattern_stored": pattern_stored,
                    "patterns_retrieved_count": len(retrieved_patterns) if retrieved_patterns else 0,
                    "patterns_applied_count": len(pattern_metadata),
                    "pattern_metadata": pattern_metadata  # For API layer to record usage
                },
                "extracted_pattern": pattern  # Include pattern for storage
            }
            
            logger.info(
                "reasoning_process_complete",
                session_id=session_id,
                processing_time=processing_time,
                steps_count=len(reasoning_steps)
            )
            
            return result
            
        except Exception as e:
            logger.error("reasoning_process_error", session_id=session_id, error=str(e))
            raise
    
    async def _generate_reasoning_steps(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> List[Dict[str, str]]:
        """Generate structured reasoning steps for the query.
        
        This is the core of the self-improvement logic: breaking down
        the problem into explicit reasoning steps.
        """
        prompt = self._build_reasoning_prompt(query, context)
        
        llm_response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=800
        )
        
        # Parse the response into structured steps
        steps = self._parse_reasoning_steps(llm_response["response"])
        
        logger.info("reasoning_steps_generated", steps_count=len(steps))
        
        return steps
    
    async def _generate_response(
        self,
        query: str,
        reasoning_steps: List[Dict[str, str]],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate final response based on reasoning steps."""
        prompt = self._build_response_prompt(query, reasoning_steps, context)
        
        llm_response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "text": llm_response["response"],
            "usage": llm_response["usage"],
            "confidence": 0.85  # Placeholder for future confidence scoring
        }
    
    def _build_reasoning_prompt(
        self,
        query: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build prompt for reasoning step generation."""
        prompt = f"""You are a reasoning assistant. Break down the following query into clear, logical reasoning steps.

Query: {query}
"""
        
        # Add pattern guidance if available
        if context and context.get('pattern_guidance'):
            prompt += f"\n\n{context['pattern_guidance']}\n"
        
        prompt += """\nProvide 3-5 reasoning steps in this exact format:
1. [Step description]
2. [Step description]
3. [Step description]

Each step should be a single, clear thought or action needed to answer the query.
"""
        
        if context and context.get("history"):
            prompt += f"\n\nPrevious context: {context['history'][:200]}"
            
        return prompt
    
    def _build_response_prompt(
        self,
        query: str,
        reasoning_steps: List[Dict[str, str]],
        context: Dict[str, Any] = None
    ) -> str:
        """Build prompt for final response generation."""
        steps_text = "\n".join([
            f"{i+1}. {step['description']}" 
            for i, step in enumerate(reasoning_steps)
        ])
        
        prompt = f"""Based on the following reasoning steps, provide a clear, concise answer to the user's query.

Query: {query}

Reasoning Steps:
{steps_text}

Provide a direct answer that incorporates the reasoning above. Be specific and helpful.
"""
        
        if context and context.get("history"):
            prompt += f"\n\nPrevious context: {context['history'][:200]}"
            
        return prompt
    
    def _parse_reasoning_steps(self, llm_output: str) -> List[Dict[str, str]]:
        """Parse LLM output into structured reasoning steps."""
        steps = []
        lines = llm_output.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Match numbered steps (1., 2., etc.)
            if line and line[0].isdigit() and '.' in line[:3]:
                step_text = line.split('.', 1)[1].strip()
                if step_text:
                    steps.append({
                        "step_number": len(steps) + 1,
                        "description": step_text,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
        
        # If parsing failed, create a single step
        if not steps:
            steps.append({
                "step_number": 1,
                "description": llm_output[:200],
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return steps


async def create_reasoning_engine() -> ReasoningEngine:
    """Factory function to create reasoning engine."""
    return ReasoningEngine()
