#!/bin/bash
# Development environment startup script
# Starts all services using Docker Compose

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Buffett Screener Development Environment${NC}"
echo ""

# Check if .env file exists, if not copy from .env.example
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
    else
        echo -e "${RED}✗ Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Docker is not running${NC}"
    echo "Please start Docker and try again"
    exit 1
fi

# Stop any existing containers
echo -e "${YELLOW}Stopping existing containers...${NC}"
docker compose down > /dev/null 2>&1 || true

# Build and start services
echo -e "${GREEN}Building services...${NC}"
docker compose build

echo ""
echo -e "${GREEN}Starting services...${NC}"
docker compose up -d

# Wait for services to be healthy
echo ""
echo -e "${YELLOW}Waiting for services to be ready...${NC}"
sleep 5

# Check service health
echo ""
echo -e "${GREEN}Service Status:${NC}"
docker compose ps

echo ""
echo -e "${GREEN}✓ Development environment started successfully!${NC}"
echo ""
echo "Services are available at:"
echo "  • Frontend:  http://localhost:3000"
echo "  • API:       http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/docs"
echo "  • Mailhog:   http://localhost:8025"
echo "  • Database:  postgresql://postgres:postgres@localhost:5432/buffett_screener"
echo ""
echo "To view logs:"
echo "  docker compose logs -f [service_name]"
echo ""
echo "To stop services:"
echo "  ./scripts/dev/stop.sh"
echo ""
