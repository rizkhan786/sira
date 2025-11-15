# Code Quality Guidelines

This document outlines the code quality tools and practices for the SIRA project.

## Tools

### 1. Black (Code Formatter)
**Purpose**: Automatically format Python code to maintain consistent style.

**Configuration**: `pyproject.toml`
- Line length: 100 characters
- Target: Python 3.12

**Usage**:
```powershell
# Inside container
docker exec sira-api-dev black src/

# Using quality script
.\scripts\quality.ps1 -Format
```

### 2. isort (Import Sorter)
**Purpose**: Automatically organize and sort import statements.

**Configuration**: `pyproject.toml` (black-compatible profile)

**Usage**:
```powershell
# Inside container
docker exec sira-api-dev isort src/

# Using quality script
.\scripts\quality.ps1 -Format
```

### 3. Ruff (Fast Linter)
**Purpose**: Fast Python linter for catching common errors and code smells.

**Configuration**: `ruff.toml`
- Checks: pycodestyle, pyflakes, isort, bugbear, comprehensions, pyupgrade
- Line length: 100 characters

**Usage**:
```powershell
# Inside container
docker exec sira-api-dev ruff check src/ --fix

# Using quality script
.\scripts\quality.ps1 -Lint
```

### 4. MyPy (Type Checker)
**Purpose**: Static type checking for Python.

**Configuration**: `pyproject.toml`
- Target: Python 3.12
- Strict equality, warn on return types, unused ignores

**Usage**:
```powershell
# Inside container
docker exec sira-api-dev mypy src/

# Using quality script
.\scripts\quality.ps1 -TypeCheck
```

### 5. pytest (Testing Framework)
**Purpose**: Unit and integration testing.

**Configuration**: `pyproject.toml`
- Test directory: `tests/`
- Coverage reporting enabled

**Usage**:
```powershell
# Inside container
docker exec sira-api-dev pytest tests/ -v

# With coverage
docker exec sira-api-dev pytest tests/ --cov=src --cov-report=html

# Using quality script
.\scripts\quality.ps1 -Test
```

## Quick Start

### Run All Quality Checks
```powershell
# Format, lint, typecheck, and test
.\scripts\quality.ps1 -All
```

### Run Individual Checks
```powershell
# Format code only
.\scripts\quality.ps1 -Format

# Lint only
.\scripts\quality.ps1 -Lint

# Type check only
.\scripts\quality.ps1 -TypeCheck

# Tests only
.\scripts\quality.ps1 -Test
```

### Run Multiple Checks
```powershell
# Lint and type check
.\scripts\quality.ps1 -Lint -TypeCheck
```

## Pre-Commit Hooks

Pre-commit hooks automatically run quality checks before commits.

### Installation
```powershell
# Inside container
docker exec sira-api-dev pip install pre-commit
docker exec sira-api-dev pre-commit install
```

### Usage
Hooks run automatically on `git commit`. To run manually:
```powershell
docker exec sira-api-dev pre-commit run --all-files
```

## Code Quality Standards

### Python Style
- Follow PEP 8 with 100 character line length
- Use type hints where beneficial
- Write docstrings for public functions/classes
- Keep functions focused and small
- Avoid deeply nested code

### Import Organization
```python
# Standard library imports
import json
import logging
from typing import Dict, Any

# Third-party imports
import chromadb
from fastapi import FastAPI

# Local application imports
from src.core.logging import get_logger
from src.patterns.storage import PatternStorage
```

### Type Hints
```python
def process_query(
    query: str,
    session_id: str,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Process a user query.
    
    Args:
        query: User's input query
        session_id: Session identifier
        context: Optional additional context
        
    Returns:
        Processing result dictionary
    """
    pass
```

### Error Handling
```python
try:
    result = risky_operation()
except SpecificException as e:
    logger.error(
        "operation_failed",
        extra={"error": str(e)}
    )
    raise
```

## Continuous Integration

Quality checks should run in CI/CD pipeline:

1. **Pre-commit**: On every commit (local)
2. **Lint + TypeCheck**: On pull request
3. **Tests**: On pull request and main branch
4. **Coverage**: Maintain >80% code coverage

## Configuration Files

- `pyproject.toml` - Black, isort, mypy, pytest configuration
- `ruff.toml` - Ruff linter configuration
- `.flake8` - Flake8 configuration (legacy)
- `.pre-commit-config.yaml` - Pre-commit hooks
- `Makefile` - Make commands for quality checks
- `scripts/quality.ps1` - PowerShell script for Windows

## Troubleshooting

### Black and isort conflicts
Both tools are configured to be compatible via `profile = "black"` in isort config.

### MyPy import errors
Add missing type stubs to `tool.mypy.overrides` in `pyproject.toml`:
```toml
[[tool.mypy.overrides]]
module = ["chromadb.*"]
ignore_missing_imports = true
```

### Ruff vs Flake8
Ruff is preferred as it's faster and more comprehensive. Flake8 config is kept for compatibility.

## Best Practices

1. **Format before committing**: Always run `.\scripts\quality.ps1 -Format`
2. **Fix linting issues**: Run `.\scripts\quality.ps1 -Lint` regularly
3. **Add type hints**: Improve code with type annotations
4. **Write tests**: Maintain test coverage above 80%
5. **Use pre-commit**: Install hooks to catch issues early
6. **Review tool output**: Don't ignore warnings

## Sprint 2 Deliverable

**DEL-022: Code Quality Setup** ✅
- Black formatter configured
- isort for import sorting
- Ruff linter configured
- MyPy type checker configured
- pytest testing framework
- Pre-commit hooks setup
- Quality scripts for Windows
- Makefile for Unix systems
- Comprehensive documentation

All tools are containerized and ready for development workflow.
