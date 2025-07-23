# Citizen Developer Posting Board - Claude Development Notes

## Project Context
This is a web application for posting and claiming citizen developer ideas. It allows teams to post development needs with required skills, and developers to browse and claim ideas they can work on.

## Current Implementation: Flask (Python)

The application uses Flask with server-side rendering and a REST API for dynamic functionality.

### Configuration
- **Port**: The application runs on port **9094** (changed from default 5000)
- **Python Version**: Requires Python 3.8 or newer (Python 3.12 preferred)
- **Proxy Support**: Automatic pip proxy configuration via HTTP_PROXY/HTTPS_PROXY environment variables

### Python Setup
The `start-flask.sh` script handles Python version detection and virtual environment creation:
- **Automatic version check**: Verifies Python 3.8+ is available
- **Python 3.12 priority**: Uses Python 3.12 if found, otherwise falls back to system Python 3
- **No root required**: All installation happens in user space (virtual environment)
- **Version compatibility**: Requirements use flexible version ranges for better compatibility

### Flask Architecture
- **MVC Pattern**: Flask app with blueprints for organization
- **Template Rendering**: Jinja2 templates for server-side rendering
- **REST API**: JSON endpoints for dynamic functionality
- **Session Management**: Flask-Session for user tracking and authentication
- **Static Assets**: CSS and JavaScript in `static/` folder

### Key Components

#### Main Application (`app.py`)
- Flask application factory pattern
- Registers blueprints for modular routing
- Configures session management
- Sets up error handlers

#### Blueprint Structure
```
blueprints/
├── main.py          # Main routes (home, submit, claim, etc.)
├── api.py           # REST API endpoints for AJAX calls
└── admin.py         # Admin panel routes
```

#### Templates Structure
```
templates/
├── base.html        # Base template with navigation
├── home.html        # Browse/filter ideas
├── submit.html      # Submit new ideas
├── my_ideas.html    # View submitted and claimed ideas
├── idea_detail.html # Individual idea view
└── admin/           # Admin panel templates
    ├── login.html
    ├── dashboard.html
    ├── ideas.html
    └── skills.html
```

#### Database Models (unchanged from original)
- **Idea**: Main entity with title, description, priority, size, status
- **Skill**: Many-to-many relationship with ideas
- **Claim**: Tracks who claimed which idea
- **Enums**: PriorityLevel, IdeaSize, IdeaStatus

### Flask-Specific Features

#### API Endpoints
- `/api/ideas` - Get filtered ideas list
- `/api/my-ideas` - Get user's submitted and claimed ideas
- `/api/skills` - Get all available skills
- `/api/admin/stats` - Get dashboard statistics
- RESTful design with JSON responses

#### Session Management
- Tracks submitted idea IDs in `session['submitted_ideas']`
- Tracks claimed idea IDs in `session['claimed_ideas']`
- Stores user email in `session['user_email']` for persistence
- Admin authentication with `session['is_admin']`
- Session data provides immediate access within same browser session
- Database persistence ensures data is never lost

#### Frontend JavaScript
- Vanilla JavaScript for interactivity
- AJAX calls using Fetch API
- Dynamic DOM manipulation
- Auto-refresh functionality
- Form validation and submission

#### My Ideas Features
- Shows both submitted and claimed ideas
- Email lookup functionality for cross-session access
- Visual distinction between submitted/claimed/both
- Statistics showing submitted, claimed, open, and complete counts
- Color-coded left borders and relationship badges

#### Admin Features
- Password authentication (password: "2929arch")
- Dashboard with charts and statistics
- Idea management with inline editing
- Skill management (add/edit/delete)
- Real-time updates

### Styling
- Custom CSS in `static/css/styles.css`
- Responsive design with CSS Grid and Flexbox
- Hover effects for interactive elements
- Modal dialogs for claims
- Consistent color scheme for priorities/statuses

## Docker Configuration

### Flask Docker Setup
- `docker-compose-flask.yml`: Single service configuration
- `backend/Dockerfile`: Runs Flask with Gunicorn
- Volume mounts for database persistence
- Environment variables for configuration

### Start Scripts
- `start-flask.sh`: Unified script for Flask development
  - Native mode: Sets up venv, installs deps, runs `python app.py`
  - Docker mode: Uses `docker-compose-flask.yml`
  - Port conflict detection and resolution
  - Service management (start/stop/logs)

## Development Workflow

### Local Development
```bash
# Using convenience script
./start-flask.sh              # Start with Docker (default)
./start-flask.sh native       # Start in native mode
./start-flask.sh down         # Stop all services

# With proxy configuration
HTTP_PROXY=http://proxy:8080 HTTPS_PROXY=http://proxy:8080 ./start-flask.sh

# Manual commands
source venv/bin/activate
pip install -r requirements.txt
cd backend
python app.py
```

The application will be accessible at http://localhost:9094

### Testing Flask App
- API endpoints: `curl http://localhost:9094/api/ideas`
- Templates render server-side HTML
- Check Flask logs for errors
- Browser DevTools for JavaScript debugging

## Key Features

### Session-Based Tracking
- Ideas submitted by users tracked in session
- Claims tracked separately in session
- Email stored for cross-session persistence
- No user accounts required

### Database Persistence
- **Ideas table**: Stores submitter's email in `email` column (required field)
- **Claims table**: Stores claimer's email in `claimer_email` column (required field)
- All submitted ideas permanently associated with submitter's email
- All claims permanently associated with claimer's email
- Enables cross-session access without user accounts

### Email Lookup
- My Ideas page shows email lookup when no session data
- Users can retrieve all their ideas by email
- Works for both submitted and claimed ideas
- Queries database for:
  - `Idea.email == user_email` (submitted ideas)
  - `Claim.claimer_email == user_email` (claimed ideas)
- Returns combined results with relationship indicators

## Performance Considerations
- Server-side rendering reduces initial load time
- API endpoints return minimal JSON data
- Auto-refresh intervals set to 30 seconds
- Efficient database queries with SQLAlchemy
- Session storage for user tracking

## Production Deployment
```bash
# With Gunicorn
gunicorn -w 4 -b 0.0.0.0:9094 app:app

# With Docker
docker compose -f docker-compose-flask.yml up -d
```

## API Documentation

### Public Endpoints
- `GET /api/ideas` - List ideas with filters
  - Query params: `skill`, `priority`, `status`, `sort`
- `GET /api/my-ideas` - Get user's submitted and claimed ideas
  - Query params: `email` (optional for email-based lookup)
  - Returns: Array of ideas with `relationship` field (submitted/claimed/both)
  - Includes `claim_info` for claimed ideas
- `GET /api/skills` - List all available skills
- `POST /idea/<id>/claim` - Claim an idea
  - Updates session with claimed idea ID and email
  - Stores claimer email in database

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- Requires admin session authentication

## Common Issues and Solutions

### Enum Case Mismatches
- Database may have uppercase enum values (OPEN, SMALL, etc.)
- Python enums use lowercase (open, small, etc.)
- Fix by running: `UPDATE ideas SET status = LOWER(status)`
- Same for priority and size fields

### Session Not Persisting
- Flask-Session uses filesystem storage
- Check `flask_session/` directory permissions
- Set `session.permanent = True` after updates

### API Errors
- Check Flask logs for detailed error messages
- Ensure all required fields are provided
- Validate email format on frontend

## Future Enhancements
1. WebSocket support for real-time updates
2. File upload capabilities
3. Export functionality (CSV/Excel)
4. Advanced filtering with date ranges
5. User authentication system
6. Email templates
7. Audit logging
8. Performance monitoring

## Debug Tips
- Enable Flask debug mode in `dash_app.py`
- Check terminal for callback errors
- Use browser DevTools for network/console
- Add print statements in callbacks
- Check `flask_session/` for session files

## Troubleshooting

### Database Not Initialized
If ideas are not showing or you get "no such table" errors:
```bash
# Initialize database in Docker container
docker exec postingboard-flask-app-1 python database.py
```

### Admin Portal Routes
The admin panel is accessible at `/admin` which redirects to:
- `/admin/login` if not authenticated
- `/admin/dashboard` if authenticated
- Password: `2929arch`

### PR_END_OF_FILE_ERROR
This error means the browser is trying HTTPS on an HTTP-only server. Always use:
- Correct: `http://192.168.1.189:9094`
- Wrong: `https://192.168.1.189:9094`

### Ideas Not Showing on Home Page
If ideas exist in the database but aren't displaying, check enum comparisons in filters:

**Problem**: SQLAlchemy enums can't be compared directly with strings
```python
# Wrong - will always return False
query.filter(Idea.status == 'open')

# Correct - convert string to enum first
query.filter(Idea.status == IdeaStatus('open'))
```

**Fix in `backend/pages/home.py`** (lines 128-132):
```python
if priority_filter:
    query = query.filter(Idea.priority == PriorityLevel(priority_filter))
    
if status_filter:
    query = query.filter(Idea.status == IdeaStatus(status_filter))
```

**Apply fixes to Docker container**:
```bash
docker cp backend/blueprints/api.py postingboard-flask-app-1:/app/blueprints/api.py
docker restart postingboard-flask-app-1
```

**Testing enum queries**:
```bash
# Verify the query works correctly
docker exec postingboard-flask-app-1 python -c "
from database import get_session
from models import Idea, IdeaStatus
db = get_session()
open_ideas = db.query(Idea).filter(Idea.status == IdeaStatus.open).count()
print(f'Open ideas found: {open_ideas}')
db.close()
"
```

This issue affects all enum-based filters (priority, status, size) throughout the application. Always convert string values to enum instances before comparison in SQLAlchemy queries.


## Admin Access
- Navigate to `/admin/login`
- Password: `2929arch`
- After login, redirects to `/admin/dashboard`

The Flask implementation provides a traditional web application architecture with server-side rendering and REST APIs for dynamic functionality.

## User Features

### My Ideas Functionality
The application includes a "My Ideas" feature that allows users to track both submitted and claimed ideas without requiring user accounts.

#### Implementation Details
- **Hybrid tracking approach**: Combines session-based and email-based tracking
- **Session storage**: 
  - Submitted idea IDs stored in `session['submitted_ideas']`
  - Claimed idea IDs stored in `session['claimed_ideas']`
  - User email stored in `session['user_email']`
- **Database persistence**:
  - Ideas table stores submitter email in `email` column
  - Claims table stores claimer email in `claimer_email` column
  - All data permanently accessible via email lookup
- **Query logic**: Shows ideas that match:
  - Session IDs (immediate access)
  - Database email matches (cross-session access)
  - Identifies relationship: submitted, claimed, or both

#### Key Files Modified
1. **`blueprints/main.py`**:
   - Submit route stores idea IDs and email in session
   - Claim route stores claimed idea IDs and email in session
   - Email always saved to database for persistence

2. **`blueprints/api.py`**:
   - `/api/my-ideas` endpoint enhanced to return both submitted and claimed ideas
   - Accepts optional `email` parameter for cross-session lookup
   - Returns relationship type and claim info for each idea

3. **`templates/my_ideas.html`**:
   - Displays both submitted and claimed ideas with visual distinction
   - Shows 4 stats: Submitted, Claimed by Me, Open, Complete
   - Email lookup form when no session data exists
   - Color-coded borders and relationship badges
   - Auto-refreshes every 30 seconds

#### Usage
- Users can access their submitted and claimed ideas by clicking "My Ideas" in the navigation
- Within same browser session: Instant access via session storage
- Across different sessions: Email lookup retrieves full history from database
- No login required - completely session/email based
- Data is never lost - emails are permanently stored in database


### Docker Deployment Notes

#### Rebuilding After Code Changes
When making changes to the Flask application, you must rebuild the Docker container:

```bash
# Stop and rebuild with new changes
docker compose -f docker-compose-flask.yml down
docker compose -f docker-compose-flask.yml up -d --build
```

**Important**: Always ensure your changes are saved in the host directory before rebuilding, as Docker will copy files from the host during the build process.

#### Verifying Changes in Container
To confirm your changes are present in the running container:

```bash
# Check if a file exists
docker exec postingboard-flask-app-1 ls -la templates/my_ideas.html

# View specific content
docker exec postingboard-flask-app-1 cat app.py | grep "my-ideas"

# Check container logs for errors
docker logs postingboard-flask-app-1 --tail 50
```


## Dependency Management

### Python Version Compatibility
- **Minimum Python version**: 3.8 (required for all dependencies)
- **Recommended Python version**: 3.12 (optimal performance and compatibility)
- **Virtual environment**: Always created in user space, no root access required

### Package Versions
Updated for Python 3.12 compatibility:
- **numpy**: >=1.26.0,<2.0.0 (flexible range to avoid compatibility issues)
- **pandas**: >=2.1.0,<3.0.0 (ensures numpy compatibility)
- Other packages use fixed versions for stability

### Known Issues and Solutions
1. **"Failed to import site module" error**: This occurs when trying to use a locally built Python with missing dependencies. Solution: Use system Python (3.8+) instead.
2. **numpy/pandas compatibility**: Earlier versions (numpy 1.24.3, pandas 2.0.3) don't support Python 3.12. Solution: Use the updated flexible version ranges.