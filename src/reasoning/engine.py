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
from src.reasoning.refinement import RefinementLoop, RefinementConfig
from src.matlab.config_reader import ConfigReader
from src.core.logging import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)
settings = get_settings()


class ReasoningEngine:
    """Core reasoning engine with self-improvement capabilities."""
    
    def __init__(self, config_reader: ConfigReader = None):
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
        
        # Initialize config reader if not provided
        self.config_reader = config_reader or ConfigReader()
        
        # Get MATLAB-optimized config parameters
        max_iterations = self.config_reader.get_config('max_iterations', default=3)
        quality_threshold = self.config_reader.get_config('refinement_threshold', default=0.8)
        
        # Create refinement config with MATLAB parameters
        refinement_config = RefinementConfig(
            max_iterations=max_iterations,
            quality_threshold=quality_threshold
        )
        
        self.refinement_loop = RefinementLoop(refinement_config)
        
        logger.info(
            "reasoning_engine_initialized",
            matlab_max_iterations=max_iterations,
            matlab_quality_threshold=quality_threshold
        )
        
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
            # Fast mode: skip pattern retrieval for speed
            retrieved_patterns = []
            if not settings.fast_mode:
                # Retrieve similar patterns before reasoning
                retrieved_patterns = await self.pattern_retriever.retrieve_patterns(
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
            
            initial_quality = quality_result["quality_score"]
            
            # Iterative refinement if quality below threshold
            refinement_result = None
            # Fast mode: skip refinement iterations
            if not settings.fast_mode and self.refinement_loop.should_refine(initial_quality):
                logger.info(
                    "starting_refinement",
                    initial_quality=initial_quality,
                    threshold=self.refinement_loop.config.quality_threshold
                )
                
                refinement_result = await self.refinement_loop.refine(
                    query=query,
                    initial_response=response["text"],
                    initial_steps=reasoning_steps,
                    initial_quality=initial_quality,
                    reasoning_engine=self,
                    quality_scorer=self.quality_scorer,
                    context=context
                )
                
                # Use refined response
                response["text"] = refinement_result.response
                reasoning_steps = refinement_result.reasoning_steps
                quality_result["quality_score"] = refinement_result.final_quality
                
                # Update quality breakdown with final iteration
                final_quality = await self.quality_scorer.calculate_quality_score(
                    query=query,
                    response=refinement_result.response,
                    reasoning_steps=refinement_result.reasoning_steps
                )
                quality_result["quality_level"] = final_quality["quality_level"]
                quality_result["rule_based"] = final_quality["rule_based"]
                quality_result["llm_based"] = final_quality["llm_based"]
            
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
            
            # Build metadata including refinement info
            metadata = {
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
            }
            
            # Add refinement metadata if refinement occurred
            if refinement_result:
                metadata["refinement"] = {
                    "performed": True,
                    "iterations": refinement_result.iterations,
                    "initial_quality": initial_quality,
                    "final_quality": refinement_result.final_quality,
                    "quality_progression": refinement_result.quality_progression,
                    "convergence_reason": refinement_result.convergence_reason
                }
            else:
                metadata["refinement"] = {
                    "performed": False,
                    "reason": "quality_above_threshold" if initial_quality >= self.refinement_loop.config.quality_threshold else "not_applicable"
                }
            
            result = {
                "response": response["text"],
                "reasoning_steps": reasoning_steps,
                "metadata": metadata,
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
        
        # Include extracted preferences FIRST (rule-based, explicit)
        if context and context.get("preference_prompt"):
            prompt += f"\n{context['preference_prompt']}"
        
        # Include full conversation history for additional context
        if context and context.get("conversation_history"):
            prompt += f"""\n=== Previous Conversation (for reference) ===
{context['conversation_history']}
============================================
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
"""
        
        # Include extracted preferences FIRST (rule-based, explicit)
        if context and context.get("preference_prompt"):
            prompt += f"\n{context['preference_prompt']}"
        
        # Include full conversation history for additional context
        if context and context.get("conversation_history"):
            prompt += f"""\n=== Previous Conversation (for reference) ===
{context['conversation_history']}
============================================

IMPORTANT: When providing your answer, strictly follow the USER PREFERENCES above.
If multiple preferences are listed, your answer MUST combine ALL of them.
"""
        else:
            prompt += "\n\nProvide a direct answer that incorporates the reasoning above. Be specific and helpful.\n"
            
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


async def create_reasoning_engine(config_reader: ConfigReader = None) -> ReasoningEngine:
    """Factory function to create reasoning engine.
    
    Args:
        config_reader: Optional ConfigReader instance for MATLAB integration
        
    Returns:
        ReasoningEngine instance with MATLAB config applied
    """
    return ReasoningEngine(config_reader=config_reader)
