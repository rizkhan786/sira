"""Pattern retrieval and ranking for query processing."""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class PatternRetriever:
    """Retrieves and ranks patterns for incoming queries."""
    
    # Ranking weights for pattern selection
    WEIGHT_SIMILARITY = 0.6
    WEIGHT_QUALITY = 0.2
    WEIGHT_SUCCESS_RATE = 0.15
    WEIGHT_USAGE_COUNT = 0.05
    
    def __init__(self, pattern_storage):
        """Initialize pattern retriever.
        
        Args:
            pattern_storage: PatternStorage instance
        """
        self.storage = pattern_storage
        
    def retrieve_patterns(
        self,
        query: str,
        n_results: int = 3,
        min_quality: float = 0.7,
        min_similarity: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant patterns for a query.
        
        Args:
            query: Query text to find patterns for
            n_results: Maximum number of patterns to retrieve
            min_quality: Minimum quality score threshold
            min_similarity: Minimum similarity score threshold
            
        Returns:
            List of ranked patterns with scores
        """
        logger.info(
            "retrieving_patterns",
            extra={
                "query_length": len(query),
                "n_results": n_results,
                "min_quality": min_quality
            }
        )
        
        # Search for similar patterns
        similar_patterns = self.storage.search_similar_patterns(
            query=query,
            n_results=n_results * 2,  # Get more candidates for ranking
            min_quality=min_quality
        )
        
        if not similar_patterns:
            logger.info(
                "no_patterns_found",
                extra={"query_length": len(query)}
            )
            return []
        
        # Filter by minimum similarity
        filtered_patterns = [
            p for p in similar_patterns
            if p['similarity_score'] >= min_similarity
        ]
        
        if not filtered_patterns:
            logger.info(
                "patterns_filtered_out",
                extra={
                    "candidates": len(similar_patterns),
                    "min_similarity": min_similarity
                }
            )
            return []
        
        # Rank patterns using composite score
        ranked_patterns = self._rank_patterns(filtered_patterns)
        
        # Return top N results
        top_patterns = ranked_patterns[:n_results]
        
        logger.info(
            "patterns_retrieved",
            extra={
                "retrieved_count": len(top_patterns),
                "top_pattern_score": top_patterns[0]['ranking_score'] if top_patterns else 0
            }
        )
        
        return top_patterns
    
    def _rank_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank patterns using weighted scoring.
        
        Args:
            patterns: List of pattern candidates
            
        Returns:
            Sorted list of patterns with ranking scores
        """
        for pattern in patterns:
            metadata = pattern['metadata']
            
            # Normalize scores (0-1 range)
            similarity = pattern['similarity_score']
            quality = metadata['quality_score']
            success_rate = metadata.get('success_rate', 0.0)
            
            # Normalize usage count (log scale, cap at 100)
            usage_count = min(metadata.get('usage_count', 0), 100)
            normalized_usage = usage_count / 100.0 if usage_count > 0 else 0.0
            
            # Calculate composite ranking score
            ranking_score = (
                self.WEIGHT_SIMILARITY * similarity +
                self.WEIGHT_QUALITY * quality +
                self.WEIGHT_SUCCESS_RATE * success_rate +
                self.WEIGHT_USAGE_COUNT * normalized_usage
            )
            
            pattern['ranking_score'] = ranking_score
            
            logger.debug(
                "pattern_scored",
                extra={
                    "pattern_id": pattern['pattern_id'],
                    "ranking_score": ranking_score,
                    "similarity": similarity,
                    "quality": quality
                }
            )
        
        # Sort by ranking score (descending)
        patterns.sort(key=lambda p: p['ranking_score'], reverse=True)
        
        return patterns
    
    def extract_pattern_guidance(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Extract guidance from a pattern for reasoning.
        
        Args:
            pattern: Pattern dictionary
            
        Returns:
            Guidance dictionary with steps and template
        """
        metadata = pattern['metadata']
        
        # Parse document back to structured format
        # (In a real system, we'd store the full pattern separately)
        guidance = {
            'pattern_id': pattern['pattern_id'],
            'pattern_type': metadata['pattern_type'],
            'domain': metadata['domain'],
            'applicability': metadata['applicability'],
            'similarity_score': pattern['similarity_score'],
            'ranking_score': pattern['ranking_score']
        }
        
        return guidance
    
    def format_patterns_for_prompt(self, patterns: List[Dict[str, Any]]) -> str:
        """Format retrieved patterns for inclusion in LLM prompt.
        
        Args:
            patterns: List of retrieved patterns
            
        Returns:
            Formatted string for prompt
        """
        if not patterns:
            return ""
        
        lines = ["Here are similar reasoning patterns that may help:"]
        
        for i, pattern in enumerate(patterns, 1):
            metadata = pattern['metadata']
            lines.append(f"\n{i}. Pattern ({metadata['pattern_type']}, {metadata['domain']})")
            lines.append(f"   Similarity: {pattern['similarity_score']:.2f}")
            lines.append(f"   Quality: {metadata['quality_score']:.2f}")
            lines.append(f"   Applicability: {metadata['applicability'][:200]}...")
        
        return "\n".join(lines)
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get statistics about pattern retrieval.
        
        Returns:
            Dictionary with stats
        """
        return {
            'total_patterns': self.storage.get_pattern_count(),
            'ranking_weights': {
                'similarity': self.WEIGHT_SIMILARITY,
                'quality': self.WEIGHT_QUALITY,
                'success_rate': self.WEIGHT_SUCCESS_RATE,
                'usage_count': self.WEIGHT_USAGE_COUNT
            }
        }
