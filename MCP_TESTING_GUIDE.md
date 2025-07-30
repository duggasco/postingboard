# MCP Playwright Testing Guide for Posting Board

## Overview
This guide provides detailed instructions for testing the Citizen Developer Posting Board application using Claude's MCP (Model Context Protocol) Playwright server integration.

## Prerequisites

1. **Claude Code with MCP Playwright server enabled**
2. **Docker installed** on your system
3. **Application running** on http://localhost:9094

## Quick Start

```bash
# 1. Start the application
./start-flask.sh

# 2. Wait for startup
sleep 5

# 3. Begin testing with MCP
mcp__playwright__browser_navigate(url: "http://localhost:9094")
```

## Core Testing Functions

### Navigation & Interaction

```javascript
// Navigate to a URL
mcp__playwright__browser_navigate(url: "http://localhost:9094/submit")

// Click an element
mcp__playwright__browser_click(element: "Submit button", ref: "e45")

// Type text
mcp__playwright__browser_type(element: "Title input", ref: "e30", text: "My Test Idea")

// Select dropdown option
mcp__playwright__browser_select_option(
  element: "Priority dropdown", 
  ref: "e42", 
  values: ["high"]
)
```

### Inspection & Debugging

```javascript
// Get page snapshot (accessibility tree)
mcp__playwright__browser_snapshot()

// View console messages
mcp__playwright__browser_console_messages()

// Check network requests
mcp__playwright__browser_network_requests()

// Take screenshot
mcp__playwright__browser_take_screenshot(filename: "test-result.png")

// Execute JavaScript
mcp__playwright__browser_evaluate(
  function: "() => { return document.title }"
)
```

### Waiting & Timing

```javascript
// Wait for specific time
mcp__playwright__browser_wait_for(time: 3)  // seconds

// Wait for text to appear
mcp__playwright__browser_wait_for(text: "Success")

// Wait for text to disappear
mcp__playwright__browser_wait_for(textGone: "Loading...")
```

## Test Scenarios

### 1. Complete Authentication Flow

```javascript
// Navigate to verify email page
mcp__playwright__browser_navigate(url: "http://localhost:9094/verify-email")

// Enter email
mcp__playwright__browser_type(
  element: "Email input", 
  ref: "e30", 
  text: "developer1@company.com"
)

// Click send code
mcp__playwright__browser_click(element: "Send Verification Code", ref: "e31")

// Get verification code from database
bash("cd /root/postingboard/backend && sqlite3 data/posting_board_uuid.db \"SELECT code FROM verification_codes WHERE email='developer1@company.com' ORDER BY created_at DESC LIMIT 1;\"")

// Enter code (use actual code from above)
mcp__playwright__browser_type(element: "Code input", ref: "e40", text: "123456")

// Submit code
mcp__playwright__browser_click(element: "Verify Code", ref: "e41")
```

### 2. Submit New Idea

```javascript
// Navigate to submit page
mcp__playwright__browser_navigate(url: "http://localhost:9094/submit")

// Fill form
mcp__playwright__browser_type(element: "Title", ref: "e30", text: "Automated Testing Framework")
mcp__playwright__browser_type(element: "Description", ref: "e35", text: "Build comprehensive test suite")
mcp__playwright__browser_select_option(element: "Team", ref: "e37", values: ["COO - IDA"])
mcp__playwright__browser_select_option(element: "Priority", ref: "e42", values: ["high"])
mcp__playwright__browser_select_option(element: "Size", ref: "e47", values: ["large"])

// Add skills
mcp__playwright__browser_click(element: "Python skill", ref: "e55")

// Submit
mcp__playwright__browser_click(element: "Submit Idea", ref: "e78")
```

### 3. Test Claim Approval Workflow

```javascript
// Step 1: Login as developer2 and claim an idea
mcp__playwright__browser_navigate(url: "http://localhost:9094/idea/[IDEA_UUID]")
mcp__playwright__browser_click(element: "Claim This Idea", ref: "e45")

// Step 2: Logout and login as idea owner
mcp__playwright__browser_navigate(url: "http://localhost:9094/logout")
// ... login as submitter1@company.com

// Step 3: Check notifications
mcp__playwright__browser_click(element: "Notification bell", ref: "e15")
mcp__playwright__browser_click(element: "View notification", ref: "e25")

// Step 4: Approve claim
mcp__playwright__browser_click(element: "Approve", ref: "e67")

// Step 5: Verify status change
mcp__playwright__browser_navigate(url: "http://localhost:9094/idea/[IDEA_UUID]")
// Check that status shows "CLAIMED"
```

### 4. Admin Portal Testing

```javascript
// Navigate to admin
mcp__playwright__browser_navigate(url: "http://localhost:9094/admin/login")

// Enter password
mcp__playwright__browser_type(element: "Password", ref: "e20", text: "2929arch")
mcp__playwright__browser_click(element: "Login", ref: "e22")

// Test admin features
mcp__playwright__browser_click(element: "Manage Ideas", ref: "e45")
mcp__playwright__browser_click(element: "Manage Users", ref: "e50")
mcp__playwright__browser_click(element: "Manage Skills", ref: "e55")
```

## Debugging Common Issues

### 1. Authentication Problems

```javascript
// Check if user is logged in
mcp__playwright__browser_evaluate(
  function: "() => { return fetch('/api/user/profile').then(r => r.json()) }"
)

// Force logout
mcp__playwright__browser_navigate(url: "http://localhost:9094/logout")
```

### 2. API Errors

```javascript
// Check API response directly
mcp__playwright__browser_evaluate(
  function: "() => { return fetch('/api/my-ideas').then(r => r.json()) }"
)

// Check Docker logs for backend errors
bash("docker logs postingboard-flask-app-1 --tail 50")
```

### 3. JavaScript Errors

```javascript
// Get all console messages
mcp__playwright__browser_console_messages()

// Check specific element exists
mcp__playwright__browser_evaluate(
  function: "() => { return document.querySelector('.error-message')?.textContent }"
)
```

## Test Data Reference

### Pre-existing Users
- **Admin**: admin@system.local (password: 2929arch for admin portal)
- **Manager**: manager1@company.com (Sarah Manager)
- **Developers**: 
  - developer1@company.com (John Developer)
  - developer2@company.com (Jane Developer)
- **Submitter**: submitter1@company.com (Alice Submitter)

### Test Database Queries

```bash
# Get all users
sqlite3 backend/data/posting_board_uuid.db "SELECT email, name, role FROM user_profiles;"

# Get verification code
sqlite3 backend/data/posting_board_uuid.db "SELECT code FROM verification_codes WHERE email='[EMAIL]' ORDER BY created_at DESC LIMIT 1;"

# Check claim approvals
sqlite3 backend/data/posting_board_uuid.db "SELECT * FROM claim_approvals WHERE idea_uuid='[UUID]';"

# Get idea status
sqlite3 backend/data/posting_board_uuid.db "SELECT title, status FROM ideas WHERE uuid='[UUID]';"
```

## Best Practices

1. **Always use Docker mode** for testing - provides better log access
2. **Rebuild after code changes**: `./start-flask.sh down && ./start-flask.sh`
3. **Use snapshots over screenshots** for faster testing
4. **Test with existing users** to avoid email verification issues
5. **Check both frontend and backend** when debugging errors
6. **Wait for async operations** using wait_for functions
7. **Batch related tests** to maintain session state

## Example: Full Test Suite

```javascript
// 1. Setup
bash("./start-flask.sh")
mcp__playwright__browser_wait_for(time: 5)

// 2. Test homepage
mcp__playwright__browser_navigate(url: "http://localhost:9094")
mcp__playwright__browser_snapshot()

// 3. Test authentication
// ... authentication flow

// 4. Test core features
// - Submit idea
// - Browse ideas with filters
// - Claim idea
// - Approve claim
// - Check notifications

// 5. Test admin features
// ... admin tests

// 6. Generate report
// Document all findings, errors, and recommendations
```

## Troubleshooting

### Browser not responding
```bash
# Restart MCP server
mcp__playwright__browser_close()
# Then start fresh
```

### Session expired
```javascript
// Re-authenticate
mcp__playwright__browser_navigate(url: "http://localhost:9094/verify-email")
// ... complete login flow
```

### Docker container issues
```bash
# Check container status
docker ps

# Restart container
./start-flask.sh restart

# View logs
docker logs postingboard-flask-app-1 -f
```

## Advanced Testing

### Performance Testing
```javascript
// Measure page load time
mcp__playwright__browser_evaluate(
  function: "() => { return performance.timing.loadEventEnd - performance.timing.navigationStart }"
)
```

### Accessibility Testing
```javascript
// Get full accessibility tree
mcp__playwright__browser_snapshot()
// Review for proper ARIA labels, roles, and structure
```

### Mobile Testing
```javascript
// Resize browser
mcp__playwright__browser_resize(width: 375, height: 667)
// Test responsive behavior
```

## Conclusion

The MCP Playwright integration provides powerful browser automation capabilities for comprehensive testing of the Posting Board application. By following this guide, you can efficiently test all features, debug issues, and ensure the application works correctly across different scenarios and user roles.