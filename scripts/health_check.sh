#!/bin/bash
# scripts/health_check.sh
# Comprehensive health check for all services

set -e

echo "🏥 HEALTH CHECK - Sovereign Data Fortress"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track overall health
ALL_HEALTHY=true

# Check Docker
echo -e "🐳 Docker Status:"
if docker ps > /dev/null 2>&1; then
    echo -e "  ${GREEN}✅ Docker daemon running${NC}"
else
    echo -e "  ${RED}❌ Docker daemon not running${NC}"
    ALL_HEALTHY=false
fi

echo ""

# Check containers
echo -e "📦 Container Status:"

check_container() {
    local container_name=$1
    local port=$2
    
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        local status=$(docker inspect --format='{{.State.Health.Status}}' ${container_name} 2>/dev/null || echo "no-healthcheck")
        if [ "$status" = "healthy" ] || [ "$status" = "no-healthcheck" ]; then
            echo -e "  ${GREEN}✅${NC} ${container_name} (port ${port})"
        else
            echo -e "  ${YELLOW}⏳${NC} ${container_name} (status: ${status})"
        fi
    else
        echo -e "  ${RED}❌${NC} ${container_name} (not running)"
        ALL_HEALTHY=false
    fi
}

check_container "fortress-postgres" "5433"
check_container "fortress-minio" "9000, 9001"
check_container "fortress-localstack" "4566"

echo ""

# Check endpoints
echo -e "🌐 Service Endpoints:"

check_endpoint() {
    local name=$1
    local url=$2
    
    if curl -s -f -o /dev/null --max-time 5 "$url"; then
        echo -e "  ${GREEN}✅${NC} ${name}: ${url}"
    else
        echo -e "  ${RED}❌${NC} ${name}: ${url} (unreachable)"
        ALL_HEALTHY=false
    fi
}

check_endpoint "MinIO Console" "http://localhost:9001/minio/health/live"
check_endpoint "LocalStack Health" "http://localhost:4566/_localstack/health"

echo ""

# Check Python environment
echo -e "🐍 Python Environment:"

if [ -d "venv" ]; then
    echo -e "  ${GREEN}✅${NC} Virtual environment exists"
    source venv/bin/activate
    
    # Check critical packages
    if python -c "import duckdb" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} DuckDB installed"
    else
        echo -e "  ${RED}❌${NC} DuckDB not installed"
        ALL_HEALTHY=false
    fi
    
    if python -c "import minio" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} MinIO SDK installed"
    else
        echo -e "  ${RED}❌${NC} MinIO SDK not installed"
        ALL_HEALTHY=false
    fi
    
    if python -c "import boto3" 2>/dev/null; then
        echo -e "  ${GREEN}✅${NC} Boto3 installed"
    else
        echo -e "  ${RED}❌${NC} Boto3 not installed"
        ALL_HEALTHY=false
    fi
else
    echo -e "  ${RED}❌${NC} Virtual environment not found"
    ALL_HEALTHY=false
fi

echo ""

# Check data directories
echo -e "📁 Data Directories:"

check_dir() {
    local dir=$1
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✅${NC} ${dir}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  ${dir} (will be created on first run)"
    fi
}

check_dir "data/postgres"
check_dir "data/minio"
check_dir "data/localstack"
check_dir "data/analytics"

echo ""

# Final summary
echo "=========================================="
if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
    echo "=========================================="
    exit 0
else
    echo -e "${RED}⚠️  SOME ISSUES DETECTED${NC}"
    echo "=========================================="
    echo ""
    echo "Troubleshooting:"
    echo "  - Run: make infra-up (to start services)"
    echo "  - Run: ./scripts/setup.sh (to fix environment)"
    echo "  - Check logs: docker logs <container-name>"
    exit 1
fi
