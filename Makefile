# Makefile - Easy commands for fortress operations

.PHONY: help infra-up infra-down infra-restart infra-logs db-connect

help: ## Show this help message
	@echo "🏰 Sovereign Data Fortress - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

infra-up: ## Start all infrastructure containers
	@echo "🚀 Starting Sovereign Data Fortress..."
	docker-compose up -d
	@echo "✅ Infrastructure is up!"
	@echo "📊 Postgres: localhost:5432"

infra-down: ## Stop all infrastructure containers
	@echo "🛑 Stopping infrastructure..."
	docker-compose down
	@echo "✅ Infrastructure stopped"

infra-restart: ## Restart all containers
	@echo "🔄 Restarting infrastructure..."
	docker-compose restart
	@echo "✅ Infrastructure restarted"

infra-logs: ## Show logs from all containers
	docker-compose logs -f

db-connect: ## Connect to PostgreSQL database
	@echo "🔌 Connecting to Postgres..."
	docker exec -it fortress-postgres psql -U dataeng -d warehouse
