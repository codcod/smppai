# Makefile for SMPPAI - Async SMPP Protocol v3.4 Implementation
# Modern uv-based development workflow

export PYTHONPATH := src:$(PYTHONPATH)

# Variables
UV := uv
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs
EXAMPLES_DIR := examples

# Default target
.DEFAULT_GOAL := help

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
MAGENTA := \033[0;35m
CYAN := \033[0;36m
WHITE := \033[0;37m
RESET := \033[0m

.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)SMPPAI Development Makefile$(RESET)"
	@echo ""
	@echo "$(YELLOW)Available targets:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

# Environment setup
.PHONY: sync
sync: ## Sync dependencies from uv.lock
	@echo "$(BLUE)Syncing dependencies...$(RESET)"
	$(UV) sync
	@echo "$(GREEN)Dependencies synced$(RESET)"

.PHONY: dev
dev: ## Install development dependencies and sync
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	$(UV) sync --dev
	@echo "$(GREEN)Development environment ready!$(RESET)"

# Code quality
.PHONY: format
format: ## Format code with ruff
	@echo "$(BLUE)Formatting code...$(RESET)"
	$(UV) run ruff format $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)
	@echo "$(GREEN)Code formatted$(RESET)"

.PHONY: lint
lint: ## Run linting with ruff
	@echo "$(BLUE)Running linter...$(RESET)"
	$(UV) run ruff check $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)
	@echo "$(GREEN)Linting completed$(RESET)"

.PHONY: lint-fix
lint-fix: ## Run linting with auto-fix
	@echo "$(BLUE)Running linter with auto-fix...$(RESET)"
	$(UV) run ruff check --fix $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)
	@echo "$(GREEN)Linting with auto-fix completed$(RESET)"

.PHONY: typecheck
typecheck: ## Run type checking with mypy
	@echo "$(BLUE)Running type checker...$(RESET)"
	$(UV) run mypy $(SRC_DIR)
	@echo "$(GREEN)Type checking completed$(RESET)"

.PHONY: check
check: lint typecheck ## Run all code quality checks
	@echo "$(GREEN)All code quality checks passed$(RESET)"

# Testing
.PHONY: test
test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(RESET)"
	$(UV) run pytest $(TESTS_DIR) -v
	@echo "$(GREEN)Tests completed$(RESET)"

.PHONY: test-cov
test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(RESET)"
	$(UV) run pytest $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term-missing -v
	@echo "$(GREEN)Tests with coverage completed$(RESET)"
	@echo "$(YELLOW)Coverage report available at htmlcov/index.html$(RESET)"

# Building and packaging
.PHONY: build
build: clean ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(RESET)"
	$(UV) build
	@echo "$(GREEN)Build completed$(RESET)"

.PHONY: publish-test
publish-test: build ## Publish to TestPyPI
	@echo "$(BLUE)Publishing to TestPyPI...$(RESET)"
	$(UV) publish --index-url https://test.pypi.org/legacy/
	@echo "$(GREEN)Published to TestPyPI$(RESET)"

.PHONY: publish
publish: build ## Publish to PyPI
	@echo "$(BLUE)Publishing to PyPI...$(RESET)"
	$(UV) publish
	@echo "$(GREEN)Published to PyPI$(RESET)"

# Cleaning
.PHONY: clean
clean: ## Clean build artifacts
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	@echo "$(GREEN)Build artifacts cleaned$(RESET)"

.PHONY: clean-all
clean-all: clean ## Clean everything including uv cache
	@echo "$(BLUE)Cleaning everything...$(RESET)"
	$(UV) cache clean
	@echo "$(GREEN)Everything cleaned$(RESET)"

# Development workflows
.PHONY: ci
ci: dev lint test ## Run CI pipeline (install, lint, test)
	@echo "$(GREEN)CI pipeline completed successfully$(RESET)"

.PHONY: pre-commit
pre-commit: format lint-fix typecheck test ## Run pre-commit checks
	@echo "$(GREEN)Pre-commit checks completed$(RESET)"

.PHONY: release-check
release-check: clean dev check test-cov build ## Check if ready for release
	@echo "$(GREEN)Release check completed - ready for release!$(RESET)"

# Dependency management
.PHONY: lock
lock: ## Update dependency lock file
	@echo "$(BLUE)Updating lock file...$(RESET)"
	$(UV) lock
	@echo "$(GREEN)Lock file updated$(RESET)"

.PHONY: deps-add
deps-add: ## Add a new dependency (use: make deps-add DEPS="package_name")
	@if [ -z "$(DEPS)" ]; then \
		echo "$(RED)Error: Please specify DEPS variable$(RESET)"; \
		echo "$(YELLOW)Usage: make deps-add DEPS=\"package_name\"$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Adding dependency: $(DEPS)$(RESET)"
	$(UV) add $(DEPS)
	@echo "$(GREEN)Dependency $(DEPS) added$(RESET)"

.PHONY: deps-add-dev
deps-add-dev: ## Add a new dev dependency (use: make deps-add-dev DEPS="package_name")
	@if [ -z "$(DEPS)" ]; then \
		echo "$(RED)Error: Please specify DEPS variable$(RESET)"; \
		echo "$(YELLOW)Usage: make deps-add-dev DEPS=\"package_name\"$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Adding dev dependency: $(DEPS)$(RESET)"
	$(UV) add --dev $(DEPS)
	@echo "$(GREEN)Dev dependency $(DEPS) added$(RESET)"

.PHONY: deps-remove
deps-remove: ## Remove a dependency (use: make deps-remove DEPS="package_name")
	@if [ -z "$(DEPS)" ]; then \
		echo "$(RED)Error: Please specify DEPS variable$(RESET)"; \
		echo "$(YELLOW)Usage: make deps-remove DEPS=\"package_name\"$(RESET)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Removing dependency: $(DEPS)$(RESET)"
	$(UV) remove $(DEPS)
	@echo "$(GREEN)Dependency $(DEPS) removed$(RESET)"

.PHONY: deps-update
deps-update: ## Update all dependencies
	@echo "$(BLUE)Updating all dependencies...$(RESET)"
	$(UV) lock --upgrade
	@echo "$(GREEN)All dependencies updated$(RESET)"

# Utility targets
.PHONY: info
info: ## Show project and environment information
	@echo "$(CYAN)SMPPAI Project Information$(RESET)"
	@echo "$(YELLOW)uv version:$(RESET) $(shell $(UV) --version 2>/dev/null || echo 'not installed')"
	@echo "$(YELLOW)Python version:$(RESET) $(shell $(UV) run python --version 2>/dev/null || echo 'environment not ready')"
	@echo "$(YELLOW)Source directory:$(RESET) $(SRC_DIR)"
	@echo "$(YELLOW)Tests directory:$(RESET) $(TESTS_DIR)"
	@echo "$(YELLOW)Examples directory:$(RESET) $(EXAMPLES_DIR)"
	@echo "$(YELLOW)Lock file:$(RESET) $(shell test -f uv.lock && echo 'uv.lock (exists)' || echo 'uv.lock (missing)')"
	@echo ""
	@echo "$(CYAN)Environment Status:$(RESET)"
	@$(UV) run python -c "import sys; print(f'$(YELLOW)Virtual environment:$(RESET) {sys.prefix}')" 2>/dev/null || echo "$(RED)Environment not ready$(RESET)"

# Security
.PHONY: security
security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(RESET)"
	$(UV) run bandit -r $(SRC_DIR)
	@echo "$(GREEN)Security checks completed$(RESET)"

.PHONY: shell
shell: ## Start Python shell with project loaded
	@echo "$(BLUE)Starting Python shell...$(RESET)"
	$(UV) run python
