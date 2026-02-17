#!/bin/bash
# scripts/test_all.sh
# Run all tests to verify the platform

set -e

echo "🧪 COMPREHENSIVE TEST SUITE"
echo "=========================================="
echo ""

# Activate venv
source venv/bin/activate

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -e "${BLUE}▶ Running: ${test_name}${NC}"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "  ${RED}❌ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
    echo ""
}

# 1. Infrastructure tests
echo "🏗️  Infrastructure Tests"
echo "─────────────────────────────────────────"

run_test "Docker containers running" \
    "docker ps | grep -q fortress-postgres && docker ps | grep -q fortress-minio"

run_test "PostgreSQL connectivity" \
    "docker exec fortress-postgres pg_isready -U dataeng"

run_test "MinIO API reachable" \
    "curl -f -s http://localhost:9000/minio/health/live"

echo ""

# 2. Service tests
echo "🧪 Service Tests"
echo "─────────────────────────────────────────"

run_test "MinIO S3 operations" \
    "python test_minio.py"

run_test "DuckDB analytics" \
    "python analytics/duckdb_demo.py"

echo ""

# 3. Data tests
echo "📊 Data Tests"
echo "─────────────────────────────────────────"

run_test "Sample data generated" \
    "test -f data/analytics/crypto_prices.parquet"

run_test "Parquet file readable" \
    "python -c 'import duckdb; duckdb.sql(\"SELECT COUNT(*) FROM read_parquet(\\\"data/analytics/crypto_prices.parquet\\\")\")'"

echo ""

# Summary
echo "=========================================="
echo -e "Test Results:"
echo -e "  ${GREEN}Passed: ${TESTS_PASSED}${NC}"
echo -e "  ${RED}Failed: ${TESTS_FAILED}${NC}"
echo "=========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo "Your Sovereign Data Fortress is fully operational."
    exit 0
else
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo "Please check the output above for details."
    exit 1
fi
