.PHONY: help build build-wheel clean

# Born-new window: the check/fix/test targets return with the implementation
# and its tooling (ruff/mypy/pytest are not yet dependencies of the new
# package). Import contracts run in CI (import-rules.yml) via
# `uv run --group lint lint-imports`.

# Default target
help:
	@echo "Available commands:"
	@echo ""
	@echo "  Build:"
	@echo "    make build        - Build sdist and wheel"
	@echo "    make build-wheel  - Build wheel only"
	@echo "    make clean        - Remove build artifacts"

# === Build ===

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
