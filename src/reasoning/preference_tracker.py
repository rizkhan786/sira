"""Preference tracker for extracting and maintaining user preferences across conversation."""
import re
from typing import List, Dict, Set
from src.core.logging import get_logger

logger = get_logger(__name__)


class PreferenceTracker:
    """Tracks and combines user preferences across conversation turns."""
    
    # Keywords that indicate preference statements
    PREFERENCE_PATTERNS = [
        r"i like ([\w\s]+)",
        r"i prefer ([\w\s]+)",
        r"i want ([\w\s]+)",
        r"i'm interested in ([\w\s]+)",
        r"i need ([\w\s]+)",
        r"focus on ([\w\s]+)",
        r"specifically ([\w\s]+)",
    ]
    
    # Keywords that indicate constraints
    CONSTRAINT_PATTERNS = [
        r"must be ([\w\s]+)",
        r"should be ([\w\s]+)",
        r"needs to be ([\w\s]+)",
        r"has to be ([\w\s]+)",
        r"within ([\w\s]+)",
        r"budget of ([\w\s]+)",
    ]
    
    # Negation patterns
    NEGATION_PATTERNS = [
        r"not ([\w\s]+)",
        r"don't want ([\w\s]+)",
        r"avoid ([\w\s]+)",
        r"except ([\w\s]+)",
    ]
    
    def extract_preferences(self, conversation_history: List[Dict[str, str]]) -> Dict[str, any]:
        """Extract all preferences, constraints, and context from conversation.
        
        Args:
            conversation_history: List of {query_text, response_text} dicts
            
        Returns:
            Dict with preferences, constraints, negations, and combined_context
        """
        preferences = set()
        constraints = set()
        negations = set()
        
        for item in conversation_history:
            query = item['query_text'].lower()
            
            # Extract preferences
            for pattern in self.PREFERENCE_PATTERNS:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    pref = match.group(1).strip()
                    if pref and len(pref) > 2:  # Avoid single words like "it"
                        preferences.add(pref)
            
            # Extract constraints
            for pattern in self.CONSTRAINT_PATTERNS:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    constraint = match.group(1).strip()
                    if constraint and len(constraint) > 2:
                        constraints.add(constraint)
            
            # Extract negations
            for pattern in self.NEGATION_PATTERNS:
                matches = re.finditer(pattern, query, re.IGNORECASE)
                for match in matches:
                    neg = match.group(1).strip()
                    if neg and len(neg) > 2:
                        negations.add(neg)
        
        # Build combined context string
        context_parts = []
        
        if preferences:
            pref_list = list(preferences)
            if len(pref_list) == 1:
                context_parts.append(f"User is interested in {pref_list[0]}")
            elif len(pref_list) == 2:
                context_parts.append(f"User is interested in {pref_list[0]} AND {pref_list[1]}")
            else:
                pref_str = ", ".join(pref_list[:-1]) + f", AND {pref_list[-1]}"
                context_parts.append(f"User is interested in {pref_str}")
            
            # Add explicit intersection note for multiple preferences
            if len(pref_list) > 1:
                context_parts.append(f"CRITICAL: User wants ideas that combine ALL of these interests: {' + '.join(pref_list)}")
        
        if constraints:
            context_parts.append(f"Constraints: {', '.join(constraints)}")
        
        if negations:
            context_parts.append(f"Exclude: {', '.join(negations)}")
        
        combined_context = ". ".join(context_parts) if context_parts else ""
        
        result = {
            "preferences": list(preferences),
            "constraints": list(constraints),
            "negations": list(negations),
            "combined_context": combined_context,
            "has_multiple_preferences": len(preferences) > 1
        }
        
        logger.info(
            "preferences_extracted",
            preferences=list(preferences),
            has_multiple=len(preferences) > 1
        )
        
        return result
    
    def build_context_prompt(self, preferences_data: Dict[str, any]) -> str:
        """Build a context prompt from extracted preferences.
        
        Args:
            preferences_data: Output from extract_preferences()
            
        Returns:
            Formatted context string for prompts
        """
        if not preferences_data["combined_context"]:
            return ""
        
        prompt = f"""=== USER PREFERENCES (CUMULATIVE) ===
{preferences_data['combined_context']}

"""
        
        if preferences_data["has_multiple_preferences"]:
            prefs_combined = " + ".join(preferences_data["preferences"])
            prompt += f"""CRITICAL - DO NOT IGNORE:
⚠️ The user wants ideas that combine ALL of these: {prefs_combined}
⚠️ Your answer MUST include ONLY ideas that have ALL these elements together
⚠️ DO NOT give separate ideas for each interest
⚠️ COMBINE {prefs_combined} in EVERY single idea you provide

Example: If interests are "healthcare + technology", give ideas like:
- AI-powered medical diagnosis systems
- Telemedicine platforms
- Health tracking wearables
- Electronic health records systems
DO NOT give generic healthcare OR generic technology ideas!

"""
        
        return prompt
