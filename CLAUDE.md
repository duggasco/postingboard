# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Citizen Developer Posting Board - A Flask web application for posting and claiming development ideas with skill matching, team management, and approval workflows.

## Development Commands

### Starting the Application
```bash
# Docker mode (default)
./start-flask.sh              # Start with Docker
./start-flask.sh down         # Stop services
./start-flask.sh logs         # View logs
./start-flask.sh restart      # Restart services

# Native mode (Python 3.8+ required, 3.12 preferred)
./start-flask.sh native       # Start without Docker

# Manual start
cd backend
source ../venv/bin/activate
python app.py                 # Runs on http://localhost:9094
```

### Database Operations
```bash
# Initialize database (auto-created on startup)
cd backend
python database.py

# Database location: backend/data/posting_board_uuid.db
```

### Testing & Debugging
- No formal test framework configured yet
- Test endpoints manually: `curl http://localhost:9094/api/ideas`
- Check logs: `docker logs postingboard-flask-app-1`
- Flask debug mode enabled in development
- **Automated testing with MCP Playwright server** (see Testing with MCP section)

## Architecture Overview

### Flask Application Structure
```
backend/
├── app.py                 # Flask app factory, blueprints registration
├── blueprints/           # Modular routes
│   ├── main.py          # Public routes (/, /submit, /my-ideas, etc.)
│   ├── api.py           # REST API endpoints (/api/*)
│   ├── admin.py         # Admin panel routes (/admin/*)
│   └── auth.py          # Authentication routes (/verify-email, /profile)
├── models/              # SQLAlchemy models (UUID-based)
├── templates/           # Jinja2 templates (server-side rendering)
├── static/              # CSS, JavaScript assets
└── data/               # SQLite database location
```

### Key Design Decisions

1. **UUID Primary Keys**: All tables use 36-character UUID strings (not integers)
   - Field naming: `uuid` for primary keys, `*_uuid` for foreign keys
   - Session variables use `*_uuid` suffix

2. **Email-Based Auth**: No passwords, email verification with 6-digit codes
   - Session-based persistence (`session['user_email']`, `session['user_verified']`)
   - Role-based access: manager, developer, citizen_developer, idea_submitter

3. **Dual Approval Workflow**: Claims require approval from idea owner + manager
   - ClaimApproval model tracks pending requests
   - Auto-approval if claimer has no manager

4. **Blueprint Organization**: Separation of concerns
   - `main.py`: UI routes with template rendering
   - `api.py`: JSON API endpoints for AJAX
   - `admin.py`: Admin portal (password: "2929arch")
   - `auth.py`: Email verification and profiles

## Common Development Tasks

### Adding a New Feature
1. Define model in `models/__init__.py` if needed
2. Add route in appropriate blueprint
3. Create/update template in `templates/`
4. Add JavaScript in `static/js/` if interactive
5. Update API endpoint in `blueprints/api.py` if needed

### Working with the Database
```python
# Get database session
from database import get_session
db = get_session()

# Query examples
from models import Idea, IdeaStatus
ideas = db.query(Idea).filter(Idea.status == IdeaStatus.open).all()

# Always close session
db.close()
```

### Session Management
```python
# Store in session
session['user_email'] = email
session['user_verified'] = True
session.permanent = True  # Important for persistence

# UUID fields in session
session['user_managed_team_uuid']  # Not user_managed_team_id
```

### Admin Access
- Hidden entry: Click version number (e.g., "v.446f372") in bottom-right
- Direct URL: `/admin/login`
- Password: `2929arch`

## Important Implementation Details

### Enum Handling
```python
# Always convert strings to enums for queries
from models import IdeaStatus, PriorityLevel
query.filter(Idea.status == IdeaStatus(status_string))
```

### Frontend Patterns
- Vanilla JavaScript (no framework)
- Utils in `/static/js/main.js` (formatDate, escapeHtml, etc.)
- Auto-refresh: 30-second intervals
- Modal pattern for editing

### API Response Format
```json
{
  "success": true,
  "data": {...},
  "error": "message if failed"
}
```

### Critical Files to Understand
1. `models/__init__.py` - All database models and relationships
2. `blueprints/api.py` - Core business logic in API endpoints  
3. `decorators.py` - Authentication decorators
4. `static/js/home.js` - Idea browsing/filtering logic
5. `templates/base.html` - Layout and navigation

## Current Features

### Core Functionality
- Browse/filter ideas by skills, priority, status, team
- Submit ideas with skills, priority, size, bounty
- Claim ideas with dual approval workflow
- Email-based authentication (no passwords)
- Team management with managers and members
- Admin portal for full system control

### Advanced Features
- Monetary bounties with expense tracking and approval
- Sub-status tracking for development lifecycle
- SVG GANTT charts for project timelines
- Notifications system with bell icon
- Bulk CSV import for ideas and users
- Team spending analytics and KPIs
- Skills gap analysis for teams

### Key Models
- **Idea**: Core entity with title, description, status, bounty
- **UserProfile**: Email-based users with role, team, skills
- **Team**: Organizations with approval status
- **Claim/ClaimApproval**: Dual approval tracking
- **Bounty**: Monetary bounty details and approvals
- **Notification**: User notifications for events

## Deployment

### Docker Production
```bash
docker compose -f docker-compose-flask.yml up -d --build
```

### Environment Variables
- `PORT`: Default 9094
- `DATABASE_URL`: SQLite path
- `MAIL_*`: SMTP configuration
- `HTTP(S)_PROXY`: Corporate proxy support

## Known Gotchas

1. **UUID Migration**: Never use `parseInt()` on IDs
2. **Enum Case**: Database may have uppercase, Python uses lowercase
3. **Session Persistence**: Always set `session.permanent = True`
4. **Team UUIDs**: Use `team_uuid` not `team_id` in all contexts
5. **API Auth**: Check both manager role AND admin status

## Quick Debugging

```bash
# Check if database exists
ls -la backend/data/

# View recent logs
docker logs postingboard-flask-app-1 --tail 50

# Test API endpoint
curl http://localhost:9094/api/ideas

# Check session data
ls -la backend/flask_session/

# Force cache refresh (if JS/CSS changes not showing)
# Add ?v=123 to static file URLs in templates
```

## Testing with MCP Playwright Server

The application can be comprehensively tested using the MCP (Model Context Protocol) Playwright server integration. This enables automated browser testing with full UI interaction capabilities.

### Setting Up MCP Testing

1. **Ensure MCP Playwright server is configured** in Claude
2. **Start the application in Docker mode** for easier log access:
   ```bash
   ./start-flask.sh  # Starts on http://localhost:9094
   ```

### Common Testing Workflows

#### 1. Basic Navigation Test
```javascript
// Navigate to homepage
mcp__playwright__browser_navigate(url: "http://localhost:9094")

// Take a snapshot to see page structure
mcp__playwright__browser_snapshot()

// Click on specific elements
mcp__playwright__browser_click(element: "Submit Idea link", ref: "e13")
```

#### 2. User Authentication Testing
```javascript
// Navigate to email verification
mcp__playwright__browser_navigate(url: "http://localhost:9094/verify-email")

// Enter email
mcp__playwright__browser_type(
  element: "Email input", 
  ref: "e30", 
  text: "developer1@company.com"
)

// Click send code button
mcp__playwright__browser_click(element: "Send Code button", ref: "e31")

// Get verification code from database (since no email configured)
// Run bash command: sqlite3 backend/data/posting_board_uuid.db \
//   "SELECT code FROM verification_codes WHERE email='developer1@company.com' ORDER BY created_at DESC LIMIT 1;"

// Enter verification code
mcp__playwright__browser_type(element: "Code input", ref: "e40", text: "123456")
```

#### 3. Testing Idea Submission
```javascript
// Fill out idea form
mcp__playwright__browser_type(element: "Title input", ref: "e30", text: "Test Idea")
mcp__playwright__browser_type(element: "Description", ref: "e35", text: "Test description")

// Select dropdown values
mcp__playwright__browser_select_option(
  element: "Priority dropdown", 
  ref: "e42", 
  values: ["high"]
)

// Submit form
mcp__playwright__browser_click(element: "Submit button", ref: "e78")
```

#### 4. Testing Complex Workflows (Claim Approval)
```javascript
// 1. Login as developer
// 2. Navigate to idea details page
// 3. Click claim button
// 4. Switch user (logout/login as idea owner)
// 5. Navigate to notifications
// 6. Approve claim request
// 7. Verify idea status changed
```

### Debugging Test Failures

1. **Check console errors**:
   ```javascript
   mcp__playwright__browser_console_messages()
   ```

2. **View network requests**:
   ```javascript
   mcp__playwright__browser_network_requests()
   ```

3. **Take screenshots**:
   ```javascript
   mcp__playwright__browser_take_screenshot(filename: "error-state.png")
   ```

4. **Check Docker logs**:
   ```bash
   docker logs postingboard-flask-app-1 --tail 50
   ```

5. **Evaluate JavaScript directly**:
   ```javascript
   mcp__playwright__browser_evaluate(
     function: "() => { return document.querySelector('.error-message')?.textContent }"
   )
   ```

### Best Practices for MCP Testing

1. **Always start with Docker mode** - easier to check logs and grab verification codes
2. **Use browser snapshots** instead of screenshots for navigation
3. **Wait for page loads** when needed:
   ```javascript
   mcp__playwright__browser_wait_for(time: 3)  // Wait 3 seconds
   mcp__playwright__browser_wait_for(text: "Success")  // Wait for text
   ```

4. **Test with actual database users** rather than creating new ones:
   - developer1@company.com (John Developer)
   - developer2@company.com (Jane Developer)  
   - manager1@company.com (Sarah Manager)
   - admin@system.local (Admin User)

5. **Rebuild Docker when testing fixes**:
   ```bash
   ./start-flask.sh down
   ./start-flask.sh  # This rebuilds the image
   ```

### Example: Complete Test Session

```javascript
// 1. Start application
bash("./start-flask.sh")
sleep(5)

// 2. Navigate and login
mcp__playwright__browser_navigate(url: "http://localhost:9094")
mcp__playwright__browser_click(element: "My Ideas", ref: "e9")
// ... handle login flow

// 3. Test main functionality
mcp__playwright__browser_navigate(url: "http://localhost:9094/")
// ... test filtering, claiming, etc.

// 4. Check admin panel
mcp__playwright__browser_navigate(url: "http://localhost:9094/admin/login")
mcp__playwright__browser_type(element: "Password", ref: "e20", text: "2929arch")

// 5. Generate test report
// Document findings, errors, and recommendations
```

### Common Issues and Solutions

1. **AttributeError in API**: Check model field names match between backend and frontend
2. **500 Errors**: Always check Docker logs for Python stack traces
3. **JavaScript errors**: Use formatDate() from utils, not direct date manipulation
4. **Session issues**: Ensure session.permanent = True in auth flows
5. **Missing data**: Remember to query related models (e.g., UserProfile for team info)