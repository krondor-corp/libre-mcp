INSTALL_DIR ?= $(HOME)/.local/bin

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  %-20s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: sync
sync: ## Sync dependencies
	@uv sync

.PHONY: install
install: binary ## Build and install the binary to INSTALL_DIR (default ~/.local/bin)
	@mkdir -p "$(INSTALL_DIR)"
	@cp dist/libre-mcp "$(INSTALL_DIR)/libre-mcp"
	@chmod +x "$(INSTALL_DIR)/libre-mcp"
	@echo "installed libre-mcp -> $(INSTALL_DIR)/libre-mcp"
	@echo "register with: claude mcp add libre -- $(INSTALL_DIR)/libre-mcp"

.PHONY: dev
dev: ## Run the MCP server in dev mode (debug logging + hot-reload)
	@./bin/run.sh --dev

.PHONY: run
run: ## Run the MCP server over stdio
	@./bin/run.sh

.PHONY: inspect
inspect: ## Launch the MCP Inspector against the server
	@npx @modelcontextprotocol/inspector uv run libre-mcp

.PHONY: test
test: ## Run tests
	@uv run pytest || test $$? -eq 5

.PHONY: lint
lint: ## Run linting
	@uv run ruff check src/ tests/

.PHONY: fmt
fmt: ## Format code
	@uv run black src/ tests/

.PHONY: fmt-check
fmt-check: ## Check formatting
	@uv run black --check src/ tests/

.PHONY: types
types: ## Run type checking with ty
	@uv run ty check src/

.PHONY: check
check: fmt-check lint types test ## Run all checks

.PHONY: binary
binary: ## Build the standalone binary into dist/libre-mcp
	@uv run --group build pyinstaller libre-mcp.spec --clean -y

.PHONY: clean
clean: ## Clean build artifacts and runtime profiles
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@rm -rf .lo_profiles dist build pkg
	@rm -rf scratch/* && touch scratch/.gitkeep
