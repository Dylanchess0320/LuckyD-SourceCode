# ── Makefile for LuckyD Code ──────────────────────────────────────────
# Commands: make install, make test, make lint, make format, etc.

.PHONY: install install-dev setup test lint format typecheck security clean docs build run help

help: ## Show this help
	@echo "LuckyD Code — Makefile Commands"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Installation ─────────────────────────────────────────────────────

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install dev dependencies
	pip install -r requirements-dev.txt

setup: install install-dev pre-commit ## Full dev setup
	pre-commit install

# ── Testing ──────────────────────────────────────────────────────────

test: ## Run tests with coverage
	pytest -v --cov --cov-report=term-missing --cov-report=html

test-fast: ## Run fast tests only (skip slow/integration)
	pytest -v -m "not slow and not integration and not llm"

test-slow: ## Run all tests including slow ones
	pytest -v --runslow

test-watch: ## Run tests in watch mode (requires pytest-watch)
	pytest-watch -- -v

# ── Linting & Formatting ──────────────────────────────────────────────

lint: ## Run Ruff linter
	ruff check .

lint-fix: ## Auto-fix lint issues
	ruff check --fix .

format: ## Format code with Black
	black .

format-check: ## Check formatting (CI use)
	black --check .

typecheck: ## Run mypy type checker
	mypy tools llm memory project features

# ── Security ─────────────────────────────────────────────────────────

security: ## Run bandit security scanner
	bandit -r tools llm memory project -f json -o bandit-report.json || true

safety: ## Check dependency vulnerabilities
	safety check -r requirements.txt || true

# ── Quality ──────────────────────────────────────────────────────────

quality: lint format-check typecheck security ## Run all quality checks

all-checks: quality test ## Run everything

# ── Code Maintenance ──────────────────────────────────────────────────

dead-code: ## Find dead code with vulture
	vulture tools llm memory project --min-confidence 70

clean: ## Clean build artifacts
	@echo "Cleaning..."
	rm -rf build dist *.egg-info .coverage htmlcov
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Done."

clean-all: clean ## Deep clean including venv
	rm -rf .venv venv

# ── Documentation ────────────────────────────────────────────────────

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

# ── Build & Run ──────────────────────────────────────────────────────

build: ## Build package
	python -m build

run: ## Run the agent
	python main.py

run-repl: ## Run interactive REPL
	python main.py

# ── Pre-commit ───────────────────────────────────────────────────────

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-all: ## Run pre-commit on all files
	pre-commit run --all-files

# ── Docker ───────────────────────────────────────────────────────────

docker-build: ## Build Docker image
	docker build -t luckyd-code .

docker-run: ## Run in Docker
	docker run -it --rm \
		-v "$$(pwd):/workspace" \
		--env-file .env \
		luckyd-code

# ── CI Simulation ────────────────────────────────────────────────────

ci: ## Simulate CI pipeline locally
	@echo "=== LuckyD Code CI Pipeline ==="
	@echo "--- Step 1: Install ---"
	pip install -r requirements-dev.txt
	@echo "--- Step 2: Format Check ---"
	black --check .
	@echo "--- Step 3: Lint ---"
	ruff check .
	@echo "--- Step 4: Type Check ---"
	mypy tools llm memory project features || true
	@echo "--- Step 5: Security ---"
	bandit -r tools llm memory project || true
	@echo "--- Step 6: Test ---"
	pytest -v --cov --cov-report=term
	@echo "=== CI Complete ==="

# ── Git hooks creation ────────────────────────────────────────────────

git-hooks: ## Create useful git hooks
	@echo "Creating pre-push hook..."
	mkdir -p .git/hooks
	printf '#!/bin/sh\necho "Running pre-push checks..."\nmake all-checks\n' > .git/hooks/pre-push
	chmod +x .git/hooks/pre-push
	@echo "Done."
