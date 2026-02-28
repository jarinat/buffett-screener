# Development Scripts

This directory contains scripts to help with development workflows.

## Available Scripts

### Development Scripts

#### `dev/start.sh`
Starts the entire development environment using Docker Compose.

**Features:**
- Checks for Docker installation
- Automatically creates `.env` from `.env.example` if needed
- Builds and starts all services
- Displays service URLs and status
- Color-coded output for better readability

**Usage:**
```bash
./scripts/dev/start.sh
```

**Services Started:**
- PostgreSQL database (port 5432)
- FastAPI backend (port 8000)
- Next.js frontend (port 3000)
- Mailhog email testing (ports 1025, 8025)

#### `dev/stop.sh`
Stops all development services.

**Usage:**
```bash
./scripts/dev/stop.sh
```

**Options:**
- Gracefully stops all containers
- Preserves volumes and data
- Use `docker compose down -v` to remove volumes

### Verification Scripts

#### `verify-docker-setup.sh`
Comprehensive verification script for Docker Compose setup.

**Features:**
- Validates Docker installation
- Checks all required files exist
- Validates docker-compose.yml configuration
- Builds all services
- Starts services and waits for initialization
- Tests all service endpoints
- Displays service health status
- Shows all service URLs

**Usage:**
```bash
./scripts/verify-docker-setup.sh
```

**What it verifies:**
1. ✓ Docker and Docker Compose installed
2. ✓ All required files present
3. ✓ docker-compose.yml is valid
4. ✓ Services build successfully
5. ✓ Services start successfully
6. ✓ Database is healthy
7. ✓ API health check passes
8. ✓ Frontend is accessible
9. ✓ Mailhog UI is accessible

**Expected Output:**
```
╔════════════════════════════════════════════════════════════╗
║  Buffett Screener - Docker Compose Verification Script    ║
╚════════════════════════════════════════════════════════════╝

=== Checking Docker Installation ===
✓ Docker is installed
✓ Docker Compose is installed

=== Checking Required Files ===
✓ docker-compose.yml
✓ .env
✓ apps/api/Dockerfile
...

=== Service URLs ===
Frontend:         http://localhost:3000
API:              http://localhost:8000
API Docs:         http://localhost:8000/docs
Mailhog UI:       http://localhost:8025
PostgreSQL:       localhost:5432

=== Verification Complete ===
✓ All services are running!
```

#### `test-api-health.sh`
Focused verification script for the API health check endpoint.

**Features:**
- Tests HTTP 200 response from API
- Validates JSON response structure
- Color-coded pass/fail results
- Displays health check details
- Includes troubleshooting guidance

**Usage:**
```bash
./scripts/test-api-health.sh
```

**Prerequisites:**
- Docker services running (`docker compose up -d`)
- API service is healthy (wait 30-60 seconds)

**What it tests:**
- GET http://localhost:8000/health returns 200 OK
- Response is valid JSON
- Response contains: status, service, version, environment, timestamp

**Expected Output:**
```
========================================
API Health Check Verification
========================================

Testing: http://localhost:8000/health

✓ API Health Check: PASSED
✓ HTTP Status: 200 OK

Response:
{
  "status": "healthy",
  "service": "buffett-screener-api",
  "version": "0.1.0",
  "environment": "development",
  "timestamp": "2026-02-28T10:30:00.000000"
}
```

#### `test-frontend.sh`
Focused verification script for the frontend application.

**Features:**
- Tests HTTP 200 response from frontend
- Validates HTML content
- Checks for Tailwind CSS classes
- Verifies expected page content
- Color-coded results

**Usage:**
```bash
./scripts/test-frontend.sh
```

**Prerequisites:**
- Docker services running (`docker compose up -d`)
- Web service is healthy (wait 30-60 seconds for first compile)

**What it tests:**
- GET http://localhost:3000 returns 200 OK
- Response is valid HTML
- Tailwind CSS utilities are present
- Expected content: "Buffett Screener", feature cards

**Expected Output:**
```
========================================
Frontend Verification Test
========================================

Testing: http://localhost:3000

✓ Status Code: 200 OK
✓ HTML Response: Valid HTML document received

Checking for Tailwind CSS:
✓ Tailwind utilities detected: min-h-screen
✓ Tailwind utilities detected: flex-col
✓ Tailwind utilities detected: text-4xl

Checking for expected content:
✓ Page title found: 'Buffett Screener'
✓ Content found: 'Quality Companies' section
✓ Content found: 'Value Analysis' section
✓ Content found: 'Long-term Focus' section

========================================
✓ Frontend Verification PASSED
========================================
```

#### `test-mailhog.sh`
Focused verification script for the Mailhog email testing service.

**Features:**
- Tests HTTP 200 response from Mailhog web UI
- Validates HTML content
- Checks for Mailhog UI elements
- Tests Mailhog API endpoint
- Displays current message count
- Color-coded results
- Includes SMTP configuration examples

**Usage:**
```bash
./scripts/test-mailhog.sh
```

**Prerequisites:**
- Docker services running (`docker compose up -d`)
- Mailhog service is healthy

**What it tests:**
- GET http://localhost:8025 returns 200 OK
- Response is valid HTML
- Mailhog branding and UI elements are present
- API endpoint at http://localhost:8025/api/v2/messages is accessible

**Expected Output:**
```
========================================
Mailhog Web Interface Verification
========================================

Testing: http://localhost:8025

[1/3] Checking Mailhog Web Interface...
HTTP Status Code: 200

✓ Status Code: 200 OK
[2/3] Validating HTML Response...
✓ HTML Response: Valid HTML document received

[3/3] Checking for Mailhog UI Elements...
✓ Mailhog branding detected
✓ Web application scripts detected

Bonus: Testing Mailhog API...
✓ Mailhog API is accessible (http://localhost:8025/api/v2/messages)
  Current messages in inbox: 0

========================================
✓ Mailhog Verification PASSED
========================================
```

## Quick Start

For first-time setup, use the verification script:

```bash
# Make scripts executable (if needed)
chmod +x scripts/dev/start.sh
chmod +x scripts/dev/stop.sh
chmod +x scripts/verify-docker-setup.sh
chmod +x scripts/test-api-health.sh
chmod +x scripts/test-frontend.sh
chmod +x scripts/test-mailhog.sh

# Run comprehensive verification script (does everything)
./scripts/verify-docker-setup.sh

# Or run individual service tests
./scripts/test-api-health.sh
./scripts/test-frontend.sh
./scripts/test-mailhog.sh
```

For daily development:

```bash
# Start development environment
./scripts/dev/start.sh

# Stop development environment
./scripts/dev/stop.sh
```

## Troubleshooting

### Scripts not executable
```bash
chmod +x scripts/dev/*.sh
chmod +x scripts/*.sh
```

### Docker not installed
Visit https://docs.docker.com/get-docker/

### Port conflicts
Check what's using the ports:
```bash
lsof -i :3000  # Frontend
lsof -i :8000  # API
lsof -i :5432  # Database
lsof -i :8025  # Mailhog
```

### Services not starting
```bash
# View logs
docker compose logs

# View specific service logs
docker compose logs api
docker compose logs web

# Restart from scratch
docker compose down -v
./scripts/verify-docker-setup.sh
```

## Adding New Scripts

When adding new scripts to this directory:

1. Make them executable: `chmod +x scripts/your-script.sh`
2. Add a shebang: `#!/bin/bash`
3. Include error handling: `set -e`
4. Add color-coded output for better UX
5. Include help text/usage instructions
6. Document the script in this README

## Script Conventions

- Use `#!/bin/bash` shebang
- Include `set -e` for error handling
- Use color codes for output:
  - Green (✓) for success
  - Red (✗) for errors
  - Yellow (⚠) for warnings
  - Blue (ℹ) for info
- Provide clear error messages
- Check for prerequisites (Docker, files, etc.)
- Include usage instructions in comments
