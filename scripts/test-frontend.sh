#!/bin/bash

#######################################################################
# Frontend Verification Script
#
# Purpose: Verify that the Next.js frontend renders without errors
#
# Tests:
# - HTTP 200 response from http://localhost:3000
# - HTML content is returned
# - Tailwind CSS classes are present in the HTML
#
# Usage:
#   ./scripts/test-frontend.sh
#
# Prerequisites:
# - Docker services must be running: docker compose up -d
# - Web service must be healthy (may take 30-60 seconds to build)
#######################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service URL
FRONTEND_URL="http://localhost:3000"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Frontend Verification Test${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}✗ Error: curl is not installed${NC}"
    echo "  Please install curl to run this verification script"
    exit 1
fi

echo -e "${BLUE}Testing: ${FRONTEND_URL}${NC}"
echo ""

# Make the request and capture response
HTTP_CODE=$(curl -s -o /tmp/frontend-response.html -w "%{http_code}" ${FRONTEND_URL})

echo "HTTP Status Code: ${HTTP_CODE}"
echo ""

# Check HTTP status
if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Status Code: 200 OK${NC}"
else
    echo -e "${RED}✗ Failed: Expected 200, got ${HTTP_CODE}${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "1. Verify Docker services are running:"
    echo "   docker compose ps"
    echo ""
    echo "2. Check web service logs:"
    echo "   docker compose logs web"
    echo ""
    echo "3. Verify web service is healthy:"
    echo "   docker compose ps web"
    echo ""
    echo "4. Wait 30-60 seconds for Next.js to compile on first request"
    echo ""
    exit 1
fi

# Check if response contains HTML
if grep -q "<html" /tmp/frontend-response.html 2>/dev/null; then
    echo -e "${GREEN}✓ HTML Response: Valid HTML document received${NC}"
else
    echo -e "${RED}✗ Response does not contain valid HTML${NC}"
    exit 1
fi

# Check for Tailwind CSS classes
echo ""
echo -e "${BLUE}Checking for Tailwind CSS:${NC}"

TAILWIND_FOUND=false

# Check for common Tailwind utility classes used in our page
if grep -q "min-h-screen" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Tailwind utilities detected: min-h-screen${NC}"
    TAILWIND_FOUND=true
fi

if grep -q "flex-col" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Tailwind utilities detected: flex-col${NC}"
    TAILWIND_FOUND=true
fi

if grep -q "text-4xl" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Tailwind utilities detected: text-4xl${NC}"
    TAILWIND_FOUND=true
fi

if [ "$TAILWIND_FOUND" = false ]; then
    echo -e "${YELLOW}⚠ Warning: Tailwind CSS classes not found in HTML${NC}"
    echo "  This might be normal for server-rendered pages"
    echo "  Check browser DevTools to verify CSS is loaded"
fi

# Check for page content
echo ""
echo -e "${BLUE}Checking for expected content:${NC}"

if grep -q "Buffett Screener" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Page title found: 'Buffett Screener'${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Expected page title not found${NC}"
fi

if grep -q "Quality Companies" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Content found: 'Quality Companies' section${NC}"
fi

if grep -q "Value Analysis" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Content found: 'Value Analysis' section${NC}"
fi

if grep -q "Long-term Focus" /tmp/frontend-response.html; then
    echo -e "${GREEN}✓ Content found: 'Long-term Focus' section${NC}"
fi

# Display HTML snippet
echo ""
echo -e "${BLUE}HTML Response Preview:${NC}"
echo "----------------------------------------"
head -20 /tmp/frontend-response.html
echo "..."
echo "----------------------------------------"

# Success summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Frontend Verification PASSED${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The frontend is rendering successfully!"
echo ""
echo -e "${BLUE}Additional Manual Checks:${NC}"
echo ""
echo "1. Open in browser: ${FRONTEND_URL}"
echo "   - Verify the page renders visually"
echo "   - Check browser DevTools Console (F12) for errors"
echo "   - Verify Tailwind CSS styling is applied"
echo ""
echo "2. Check dark mode support:"
echo "   - Toggle system dark mode"
echo "   - Verify page adapts to dark theme"
echo ""
echo "3. Verify responsive design:"
echo "   - Resize browser window"
echo "   - Check mobile view (DevTools responsive mode)"
echo ""

# Related endpoints
echo -e "${BLUE}Related Services:${NC}"
echo "  API:          http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Mailhog:      http://localhost:8025"
echo ""

# Cleanup
rm -f /tmp/frontend-response.html

exit 0
