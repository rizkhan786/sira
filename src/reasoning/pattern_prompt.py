"""Pattern prompt formatting for reasoning guidance."""
from typing import List, Dict, Any


class PatternPromptFormatter:
    """Formats retrieved patterns into structured reasoning guidance."""
    
    MAX_TOKENS_PER_PATTERN = 500
    
    def format_patterns_for_prompt(
        self,
        patterns: List[Dict[str, Any]],
        max_patterns: int = 3
    ) -> str:
        """Format patterns into prompt guidance for LLM.
        
        Args:
            patterns: List of retrieved patterns with metadata
            max_patterns: Maximum number of patterns to include
            
        Returns:
            Formatted string to inject into reasoning prompt
        """
        if not patterns:
            return ""
        
        # Limit to top patterns
        patterns = patterns[:max_patterns]
        
        guidance_parts = ["=== LEARNED PATTERNS ==="]
        guidance_parts.append(
            "The following patterns have been learned from previous successful "
            "reasoning. Use them to guide your approach:\n"
        )
        
        for i, pattern in enumerate(patterns, 1):
            pattern_text = self._format_single_pattern(pattern, index=i)
            guidance_parts.append(pattern_text)
        
        guidance_parts.append("=== END PATTERNS ===\n")
        
        return "\n".join(guidance_parts)
    
    def _format_single_pattern(
        self,
        pattern: Dict[str, Any],
        index: int
    ) -> str:
        """Format a single pattern for prompt inclusion.
        
        Args:
            pattern: Pattern data with metadata
            index: Pattern number in list
            
        Returns:
            Formatted pattern string
        """
        parts = [f"\n--- Pattern {index} ---"]
        
        # Pattern type and domain
        pattern_type = pattern.get("pattern_type", "Unknown")
        domain = pattern.get("domain", "General")
        parts.append(f"Type: {pattern_type} | Domain: {domain}")
        
        # Quality and relevance
        quality = pattern.get("quality_score", 0.0)
        similarity = pattern.get("similarity", 0.0)
        parts.append(f"Quality: {quality:.2f} | Relevance: {similarity:.2f}")
        
        # Reasoning steps
        if pattern.get("reasoning_steps"):
            parts.append("\nRecommended Approach:")
            steps = pattern["reasoning_steps"]
            if isinstance(steps, list):
                for i, step in enumerate(steps[:5], 1):  # Max 5 steps
                    parts.append(f"  {i}. {step}")
            elif isinstance(steps, str):
                # Try to parse string as numbered list
                step_lines = [
                    line.strip() 
                    for line in steps.split('\n') 
                    if line.strip()
                ]
                for line in step_lines[:5]:
                    parts.append(f"  {line}")
        
        # Success indicators
        if pattern.get("success_indicators"):
            parts.append("\nSuccess Indicators:")
            indicators = pattern["success_indicators"]
            if isinstance(indicators, list):
                for indicator in indicators[:3]:  # Max 3 indicators
                    parts.append(f"  • {indicator}")
            elif isinstance(indicators, str):
                parts.append(f"  • {indicators}")
        
        # Applicability notes
        if pattern.get("applicability"):
            applicability = pattern["applicability"]
            if len(applicability) <= 150:  # Keep it concise
                parts.append(f"\nWhen to use: {applicability}")
        
        return "\n".join(parts)
    
    def format_pattern_ids_summary(
        self,
        patterns: List[Dict[str, Any]]
    ) -> str:
        """Create brief summary of pattern IDs for logging.
        
        Args:
            patterns: List of patterns
            
        Returns:
            Comma-separated pattern IDs
        """
        if not patterns:
            return "none"
        
        pattern_ids = [
            p.get("pattern_id", "unknown") 
            for p in patterns
        ]
        return ", ".join(pattern_ids[:5])  # Max 5 IDs
    
    def extract_pattern_metadata(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract minimal metadata for pattern usage tracking.
        
        Args:
            patterns: Full pattern data
            
        Returns:
            List of pattern metadata dicts
        """
        metadata = []
        for pattern in patterns:
            metadata.append({
                "pattern_id": pattern.get("pattern_id"),
                "similarity": pattern.get("similarity", 0.0),
                "quality_score": pattern.get("quality_score", 0.0),
                "domain": pattern.get("domain"),
                "pattern_type": pattern.get("pattern_type")
            })
        return metadata
