# Subtask 5-4 Verification: Mailhog Web Interface

## Overview
This document describes how to verify that the Mailhog web interface is accessible at http://localhost:8025.

## Prerequisites
- Docker and Docker Compose must be installed
- All services must be running via `docker compose up -d`

## Verification Methods

### Method 1: Automated Script (Recommended)

Run the verification script:
```bash
./scripts/test-mailhog.sh
```

This script will:
- ✅ Test HTTP 200 response from http://localhost:8025
- ✅ Validate HTML content is returned
- ✅ Check for Mailhog UI elements
- ✅ Test Mailhog API endpoint
- ✅ Display current message count
- ✅ Provide usage instructions

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

### Method 2: Browser Verification

1. **Open Mailhog UI in your browser:**
   ```
   http://localhost:8025
   ```

2. **Visual Checks:**
   - ✅ Mailhog UI loads successfully
   - ✅ Page displays "Mailhog" branding
   - ✅ Email list is visible (may be empty)
   - ✅ Search and filter controls are present
   - ✅ No JavaScript errors in browser console (F12)

3. **UI Elements to Verify:**
   - Header with "Mailhog" title
   - Email list/inbox area
   - Search functionality
   - Message preview pane
   - Navigation controls

### Method 3: Manual curl Test

Test the web interface endpoint:
```bash
curl -i http://localhost:8025
```

**Expected Response:**
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
...

<!DOCTYPE html>
<html>
...
```

Test the API endpoint:
```bash
curl -s http://localhost:8025/api/v2/messages | python3 -m json.tool
```

**Expected Response:**
```json
{
    "total": 0,
    "count": 0,
    "start": 0,
    "items": []
}
```

### Method 4: Docker Health Check

Verify the Mailhog service is running and healthy:
```bash
docker compose ps mailhog
```

**Expected Output:**
```
NAME      IMAGE                        STATUS
mailhog   mailhog/mailhog:latest      Up (healthy)
```

Check Mailhog logs:
```bash
docker compose logs mailhog
```

### Method 5: Test Email Sending

1. **Send a test email using Python:**
   ```python
   import smtplib
   from email.message import EmailMessage

   msg = EmailMessage()
   msg.set_content('This is a test email from Buffett Screener')
   msg['Subject'] = 'Test Email'
   msg['From'] = 'test@buffettscreener.com'
   msg['To'] = 'recipient@example.com'

   # For local testing (outside Docker)
   with smtplib.SMTP('localhost', 1025) as smtp:
       smtp.send_message(msg)

   # For Docker container
   # with smtplib.SMTP('mailhog', 1025) as smtp:
   #     smtp.send_message(msg)
   ```

2. **Verify email appears in Mailhog UI:**
   - Open http://localhost:8025
   - Check that the test email appears in the inbox
   - Click on the email to view its contents

## Troubleshooting

### Issue: Cannot connect to http://localhost:8025

**Solution 1: Verify services are running**
```bash
docker compose ps
```

All services should show "Up" status.

**Solution 2: Check Mailhog logs**
```bash
docker compose logs mailhog
```

Look for any error messages.

**Solution 3: Verify port mapping**
```bash
docker compose ps mailhog
```

Should show: `0.0.0.0:8025->8025/tcp`

**Solution 4: Restart Mailhog service**
```bash
docker compose restart mailhog
docker compose ps mailhog
```

### Issue: Page loads but looks broken

**Solution: Check for port conflicts**
```bash
# Check if another process is using port 8025
lsof -i :8025  # macOS/Linux
netstat -ano | findstr :8025  # Windows
```

### Issue: Mailhog returns non-200 status

**Solution: Rebuild and restart**
```bash
docker compose down
docker compose up -d --build mailhog
```

### Issue: Email sending fails (connection refused to port 1025)

**Solution: Verify SMTP port is exposed**
```bash
docker compose ps mailhog
```

Should show both ports:
- `0.0.0.0:1025->1025/tcp` (SMTP)
- `0.0.0.0:8025->8025/tcp` (Web UI)

## Success Criteria

All of the following must be true:
- ✅ `./scripts/test-mailhog.sh` exits with code 0
- ✅ HTTP request to http://localhost:8025 returns 200
- ✅ Mailhog UI loads in browser without errors
- ✅ Mailhog API endpoint returns valid JSON
- ✅ Test emails can be sent to port 1025 and appear in UI

## Configuration Details

### Docker Compose Configuration
```yaml
mailhog:
  image: mailhog/mailhog:latest
  container_name: buffett-mailhog
  ports:
    - "1025:1025"  # SMTP server
    - "8025:8025"  # Web UI
  networks:
    - buffett-network
```

### SMTP Settings for Applications
When configuring your application to send emails via Mailhog:

**From within Docker containers:**
- Host: `mailhog`
- Port: `1025`
- Authentication: None required
- TLS/SSL: Disabled

**From host machine (local development):**
- Host: `localhost`
- Port: `1025`
- Authentication: None required
- TLS/SSL: Disabled

### Python Configuration Example
```python
# apps/api/app/core/config.py
MAIL_SERVER: str = "mailhog"  # or "localhost" for local testing
MAIL_PORT: int = 1025
MAIL_USE_TLS: bool = False
MAIL_USE_SSL: bool = False
MAIL_USERNAME: str = ""
MAIL_PASSWORD: str = ""
```

## Related Documentation
- Mailhog GitHub: https://github.com/mailhog/MailHog
- Docker Compose setup: `docker-compose.yml`
- Environment configuration: `.env.example`
- API email config: `apps/api/app/core/config.py`

## Notes
- Mailhog is for **local development only** - never use in production
- All emails are stored in memory and lost when the container restarts
- No actual emails are sent - all are captured locally
- Perfect for testing email functionality without spam or delivery issues
