
DIST_DIR = ./dist

.PHONY: help install install-dev test test-cov lint format format-check type-check check-all clean run run-debug run-help setup build deploy-testpypi deploy pre-commit-install pre-commit-run pre-commit-update

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# Development targets
install:  ## Install the package in editable mode
	pip3 install -e .

install-dev:  ## Install package with development dependencies
	pip3 install -e ".[dev]"
	@echo ""
	@echo "✅ Dev dependencies installed!"
	@echo "💡 Run 'make pre-commit-install' to set up git hooks"

pre-commit-install:  ## Install pre-commit git hooks
	pre-commit install
	@echo "✅ Pre-commit hooks installed!"
	@echo "   Hooks will run automatically on 'git commit'"

pre-commit-run:  ## Run pre-commit hooks on all files
	pre-commit run --all-files

pre-commit-update:  ## Update pre-commit hooks to latest versions
	pre-commit autoupdate

test:  ## Run unit tests
	python3 -m pytest tests/ -v

test-cov:  ## Run tests with coverage report
	python3 -m pytest tests/ --cov=src/ucm --cov-report=term-missing

lint:  ## Run ruff linter
	python3 -m ruff check src/ tests/

format:  ## Format code with ruff
	python3 -m ruff format src/ tests/

format-check:  ## Check code formatting without making changes
	python3 -m ruff format --check src/ tests/

type-check:  ## Run mypy type checker
	python3 -m mypy src/ucm/

check-all: lint format-check type-check test  ## Run all checks (lint, format, type-check, test)

pre-commit-check:  ## Run pre-commit on all files (same as pre-commit-run)
	pre-commit run --all-files

run:  ## Run the application
	python3 -m ucm

run-debug:  ## Run with debug logging
	python3 -m ucm --log-level DEBUG

run-help:  ## Show application help
	python3 -m ucm --help

# Build and deployment targets
setup:  ## Install build tools
	python3 -m pip install --upgrade build twine

build: setup clean  ## Build distribution packages
	python3 -m build

deploy-testpypi: build  ## Deploy to TestPyPI
	python3 -m twine upload --repository testpypi dist/*

deploy: build  ## Deploy to PyPI
	python3 -m twine upload --repository pypi dist/*

clean:  ## Clean build artifacts and cache
	rm -rf ${DIST_DIR} || true
	rm -rf build/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete
