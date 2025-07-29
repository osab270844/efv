.PHONY: help install install-dev test test-cov lint format clean build publish

help: ## Show this help message
	@echo "Embedded Filesystem Visualizer (EFV) - Development Commands"
	@echo "=========================================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install the package in development mode
	pip install -e .

install-dev: ## Install the package with development dependencies
	pip install -e ".[dev]"

test: ## Run tests
	pytest tests/

test-cov: ## Run tests with coverage
	pytest tests/ --cov=efv --cov-report=html --cov-report=term-missing

lint: ## Run linting checks
	flake8 efv/ tests/
	mypy efv/

format: ## Format code with black
	black efv/ tests/

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: ## Build the package
	python -m build

publish: ## Publish to PyPI (requires twine)
	twine upload dist/*

demo: ## Run the demo
	python3 demo.py

cli: ## Run the CLI tool
	python3 -m efv.cli

gui: ## Run the GUI tool
	efv-gui

check: format lint test ## Run all checks (format, lint, test) 