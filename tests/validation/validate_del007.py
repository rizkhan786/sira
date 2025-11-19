"""
Validation script for DEL-007: Pattern Application Logic
Generated from: docs/30-Planning/sprints/sprint-03-scope.md lines 36-95
"""

DELIVERABLE = "DEL-007"
SPEC_LOCATION = "sprint-03-scope.md lines 36-95 (AC-019, AC-020, AC-021)"

# Fields extracted from acceptance criteria and implementation details
REQUIRED_FIELDS = {
    "metadata": {
        # Pattern application tracking (AC-020)
        "patterns_retrieved_count": int,
        "patterns_applied_count": int,  # From lines 193-200: "Pattern count applied"
        
        # Pattern extraction (AC-019, AC-021)
        "pattern_extracted": bool,
        "pattern_id": (str, type(None)),
        "pattern_stored": bool,
        
        # Basic metadata
        "session_id": str,
        "timestamp": str,
        "processing_time_seconds": (int, float),
        "llm_usage": dict,
        "confidence_score": (int, float),
        
        # Quality metrics (for AC-021: quality comparison)
        "quality_score": (int, float),
        "quality_level": str,
        "quality_breakdown": dict,
        
        # Refinement info
        "refinement": dict,
    },
    "response": str,
    "reasoning_steps": list,
}


def validate_response(response_json):
    """Validate API response has all required fields.
    
    Args:
        response_json: Dict containing API response
        
    Returns:
        List of error strings (empty if validation passed)
    """
    errors = []
    
    # Check top-level fields
    for field in ["response", "reasoning_steps", "metadata"]:
        if field not in response_json:
            errors.append(f"❌ Missing top-level field: {field}")
    
    if "metadata" not in response_json:
        return errors  # Can't check metadata fields if metadata missing
    
    metadata = response_json["metadata"]
    
    # Check all required metadata fields
    required_metadata = REQUIRED_FIELDS["metadata"]
    for field, expected_type in required_metadata.items():
        if field not in metadata:
            errors.append(f"❌ Missing metadata field: {field}")
        elif metadata[field] is not None:  # Allow None for Optional fields
            actual_type = type(metadata[field])
            if isinstance(expected_type, tuple):
                # Multiple allowed types
                if actual_type not in expected_type:
                    errors.append(
                        f"❌ Wrong type for metadata.{field}: "
                        f"expected {expected_type}, got {actual_type}"
                    )
            else:
                # Single expected type
                if not isinstance(metadata[field], expected_type):
                    errors.append(
                        f"❌ Wrong type for metadata.{field}: "
                        f"expected {expected_type}, got {actual_type}"
                    )
    
    return errors


def print_validation_report(response_json, errors):
    """Print a formatted validation report."""
    print(f"\n{'='*70}")
    print(f"DEL-007 Pattern Application Logic - Validation Report")
    print(f"{'='*70}\n")
    
    if not errors:
        print("✅ VALIDATION PASSED - All required fields present\n")
        
        # Show key pattern fields
        metadata = response_json.get("metadata", {})
        print("Key Pattern Fields:")
        print(f"  - patterns_retrieved_count: {metadata.get('patterns_retrieved_count')}")
        print(f"  - patterns_applied_count: {metadata.get('patterns_applied_count')}")
        print(f"  - pattern_extracted: {metadata.get('pattern_extracted')}")
        print(f"  - pattern_id: {metadata.get('pattern_id')}")
        print(f"  - pattern_stored: {metadata.get('pattern_stored')}")
        print(f"  - quality_score: {metadata.get('quality_score')}")
    else:
        print(f"❌ VALIDATION FAILED - {len(errors)} issue(s) found:\n")
        for error in errors:
            print(f"  {error}")
        print("\n⚠️  DO NOT mark DEL-007 as complete until all issues resolved!")
    
    print(f"\n{'='*70}\n")


def validate_acceptance_criteria(response_json):
    """Check specific acceptance criteria for DEL-007.
    
    AC-019: Retrieved patterns injected into reasoning prompts
    AC-020: Pattern usage tracked per query
    AC-021: Response quality improves with patterns
    """
    issues = []
    metadata = response_json.get("metadata", {})
    
    # AC-020: Pattern usage tracked
    if metadata.get("patterns_retrieved_count") is not None:
        if metadata.get("patterns_applied_count") is None:
            issues.append("AC-020 FAIL: patterns_applied_count missing (usage not fully tracked)")
        elif metadata.get("patterns_retrieved_count", 0) > 0 and metadata.get("patterns_applied_count", 0) == 0:
            issues.append("AC-020 WARNING: Patterns retrieved but none applied")
    
    # AC-021: Quality tracking for pattern effectiveness
    if metadata.get("quality_score") is None:
        issues.append("AC-021 FAIL: quality_score missing (can't measure improvement)")
    
    if metadata.get("quality_breakdown") is None:
        issues.append("AC-021 WARNING: quality_breakdown missing (limited quality analysis)")
    
    return issues


if __name__ == "__main__":
    import sys
    import json
    
    print(f"\nDEL-007 Validation Script")
    print(f"Spec: {SPEC_LOCATION}\n")
    
    if len(sys.argv) > 1:
        # Load from file
        with open(sys.argv[1], 'r') as f:
            response = json.load(f)
    else:
        # Example usage
        print("Usage: python validate_del007.py <response.json>")
        print("\nOr use in Python:")
        print("  from tests.validation.validate_del007 import validate_response")
        print("  errors = validate_response(api_response)")
        print("  if not errors:")
        print("      print('✅ Validation passed')")
        sys.exit(0)
    
    # Validate
    errors = validate_response(response)
    print_validation_report(response, errors)
    
    # Check acceptance criteria
    ac_issues = validate_acceptance_criteria(response)
    if ac_issues:
        print("\nAcceptance Criteria Issues:")
        for issue in ac_issues:
            print(f"  - {issue}")
    
    # Exit with error code if validation failed
    sys.exit(1 if errors or ac_issues else 0)
