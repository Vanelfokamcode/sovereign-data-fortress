#!/bin/bash
# scripts/setup.sh
# One-command setup for Sovereign Data Fortress

set -e  # Exit on error

echo "🏰 SOVEREIGN DATA FORTRESS - Setup Script"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on supported OS
if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  Warning: This script is tested on Linux and macOS"
fi

# 1. Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || {
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
}
echo "✅ Docker found: $(docker --version)"

command -v terraform >/dev/null 2>&1 || {
    echo "❌ Terraform is not installed. Please install Terraform first."
    echo "   Visit: https://www.terraform.io/downloads"
    exit 1
}
echo "✅ Terraform found: $(terraform --version | head -n1)"

command -v python3 >/dev/null 2>&1 || {
    echo "❌ Python3 is not installed. Please install Python3 first."
    exit 1
}
echo "✅ Python3 found: $(python3 --version)"

# 2. Setup environment file if not exists
echo ""
echo -e "${BLUE}🔧 Setting up environment...${NC}"

if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "✅ .env created (you can edit it later for custom values)"
else
    echo "✅ .env already exists"
fi

# 3. Create data directories
echo ""
echo -e "${BLUE}📁 Creating data directories...${NC}"

mkdir -p data/postgres
mkdir -p data/minio
mkdir -p data/localstack
mkdir -p data/analytics

echo "✅ Data directories created"

# 4. Setup Python virtual environment
echo ""
echo -e "${BLUE}🐍 Setting up Python virtual environment...${NC}"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate venv and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Python dependencies installed"

# 5. Initialize Terraform
echo ""
echo -e "${BLUE}⚙️  Initializing Terraform...${NC}"

cd terraform
terraform init > /dev/null 2>&1
cd ..

echo "✅ Terraform initialized"

# 6. Summary
echo ""
echo "=========================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Review .env file for credentials"
echo "  2. Run: ${YELLOW}make infra-up${NC} to start infrastructure"
echo "  3. Run: ${YELLOW}make test-all${NC} to verify everything works"
echo ""
echo "Documentation: README.md"
echo "Help: make help"
