.PHONY: format lint typecheck test quality all help

help:
	@echo "SIRA Code Quality Commands"
	@echo "==========================="
	@echo "make format     - Format code with black and isort"
	@echo "make lint       - Run ruff linter"
	@echo "make typecheck  - Run mypy type checker"
	@echo "make test       - Run pytest tests"
	@echo "make quality    - Run all quality checks (lint + typecheck)"
	@echo "make all        - Format, lint, typecheck, and test"

format:
	@echo "Formatting code with black..."
	black src/
	@echo "Sorting imports with isort..."
	isort src/

lint:
	@echo "Running ruff linter..."
	ruff check src/ --fix

typecheck:
	@echo "Running mypy type checker..."
	mypy src/

test:
	@echo "Running pytest..."
	pytest tests/ -v

quality: lint typecheck
	@echo "All quality checks passed!"

all: format quality test
	@echo "All checks completed!"
