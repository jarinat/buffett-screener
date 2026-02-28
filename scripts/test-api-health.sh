#!/bin/bash
# API Health Check Verification Script
# Tests the FastAPI health check endpoint at http://localhost:8000/health
# Expected: 200 status code with JSON response

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Test API health endpoint
test_api_health() {
    print_header "API Health Check Verification"

    local api_url="http://localhost:8000/health"

    print_info "Testing endpoint: $api_url"
    echo ""

    # Test with curl and capture status code
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" "$api_url" 2>/dev/null || echo "000")

    if [ "$http_code" = "200" ]; then
        print_success "API health check endpoint returns 200 OK"
        echo ""

        # Display the response body
        print_info "Response body:"
        echo ""
        curl -s "$api_url" | python3 -m json.tool 2>/dev/null || curl -s "$api_url"
        echo ""

        return 0
    elif [ "$http_code" = "000" ]; then
        print_error "Cannot connect to API endpoint"
        echo ""
        print_info "Possible reasons:"
        echo "  1. API service is not running"
        echo "  2. Docker containers are not started"
        echo "  3. API is still initializing"
        echo ""
        print_info "To start services, run:"
        echo "  ./scripts/dev/start.sh"
        echo "  or"
        echo "  docker compose up -d"
        echo ""
        return 1
    else
        print_error "API health check returned unexpected status: $http_code"
        echo ""
        print_info "Response body:"
        curl -s "$api_url"
        echo ""
        return 1
    fi
}

# Check if curl is available
check_curl() {
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed"
        echo "Please install curl to run this verification"
        exit 1
    fi
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔═══════════════════════════════════════════════════════╗"
    echo "║  Buffett Screener - API Health Check Verification    ║"
    echo "╚═══════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    check_curl

    if test_api_health; then
        print_header "Verification Result"
        print_success "API health check verification PASSED"
        echo ""
        print_info "The API service is running and healthy!"
        echo ""
        print_info "Other available endpoints:"
        echo "  • API Documentation: http://localhost:8000/docs"
        echo "  • API Redoc:         http://localhost:8000/redoc"
        echo "  • Readiness Check:   http://localhost:8000/readiness"
        echo ""
        exit 0
    else
        print_header "Verification Result"
        print_error "API health check verification FAILED"
        echo ""
        print_info "Troubleshooting steps:"
        echo "  1. Check if services are running: docker compose ps"
        echo "  2. View API logs: docker compose logs api"
        echo "  3. Restart services: docker compose restart api"
        echo ""
        exit 1
    fi
}

# Run main function
main
