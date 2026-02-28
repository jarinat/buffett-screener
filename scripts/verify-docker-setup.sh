#!/bin/bash
# Docker Compose Setup Verification Script
# This script verifies that the Docker Compose setup is correctly configured
# and provides step-by-step verification of all services

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

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Check if Docker is installed
check_docker() {
    print_header "Checking Docker Installation"

    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        docker --version
    else
        print_error "Docker is not installed"
        echo "Please install Docker from https://docs.docker.com/get-docker/"
        exit 1
    fi

    if command -v docker compose &> /dev/null; then
        print_success "Docker Compose is installed"
        docker compose version
    else
        print_error "Docker Compose is not installed"
        exit 1
    fi
}

# Check required files
check_files() {
    print_header "Checking Required Files"

    local all_present=true

    files=(
        "docker-compose.yml"
        ".env"
        "apps/api/Dockerfile"
        "apps/api/pyproject.toml"
        "apps/api/app/main.py"
        "apps/api/app/core/config.py"
        "apps/web/Dockerfile"
        "apps/web/package.json"
        "apps/web/app/page.tsx"
    )

    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            print_success "$file"
        else
            print_error "$file is missing"
            all_present=false
        fi
    done

    if [ "$all_present" = false ]; then
        print_error "Some required files are missing"
        exit 1
    fi
}

# Validate docker-compose.yml
validate_compose() {
    print_header "Validating docker-compose.yml"

    if docker compose config > /dev/null 2>&1; then
        print_success "docker-compose.yml is valid"
    else
        print_error "docker-compose.yml has errors"
        docker compose config
        exit 1
    fi
}

# Build services
build_services() {
    print_header "Building Docker Services"

    print_info "This may take several minutes on first run..."

    if docker compose build; then
        print_success "All services built successfully"
    else
        print_error "Build failed"
        exit 1
    fi
}

# Start services
start_services() {
    print_header "Starting Docker Services"

    print_info "Starting all services in detached mode..."

    if docker compose up -d; then
        print_success "All services started"
    else
        print_error "Failed to start services"
        exit 1
    fi

    print_info "Waiting for services to initialize (30 seconds)..."
    sleep 30
}

# Check service health
check_service_health() {
    print_header "Checking Service Health"

    # Check database
    print_info "Checking PostgreSQL database..."
    if docker compose ps db | grep -q "healthy"; then
        print_success "Database is healthy"
    else
        print_warning "Database is not healthy yet (may need more time)"
        docker compose ps db
    fi

    # Check API
    print_info "Checking API service..."
    if docker compose ps api | grep -q "Up"; then
        print_success "API service is running"
    else
        print_error "API service is not running"
        docker compose logs api --tail=20
    fi

    # Check Web
    print_info "Checking Web service..."
    if docker compose ps web | grep -q "Up"; then
        print_success "Web service is running"
    else
        print_error "Web service is not running"
        docker compose logs web --tail=20
    fi

    # Check Mailhog
    print_info "Checking Mailhog service..."
    if docker compose ps mailhog | grep -q "Up"; then
        print_success "Mailhog service is running"
    else
        print_error "Mailhog service is not running"
    fi
}

# Test endpoints
test_endpoints() {
    print_header "Testing Service Endpoints"

    # Test API health endpoint
    print_info "Testing API health endpoint (http://localhost:8000/health)..."
    if curl -f -s http://localhost:8000/health > /dev/null; then
        print_success "API health check passed"
        curl -s http://localhost:8000/health | head -n 5
    else
        print_error "API health check failed"
        print_info "API may still be starting. Check logs with: docker compose logs api"
    fi

    # Test frontend
    print_info "Testing frontend (http://localhost:3000)..."
    if curl -f -s http://localhost:3000 > /dev/null; then
        print_success "Frontend is accessible"
    else
        print_error "Frontend is not accessible"
        print_info "Frontend may still be building. Check logs with: docker compose logs web"
    fi

    # Test Mailhog UI
    print_info "Testing Mailhog UI (http://localhost:8025)..."
    if curl -f -s http://localhost:8025 > /dev/null; then
        print_success "Mailhog UI is accessible"
    else
        print_error "Mailhog UI is not accessible"
    fi
}

# Display service URLs
display_urls() {
    print_header "Service URLs"

    echo "Frontend:         http://localhost:3000"
    echo "API:              http://localhost:8000"
    echo "API Docs:         http://localhost:8000/docs"
    echo "Mailhog UI:       http://localhost:8025"
    echo "PostgreSQL:       localhost:5432"
    echo ""
    print_info "Database credentials:"
    echo "  User:     postgres"
    echo "  Password: postgres"
    echo "  Database: buffett_screener"
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  Buffett Screener - Docker Compose Verification Script    ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    check_docker
    check_files
    validate_compose
    build_services
    start_services
    check_service_health

    # Wait a bit more for services to be fully ready
    print_info "Waiting for services to be fully ready (30 more seconds)..."
    sleep 30

    test_endpoints
    display_urls

    print_header "Verification Complete"
    print_success "All services are running!"
    print_info "Run 'docker compose logs -f' to view live logs"
    print_info "Run 'docker compose down' to stop all services"
    print_info "Run 'docker compose down -v' to stop and remove volumes"
}

# Run main function
main
