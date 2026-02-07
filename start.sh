#!/bin/bash

# Azure Blob Storage File Transfer - Quick Start Script
# Usage: ./start.sh [command] [options]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found!${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your Azure credentials${NC}"
    exit 1
fi

# Source environment variables
export $(cat .env | grep -v '#' | xargs)

# Check required variables
if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
    echo -e "${RED}❌ AZURE_STORAGE_CONNECTION_STRING not set in .env${NC}"
    exit 1
fi

if [ -z "$AZURE_CONTAINER_NAME" ]; then
    echo -e "${RED}❌ AZURE_CONTAINER_NAME not set in .env${NC}"
    exit 1
fi

# Create required directories
mkdir -p uploads downloads logs

# Display menu if no arguments
if [ $# -eq 0 ]; then
    echo -e "${GREEN}Azure Blob Storage File Transfer${NC}"
    echo ""
    echo "Usage: ./start.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  ./start.sh upload      - Upload files from uploads/ directory"
    echo "  ./start.sh download    - Download files from Azure storage"
    echo "  ./start.sh list [prefix] - List files in storage"
    echo "  ./start.sh shell       - Start interactive shell"
    echo "  ./start.sh build       - Build Docker image"
    echo "  ./start.sh compose     - Run with docker-compose"
    echo ""
    exit 0
fi

case "$1" in
    upload)
        echo -e "${GREEN}📤 Uploading files from uploads/ directory...${NC}"
        docker-compose run --rm file-transfer upload-dir --local-path /app/uploads --blob-prefix $(date +%Y/%m/%d)
        echo -e "${GREEN}✅ Upload complete${NC}"
        ;;
    download)
        echo -e "${GREEN}📥 Starting download shell...${NC}"
        docker-compose run --rm file-transfer bash
        ;;
    list)
        PREFIX=${2:-""}
        echo -e "${GREEN}📋 Listing files...${NC}"
        docker-compose run --rm file-transfer list --blob-prefix "$PREFIX"
        ;;
    shell)
        echo -e "${GREEN}🐚 Starting interactive shell...${NC}"
        docker-compose run --rm file-transfer /bin/bash
        ;;
    build)
        echo -e "${GREEN}🔨 Building Docker image...${NC}"
        docker-compose build
        echo -e "${GREEN}✅ Build complete${NC}"
        ;;
    compose)
        echo -e "${GREEN}🐳 Running docker-compose...${NC}"
        docker-compose "$@"
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Use './start.sh' for help"
        exit 1
        ;;
esac
