# Makefile - Sovereign Data Fortress
# One-command infrastructure management

.DEFAULT_GOAL := help
.PHONY: help setup infra-up infra-down health test-all clean

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

##@ General Commands

help: ## Show this help message
	@echo "$(BLUE)🏰 SOVEREIGN DATA FORTRESS$(NC)"
	@echo "Cloud-Agnostic Data Platform"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(BLUE)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

setup: ## Complete setup (first time only)
	@echo "$(BLUE)🔧 Running complete setup...$(NC)"
	@./scripts/setup.sh
	@echo "$(GREEN)✅ Setup complete!$(NC)"

##@ Infrastructure Management

infra-up: ## Start all infrastructure
	@echo "$(BLUE)🚀 Starting infrastructure...$(NC)"
	@cd terraform && terraform apply -auto-approve
	@echo "$(GREEN)✅ Infrastructure is running!$(NC)"
	@echo ""
	@echo "Services available at:"
	@echo "  📊 PostgreSQL:    localhost:5433"
	@echo "  🗄️  MinIO Console: http://localhost:9001"
	@echo "  🔌 MinIO API:     localhost:9000"
	@echo "  ☁️  LocalStack:    http://localhost:4566"
	@echo ""
	@echo "Run '$(BLUE)make health$(NC)' to verify all services"

infra-down: ## Stop and remove all infrastructure
	@echo "$(YELLOW)🛑 Stopping infrastructure...$(NC)"
	@cd terraform && terraform destroy -auto-approve
	@echo "$(GREEN)✅ Infrastructure stopped$(NC)"

infra-status: ## Show current infrastructure status
	@cd terraform && terraform show

infra-plan: ## Preview infrastructure changes
	@cd terraform && terraform plan

##@ Service Access

db-connect: ## Connect to PostgreSQL database
	@echo "$(BLUE)🔌 Connecting to PostgreSQL...$(NC)"
	@docker exec -it fortress-postgres psql -U dataeng -d warehouse

minio-console: ## Open MinIO console (browser)
	@echo "$(BLUE)🗄️  MinIO Console Info:$(NC)"
	@echo "  URL:  http://localhost:9001"
	@echo "  User: minioadmin"
	@echo "  Pass: minioadmin123"
	@command -v open >/dev/null 2>&1 && open http://localhost:9001 || \
	 command -v xdg-open >/dev/null 2>&1 && xdg-open http://localhost:9001 || \
	 echo "  (Please open manually in browser)"

duckdb-shell: ## Open DuckDB interactive shell
	@echo "$(BLUE)🦆 Opening DuckDB shell...$(NC)"
	@source venv/bin/activate && python3 -c "import duckdb; duckdb.connect().sql('SELECT \\'🏰 Sovereign Data Fortress - DuckDB Ready!\\' as message').show()"

##@ Testing & Validation

health: ## Run health check on all services
	@./scripts/health_check.sh

test-all: ## Run comprehensive test suite
	@./scripts/test_all.sh

test-minio: ## Test MinIO S3 operations
	@echo "$(BLUE)🧪 Testing MinIO...$(NC)"
	@source venv/bin/activate && python test_minio.py

test-localstack: ## Test LocalStack AWS simulation
	@echo "$(BLUE)🧪 Testing LocalStack...$(NC)"
	@source venv/bin/activate && python test_localstack.py

test-duckdb: ## Run DuckDB analytics demo
	@echo "$(BLUE)🦆 Running DuckDB demo...$(NC)"
	@source venv/bin/activate && python analytics/duckdb_demo.py

##@ Development

logs: ## Show logs from all containers
	@docker compose logs -f 2>/dev/null || docker logs fortress-postgres fortress-minio fortress-localstack -f

shell: ## Activate Python virtual environment
	@echo "$(BLUE)🐍 Activating virtual environment...$(NC)"
	@echo "Run: source venv/bin/activate"

format: ## Format Python code
	@echo "$(BLUE)🎨 Formatting Python code...$(NC)"
	@source venv/bin/activate && black *.py analytics/ 2>/dev/null || echo "Install black: pip install black"

##@ Cleanup

clean: ## Remove generated files and caches
	@echo "$(YELLOW)🧹 Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete$(NC)"

clean-data: ## Remove all data (WARNING: irreversible!)
	@echo "$(YELLOW)⚠️  WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (y/N) " -n 1 -r; \
	echo ""; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -rf data/*; \
		echo "$(GREEN)✅ Data removed$(NC)"; \
	else \
		echo "Cancelled"; \
	fi

reset: clean infra-down ## Full reset (stop infra + clean)
	@echo "$(GREEN)✅ Full reset complete$(NC)"

##@ Documentation

docs: ## Generate project documentation
	@echo "$(BLUE)📚 Documentation:$(NC)"
	@echo "  README.md       - Main documentation"
	@echo "  terraform/      - Infrastructure code"
	@echo "  analytics/      - DuckDB analytics"
	@echo "  scripts/        - Automation scripts"

demo: ## Quick demo of the entire platform
	@echo "$(BLUE)🎬 SOVEREIGN DATA FORTRESS - Quick Demo$(NC)"
	@echo "==========================================="
	@echo ""
	@echo "$(YELLOW)Step 1: Starting infrastructure...$(NC)"
	@make infra-up
	@echo ""
	@echo "$(YELLOW)Step 2: Running health checks...$(NC)"
	@make health
	@echo ""
	@echo "$(YELLOW)Step 3: Running tests...$(NC)"
	@make test-all
	@echo ""
	@echo "$(GREEN)🎉 Demo complete!$(NC)"
	@echo "Your cloud-agnostic data platform is operational."
