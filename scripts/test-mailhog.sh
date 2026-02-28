#!/bin/bash

#######################################################################
# Mailhog Web Interface Verification Script
#
# Purpose: Verify that the Mailhog web interface is accessible
#
# Tests:
# - HTTP 200 response from http://localhost:8025
# - HTML content is returned
# - Mailhog UI elements are present
#
# Usage:
#   ./scripts/test-mailhog.sh
#
# Prerequisites:
# - Docker services must be running: docker compose up -d
# - Mailhog service must be healthy
#######################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service URLs
MAILHOG_WEB_URL="http://localhost:8025"
MAILHOG_API_URL="http://localhost:8025/api/v2/messages"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Mailhog Web Interface Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${RED}✗ Error: curl is not installed${NC}"
    echo "  Please install curl to run this verification script"
    exit 1
fi

echo -e "${BLUE}Testing: ${MAILHOG_WEB_URL}${NC}"
echo ""

# Test 1: Check web interface
echo -e "${BLUE}[1/3] Checking Mailhog Web Interface...${NC}"
HTTP_CODE=$(curl -s -o /tmp/mailhog-response.html -w "%{http_code}" ${MAILHOG_WEB_URL})

echo "HTTP Status Code: ${HTTP_CODE}"
echo ""

if [ "$HTTP_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Status Code: 200 OK${NC}"
else
    echo -e "${RED}✗ Failed: Expected 200, got ${HTTP_CODE}${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo "1. Verify Docker services are running:"
    echo "   docker compose ps"
    echo ""
    echo "2. Check mailhog service logs:"
    echo "   docker compose logs mailhog"
    echo ""
    echo "3. Verify mailhog service is healthy:"
    echo "   docker compose ps mailhog"
    echo ""
    echo "4. Try restarting the mailhog service:"
    echo "   docker compose restart mailhog"
    echo ""
    exit 1
fi

# Test 2: Check if response contains HTML
echo -e "${BLUE}[2/3] Validating HTML Response...${NC}"
if grep -q "<html" /tmp/mailhog-response.html 2>/dev/null; then
    echo -e "${GREEN}✓ HTML Response: Valid HTML document received${NC}"
else
    echo -e "${RED}✗ Response does not contain valid HTML${NC}"
    exit 1
fi

# Test 3: Check for Mailhog-specific content
echo ""
echo -e "${BLUE}[3/3] Checking for Mailhog UI Elements...${NC}"

MAILHOG_UI_FOUND=false

# Check for Mailhog-specific elements
if grep -qi "mailhog" /tmp/mailhog-response.html; then
    echo -e "${GREEN}✓ Mailhog branding detected${NC}"
    MAILHOG_UI_FOUND=true
fi

# Check for common UI elements (div, script tags indicating a web app)
if grep -q "<script" /tmp/mailhog-response.html; then
    echo -e "${GREEN}✓ Web application scripts detected${NC}"
    MAILHOG_UI_FOUND=true
fi

if [ "$MAILHOG_UI_FOUND" = false ]; then
    echo -e "${YELLOW}⚠ Warning: Mailhog UI elements not clearly identified${NC}"
    echo "  The page may still be functional - check browser"
fi

# Test 4: Check API endpoint
echo ""
echo -e "${BLUE}Bonus: Testing Mailhog API...${NC}"
API_CODE=$(curl -s -o /tmp/mailhog-api.json -w "%{http_code}" ${MAILHOG_API_URL})

if [ "$API_CODE" -eq 200 ]; then
    echo -e "${GREEN}✓ Mailhog API is accessible (${MAILHOG_API_URL})${NC}"

    # Try to parse the JSON response
    if command -v python3 &> /dev/null; then
        MESSAGE_COUNT=$(python3 -c "import json; data=json.load(open('/tmp/mailhog-api.json')); print(data.get('total', 0))" 2>/dev/null || echo "N/A")
        echo -e "${BLUE}  Current messages in inbox: ${MESSAGE_COUNT}${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Mailhog API returned status: ${API_CODE}${NC}"
fi

# Display HTML snippet
echo ""
echo -e "${BLUE}HTML Response Preview:${NC}"
echo "----------------------------------------"
head -15 /tmp/mailhog-response.html
echo "..."
echo "----------------------------------------"

# Success summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ Mailhog Verification PASSED${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "The Mailhog web interface is accessible!"
echo ""

# Usage instructions
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. Open Mailhog UI in browser:"
echo -e "   ${BLUE}${MAILHOG_WEB_URL}${NC}"
echo ""
echo "2. Test email sending from your application:"
echo "   - Configure your app to use SMTP:"
echo "     Host: localhost (or 'mailhog' in Docker)"
echo "     Port: 1025"
echo "     No authentication required"
echo ""
echo "3. View captured emails:"
echo "   - All emails sent to port 1025 will appear in the Mailhog UI"
echo "   - No emails are actually delivered (safe for testing)"
echo ""

# Related endpoints
echo -e "${BLUE}Related Services:${NC}"
echo "  Frontend:     http://localhost:3000"
echo "  API:          http://localhost:8000"
echo "  API Docs:     http://localhost:8000/docs"
echo "  Mailhog Web:  http://localhost:8025"
echo "  Mailhog SMTP: localhost:1025 (use in app config)"
echo ""

# Cleanup
rm -f /tmp/mailhog-response.html
rm -f /tmp/mailhog-api.json

exit 0
