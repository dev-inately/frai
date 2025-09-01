.PHONY: help install install-dev test test-unit test-integration test-cov format lint type-check start clean

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$1, $$2}'

install: ## Install production dependencies
	uv pip install -e .

install-dev: ## Install development dependencies
	uv pip install -e ".[dev]"

install-test: ## Install test dependencies
	uv pip install -r requirements-test.txt

test: ## Run all tests
	uv run pytest test_main.py -v

test-unit: ## Run unit tests only
	uv run pytest test_main.py -m "not integration" -v

test-integration: ## Run integration tests only
	uv run pytest test_main.py -m "integration" -v

test-cov: ## Run tests with coverage
	uv run pytest test_main.py --cov=app --cov-report=html --cov-report=term-missing

test-fast: ## Run tests quickly (no coverage, minimal output)
	uv run pytest test_main.py -x --tb=no

test-debug: ## Run tests with debug output
	uv run pytest test_main.py -v -s --tb=long

format: ## Format code with black and isort
	uv run black .
	uv run isort .

lint: ## Run linting with flake8
	uv run flake8 .

type-check: ## Run type checking with mypy
	uv run mypy .

start: ## Start the development server
	uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000

start-prod: ## Start the production server
	uv run uvicorn main:app --host 0.0.0.0 --port 8000

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .coverage htmlcov .pytest_cache .mypy_cache

check: format lint type-check test ## Run all checks

dev-setup: install-dev install-test ## Set up development environment
	@echo "Development environment ready!"
	@echo "Run 'make start' to start the server"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make format' to format code"
