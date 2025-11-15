"""Pattern extraction from high-quality query-response pairs."""

import json
import logging
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


class PatternExtractor:
    """Extracts reasoning patterns from high-quality responses."""
    
    QUALITY_THRESHOLD = 0.8
    
    def __init__(self, llm_service, config: Dict[str, Any]):
        """Initialize pattern extractor.
        
        Args:
            llm_service: LLM service for pattern extraction
            config: Configuration dictionary
        """
        self.llm = llm_service
        self.config = config
        self.extraction_prompt = self._load_extraction_prompt()
        
    def _load_extraction_prompt(self) -> str:
        """Load pattern extraction prompt template."""
        return """You are an expert at identifying reasoning patterns. Analyze this query-response pair and extract the underlying reasoning pattern.

Query: {query}
Response: {response}
Quality Score: {quality_score}

Extract a reusable pattern by identifying:
1. The type of question being asked
2. The reasoning steps used
3. The information sources referenced
4. The structure of the response
5. Key characteristics that make this response high quality

Provide your analysis in this exact JSON format:
{{
    "pattern_type": "type of reasoning pattern (e.g., 'factual_lookup', 'multi_step_reasoning', 'comparative_analysis')",
    "domain": "domain or topic area (e.g., 'geography', 'mathematics', 'history')",
    "reasoning_steps": [
        "step 1 description",
        "step 2 description",
        "step 3 description"
    ],
    "success_indicators": [
        "what made this response high quality",
        "key characteristics to replicate"
    ],
    "applicability": "when this pattern should be applied",
    "template": "generalized template with placeholders like {{query_topic}}, {{key_facts}}, {{conclusion}}"
}}

Respond ONLY with valid JSON, no additional text."""

    def should_extract_pattern(self, quality_score: float) -> bool:
        """Determine if a pattern should be extracted based on quality score.
        
        Args:
            quality_score: Quality score of the response (0-1)
            
        Returns:
            True if pattern should be extracted, False otherwise
        """
        return quality_score >= self.QUALITY_THRESHOLD
        
    async def extract_pattern(
        self,
        query: str,
        response: str,
        quality_score: float,
        quality_breakdown: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Extract a reasoning pattern from a query-response pair.
        
        Args:
            query: Original query
            response: Generated response
            quality_score: Overall quality score
            quality_breakdown: Detailed quality metrics
            
        Returns:
            Extracted pattern dictionary or None if extraction fails
        """
        if not self.should_extract_pattern(quality_score):
            logger.info(
                "pattern_extraction_skipped",
                extra={
                    "quality_score": quality_score,
                    "threshold": self.QUALITY_THRESHOLD,
                    "reason": "score_below_threshold"
                }
            )
            return None
            
        logger.info(
            "extracting_pattern",
            extra={
                "query_length": len(query),
                "response_length": len(response),
                "quality_score": quality_score
            }
        )
        
        try:
            # Format the extraction prompt
            prompt = self.extraction_prompt.format(
                query=query,
                response=response,
                quality_score=quality_score
            )
            
            # Call LLM for pattern extraction
            extraction_result = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=1000
            )
            
            # Parse the extracted pattern
            pattern_text = extraction_result['response'].strip()
            
            # Try to find JSON in the response
            start_idx = pattern_text.find('{')
            end_idx = pattern_text.rfind('}') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.error(
                    "pattern_extraction_invalid",
                    extra={
                        "reason": "no_json_found",
                        "response_preview": pattern_text[:300]
                    }
                )
                return None
                
            json_str = pattern_text[start_idx:end_idx]
            
            logger.info(
                "parsing_pattern_json",
                extra={
                    "json_length": len(json_str),
                    "json_preview": json_str[:200]
                }
            )
            
            pattern_data = json.loads(json_str)
            
            # Validate required fields
            required_fields = [
                'pattern_type',
                'domain',
                'reasoning_steps',
                'success_indicators',
                'applicability',
                'template'
            ]
            
            for field in required_fields:
                if field not in pattern_data:
                    logger.error(
                        "pattern_extraction_incomplete",
                        extra={"missing_field": field}
                    )
                    return None
            
            # Enrich pattern with metadata
            pattern = {
                'pattern_id': self._generate_pattern_id(pattern_data),
                'pattern_type': pattern_data['pattern_type'],
                'domain': pattern_data['domain'],
                'reasoning_steps': pattern_data['reasoning_steps'],
                'success_indicators': pattern_data['success_indicators'],
                'applicability': pattern_data['applicability'],
                'template': pattern_data['template'],
                'source_query': query,
                'source_response': response,
                'quality_score': quality_score,
                'quality_breakdown': quality_breakdown or {},
                'extracted_at': datetime.utcnow().isoformat(),
                'usage_count': 0,
                'success_rate': 0.0
            }
            
            logger.info(
                "pattern_extracted_successfully",
                extra={
                    "pattern_id": pattern['pattern_id'],
                    "pattern_type": pattern['pattern_type'],
                    "domain": pattern['domain']
                }
            )
            
            return pattern
            
        except json.JSONDecodeError as e:
            logger.error(
                "pattern_extraction_json_error",
                extra={
                    "error": str(e),
                    "response_preview": extraction_result.get('response', '')[:200]
                }
            )
            return None
            
        except Exception as e:
            logger.error(
                "pattern_extraction_error",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            return None
    
    def _generate_pattern_id(self, pattern_data: Dict[str, Any]) -> str:
        """Generate a unique ID for a pattern.
        
        Args:
            pattern_data: Extracted pattern data
            
        Returns:
            Pattern ID string
        """
        # Create ID from pattern type and domain
        id_source = f"{pattern_data['pattern_type']}_{pattern_data['domain']}"
        hash_value = hashlib.md5(id_source.encode()).hexdigest()[:8]
        
        return f"pattern_{hash_value}"
    
    def generate_template(self, pattern: Dict[str, Any]) -> str:
        """Generate a reusable template from a pattern.
        
        Args:
            pattern: Extracted pattern dictionary
            
        Returns:
            Template string with placeholders
        """
        return pattern.get('template', '')
    
    def apply_template(
        self,
        template: str,
        variables: Dict[str, str]
    ) -> str:
        """Apply variables to a template.
        
        Args:
            template: Template string with placeholders
            variables: Dictionary of variable name to value
            
        Returns:
            Filled template string
        """
        result = template
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, var_value)
            
        return result
    
    def get_pattern_metadata(self, pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from a pattern for storage/retrieval.
        
        Args:
            pattern: Pattern dictionary
            
        Returns:
            Metadata dictionary
        """
        return {
            'pattern_id': pattern['pattern_id'],
            'pattern_type': pattern['pattern_type'],
            'domain': pattern['domain'],
            'quality_score': pattern['quality_score'],
            'extracted_at': pattern['extracted_at'],
            'usage_count': pattern['usage_count'],
            'success_rate': pattern['success_rate'],
            'reasoning_steps_count': len(pattern.get('reasoning_steps', [])),
            'applicability': pattern['applicability']
        }
