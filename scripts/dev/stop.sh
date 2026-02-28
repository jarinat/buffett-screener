#!/bin/bash
# Development environment shutdown script
# Stops all services using Docker Compose

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Stopping Buffett Screener Development Environment${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Error: Docker is not running${NC}"
    exit 1
fi

# Stop services
echo -e "${YELLOW}Stopping services...${NC}"
docker compose down

echo ""
echo -e "${GREEN}✓ Development environment stopped successfully!${NC}"
echo ""
echo "To start services again:"
echo "  ./scripts/dev/start.sh"
echo ""
echo "To remove all data (volumes):"
echo "  docker compose down -v"
echo ""
