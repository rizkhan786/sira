"""Iterative refinement system for improving response quality."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
from src.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RefinementConfig:
    """Configuration for refinement loop."""
    max_iterations: int = 3
    quality_threshold: float = 0.8
    enable_critique: bool = True
    plateau_tolerance: float = 0.02  # Stop if improvement < 2%
    min_quality_improvement: float = 0.01  # Minimum improvement to continue


@dataclass
class RefinementResult:
    """Result of refinement process."""
    response: str
    reasoning_steps: List[Dict[str, Any]]
    iterations: int
    quality_progression: List[float]
    final_quality: float
    convergence_reason: str
    iteration_history: List[Dict[str, Any]]


class RefinementLoop:
    """Manages iterative refinement of responses."""
    
    def __init__(self, config: Optional[RefinementConfig] = None):
        """Initialize refinement loop.
        
        Args:
            config: Refinement configuration, uses defaults if None
        """
        self.config = config or RefinementConfig()
        logger.info(
            "refinement_loop_initialized",
            max_iterations=self.config.max_iterations,
            quality_threshold=self.config.quality_threshold
        )
    
    async def refine(
        self,
        query: str,
        initial_response: str,
        initial_steps: List[Dict[str, Any]],
        initial_quality: float,
        reasoning_engine,
        quality_scorer,
        context: Optional[Dict[str, Any]] = None
    ) -> RefinementResult:
        """Refine a response through multiple iterations.
        
        Args:
            query: Original user query
            initial_response: First attempt response
            initial_steps: First attempt reasoning steps
            initial_quality: Quality score of first attempt
            reasoning_engine: Engine to generate refined responses
            quality_scorer: Scorer to evaluate quality
            context: Optional context (patterns, history, etc.)
            
        Returns:
            RefinementResult with best response and iteration history
        """
        logger.info(
            "refinement_started",
            initial_quality=initial_quality,
            threshold=self.config.quality_threshold
        )
        
        # Track all iterations
        iteration_history = [{
            "iteration": 1,
            "response": initial_response,
            "reasoning_steps": initial_steps,
            "quality": initial_quality,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "refinement_prompt": None
        }]
        
        quality_progression = [initial_quality]
        
        # Check if refinement is needed
        if initial_quality >= self.config.quality_threshold:
            logger.info(
                "refinement_not_needed",
                quality=initial_quality,
                threshold=self.config.quality_threshold
            )
            return RefinementResult(
                response=initial_response,
                reasoning_steps=initial_steps,
                iterations=1,
                quality_progression=quality_progression,
                final_quality=initial_quality,
                convergence_reason="quality_threshold_met",
                iteration_history=iteration_history
            )
        
        # Refinement loop
        best_response = initial_response
        best_steps = initial_steps
        best_quality = initial_quality
        
        for iteration in range(2, self.config.max_iterations + 1):
            logger.info(
                "refinement_iteration_start",
                iteration=iteration,
                current_quality=best_quality
            )
            
            # Generate refinement prompt based on iteration
            refinement_prompt = self._build_refinement_prompt(
                query=query,
                previous_response=best_response,
                previous_steps=best_steps,
                previous_quality=best_quality,
                iteration=iteration,
                context=context
            )
            
            # Generate refined response
            try:
                refined_steps = await reasoning_engine._generate_reasoning_steps(
                    query=query,
                    context={
                        **(context or {}),
                        "refinement_prompt": refinement_prompt,
                        "iteration": iteration,
                        "previous_quality": best_quality
                    }
                )
                
                refined_response_data = await reasoning_engine._generate_response(
                    query=query,
                    reasoning_steps=refined_steps,
                    context=context
                )
                
                refined_response = refined_response_data["text"]
                
                # Score refined response
                quality_result = await quality_scorer.calculate_quality_score(
                    query=query,
                    response=refined_response,
                    reasoning_steps=refined_steps
                )
                
                refined_quality = quality_result["quality_score"]
                quality_progression.append(refined_quality)
                
                # Record iteration
                iteration_history.append({
                    "iteration": iteration,
                    "response": refined_response,
                    "reasoning_steps": refined_steps,
                    "quality": refined_quality,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "refinement_prompt": refinement_prompt
                })
                
                logger.info(
                    "refinement_iteration_complete",
                    iteration=iteration,
                    quality=refined_quality,
                    improvement=refined_quality - best_quality
                )
                
                # Check convergence criteria
                convergence_reason = self._check_convergence(
                    iteration=iteration,
                    quality_progression=quality_progression
                )
                
                # Update best response if improved
                if refined_quality > best_quality:
                    best_response = refined_response
                    best_steps = refined_steps
                    best_quality = refined_quality
                
                # Stop if converged
                if convergence_reason:
                    logger.info(
                        "refinement_converged",
                        reason=convergence_reason,
                        iterations=iteration,
                        final_quality=best_quality
                    )
                    return RefinementResult(
                        response=best_response,
                        reasoning_steps=best_steps,
                        iterations=iteration,
                        quality_progression=quality_progression,
                        final_quality=best_quality,
                        convergence_reason=convergence_reason,
                        iteration_history=iteration_history
                    )
                
            except Exception as e:
                logger.error(
                    "refinement_iteration_failed",
                    iteration=iteration,
                    error=str(e)
                )
                # Continue with best response so far
                break
        
        # Max iterations reached
        logger.info(
            "refinement_max_iterations",
            iterations=self.config.max_iterations,
            final_quality=best_quality
        )
        
        return RefinementResult(
            response=best_response,
            reasoning_steps=best_steps,
            iterations=self.config.max_iterations,
            quality_progression=quality_progression,
            final_quality=best_quality,
            convergence_reason="max_iterations_reached",
            iteration_history=iteration_history
        )
    
    def _build_refinement_prompt(
        self,
        query: str,
        previous_response: str,
        previous_steps: List[Dict[str, Any]],
        previous_quality: float,
        iteration: int,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build refinement prompt for next iteration.
        
        Args:
            query: Original query
            previous_response: Previous attempt's response
            previous_steps: Previous reasoning steps
            previous_quality: Previous quality score
            iteration: Current iteration number (2 or 3)
            context: Optional context
            
        Returns:
            Refinement prompt string
        """
        if iteration == 2:
            # Iteration 2: Self-critique
            prompt = f"""=== REFINEMENT ITERATION {iteration} ===

Previous response quality: {previous_quality:.2f} (below threshold of {self.config.quality_threshold})

PREVIOUS RESPONSE:
{previous_response}

TASK: Critically analyze the previous response and identify its weaknesses.

Consider:
1. Accuracy: Are there any errors or inaccuracies?
2. Completeness: Is any important information missing?
3. Clarity: Could the explanation be clearer or more concise?
4. Logic: Are the reasoning steps sound and well-connected?

Then provide an improved response that addresses these weaknesses.
"""
        
        else:
            # Iteration 3: Targeted improvement
            # Identify specific issues based on quality score
            issues = []
            if previous_quality < 0.7:
                issues.append("accuracy and correctness")
            if previous_quality < 0.8:
                issues.append("completeness and detail")
            issues.append("clarity and structure")
            
            issues_text = ", ".join(issues)
            
            prompt = f"""=== REFINEMENT ITERATION {iteration} (FINAL) ===

Previous response quality: {previous_quality:.2f} 

FOCUS AREAS FOR IMPROVEMENT: {issues_text}

PREVIOUS RESPONSE:
{previous_response}

TASK: Provide your best possible response, specifically focusing on the areas above.

This is the final refinement attempt. Ensure:
- All information is accurate and verified
- The response is complete with no missing elements
- The explanation is crystal clear and well-structured
- All reasoning steps are explicit and logical
"""
        
        return prompt
    
    def _check_convergence(
        self,
        iteration: int,
        quality_progression: List[float]
    ) -> Optional[str]:
        """Check if refinement should stop.
        
        Args:
            iteration: Current iteration number
            quality_progression: List of quality scores
            
        Returns:
            Convergence reason if should stop, None otherwise
        """
        current_quality = quality_progression[-1]
        
        # Check quality threshold
        if current_quality >= self.config.quality_threshold:
            return "quality_threshold_met"
        
        # Check plateau (quality not improving)
        if len(quality_progression) >= 2:
            previous_quality = quality_progression[-2]
            improvement = current_quality - previous_quality
            
            if improvement < self.config.min_quality_improvement:
                return "plateau_detected"
            
            # Check if quality is decreasing
            if improvement < -self.config.plateau_tolerance:
                return "quality_degraded"
        
        # Check max iterations (caller handles this, but include for completeness)
        if iteration >= self.config.max_iterations:
            return "max_iterations_reached"
        
        return None
    
    def should_refine(self, quality_score: float) -> bool:
        """Determine if refinement is needed based on quality.
        
        Args:
            quality_score: Quality score to check
            
        Returns:
            True if refinement should be attempted
        """
        return quality_score < self.config.quality_threshold
