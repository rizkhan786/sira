# Test Response Artifacts

This directory stores captured API responses from deliverable testing.

## Purpose

When testing deliverables using the "Test Deliverable" WARP macro, responses are saved here for:
1. Validation script input
2. Test documentation
3. Debugging and comparison
4. Audit trail

## Naming Convention

```
del-XXX-tc-YYY.json
```

Where:
- `XXX` = Deliverable number (e.g., 007)
- `YYY` = Test case number (e.g., 019)

## Example Files

```
tests/responses/
├── del-007-tc-019.json   # DEL-007 test case TC-019 response
├── del-007-tc-020.json   # DEL-007 test case TC-020 response
├── del-008-tc-022.json   # DEL-008 test case TC-022 response
└── README.md             # This file
```

## Usage

**Capture response:**
```bash
# During testing in browser/API client, save full JSON response
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}' \
  > tests/responses/del-007-tc-019.json
```

**Validate response:**
```bash
python tests/validation/validate_del007.py tests/responses/del-007-tc-019.json
```

## Retention

- Keep response files for the current sprint
- Archive or delete after sprint completion
- Do NOT commit large response files (>100KB) - use git-lfs or summarize
- Always .gitignore sensitive data
