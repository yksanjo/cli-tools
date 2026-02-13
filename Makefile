.PHONY: help install install-dev test lint format type-check clean build check-all ci

PYTHON := python3
PIP := pip3

help:
	@echo "Available targets:"
	@echo "  install      - Install package"
	@echo "  install-dev  - Install package with dev dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linter (ruff)"
	@echo "  format       - Format code (black)"
	@echo "  format-check - Check code formatting"
	@echo "  type-check   - Run type checker (mypy)"
	@echo "  check-all    - Run all checks (lint, format, type-check, test)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  ci           - Run CI pipeline locally"

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	pytest

test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

lint:
	ruff check .

format:
	black .

format-check:
	black --check .

type-check:
	mypy file_compressor.py grep_clone.py json_parser.py

check-all: lint format-check type-check test

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf __pycache__/
	rm -rf .coverage
	rm -rf coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	$(PYTHON) -m build

ci: check-all
	@echo "All CI checks passed!"
