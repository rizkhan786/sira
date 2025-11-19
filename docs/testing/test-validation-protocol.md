# Test Validation Protocol

**Purpose**: Prevent incomplete testing by ensuring every acceptance criteria field is validated against actual API responses.

**Created**: 2025-11-19  
**Reason**: Missing `patterns_applied_count` field was not caught during testing because validation was done manually without a checklist.

---

## Problem That Occurred

**Sprint 3 - DEL-007 Testing:**
- ✅ API responded successfully
- ✅ Response had `pattern_extracted`, `pattern_stored`, `patterns_retrieved_count`
- ❌ **MISSED**: `patterns_applied_count` field was missing from response
- ❌ **MISSED**: Didn't validate response against acceptance criteria specification

**Root Cause**: Manual inspection without systematic validation against documented requirements.

---

## Required Process for ALL Future Testing

### Step 1: Extract Expected Fields from Acceptance Criteria

**Before ANY testing**, create a checklist from the sprint scope document.

For each deliverable, list **every field mentioned** in:
1. Acceptance Criteria section
2. Implementation Details section  
3. Response Schema section
4. Test Cases section

**Example for DEL-007:**

From `sprint-03-scope.md` lines 193-200:
```
Query-Level Metrics:
- Pattern count retrieved  → patterns_retrieved_count
- Pattern count applied    → patterns_applied_count
```

**Checklist:**
```
□ patterns_retrieved_count
□ patterns_applied_count
□ pattern_extracted
□ pattern_id
□ pattern_stored
```

### Step 2: Create Test Validation Script

Create a JSON schema or Python script to validate the response:

```python
# test_del007_validation.py
REQUIRED_FIELDS = {
    "metadata": {
        "patterns_retrieved_count": int,
        "patterns_applied_count": int,  # ← THIS WAS MISSING
        "pattern_extracted": bool,
        "pattern_id": (str, type(None)),
        "pattern_stored": bool,
    }
}

def validate_response(response_json):
    """Validate API response has all required fields."""
    errors = []
    
    for section, fields in REQUIRED_FIELDS.items():
        if section not in response_json:
            errors.append(f"Missing section: {section}")
            continue
            
        for field, expected_type in fields.items():
            if field not in response_json[section]:
                errors.append(f"Missing field: {section}.{field}")
            elif not isinstance(response_json[section][field], expected_type):
                errors.append(f"Wrong type for {section}.{field}: expected {expected_type}, got {type(response_json[section][field])}")
    
    return errors

# Usage:
response = get_api_response("/query")
errors = validate_response(response)
if errors:
    print("❌ VALIDATION FAILED:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✅ All required fields present")
```

### Step 3: Compare Against Actual Response

**Manual Browser Testing:**
1. Take snapshot of response
2. Check each field in checklist one-by-one
3. Mark ✅ or ❌
4. **Do NOT proceed** if any field is ❌

**Automated Testing:**
1. Run validation script
2. Script must pass before marking deliverable as tested
3. Include validation output in test report

### Step 4: Document What Was Validated

In test reports, include:

```markdown
## DEL-007 Validation Checklist

### Expected Fields (from sprint-03-scope.md lines 193-200):
- ✅ patterns_retrieved_count: 1
- ✅ patterns_applied_count: 1
- ✅ pattern_extracted: true
- ✅ pattern_id: "pattern_abc123"
- ✅ pattern_stored: true

### Response Schema Validated:
\`\`\`json
{
  "metadata": {
    "patterns_retrieved_count": 1,
    "patterns_applied_count": 1,  ← VERIFIED PRESENT
    "pattern_extracted": true,
    "pattern_id": "pattern_abc123",
    "pattern_stored": true
  }
}
\`\`\`

**Status**: ✅ All fields present and correct type
```

---

## Mandatory Testing Steps

### For Every Deliverable

**1. PRE-TEST: Create Validation Checklist**
   - Read sprint scope document
   - Extract ALL mentioned fields
   - Create checklist or validation script
   - **Time**: 10-15 minutes

**2. DURING TEST: Systematic Validation**
   - Run test
   - Capture full response
   - Validate against checklist field-by-field
   - **Do NOT skip any field**

**3. POST-TEST: Documentation**
   - Include validation checklist in report
   - Show actual values for each field
   - Mark test as ✅ ONLY if all fields present

**4. COMMIT: Test Artifacts**
   - Commit validation script
   - Commit test results with full response
   - Update test report

---

## Test Validation Scripts Location

Store in: `tests/validation/`

**Required scripts:**
- `validate_del007.py` - Pattern Application fields
- `validate_del008.py` - Iterative Refinement fields
- `validate_del010.py` - Metrics fields
- `validate_del016.py` - MATLAB Integration fields

**Template:**
```python
"""
Validation script for DEL-XXX
Generated from: docs/30-Planning/sprints/sprint-XX-scope.md
"""

DELIVERABLE = "DEL-XXX"
SPEC_LOCATION = "sprint-XX-scope.md lines XXX-YYY"

REQUIRED_FIELDS = {
    # Fields extracted from acceptance criteria
}

def validate(response):
    # Validation logic
    pass

if __name__ == "__main__":
    # CLI usage for manual testing
    pass
```

---

## Browser Testing Protocol

When using DevTools MCP for browser testing:

**1. Before clicking "Execute":**
```python
# Create expected fields list
expected = [
    "patterns_retrieved_count",
    "patterns_applied_count",  # From spec
    "pattern_extracted",
    # ... all fields
]
```

**2. After response received:**
```python
# Systematically check each field
for field in expected:
    if field in response["metadata"]:
        print(f"✅ {field}: {response['metadata'][field]}")
    else:
        print(f"❌ MISSING: {field}")
        # STOP TESTING - FIX THE ISSUE
```

**3. Document in test report:**
- Screenshot of response
- Checklist with ✅/❌ for each field
- Full JSON for reference

---

## Acceptance Criteria Validation Template

For each AC, document:

```markdown
### AC-XXX: [Description]

**Expected Behavior**: [from spec]

**Expected Fields in Response**:
1. field_name_1 (type) - description
2. field_name_2 (type) - description
3. field_name_3 (type) - description

**Actual Response**:
\`\`\`json
{
  "field_name_1": value,
  "field_name_2": value,
  "field_name_3": value
}
\`\`\`

**Validation**:
- ✅ field_name_1 present and type correct
- ✅ field_name_2 present and type correct
- ❌ field_name_3 MISSING ← ISSUE FOUND

**Status**: ❌ FAILED - field_name_3 missing
**Action**: Add field to schema, retest
```

---

## Automated Validation Integration

### In CI/CD Pipeline

```yaml
# .github/workflows/test.yml
- name: Validate API Schemas
  run: |
    python tests/validation/validate_all.py
    # Fails if any required field missing
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q "src/api/schemas.py"; then
    echo "Schema changed - running validation..."
    python tests/validation/check_schemas.py
    if [ $? -ne 0 ]; then
        echo "❌ Schema validation failed"
        exit 1
    fi
fi
```

---

## Lessons Learned

### What Went Wrong

1. **No Systematic Validation**: Looked at response, saw data, assumed complete
2. **No Reference Check**: Didn't compare against spec document
3. **No Validation Script**: Manual inspection is error-prone
4. **No Field Checklist**: Easy to miss fields in large responses

### What Should Happen

1. **Extract requirements FIRST**: Before writing any code/tests
2. **Create validation checklist**: From spec document
3. **Validate systematically**: Check every single field
4. **Automate validation**: Scripts catch what humans miss
5. **Document thoroughly**: Prove every field was checked

---

## Implementation Timeline

**Immediate (Sprint 3 Completion):**
- ✅ Fix `patterns_applied_count` field
- ✅ Create this protocol document
- [ ] Create validation scripts for all Sprint 3 deliverables
- [ ] Re-test with validation scripts
- [ ] Update test reports with validation results

**Sprint 4 Start:**
- [ ] Make validation scripts mandatory
- [ ] Add to project documentation
- [ ] Create validation script template
- [ ] Train on systematic validation process

**Ongoing:**
- [ ] Create validation script for each new deliverable
- [ ] Run validation before marking any test complete
- [ ] Include validation output in all test reports
- [ ] Review test reports for validation completeness

---

## Success Metrics

**This protocol is successful when:**
1. Zero fields missing from API responses after testing
2. Every test report includes validation checklist
3. Validation scripts exist for all deliverables
4. No user-reported missing fields (caught in testing)

---

## Appendix: DEL-007 Example

### What Should Have Been Done

**Step 1: Extract from sprint-03-scope.md (lines 193-200)**

```
Query-Level Metrics:
- Query latency (total processing time)
- Quality score (final)
- Iteration count
- Pattern count retrieved
- Pattern count applied         ← THIS ONE
- Improvement over baseline
```

**Step 2: Create checklist**
```
□ processing_time_seconds
□ quality_score
□ iteration_count (in refinement metadata)
□ patterns_retrieved_count
□ patterns_applied_count    ← WOULD HAVE CAUGHT THE ISSUE
□ quality_breakdown
```

**Step 3: Validate response**
```
✅ processing_time_seconds: 39.32
✅ quality_score: 0.973
✅ patterns_retrieved_count: 1
❌ patterns_applied_count: MISSING ← STOP AND FIX
```

**Step 4: Fix and retest**
- Add field to schema
- Restart API
- Retest and verify field present
- Mark as ✅ only after field confirmed

---

**This systematic approach would have caught the missing field BEFORE the user found it.**
