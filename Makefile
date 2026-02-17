# Makefile - Sovereign Data Fortress Commands

.PHONY: help tf-init tf-plan tf-apply tf-destroy infra-up infra-down infra-status db-connect minio-console test-minio

help: ## Show this help message
	@echo "🏰 Sovereign Data Fortress - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Terraform Commands
tf-init: ## Initialize Terraform
	@echo "🔧 Initializing Terraform..."
	cd terraform && terraform init

tf-plan: ## Preview infrastructure changes
	@echo "📋 Planning infrastructure changes..."
	cd terraform && terraform plan

tf-apply: ## Apply infrastructure (create/update)
	@echo "🚀 Applying infrastructure..."
	cd terraform && terraform apply

tf-destroy: ## Destroy all infrastructure
	@echo "💥 Destroying infrastructure..."
	cd terraform && terraform destroy

# Main Infrastructure Commands
infra-up: ## Start infrastructure with Terraform
	@echo "🚀 Starting Sovereign Data Fortress..."
	@$(MAKE) tf-apply
	@echo ""
	@echo "✅ Infrastructure is up!"
	@echo "📊 Postgres: localhost:5433"
	@echo "🗄️  MinIO Console: http://localhost:9001"
	@echo "🔌 MinIO API: localhost:9000"

infra-down: ## Stop and remove all infrastructure
	@echo "🛑 Stopping infrastructure..."
	@$(MAKE) tf-destroy

infra-status: ## Show infrastructure status
	@echo "📊 Infrastructure Status:"
	@cd terraform && terraform show

# Service Access Commands
db-connect: ## Connect to PostgreSQL database
	@echo "🔌 Connecting to Postgres..."
	docker exec -it fortress-postgres psql -U dataeng -d warehouse

minio-console: ## Open MinIO web console
	@echo "🗄️  MinIO Console Info:"
	@echo "URL: http://localhost:9001"
	@echo "User: minioadmin"
	@echo "Pass: minioadmin123"
	@open http://localhost:9001 2>/dev/null || xdg-open http://localhost:9001 2>/dev/null || echo "Open manually: http://localhost:9001"

test-minio: ## Test MinIO S3 API
	@echo "🧪 Testing MinIO..."
	python test_minio.py

# Docker fallback (legacy)
docker-up: ## Start with docker-compose (legacy)
	@echo "⚠️  Using legacy docker-compose. Consider using 'make infra-up' instead."
	docker-compose up -d

docker-down: ## Stop docker-compose (legacy)
	docker-compose down



# LocalStack Commands
localstack-health: ## Check LocalStack health
	@echo "🔍 Checking LocalStack health..."
	curl -s http://localhost:4566/_localstack/health | python3 -m json.tool

localstack-s3-list: ## List all S3 buckets in LocalStack
	@echo "🪣 S3 Buckets in LocalStack:"
	AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test \
	aws --endpoint-url=http://localhost:4566 s3 ls

test-localstack: ## Run LocalStack AWS simulation tests
	@echo "🧪 Testing LocalStack..."
	python test_localstack.py


# DuckDB Analytics Commands
analytics-demo: ## Run DuckDB analytics demo
	@echo "🦆 Running DuckDB Analytics Demo..."
	source venv/bin/activate && python analytics/duckdb_demo.py

analytics-shell: ## Open DuckDB interactive shell
	@echo "🦆 Opening DuckDB shell..."
	source venv/bin/activate && python3 -c "import duckdb; duckdb.sql('SELECT 42 as answer').show()"
