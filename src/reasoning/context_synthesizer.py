"""Context synthesizer for conversation history."""
from typing import Dict, Any, List
from src.llm.client import get_llm_client
from src.core.logging import get_logger

logger = get_logger(__name__)


class ContextSynthesizer:
    """Synthesizes conversation history into structured context."""
    
    def __init__(self):
        self.llm_client = get_llm_client()
    
    async def synthesize_context(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Extract key preferences, constraints, and context from conversation.
        
        Args:
            conversation_history: List of {query_text, response_text} dicts
            
        Returns:
            Synthesized context string with cumulative preferences
        """
        if not conversation_history or len(conversation_history) < 2:
            # Not enough history to synthesize
            return ""
        
        # Build conversation text
        history_text = "\n\n".join([
            f"User: {h['query_text']}\nSIRA: {h['response_text']}"
            for h in conversation_history
        ])
        
        # Create synthesis prompt
        prompt = f"""Review the following conversation and extract a concise summary of:
1. ALL user preferences mentioned (combine them, don't drop any)
2. ALL constraints or requirements stated
3. The cumulative context built across messages

Conversation:
{history_text}

Provide a brief synthesis (2-4 sentences) that captures the COMBINED preferences and context. 
If the user mentions multiple interests (like "healthcare" then "technology"), note they want the intersection of both.
Format: "User is interested in [X and Y and Z]. They prefer [constraints]. Context: [key points]."
"""
        
        try:
            result = await self.llm_client.generate(
                prompt=prompt,
                temperature=0.3,  # Low temp for more consistent extraction
                max_tokens=200
            )
            
            synthesis = result["response"].strip()
            logger.info("context_synthesized", synthesis_length=len(synthesis))
            return synthesis
            
        except Exception as e:
            logger.error("context_synthesis_failed", error=str(e))
            return ""
    
    def should_synthesize(self, history_count: int) -> bool:
        """Determine if context synthesis is needed.
        
        Args:
            history_count: Number of messages in history
            
        Returns:
            True if synthesis would be helpful
        """
        # Synthesize when we have 3+ messages (enough context to build cumulative understanding)
        return history_count >= 3
