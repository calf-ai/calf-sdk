.PHONY: help check lint-check format-check type-check import-check fix lint-fix format-fix build build-wheel clean

help:
	@echo "Available commands:"
	@echo ""
	@echo "  Checks (CI):"
	@echo "    make check        - Run all checks (lint, format, type, imports)"
	@echo "    make lint-check   - Run linter (ruff check)"
	@echo "    make format-check - Check code formatting (ruff format --check)"
	@echo "    make type-check   - Run type checker (ty)"
	@echo "    make import-check - Check import contracts (import-linter)"
	@echo ""
	@echo "  Fixes:"
	@echo "    make fix          - Fix all auto-fixable issues (lint + format)"
	@echo "    make lint-fix     - Fix linting issues (ruff check --fix)"
	@echo "    make format-fix   - Format code (ruff format)"
	@echo ""
	@echo "  Build:"
	@echo "    make build        - Build sdist and wheel"
	@echo "    make build-wheel  - Build wheel only"
	@echo "    make clean        - Remove build artifacts"

check: lint-check format-check type-check import-check
	@echo "✓ All checks passed"

lint-check:
	@echo "Running linter..."
	@uv run --group dev ruff check .
	@echo "✓ Lint check passed"

format-check:
	@echo "Checking format..."
	@uv run --group dev ruff format --check .
	@echo "✓ Format check passed"

type-check:
	@echo "Running type checker..."
	@uv run --group dev ty check
	@echo "✓ Type check passed"

import-check:
	@echo "Checking import contracts..."
	@uv run --group lint lint-imports
	@echo "✓ Import contracts kept"

fix: lint-fix format-fix
	@echo "✓ All auto-fixes applied"

lint-fix:
	@echo "Fixing lint issues..."
	@uv run --group dev ruff check . --fix
	@echo "✓ Lint fixes applied"

format-fix:
	@echo "Formatting code..."
	@uv run --group dev ruff format .
	@echo "✓ Format fixes applied"

build: clean
	@echo "Building sdist and wheel..."
	@uv build
	@echo "✓ Build complete (output in dist/)"

build-wheel: clean
	@echo "Building wheel..."
	@uv build --wheel
	@echo "✓ Wheel build complete (output in dist/)"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/ build/ *.egg-info
	@echo "✓ Clean complete"
