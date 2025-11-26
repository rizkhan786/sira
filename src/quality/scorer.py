"""Quality scoring for SIRA responses."""
from typing import Dict, List, Any
import re
from src.llm.client import get_llm_client
from src.core.logging import get_logger
from src.core.config import get_settings

logger = get_logger(__name__)


class QualityScorer:
    """Scores response quality using rule-based and LLM verification."""
    
    def __init__(self):
        self.settings = get_settings()
        self.llm_client = get_llm_client()
        
    async def calculate_quality_score(
        self,
        query: str,
        response: str,
        reasoning_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate comprehensive quality score for a response.
        
        Args:
            query: User's query
            response: Generated response
            reasoning_steps: List of reasoning steps taken
            
        Returns:
            Dict with quality_score (0.0-1.0) and breakdown
        """
        logger.info("calculating_quality_score", query_length=len(query), response_length=len(response))
        
        # Rule-based scoring (40%)
        rule_score = self._calculate_rule_score(query, response, reasoning_steps)
        
        # LLM-based verification (60%)
        llm_score = await self._calculate_llm_score(query, response)
        
        # Combined score
        final_score = (rule_score["total"] * 0.4) + (llm_score["total"] * 0.6)
        
        result = {
            "quality_score": round(final_score, 3),
            "rule_based": rule_score,
            "llm_based": llm_score,
            "quality_level": self._get_quality_level(final_score)
        }
        
        logger.info(
            "quality_score_calculated",
            score=result["quality_score"],
            level=result["quality_level"]
        )
        
        return result
    
    def _calculate_rule_score(
        self,
        query: str,
        response: str,
        reasoning_steps: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate rule-based quality scores."""
        
        # Completeness: Is response substantial?
        completeness = self._score_completeness(response)
        
        # Coherence: Are reasoning steps logical?
        coherence = self._score_coherence(reasoning_steps)
        
        # Relevance: Does response address query?
        relevance = self._score_relevance(query, response)
        
        total = (completeness + coherence + relevance) / 3
        
        return {
            "completeness": round(completeness, 3),
            "coherence": round(coherence, 3),
            "relevance": round(relevance, 3),
            "total": round(total, 3)
        }
    
    def _score_completeness(self, response: str) -> float:
        """Score response completeness based on length and substance."""
        response_len = len(response.strip())
        
        if response_len < 10:
            return 0.2  # Too short
        elif response_len < 30:
            return 0.5  # Brief
        elif response_len < 100:
            return 0.8  # Adequate
        else:
            return 1.0  # Comprehensive
    
    def _score_coherence(self, reasoning_steps: List[Dict[str, Any]]) -> float:
        """Score coherence of reasoning steps."""
        if not reasoning_steps:
            return 0.5  # No steps, neutral score
        
        # Check if steps are sequential
        step_numbers = [step.get("step_number", 0) for step in reasoning_steps]
        is_sequential = step_numbers == sorted(step_numbers)
        
        # Check if steps have descriptions
        has_descriptions = all(
            step.get("description", "").strip() for step in reasoning_steps
        )
        
        # Check for contradictions (simple keyword check)
        descriptions = " ".join(step.get("description", "") for step in reasoning_steps).lower()
        contradictions = ["no wait", "actually", "correction", "wrong", "mistake"]
        has_contradiction = any(word in descriptions for word in contradictions)
        
        score = 0.0
        if is_sequential:
            score += 0.4
        if has_descriptions:
            score += 0.4
        if not has_contradiction:
            score += 0.2
        
        return score
    
    def _score_relevance(self, query: str, response: str) -> float:
        """Score relevance of response to query."""
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Check for vague queries FIRST (before word extraction)
        vague_queries = ['what', 'tell', 'stuff', 'thing', 'something', 'anything', 'how', 'why']
        
        # Clean query: remove punctuation and split
        query_cleaned = re.sub(r'[^\w\s]', '', query_lower)  # Remove all punctuation
        query_terms = query_cleaned.split()
        
        # If query is very short or only contains vague words
        if len(query.strip()) < 15:
            # Check if query is only vague terms (like "What?", "tell me", "stuff")
            non_vague_terms = [term for term in query_terms 
                              if term not in vague_queries 
                              and len(term) > 2]
            
            if len(non_vague_terms) == 0:
                # Pure vague query - low relevance score
                return 0.4
        
        # Extract key terms from query (simple approach)
        query_words = set(re.findall(r'\b\w{4,}\b', query_lower))
        response_words = set(re.findall(r'\b\w{4,}\b', response_lower))
        
        if not query_words:
            # Short query with no substantial words
            return 0.5
        
        # Calculate overlap
        overlap = query_words.intersection(response_words)
        relevance = len(overlap) / len(query_words)
        
        # Ensure minimum score if any overlap
        return max(0.3, min(1.0, relevance * 1.2))
    
    async def _calculate_llm_score(self, query: str, response: str) -> Dict[str, float]:
        """Use LLM to verify response quality."""
        
        verification_prompt = f"""You are a quality assessor. Rate this response on these criteria (0.0-1.0):

Query: "{query}"

Response: "{response}"

Rate on these criteria:
1. Correctness: Is the information accurate and factually correct? If the query is vague or lacks a concrete subject (e.g., "What?", "tell me", "stuff", "thing"), score LOW (≈0.3–0.4) because a vague query cannot yield a correct, specific answer.
2. Completeness: Does it fully answer the question without omitting key information? If the query is vague or missing context, the response cannot be complete — score LOW (≈0.3–0.4).
3. Clarity: Is it clear, well-structured, and easy to understand?

Respond ONLY with JSON in this exact format:
{{"correctness": 0.0, "completeness": 0.0, "clarity": 0.0}}
"""
        
        try:
            llm_response = await self.llm_client.generate(
                prompt=verification_prompt,
                temperature=0.3,  # Lower temperature for consistent evaluation
                max_tokens=100
            )
            
            # Parse JSON response
            import json
            response_text = llm_response["response"].strip()
            
            # Extract JSON if wrapped in text
            json_match = re.search(r'\{[^}]+\}', response_text)
            if json_match:
                scores = json.loads(json_match.group())
            else:
                scores = json.loads(response_text)
            
            correctness = float(scores.get("correctness", 0.7))
            completeness = float(scores.get("completeness", 0.7))
            clarity = float(scores.get("clarity", 0.7))
            
            # Clamp values to 0.0-1.0
            correctness = max(0.0, min(1.0, correctness))
            completeness = max(0.0, min(1.0, completeness))
            clarity = max(0.0, min(1.0, clarity))
            
            total = (correctness + completeness + clarity) / 3
            
            return {
                "correctness": round(correctness, 3),
                "completeness": round(completeness, 3),
                "clarity": round(clarity, 3),
                "total": round(total, 3)
            }
            
        except Exception as e:
            logger.error("llm_verification_failed", error=str(e))
            # Fallback to neutral scores if LLM verification fails
            return {
                "correctness": 0.7,
                "completeness": 0.7,
                "clarity": 0.7,
                "total": 0.7
            }
    
    def _get_quality_level(self, score: float) -> str:
        """Convert numeric score to quality level."""
        if score < 0.7:
            return "poor"
        elif score < 0.8:
            return "acceptable"
        elif score < 0.9:
            return "good"
        else:
            return "excellent"


# Convenience function
async def calculate_quality_score(
    query: str,
    response: str,
    reasoning_steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate quality score (convenience function)."""
    scorer = QualityScorer()
    return await scorer.calculate_quality_score(query, response, reasoning_steps)
