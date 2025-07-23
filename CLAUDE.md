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
├── admin.py         # Admin panel routes
└── auth.py          # Authentication routes (verify email, profile)

#### Templates Structure
```
templates/
├── base.html        # Base template with navigation
├── home.html        # Browse/filter ideas
├── submit.html      # Submit new ideas
├── my_ideas.html    # View submitted and claimed ideas
├── idea_detail.html # Individual idea view
├── admin/           # Admin panel templates
│   ├── login.html
│   ├── dashboard.html
│   ├── ideas.html
│   └── skills.html
└── auth/            # Authentication templates
    ├── verify_email.html  # Email verification page
    └── profile.html       # User profile management
```

#### Database Models
- **Idea**: Main entity with title, description, priority, size, status, and assignment fields
- **Skill**: Many-to-many relationship with ideas and users
- **Team**: Stores team names with approval status (predefined teams are auto-approved)
- **Claim**: Tracks who claimed which idea (created after approvals)
- **ClaimApproval**: Tracks claim requests requiring dual approval before claims are created
- **UserProfile**: Stores user email, name, verification status, role, team, managed team, and skills
- **VerificationCode**: Tracks email verification codes with expiry and rate limiting
- **ManagerRequest**: Tracks requests from users to manage teams, requiring admin approval
- **Enums**: PriorityLevel, IdeaSize, IdeaStatus

### Flask-Specific Features

#### API Endpoints
- `/api/ideas` - Get filtered ideas list
- `/api/my-ideas` - Get user's submitted and claimed ideas (requires authentication)
- `/api/skills` - Get all available skills
- `/api/teams` - Get teams (all for admin, approved only for others)
- `/api/admin/stats` - Get dashboard statistics
- RESTful design with JSON responses

#### Authentication Endpoints
- `/verify-email` - Email verification page
- `/request-code` - Request verification code (POST)
- `/verify-code` - Verify submitted code (POST)
- `/profile` - User profile page (requires authentication)
- `/profile/update` - Update user profile (POST, requires authentication)
- `/logout` - Clear session and logout

#### Session Management
- Tracks submitted idea IDs in `session['submitted_ideas']`
- Tracks claimed idea IDs in `session['claimed_ideas']`
- Stores user email in `session['user_email']` for persistence
- Stores user name in `session['user_name']` after profile completion
- Stores verification status in `session['user_verified']`
- Stores user role in `session['user_role']` (manager, idea_submitter, citizen_developer, developer)
- Stores user team in `session['user_team']` (team name)
- Stores user managed team in `session['user_managed_team']` (team name) and `session['user_managed_team_id']`
- Stores pending manager request status in `session['pending_manager_request']` and `session['pending_team']`
- Stores user skills in `session['user_skills']` as list of skill names
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
- Idea management with inline editing (shows ALL ideas, not just open ones)
- Skill management (add/edit/delete)
- Team management (add/edit/delete/approve)
- **User Management**: Full CRUD operations on user profiles
  - Filter by name, email, role, and team
  - Edit user profiles including role, team, skills, and verification
  - Delete users with cascading deletion of related data
- Manager requests approval workflow
- Real-time updates
- **Bulk Upload**: Import ideas and users from CSV files
  - Download template CSV files
  - Validate data before import
  - Detailed error reporting
  - Automatic skill creation

### Styling & UI Design
- Custom CSS in `static/css/styles.css`
- **Modern Professional Design**: 
  - Smaller, consistent typography (base 14px)
  - Refined color palette with subtle backgrounds
  - Enhanced shadows and transitions
- **Typography Scale**:
  - Body text: 14px
  - Navigation: 13px
  - Metadata: 12px
  - Labels/badges: 11px uppercase
  - Page titles: 1.75rem
- **Visual Improvements**:
  - Navigation bar: Dark #1a1d23 background
  - Primary color: #4a90e2 (professional blue)
  - Status badges: Soft backgrounds instead of solid colors
  - Border radius: 10-12px for modern appearance
  - Subtle hover effects with translateY animations
- **Layout**:
  - Responsive CSS Grid (320px min card width)
  - Consistent spacing (16px gaps)
  - Proper flex alignment in cards
  - Professional table styling with uppercase headers
- **Interactive Elements**:
  - Form inputs with focus shadows
  - Buttons with hover transforms
  - Modal dialogs with backdrop blur
  - Smooth 0.2s ease transitions

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

### Claim Approval Process
- **Dual Approval System**: Claims require approval from both idea owner and claimer's manager
- **Pending Status**: Claims show as "PENDING CLAIM" while awaiting approvals
- **Denial Handling**: Denied claims show as "CLAIM DENIED" with red styling
- **Auto-Approval**: Manager approval auto-granted if claimer has no manager
- **Private Workflow**: Approval states only visible to involved parties, not on public pages
- **Approval Interface**: Integrated into My Ideas page with approve/deny buttons

### Manager Capabilities
- **Team Oversight**: View all team members' submitted and claimed ideas
- **Claim Approvals**: Approve/deny team members' claim requests
- **Idea Assignment**: Assign open ideas to specific team members
- **Assignment Tracking**: Ideas track who assigned them and when
- **Team Performance Dashboard**: Comprehensive KPIs and analytics for team activity
  - Overview metrics: team size, submissions, claims, completion rate, pending approvals
  - Visual charts: priority/status/size distributions, top skills
  - Team member activity table with individual performance metrics
  - Recent activity tracking (last 30 days)

### Submitter and Claimer Display
- **Submitter Names**: Ideas display the name of the person who submitted them
  - Shows user profile name if available
  - Falls back to email address for legacy ideas
  - Displayed on: home page, idea details, my ideas, admin panel
- **Claimer Information**: Claimed ideas show who claimed them
  - Displays claimer name and email
  - Shows claim date
  - Visible on all idea views
- **Database Relationship**: `Idea.submitter` relationship links to `UserProfile` via email
- **API Response**: Both `/api/ideas` and `/api/my-ideas` include:
  - `submitter_name`: Name from user profile (null if no profile)
  - `claims`: Array with name, email, and date for each claim

### Email-Based Authentication System
- **Email Verification**: Users verify their email with a 6-digit code
- **No Passwords**: Authentication is purely email-based for simplicity
- **Verification Codes**: 
  - 6-digit numeric codes sent via email
  - Expire after 3 minutes
  - Maximum 3 active codes per email
  - 15-minute cooldown after rate limit
- **Profile System**: Users create profiles with name, role, team, and skills
- **Role-Based Access**: Only developers and citizen developers can claim ideas
- **Protected Routes**: Submit and claim features require authentication
- **Claim Authentication**: Users must be logged in with a complete profile to claim ideas

### Session-Based Tracking
- Ideas submitted by users tracked in session
- Claims tracked separately in session
- User profile data stored in session after authentication
- Email stored for cross-session persistence

### Database Persistence
- **Ideas table**: Stores submitter's email in `email` column (required field)
- **Claims table**: Stores claimer's email in `claimer_email` column (required field)
- **UserProfile table**: Stores user email, name, verification status, role, team, and skills
- **Teams table**: Stores team names with approval status (is_approved field)
- **VerificationCode table**: Tracks verification attempts with timestamps
- All submitted ideas permanently associated with submitter's email
- All claims permanently associated with claimer's email
- User profiles enable consistent identity across sessions

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
  - Note: If no status param provided, returns ALL ideas (changed from defaulting to 'open')
- `GET /api/my-ideas` - Get user's submitted and claimed ideas (requires authentication)
  - Query params: `email` (optional for email-based lookup)
  - Returns: Array of ideas with `relationship` field (submitted/claimed/both)
  - Includes `claim_info` for claimed ideas
  - Includes `pending_claims` and `pending_approvals` for claim workflow
- `GET /api/skills` - List all available skills
- `GET /api/teams` - List teams (all with approval status for admin, approved only for others)
- `GET /api/teams/<id>/members` - Get team members (manager only for their team)
- `GET /api/team-stats` - Get comprehensive team statistics (manager only)
  - Returns overview metrics, breakdowns by priority/status/size/skills
  - Includes team member activity and recent activity (30 days)
- `POST /idea/<id>/claim` - Request to claim an idea (requires complete profile)
  - Creates ClaimApproval record requiring dual approval
  - Only developers and citizen developers can claim
- `GET /api/claim-approvals/pending` - Get pending claim approvals
- `POST /api/claim-approvals/<id>/approve` - Approve a claim request
- `POST /api/claim-approvals/<id>/deny` - Deny a claim request
- `POST /api/ideas/<id>/assign` - Assign idea to team member (manager only)

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- `POST /api/teams` - Add new team (admin only)
- `PUT /api/teams/<id>` - Update team name or approval status (admin only)
- `DELETE /api/teams/<id>` - Delete team (admin only)
- `POST /api/skills` - Add new skill (admin only)
- `PUT /api/skills/<id>` - Update skill (admin only)
- `DELETE /api/skills/<id>` - Delete skill (admin only)
- `GET /api/admin/manager-requests` - Get pending manager requests and current managers
- `POST /api/admin/manager-requests/<id>/approve` - Approve a manager request
- `POST /api/admin/manager-requests/<id>/deny` - Deny a manager request
- `POST /api/admin/remove-manager` - Remove a manager from their team
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

### Date Display Shows T-1 (Previous Day)
- **Problem**: Dates showing one day earlier than actual submission date
- **Cause**: Backend sends dates as 'YYYY-MM-DD' without timezone, JavaScript `new Date()` interprets as UTC
- **Solution**: Fixed in `static/js/main.js` formatDate function to parse date components manually
- **Implementation**: 
  ```javascript
  const [year, month, day] = dateString.split('-').map(num => parseInt(num, 10));
  const date = new Date(year, month - 1, day); // Local timezone
  ```
- **Apply fix to Docker**: `docker cp backend/static/js/main.js postingboard-flask-app-1:/app/static/js/main.js`

### API Errors
- Check Flask logs for detailed error messages
- Ensure all required fields are provided
- Validate email format on frontend

## Future Enhancements
1. WebSocket support for real-time updates
2. File upload capabilities
3. Export functionality (CSV/Excel)
4. Advanced filtering with date ranges
5. Password-based authentication option
6. Custom email templates
7. Audit logging
8. Performance monitoring
9. OAuth integration (Google, GitHub)
10. Notification system for approvals and assignments

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

### Bulk Upload Feature
The admin portal includes a bulk upload feature for importing ideas and users via CSV files.

#### Ideas CSV Format
Required columns:
- `title` - Idea title
- `description` - Detailed description
- `email` - Submitter's email address
- `benefactor_team` - Team name (must exist in system)
- `size` - small, medium, large, or extra_large
- `priority` - low, medium, or high
- `needed_by` - Date in YYYY-MM-DD format

Optional columns:
- `skills` - Comma-separated list of skill names
- `reward` - Reward description
- `status` - open, claimed, or complete (defaults to open)

#### Users CSV Format
Required columns:
- `email` - User's email address (must be unique)
- `name` - Full name
- `role` - manager, idea_submitter, citizen_developer, or developer
- `team` - Team name (must exist in system)

Optional columns:
- `skills` - Comma-separated list of skills (for developers/citizen developers)
- `is_verified` - true or false (defaults to true)

#### How to Use
1. Navigate to Admin > Bulk Upload
2. Download the template CSV file
3. Fill in your data following the format
4. Upload the CSV file
5. Review import results and any errors

Notes:
- Teams must exist before uploading users
- Skills are created automatically if they don't exist
- Duplicate user emails are skipped with error messages
- Validation ensures data integrity before import

### Admin Features
- **Dashboard**: View statistics and charts for ideas, skills, and teams
- **Ideas Management**: Edit/delete any idea, unclaim ideas, change status
- **Skills Management**: Add/edit/delete skills used across the platform
- **Teams Management**: 
  - Add/edit/delete teams
  - Approve custom teams submitted by users
  - Separate sections for approved and pending teams
- **Manager Requests**: 
  - View pending manager requests
  - Approve or deny requests to manage teams
  - Remove existing managers from their teams
  - Track request history
- **Email Settings**: Configure SMTP settings for verification emails

### Admin Dashboard Statistics Fix
The admin dashboard statistics may show blank values on page refresh due to timing issues. This was fixed by implementing a robust retry mechanism with multiple loading strategies:

1. **Retry Logic**: Up to 5 retries with 200ms delays to ensure DOM elements are rendered
2. **Multiple Loading Strategies**: Uses window.load, requestAnimationFrame, and delays
3. **Chart Instance Management**: Prevents duplicate chart instances on refresh
4. **Element Verification**: Checks all elements exist before proceeding

**Implementation in `/templates/admin/dashboard.html`**:
```javascript
(function() {
    let chartInstance = null; // Store chart instance to prevent duplicates
    
    async function loadStats() {
        let retries = 0;
        const maxRetries = 5;
        
        while (retries < maxRetries) {
            const elements = {
                totalIdeas: ensureElement('total-ideas'),
                openIdeas: ensureElement('open-ideas'),
                // ... other elements
            };
            
            const allElementsExist = Object.values(elements).every(el => el !== null);
            
            if (allElementsExist) {
                // Destroy existing chart if it exists
                if (chartInstance) {
                    chartInstance.destroy();
                    chartInstance = null;
                }
                
                // Load stats and create chart...
                return; // Success
            }
            
            // Retry after delay
            retries++;
            await new Promise(resolve => setTimeout(resolve, 200));
        }
    }
    
    function initStats() {
        // Strategy 1: If page complete, wait then load
        if (document.readyState === 'complete') {
            setTimeout(loadStats, 250);
        }
        
        // Strategy 2: Window load event
        window.addEventListener('load', () => setTimeout(loadStats, 250));
        
        // Strategy 3: RequestAnimationFrame for render completion
        if (typeof requestAnimationFrame !== 'undefined') {
            requestAnimationFrame(() => {
                requestAnimationFrame(() => loadStats());
            });
        }
    }
})();
```

This multi-layered approach ensures statistics load reliably even on fast page refreshes by:
- Retrying up to 5 times if elements aren't found
- Using multiple browser APIs to detect when rendering is complete
- Properly managing Chart.js instances to prevent memory leaks
- Providing clear console logging for debugging

### Admin Ideas Management
The admin ideas management page (`/admin/ideas`) displays ALL ideas in the system, not just open ones. This was achieved by:
- Removing the default `status='open'` filter from the `/api/ideas` endpoint
- Explicitly passing an empty status parameter in the admin JavaScript: `/api/ideas?status=`
- The home page continues to default to showing only open ideas via the HTML select default

The Flask implementation provides a traditional web application architecture with server-side rendering and REST APIs for dynamic functionality.

## User Features

### Role-Based Profiles
The application supports four user roles with different capabilities:
- **Manager**: Can submit ideas but cannot claim ideas or specify skills
  - Can request to manage a team (requires admin approval)
  - Once approved, can view team members' submitted and claimed ideas in My Ideas
- **Idea Submitter**: Can submit ideas but cannot claim ideas or specify skills  
- **Citizen Developer**: Can submit and claim ideas, must specify skills
- **Developer**: Can submit and claim ideas, must specify skills

### Team Management
Users and ideas are associated with teams:
- **Predefined Teams**: 13 pre-approved teams are available:
  - Cash - GPP, COO - IDA, COO - Business Management
  - SL - QAT, SL - Trading, SL - Product, SL - Clients, SL - Tech
  - Cash - PMG, Cash - US Product Strategy, Cash - EMEA Product Strategy
  - Cash - Sales, Cash - CMX
- **Custom Teams**: Users can enter custom team names
  - Custom teams require admin approval before appearing in selection lists
  - Stored with `is_approved=false` until admin approves
- **Team Selection**: Available in both profile creation and idea submission
  - Mutually exclusive dropdown/text input (selecting one clears the other)
  - Team selection persisted in localStorage for convenience

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
   - **Manager Dashboard**: Comprehensive team performance KPIs section
     - Team overview stats (members, submissions, claims, completion rate, pending approvals)
     - Interactive charts using Chart.js for visual analytics
     - Team member activity table with individual metrics
     - Recent activity tracking (last 30 days)

#### Usage
- Users can access their submitted and claimed ideas by clicking "My Ideas" in the navigation
- Within same browser session: Instant access via session storage
- Across different sessions: Email lookup retrieves full history from database
- No login required - completely session/email based
- Data is never lost - emails are permanently stored in database
- **Manager View**: Managers with approved team assignments see a separate "Team Ideas" section showing:
  - Ideas submitted by their team members
  - Ideas claimed by their team members
  - Team member names and emails for each idea


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

## Authentication System Details

### User Flow
1. **First Visit**: User accesses the site anonymously and can browse ideas
2. **Authentication Required**: When trying to submit/claim, redirected to `/verify-email`
3. **Email Verification**: 
   - User enters email address
   - System sends 6-digit code (console output if no SMTP configured)
   - User enters code within 3 minutes
4. **Profile Creation**: After verification, user completes profile with name and skills
5. **Full Access**: User can now submit ideas and claim others' ideas
6. **Session Persistence**: User remains logged in for 7 days (session timeout)

### Security Features
- **No Password Storage**: System doesn't store or manage passwords
- **Rate Limiting**: Prevents brute force attempts on verification codes
- **Code Expiry**: Verification codes expire after 3 minutes
- **Session Security**: HTTPOnly cookies prevent XSS attacks
- **Email Validation**: Basic validation on both client and server side

### Authentication Decorators
- `@require_verified_email`: Ensures user has verified their email
- `@require_profile_complete`: Ensures user has name and skills in profile
- Applied to routes: `/submit`, `/my-ideas`, `/api/my-ideas`, `/idea/<id>/claim`
- AJAX Detection: Decorators check for `X-Requested-With: XMLHttpRequest` header or JSON content type
- Returns JSON with 401 status for AJAX requests, redirects to `/verify-email` for regular requests

### Frontend Authentication Handling
- Claim button in `idea_detail.html` checks for 401 responses
- On authentication error, shows alert and redirects to `/verify-email`
- Modal form pre-fills user name from session if available

### Testing Authentication
```bash
# Test with curl
curl -X POST http://localhost:9094/request-code -d "email=test@example.com"

# Check Docker logs for verification code
docker logs postingboard-flask-app-1 | grep -A3 "Verification code"

# Verify code
curl -X POST http://localhost:9094/verify-code -d "code=123456" -b cookies.txt -c cookies.txt

# Test claiming without authentication
curl -X POST http://localhost:9094/idea/1/claim -H "X-Requested-With: XMLHttpRequest" -d "name=Test&team=Team"
# Returns: {"error":"Authentication required."} with 401 status
```

### Manager Approval Workflow

#### Overview
When users select the "Manager" role in their profile, they can request to manage a team. This request requires admin approval before the manager gains access to view their team members' ideas.

#### User Flow
1. **Request Submission**: 
   - User selects "Manager" role in profile
   - Selects a team from "Team to Manage" dropdown
   - On save, a `ManagerRequest` is created with `pending` status
   - User sees notification: "Your request to manage [Team] is pending admin approval"

2. **Admin Review**:
   - Admin navigates to `/admin/manager-requests`
   - Sees list of pending requests with user name, email, team, and request date
   - Can approve or deny each request

3. **Approval Process**:
   - **Approve**: Updates request status to `approved`, assigns `managed_team_id` to user
   - **Deny**: Updates request status to `denied`, user must submit new request if desired
   - Admin can also remove existing managers from their teams

4. **Manager Access**:
   - Approved managers see "Team Ideas" section in My Ideas page
   - Shows all ideas submitted or claimed by their team members
   - Excludes the manager's own ideas from team view

#### Database Schema
```python
class ManagerRequest(Base):
    __tablename__ = 'manager_requests'
    
    id = Column(Integer, primary_key=True)
    user_email = Column(String(120), ForeignKey('user_profiles.email'), nullable=False)
    requested_team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, denied
    requested_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    processed_by = Column(String(120))  # admin who processed the request
```

#### Admin API Endpoints
- `GET /api/admin/manager-requests` - Returns pending requests and current managers
- `POST /api/admin/manager-requests/<id>/approve` - Approve a request
- `POST /api/admin/manager-requests/<id>/deny` - Deny a request
- `POST /api/admin/remove-manager` - Remove manager (body: `{"email": "manager@example.com"}`)

### Claim Approval Workflow

#### Overview
Claims now require approval from both the idea owner and the claimer's manager before being finalized. This ensures proper oversight and resource allocation.

#### Workflow Steps
1. **Claim Request**: Developer/citizen developer requests to claim an idea
2. **Approval Request Created**: System creates a `ClaimApproval` record with pending status
3. **Dual Approval Required**:
   - **Idea Owner**: Must approve that the claimer can work on their idea
   - **Claimer's Manager**: Must approve their team member taking on the work
   - If claimer has no manager, manager approval is auto-granted
4. **Claim Finalized**: Once both approve, actual claim is created and idea status changes to "claimed"
5. **Denial**: If either party denies, the request is marked as denied

#### Database Schema
```python
class ClaimApproval(Base):
    __tablename__ = 'claim_approvals'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    claimer_email = Column(String(120), nullable=False)
    claimer_name = Column(String(100), nullable=False)
    claimer_team = Column(String(100))
    claimer_skills = Column(Text)
    
    # Approval tracking
    idea_owner_approved = Column(Boolean, default=None)  # None = pending
    manager_approved = Column(Boolean, default=None)
    idea_owner_approved_at = Column(DateTime)
    manager_approved_at = Column(DateTime)
    idea_owner_denied_at = Column(DateTime)
    manager_denied_at = Column(DateTime)
    
    # Who processed the approvals
    idea_owner_approved_by = Column(String(120))
    manager_approved_by = Column(String(120))
    
    # Overall status
    status = Column(String(20), default='pending')  # pending, approved, denied
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### API Endpoints
- `GET /api/claim-approvals/pending` - Get pending approvals for current user
- `POST /api/claim-approvals/<id>/approve` - Approve a claim request
- `POST /api/claim-approvals/<id>/deny` - Deny a claim request

#### UI Changes
- **My Ideas Page**: 
  - Shows "Pending Approvals" section for idea owners
  - Shows "My Pending Claims" section with approval status
  - Denied claims show as "CLAIM DENIED" with red styling
- **Status Display**: Only visible to involved parties (not on public pages)

### Manager Assignment Feature

#### Overview
Managers can assign open ideas to team members, streamlining task distribution within teams.

#### Implementation
- Added fields to Idea model: `assigned_to_email`, `assigned_at`, `assigned_by`
- Managers see "Assign to Team Member" button on open team ideas
- Assignment modal shows dropdown of eligible team members

#### API Endpoints
- `POST /api/ideas/<id>/assign` - Assign idea to team member
- `GET /api/teams/<id>/members` - Get team members for assignment dropdown

### Submitter/Claimer Implementation Details

#### Model Relationship
```python
# In models/__init__.py
class Idea(Base):
    # ... other fields ...
    email = Column(String(120), nullable=False)
    submitter = relationship('UserProfile', foreign_keys=[email], 
                           primaryjoin="Idea.email==UserProfile.email", viewonly=True)
```

#### Frontend Display
- **Home Page (`home.js`)**: Shows "Submitted by [Name]: [Date]"
- **Idea Detail (`idea_detail.html`)**: Shows full submitter info with fallback to email
- **My Ideas (`my_ideas.html`)**: Shows both submitter and claimer names
- **Admin Panel (`admin/ideas.html`)**: Shows "Name (email)" format

#### API Response Structure
```json
{
  "id": 1,
  "title": "Example Idea",
  "submitter_name": "Jane Doe",  // null if no profile
  "email": "jane@example.com",
  "claims": [
    {
      "name": "John Developer",
      "email": "john@example.com",
      "date": "2025-07-23"
    }
  ]
}
```

### UI Design System

#### Color Palette
- **Primary**: #4a90e2 (Professional blue)
- **Navigation**: #1a1d23 (Dark navy)
- **Background**: #f8f9fa (Light gray)
- **Text**: #1a1d23 (titles), #6c757d (meta), #868e96 (secondary)
- **Borders**: #e9ecef (light), #dee2e6 (medium)
- **Status Colors**:
  - Open: #e7f5ed bg, #28a745 text
  - Claimed: #fff3cd bg, #856404 text
  - Complete: #e9ecef bg, #495057 text
- **Priority Colors**:
  - High: #dc3545 (red)
  - Medium: #f0ad4e (orange)
  - Low: #28a745 (green)

#### Design Principles
1. **Minimalist**: Clean, uncluttered interface
2. **Consistent**: Unified spacing, typography, and colors
3. **Professional**: Enterprise-appropriate aesthetics
4. **Accessible**: High contrast, clear hierarchy
5. **Responsive**: Mobile-first design approach

#### Component Styling
- **Cards**: White background, subtle border, 10px radius
- **Buttons**: 8px padding, 6px radius, hover transforms
- **Forms**: 6px radius inputs with focus shadows
- **Tables**: Alternating row colors, uppercase headers
- **Modals**: 12px radius, backdrop shadow

### Admin User Management Portal

#### Overview
The admin user management portal allows administrators to view, edit, and delete user profiles with comprehensive filtering and search capabilities.

#### Features
- **User List**: Paginated table showing all users with key information
- **Filtering**: Search by name/email, filter by role and team
- **Edit Users**: Modal form to update user details including:
  - Name, role, team, managed team (for managers)
  - Skills (for developers/citizen developers)
  - Email verification status
- **Delete Users**: Remove users with cascading deletion of related data
- **Statistics**: Shows submitted and claimed idea counts per user

#### Known Issues and Fixes (Fixed in commit b589163)
- **Null Handling**: JavaScript now properly handles users with null names or roles
- **Search Filter**: Updated to handle null values gracefully, checking both name and email
- **Role Display**: Shows "Not Set" for users without roles instead of crashing
- **Edit Form**: Defaults to 'idea_submitter' role for users without roles
- **Skills Array**: Ensures skills array is never null when populating checkboxes

#### Implementation Details
- Template: `/templates/admin/users.html`
- API Endpoints:
  - `GET /api/admin/users` - List all users with statistics
  - `PUT /api/admin/users/<email>` - Update user profile
  - `DELETE /api/admin/users/<email>` - Delete user and related data
- Pagination: 20 users per page with navigation controls
- Real-time filtering without page reload