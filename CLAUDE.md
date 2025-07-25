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

#### Bounty System
- **Non-monetary bounties**: Text description field for recognition/perks
- **Monetary bounties**: Optional checkbox system with expense tracking
  - Checkbox for "This idea has a monetary bounty"
  - If checked, shows "Will be expensed" option
  - If expensed, shows amount input field ($)
  - Amounts over $50 require manager/admin approval
  - Creates notifications for approval workflow
- **Database**: Separate `bounties` table tracks monetary details
  - `is_monetary`, `is_expensed`, `amount`, `requires_approval`
  - `is_approved`, `approved_by`, `approved_at` for approval tracking

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
**IMPORTANT**: All models now use UUID (Universally Unique Identifier) primary keys instead of integer IDs.
- **Database**: `posting_board_uuid.db` (migrated from `posting_board.db`)
- **Primary Keys**: All tables use 36-character UUID strings as primary keys
- **Foreign Keys**: All relationships use UUID references (e.g., `idea_uuid`, `team_uuid`, `skill_uuid`)

**Core Models**:
- **Idea**: Main entity with UUID primary key, title, description, priority, size, status, bounty (text), and assignment fields
- **Skill**: Many-to-many relationship with ideas and users (UUID primary key)
- **Team**: Stores team names with approval status (UUID primary key, predefined teams are auto-approved)
- **Claim**: Tracks who claimed which idea using `idea_uuid` foreign key (created after approvals)
- **ClaimApproval**: Tracks claim requests requiring dual approval before claims are created
- **UserProfile**: Stores user email (primary key), name, verification status, role, `team_uuid`, `managed_team_uuid`, and skills
- **VerificationCode**: Tracks email verification codes with expiry and rate limiting (UUID primary key)
- **ManagerRequest**: Tracks requests from users to manage teams, requiring admin approval (UUID primary key)
- **Bounty**: Tracks monetary bounty details for ideas using `idea_uuid` foreign key
- **Notification**: Stores user notifications for various events including bounty approvals (UUID primary key)

**SDLC Models** (all with UUID primary keys):
- **StatusHistory**: Tracks all status and sub-status changes
- **IdeaComment**: Threaded discussions on ideas
- **IdeaActivity**: Activity feed tracking all changes
- **IdeaExternalLink**: External resources linked to ideas
- **IdeaStageData**: Stage-specific data for development phases

**Enums**: PriorityLevel, IdeaSize, IdeaStatus, SubStatus, ActivityType, ExternalLinkType

### Flask-Specific Features

#### UUID Migration (July 2025)
The entire application has been migrated from integer IDs to UUIDs for enhanced security and scalability:
- **Backward Compatibility**: All API endpoints return UUIDs in the `id` field for client compatibility
- **UUID Validation**: All endpoints validate UUID format before processing
- **Session Storage**: Session variables now use `_uuid` suffix (e.g., `user_managed_team_uuid`)
- **No Integer IDs**: The codebase no longer uses or accepts integer IDs anywhere

#### API Endpoints
- `/api/ideas` - Get filtered ideas list
- `/api/my-ideas` - Get user's submitted and claimed ideas (requires authentication)
- `/api/skills` - Get all available skills
- `/api/teams` - Get teams (all for admin, approved only for others)
- `/api/teams/<uuid>/members` - Get team members (manager only for their team)
- `/api/team-stats` - Get comprehensive team statistics (manager only)
- `/api/admin/stats` - Get dashboard statistics
- `/api/admin/team-stats` - Get team statistics for admins (all teams or specific team)
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
- **SVG GANTT Chart**: Interactive timeline visualization
  - `svg-gantt.js`: Custom SVG rendering library
  - Mouse event handling for tooltips and clicks
  - Dynamic phase calculations based on idea metadata
  - PNG export functionality via Canvas conversion

#### My Ideas Page (`/my-ideas`)
- **Personal Ideas Only**: Shows only ideas submitted or claimed by the current user
- **Statistics**: Four cards showing Submitted, Claimed by Me, Open, and Complete counts
- **Pending Approvals**: Section for idea owners to approve/deny claim requests
- **Visual Indicators**: Color-coded borders for submitted (green), claimed (blue), or both
- **Relationship Badges**: Clear labels showing user's relationship to each idea
- **Authentication Required**: Must be logged in with verified email

#### My Team Page (`/my-team`)
- **Access Control**: Only visible to managers and admins in navigation
- **Team Performance Dashboard**: Comprehensive team metrics and KPIs
  - Team overview stats: members, submissions, claims, completion rate, pending approvals
  - Recent activity tracking (last 30 days)
  - Visual charts for submitted and claimed ideas analysis
  - **Team skills distribution** chart showing current team capabilities
  - **Skills needed for team ideas** chart with gap highlighting:
    - Shows skills required by ideas submitted by team members
    - Highlights missing skills in light red (#ffcccc) with red border
    - Includes "Gap: Team lacks this skill" tooltip for missing skills
    - Helps identify training needs and hiring priorities
- **Team Member Management**:
  - Searchable and filterable member list
  - **Column totals row** at top showing sums for all numeric columns (bold formatting)
  - Edit team member profiles (name, role, skills)
  - View individual member activity metrics
  - Managers can only edit developers/citizen developers, not other managers
- **Admin Features**:
  - Team selector dropdown to view any team's data
  - All teams overview table when no team selected
  - Full access to all team analytics
- **API Endpoints**:
  - `GET /api/team/members/<email>` - Get team member details
  - `PUT /api/team/members/<email>` - Update team member profile
- **Recent Updates**:
  - Added skills gap analysis chart
  - Removed team claims pie chart (data still in table)
  - Added totals row to team members table

#### Admin Features
- Password authentication (password: "2929arch")
- Dashboard with charts and statistics
- **Idea Management**: Advanced management interface with modal editing
  - Shows ALL ideas (not just open ones) 
  - Comprehensive filtering by title/description, priority, status, size, and team
  - Modal-based editing with idea analytics section
  - Edit all fields including description, reward, and skills
  - Unclaim ideas to reset status to open
  - Delete ideas with confirmation
  - Pagination with 20 items per page
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
- **Browse Ideas Cards**:
  - Team name displayed below "Submitted by" in footer
  - Priority and Size badges styled like status badges with background colors
  - Priority badges (Traffic Light Convention):
    - High: #fce4e4 background, #cc0000 text (urgent/critical)
    - Medium: #fff4e5 background, #d94b00 text (moderate urgency)
    - Low: #e8f5e8 background, #2e7d2e text (can wait)
  - Size badges (Cool-to-Warm Gradient):
    - Small: #e0f7fa background, #00796b text (quick task)
    - Medium: #e3f2fd background, #1565c0 text (moderate effort)
    - Large: #ede7f6 background, #5e35b1 text (significant effort)
    - Extra Large: #fce4ec background, #c2185b text (major undertaking)
  - Chart colors refined for consistency:
    - Size: small=#26a69a, medium=#42a5f5, large=#7e57c2, extra_large=#ec407a
  - Truncated descriptions show full text on mouseover via title attribute with pointer cursor

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

### Development Sub-Status Tracking
Once an idea is claimed and approved, it enters the development lifecycle with detailed sub-status tracking:

#### Sub-Status Options
- **planning**: Initial planning and requirements gathering (10% progress)
- **in_development**: Active development work (30% progress)
- **testing**: QA and testing phase (60% progress)
- **awaiting_deployment**: Ready for deployment (80% progress)
- **deployed**: Deployed to production (90% progress)
- **verified**: Fully verified and complete (100% progress)
- **on_hold**: Temporarily paused (maintains current progress)
- **blocked**: Blocked by dependencies or issues (maintains current progress)
- **cancelled**: Development cancelled (0% progress)
- **rolled_back**: Deployment rolled back (0% progress)

#### Features
- **Progress Tracking**: Visual progress bar showing 0-100% completion
- **Status Updates**: Authorized users (claimer, admin, manager) can update status
- **Blocked Reasons**: Required explanation when marking as blocked/on hold
- **Expected Completion**: Optional target completion date
- **Status History**: Full timeline of all status changes with:
  - Who made the change and when
  - Duration in previous status
  - Optional comments
  - Visual timeline display
- **Notifications**: Automatic notifications sent to:
  - Idea owner when status changes
  - Manager when ideas are blocked/cancelled
  - All parties when idea is verified/complete

#### UI Components
- **Idea Detail Page**: Shows current sub-status with progress bar and update controls
- **Browse Ideas**: Displays sub-status badge and progress percentage for claimed ideas
- **My Ideas**: Shows sub-status information for all personal ideas
- **Status Timeline**: Visual representation of status changes over time

#### API Endpoints
- `PUT /api/ideas/<id>/sub-status`: Update sub-status with validation and permissions
  - Request body: `{sub_status, progress_percentage, blocked_reason, expected_completion, comment}`
  - Validates status transitions and permissions
  - Creates status history record
  - Sends notifications

### Manager Capabilities
- **Team Oversight**: View all team members' submitted and claimed ideas
- **Claim Approvals**: Approve/deny team members' claim requests
- **Idea Assignment**: Assign open ideas to specific team members
- **Assignment Tracking**: Ideas track who assigned them and when
- **Team Performance Dashboard**: Comprehensive KPIs and analytics for team activity
  - Overview metrics: team size, submissions, claims, completion rate, pending approvals
  - Visual charts split by submitted vs claimed:
    - Priority distribution (separate charts for submitted and claimed)
    - Status distribution (separate charts for submitted and claimed)
    - Size distribution (separate charts for submitted and claimed)
    - Team skills (actual team member capabilities)
    - Team claims breakdown (own team vs other teams)
  - Team member activity table with individual performance metrics including:
    - Ideas submitted, total claimed, claims for own team, claims for other teams
    - Total completed, total activity
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
- `GET /api/my-ideas` - Get user's personal submitted and claimed ideas (requires authentication)
  - Returns: Object with:
    - `ideas`: Array of personal ideas with `relationship` field (submitted/claimed/both)
    - `pending_claims`: User's pending claim requests
    - `pending_approvals`: Claim requests awaiting user's approval as idea owner
- `GET /api/skills` - List all available skills
- `GET /api/teams` - List teams (all with approval status for admin, approved only for others)
- `GET /api/teams/<id>/members` - Get team members (manager only for their team)
- `GET /api/team/members/<email>` - Get specific team member details (manager only for their team)
- `PUT /api/team/members/<email>` - Update team member profile (manager only)
  - Can update: name, role (developer/citizen_developer), skills
  - Cannot edit other managers
- `GET /api/team-stats` - Get comprehensive team statistics (manager only)
  - Returns overview metrics, breakdowns by priority/status/size/skills
  - Includes team member activity and recent activity (30 days)
  - **skills_needed**: Array of skills required by team's submitted ideas with counts
- `POST /idea/<id>/claim` - Request to claim an idea (requires complete profile)
  - Creates ClaimApproval record requiring dual approval
  - Only developers and citizen developers can claim
- `GET /api/claim-approvals/pending` - Get pending claim approvals
- `POST /api/claim-approvals/<id>/approve` - Approve a claim request
- `POST /api/claim-approvals/<id>/deny` - Deny a claim request
- `POST /api/ideas/<id>/assign` - Assign idea to team member (manager only)

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- `GET /api/admin/team-stats` - Get team statistics for admins
  - Query params: `team_id` (optional - if not provided, returns all teams overview)
  - Returns comprehensive team analytics including:
    - Team overview metrics (members, submissions, claims, completion rate)
    - Recent activity (last 30 days)
    - Breakdowns by priority/status/size split by submitted vs claimed
    - Team skills distribution
    - Team claims breakdown (own team vs other teams)
    - Individual team member activity metrics
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

## Notification System

### Overview
The application includes a comprehensive notification system that alerts users about important events and changes related to their ideas and team activities.

### Notification Types
- **Claim Requests**: When someone wants to claim your idea
- **Claim Approvals/Denials**: When your claim request is approved or denied
- **Status Changes**: When idea status changes (open → claimed → complete)
- **Assignments**: When a manager assigns an idea to you
- **Team Updates**: When new members join your team (managers only)
- **Manager Approvals**: When your request to manage a team is approved/denied

### User Interface
- **Notification Bell**: Shows unread notification count in My Ideas page
- **Notification Panel**: Sliding panel with all notifications
- **Auto-refresh**: Updates every 30 seconds
- **Mark as Read**: Click notifications to mark them as read
- **Time Display**: Shows relative time (e.g., "5 minutes ago")

### Admin Notifications
- **Dashboard Alert**: Yellow notification box on admin dashboard
- **Navigation Badges**: Shows pending counts next to menu items
- **Aggregated View**: All pending requests in one place
- **Quick Actions**: Direct links to approval pages

### API Endpoints
- `GET /api/user/notifications` - Get user notifications (requires authentication)
  - Returns unread notifications and recent read notifications (last 7 days)
- `GET /api/admin/notifications` - Get admin notifications (admin only)
  - Returns counts of pending manager requests, team approvals, and claim approvals
- `POST /api/user/notifications/<id>/read` - Mark notification as read

### Database Schema
```python
class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_email = Column(String(120), nullable=False, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    idea_id = Column(Integer, ForeignKey('ideas.id'))
    related_user_email = Column(String(120))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
```

### Implementation Details
- Notifications are created automatically when relevant events occur
- Unread notifications are highlighted with a blue background
- Read notifications are shown with a gray background
- Notifications include links to related ideas when applicable
- System automatically notifies all relevant parties (submitters, claimers, managers)

## Version Indicator

### Overview
A dynamic version indicator appears in the bottom right corner of all pages showing the git commit hash (e.g., "v.446f372").

### Features
- **Dynamic Detection**: Automatically detects current git commit
- **Docker Support**: Passes commit hash via build args when git not available
- **Hidden Admin Access**: Clicking the version indicator navigates to admin portal
- **Subtle Design**: Low opacity (0.6) with hover effect to avoid drawing attention

### Implementation
- Flask context processor injects `git_commit` into all templates
- `get_git_revision_short_hash()` in app.py handles detection
- Falls back to "v.unknown" when git unavailable
- Docker build args pass commit at build time: `GIT_COMMIT=$(git rev-parse --short HEAD)`

## Enhanced SDLC Tracking

### Overview
The application now includes comprehensive SDLC (Software Development Life Cycle) tracking features inspired by tools like JIRA and MIRO. These features enable detailed tracking of idea progress through development stages with comments, external links, activity feeds, and GANTT charts.

### Sub-Status Tracking
Ideas in "claimed" status can now have detailed sub-statuses:
- **Development Stages**: planning, in_development, testing, awaiting_deployment, deployed, verified
- **Special States**: on_hold, blocked, cancelled, rolled_back
- **Progress Tracking**: 0-100% completion with visual progress bars
- **Blocked Reasons**: Required explanation when marking as blocked/on_hold
- **Expected Completion**: Target dates for delivery

### Development Progress Section
The idea detail page shows comprehensive development progress when an idea is claimed:
- **Status Badge**: Current sub-status with color coding
- **Progress Percentage**: Manual or automatic based on phase
- **GANTT Chart**: Interactive timeline visualization
- **Last Updated**: Timestamp and user who made the update
- **Action Buttons**: Update Status, Export Timeline, Customize Timeline (all in one row)

### GANTT Chart Implementation
- **SVG Technology**: Built with Scalable Vector Graphics for full interactivity
- **Sequential Phases**: Each phase on its own row, not stacked
- **Realistic Overlaps**: Phases can overlap (e.g., testing starts before development ends)
- **Progress Coloring**: Green (complete), Yellow (in progress), Blue (planned), Red (blocked)
- **Interactive Features**: 
  - Hover tooltips with phase details, dates, duration, and linked items count
  - Click to open stage-specific data modal
  - Today marker with dashed line
  - Progress indicator line
- **Synchronization**: Progress updates automatically sync with GANTT visualization
- **Technical Architecture**:
  - `SVGGanttChart` class in `/static/js/svg-gantt.js`
  - Dynamic SVG element creation with proper namespacing
  - Event delegation for performance with many phases
  - Automatic date calculations based on idea size and timeline

### Stage-Specific Fields
The Update Status modal dynamically shows fields based on the selected stage:

**Planning Fields**:
- Requirements Document URL
- Design Specification URL

**Development Fields**:
- Repository URL
- Branch Name
- Pull Request URLs (multi-line)

**Testing Fields**:
- Test Plan URL
- Test Results Summary
- Defects Found (number)

**Deployment Fields**:
- Deployment Guide URL
- Release Notes
- Target Environment (dropdown)

**Verification Fields**:
- Verified By (name)
- Performance Metrics
- Sign-off Notes

### Tabbed Interface
The idea detail page features a tabbed interface with:
1. **Overview Tab**: Main idea details and development progress
2. **Comments Tab**: Discussion thread with internal notes option
   - Automatic activity tracking for all comments

3. **Links & Resources Tab**:
   - External link management for related resources
   - Support for: repositories, pull requests, ADO work items, documentation, GANTT charts, test results
   - Categorized display with icons and metadata

4. **Activity Tab**:
   - JIRA-style activity feed showing all changes
   - Visual timeline with action icons
   - Tracks: status changes, comments, links, progress updates, assignments

5. **Status History Tab**:
   - Complete audit trail of all status changes
   - Duration tracking between status changes
   - Change comments and user attribution

### GANTT Chart Features
- **SVG-Based Implementation**: Interactive Scalable Vector Graphics for enhanced user experience
- **Automatic Timeline**: Based on idea size and due date
- **Phase Visualization**: Color-coded phases showing progress
  - Gray: Not started
  - Green: Completed
  - Yellow: In progress
  - Red: Blocked/delayed
- **Interactive Elements**:
  - **Hover Tooltips**: Shows phase details, start/end dates, duration, and linked items count
  - **Click Actions**: Click on any phase to open the stage-specific data modal
  - **Smooth Transitions**: Visual feedback with opacity changes on hover
- **Today Marker**: Visual indicator of current date with dashed line
- **Export Function**: Download chart as PNG image with full visual fidelity
- **Customization**: Adjust phase durations and timeline dates
- **Responsive Design**: SVG scales properly across different screen sizes

### Database Schema

#### Enhanced Idea Fields
```python
class Idea(Base):
    # ... existing fields ...
    sub_status = Column(Enum(SubStatus), nullable=True)
    sub_status_updated_at = Column(DateTime)
    sub_status_updated_by = Column(String(120))
    progress_percentage = Column(Integer, default=0)
    blocked_reason = Column(Text)
    expected_completion = Column(DateTime)
```

#### Status History
```python
class StatusHistory(Base):
    __tablename__ = 'status_history'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    from_status = Column(Enum(IdeaStatus))
    to_status = Column(Enum(IdeaStatus))
    from_sub_status = Column(Enum(SubStatus))
    to_sub_status = Column(Enum(SubStatus))
    changed_by = Column(String(120), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(Text)
    duration_minutes = Column(Integer)
```

#### Comments System
```python
class IdeaComment(Base):
    __tablename__ = 'idea_comments'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    author_email = Column(String(120), nullable=False)
    author_name = Column(String(100))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_internal = Column(Boolean, default=False)
    sub_status = Column(Enum(SubStatus))
```

#### External Links
```python
class IdeaExternalLink(Base):
    __tablename__ = 'idea_external_links'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    link_type = Column(Enum(ExternalLinkType), nullable=False)
    title = Column(String(200), nullable=False)
    url = Column(String(500), nullable=False)
    description = Column(Text)
    sub_status = Column(Enum(SubStatus))
    created_by = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### Activity Feed
```python
class IdeaActivity(Base):
    __tablename__ = 'idea_activities'
    
    id = Column(Integer, primary_key=True)
    idea_id = Column(Integer, ForeignKey('ideas.id'), nullable=False)
    activity_type = Column(Enum(ActivityType), nullable=False)
    actor_email = Column(String(120), nullable=False)
    actor_name = Column(String(100))
    description = Column(Text, nullable=False)
    activity_data = Column(Text)  # JSON for additional data
    created_at = Column(DateTime, default=datetime.utcnow)
```

### API Endpoints

#### Sub-Status Management
- `PUT /api/ideas/<id>/sub-status` - Update sub-status and progress
  ```json
  {
    "sub_status": "in_development",
    "progress_percentage": 45,
    "blocked_reason": "Waiting for API access",
    "expected_completion": "2025-08-15",
    "comment": "Started backend implementation"
  }
  ```

#### Comments
- `GET /api/ideas/<id>/comments` - Get all comments for an idea
- `POST /api/ideas/<id>/comments` - Add a new comment
  ```json
  {
    "content": "Updated the API integration",
    "is_internal": false
  }
  ```

#### External Links
- `GET /api/ideas/<id>/external-links` - Get all links for an idea
- `POST /api/ideas/<id>/external-links` - Add a new link
  ```json
  {
    "link_type": "pull_request",
    "title": "Feature implementation PR #123",
    "url": "https://github.com/org/repo/pull/123",
    "description": "Main feature implementation"
  }
  ```

#### Activity Feed
- `GET /api/ideas/<id>/activities` - Get activity feed for an idea

### Permissions
- **Sub-status Updates**: Claimer, idea owner's team manager, or admin
- **Comments**: Any authenticated user can comment
- **External Links**: Any authenticated user can add links
- **View Access**: All SDLC features visible to anyone who can view the idea

### Usage Example
1. Developer claims an idea
2. Updates sub-status to "planning" with 10% progress
3. Adds comment: "Reviewing requirements with stakeholders"
4. Links design document from SharePoint
5. Updates to "in_development" at 30% after planning complete
6. Team members track progress via GANTT chart
7. Manager reviews activity feed for updates
8. On completion, full history available for review

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
10. Email notifications (in addition to in-app notifications)

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
- **Hidden Access**: Click the version indicator (e.g., "v.446f372") in the bottom right corner of any page
- Password: `2929arch`
- After login, redirects to `/admin/dashboard`
- Note: Admin link removed from navigation bar for security

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
- **Manager Requests** (integrated into User Management): 
  - View and manage pending requests directly in user edit modal
  - Approve or deny requests while editing users
  - Remove existing managers via user management
  - Smart role changes handle manager workflow automatically
- **Admin Team Analytics** (in My Team's Ideas page):
  - View performance metrics for all teams or individual teams
  - Team selector dropdown to choose specific team
  - All teams overview table showing:
    - Team name, status, member count
    - Ideas submitted, claimed, completion rate
  - Individual team analytics matching manager view but for any team
  - Same comprehensive charts and metrics as manager dashboard
- **Email Settings**: Configure SMTP settings for verification emails
- **Notification System**: Admin dashboard displays all pending requests requiring attention

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
The admin ideas management page (`/admin/ideas`) provides a comprehensive interface for managing all ideas in the system:

#### Features
- **Complete View**: Shows ALL ideas (not just open ones) by passing empty status parameter
- **Advanced Filtering**: 
  - Search by title or description
  - Filter by priority (low, medium, high)
  - Filter by status (open, claimed, complete)
  - Filter by size (small, medium, large, extra_large)
  - Filter by team
  - Clear all filters button
- **Modal-Based Editing**: Click "Edit" to open comprehensive edit modal with:
  - Idea analytics section showing ID, dates, submitter, claims, pending approvals, assignment info
  - All fields editable: title, description, team, priority, size, status, reward, email
  - Skills selection with checkboxes for all available skills
- **Bulk Actions**: 
  - Unclaim button for claimed/complete ideas (removes all claims, resets to open)
  - Delete button with confirmation
- **Pagination**: 20 items per page with navigation controls
- **Consistent UI**: Follows same patterns as admin users management page

#### API Enhancements
The `/api/ideas/<id>` PUT endpoint now supports:
- `description`: Update idea description
- `reward`: Update reward text
- `skill_ids`: Array of skill IDs to replace current skills

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

### My Ideas and My Team Pages

#### Navigation Display
- **All Users**: "My Ideas" link in navigation
- **Managers and Admins**: Additional "My Team" link appears to the right of "My Ideas"
- **Active State**: Proper highlighting based on current page

#### My Ideas Page (`/my-ideas`)
- **Personal Focus**: Shows only ideas submitted or claimed by the authenticated user
- **Authentication Required**: Users must verify their email before accessing
- **Database Queries**: 
  - Ideas where `Idea.email == user_email` (submitted)
  - Ideas where `Claim.claimer_email == user_email` (claimed)
- **Relationship Tracking**: Each idea marked as submitted, claimed, or both
- **Pending Approvals**: Shows claim requests requiring user's approval as idea owner

#### My Team Page (`/my-team`)
- **Access Control**: Only accessible to managers and admins
- **Manager View**: Shows data for their assigned team only
- **Admin View**: Team selector to view any team or all teams overview
- **Team Analytics**: Comprehensive performance metrics and charts
- **Member Management**: Edit team member profiles (excluding other managers)

#### Key Files Modified for Split
1. **`blueprints/main.py`**:
   - Added new `/my-team` route with manager/admin access control
   - My Ideas route remains for all authenticated users

2. **`blueprints/api.py`**:
   - `/api/my-ideas` simplified to return only personal ideas
   - Removed team ideas from response
   - Added `/api/team/members/<email>` GET endpoint
   - Added `/api/team/members/<email>` PUT endpoint for member updates

3. **`templates/base.html`**:
   - Updated navigation to show "My Ideas" for all users
   - Added conditional "My Team" link for managers/admins only

4. **`templates/my_ideas.html`**:
   - Removed all team-related sections and metrics
   - Shows only personal submitted/claimed ideas
   - Simplified stats to 4 personal metrics
   - Maintains pending approvals functionality

5. **`templates/my_team.html`** (new):
   - Comprehensive team performance dashboard
   - Team member management table with search/filter
   - Modal-based member editing interface
   - Admin team selector for viewing any team
   - Interactive charts for team analytics

#### Usage
- Users must verify their email before accessing My Ideas
- Shows only ideas associated with the verified user's email
- No cross-user access allowed for security
- Data is permanently stored in database and retrieved based on authenticated session
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
3. **Cron environment Python version**: If cron has Python 3.6 or older, the flask-health-monitor.sh script will automatically search for and use a compatible Python 3.8+ version from various system locations.

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
   - Admin goes to `/admin/users` to manage all user-related tasks
   - Pending requests appear in User Analytics section of edit modal
   - Can approve or deny requests directly from user management
   - Manager requests are fully integrated into user management workflow

3. **Approval Process**:
   - **Approve**: Updates request status to `approved`, assigns `managed_team_id` to user, changes role to "manager"
   - **Deny**: Updates request status to `denied`, user must submit new request if desired
   - Admin can also remove existing managers from their teams
   - Smart role changes: editing user role in admin panel handles manager workflow automatically

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
  - **Integrated Manager Request Management**:
    - Shows pending manager requests in User Analytics section
    - Approve/Deny buttons for pending requests directly in edit modal
    - "Remove as Manager" button for existing managers
- **Delete Users**: Remove users with cascading deletion of related data
- **Statistics**: Shows submitted and claimed idea counts per user
- **Smart Role Management**:
  - Changing user to manager role with pending request auto-approves it
  - Changing user from manager role automatically clears managed team
  - Approving manager request also changes user role to "manager"

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
    - Now includes `pending_manager_request` object with request details
  - `PUT /api/admin/users/<email>` - Update user profile
    - Intelligent role change handling
    - Auto-approves pending manager requests when changing to manager role
    - Clears managed_team_id when changing from manager role
  - `DELETE /api/admin/users/<email>` - Delete user and related data
  - `POST /api/admin/manager-requests/<id>/approve` - Approve manager request
    - Also changes user role to "manager"
  - `POST /api/admin/manager-requests/<id>/deny` - Deny manager request
  - `POST /api/admin/remove-manager` - Remove manager status
    - Optional: change role with `change_role` and `new_role` parameters
- Pagination: 20 users per page with navigation controls
- Real-time filtering without page reload

### Admin Portal Styling Guidelines

#### Consistent Styling Practices
To maintain consistency across all admin pages, follow these guidelines:

1. **Use Global CSS Classes** - Never embed custom CSS in admin templates
   - Tables: Use `data-table` class, or `users-data-table` for compact user listings
   - Buttons: Use `btn`, `btn-primary`, `btn-secondary`, `btn-danger`, `btn-sm`
   - Forms: Use `form-control` for inputs and selects
   - Status indicators: Use `status-badge` with status-specific classes

2. **Modal Structure**
   ```html
   <div id="modal-id" class="modal-overlay">
       <div class="modal-content">
           <div class="modal-header">
               <h3>Modal Title</h3>
               <button class="modal-close" onclick="closeModal()">&times;</button>
           </div>
           <!-- Modal body content -->
       </div>
   </div>
   ```
   - Use `classList.add('active')` to show, `classList.remove('active')` to hide
   - Never use `style.display` directly

3. **Page Structure**
   - Title format: "Page Name - Admin - Citizen Developer Posting Board"
   - Use `{% block extra_js %}` for page-specific JavaScript
   - Navigation: Admin nav links should be consistent across all pages

4. **Form Styling**
   - Skills grid: Use inline style for consistency
   ```html
   style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; padding: 10px; background: #f8f9fa; border-radius: 4px;"
   ```
   - Checkbox labels: Wrap in flex container for proper alignment
   - Form groups: Use `.form-group` with consistent margin-bottom

5. **Status Badges**
   - Verified: `status-badge status-complete` (green)
   - Unverified: `status-badge status-pending` (amber)
   - Open: `status-badge status-open`
   - Claimed: `status-badge status-claimed`
   - Denied: `status-badge status-denied`

6. **Avoid Custom Styling**
   - If additional styling is needed, add it to `/static/css/styles.css`
   - Never add `<style>` tags in templates unless absolutely necessary
   - Use existing utility classes and design system components

7. **Testing Consistency**
   - Always compare new admin pages with existing ones (Skills, Teams)
   - Ensure hover states, transitions, and animations match
   - Verify responsive behavior at different screen sizes

### Admin User Management Table

The admin users table uses a special compact design with the `users-data-table` class:

#### Table Specifications
- **Font sizes**: 11px body text, 10px uppercase headers
- **Padding**: 6px horizontal, 4px vertical (vs standard 10px)
- **Layout**: Fixed table layout with specific column widths
- **Text overflow**: Ellipsis with tooltips for truncated content

#### Column Abbreviations
- **Headers**: Shortened with full titles in tooltips
  - "Managed Team" → "Managed"
  - "Verified" → "Status"
  - "Complete" → "Done"
  - "Pending" → "Pend"
- **Role names**: 
  - "Citizen Developer" → "CitDev"
  - "Developer" → "Dev"
  - "Manager" → "Mgr"
  - "Idea Submitter" → "Submitter"
- **Verification**: ✓ (verified) or ✗ (unverified) instead of badges
- **Dates**: MM/DD format with full date/time in tooltip

#### Tooltips
All potentially truncated fields show full content on hover:
- Name, Email, Role (full name), Team, Managed Team, Skills list

#### API Compatibility
- Teams endpoint returns direct array: `[{id, name, is_approved}, ...]`
- Skills endpoint returns direct array: `[{id, name}, ...]`
- Users endpoint returns wrapped object: `{success: true, users: [...]}`

## Recent Fixes and Updates

### UUID Migration Implementation (July 2025)
Completed full migration from integer IDs to UUIDs:
- **Database Schema**: Created new `posting_board_uuid.db` with UUID-only schema
- **Model Updates**: All models now use UUID primary keys and foreign keys
- **API Changes**: 
  - All endpoints accept and return UUIDs
  - Removed all `parseInt()` calls for ID handling
  - Fixed references from `.id` to `.uuid` in SDLC models
- **Session Updates**: Changed all session storage to use UUID field names
- **Bug Fixes**:
  - Fixed `user_skills` table query to use `user_email` instead of `user_uuid`
  - Fixed `ActivityType.status_change` → `ActivityType.status_changed`
  - Fixed external link creator lookup
  - Updated all `_id` references to `_uuid` in session and API code

### Enhanced SDLC Tracking Implementation (July 2025)
Implemented comprehensive Software Development Life Cycle tracking features:
- **Sub-Status System**: Added detailed development stages (planning, in_development, testing, etc.) with progress tracking
- **Tabbed Interface**: Redesigned idea detail page with tabs for Overview, Comments, Links, Activity, and History
- **GANTT Chart Integration**: Built-in project timeline visualization with customizable phases
- **Comments System**: Added threaded discussions with internal notes capability
- **External Links**: Implemented resource linking for repos, PRs, ADO items, documentation
- **Activity Feed**: JIRA-style activity tracking with visual timeline
- **Database Models**: Created IdeaComment, IdeaExternalLink, IdeaActivity, StatusHistory tables
- **API Endpoints**: Added /api/ideas/<id>/sub-status, /comments, /external-links, /activities
- **Permissions**: Claimers, managers, and admins can update status; all authenticated users can comment
- **Timeline Calculation**: Automatic GANTT chart generation based on idea size and due dates

### Sub-Status Implementation Fix (July 2025)
Fixed 500 error on idea detail pages when implementing sub-status tracking:
- **Issue**: Jinja2 template syntax error - list comprehensions not supported in templates
- **Fix**: Replaced list comprehension with proper Jinja2 loop and variable assignment
- **Database Updates**: 
  - Created status_history table for tracking all status changes
  - Added sub_status columns to ideas table (sub_status, progress_percentage, blocked_reason, etc.)
- **Template Fix**: Changed from `idea.status_history` to `status_history_json` to properly serialize data
- **Note**: Sub-status features only display when idea has status='claimed' AND sub_status is not null

### Browse Ideas Cards Updates (July 2025)
Enhanced the browse ideas cards layout and styling for better consistency and usability:
- **Layout Changes**:
  - Moved team name from meta section to footer section below "Submitted by"
  - Stacked priority and size badges vertically instead of side-by-side
  - Team always appears on its own line below submitter information
- **Professional Color Scheme**:
  - Priority and size badges now styled like status badges with background colors
  - Priority uses traffic light convention for intuitive urgency understanding
  - Size uses cool-to-warm gradient showing increasing effort/scope
  - Chart colors refined for better visual harmony while maintaining distinction
- **Badge Colors**:
  - Priority: High (red tones), Medium (orange tones), Low (green tones)
  - Size: Small (teal), Medium (blue), Large (purple), Extra Large (pink)
- **Description Tooltips**: Added mouseover tooltips for truncated descriptions
- **Files Updated**:
  - `static/js/home.js`: Restructured card layout, stacked badges, implemented tooltips
  - `static/css/styles.css`: Added background colors for priority/size badges
  - `templates/my_team.html`: Updated chart colors for consistency
- **Visual Consistency**: All components now use the same refined color palette

### Team Request Notification Fix (July 2025)
Fixed missing notifications when users submit custom team requests:
- **Problem**: Admin portal showed notification banner but no actual notification in dashboard or bell
- **Root Cause**: No notification was created when users submitted custom teams
- **Solution**: 
  - Added notification creation in auth.py when custom teams are created
  - Updated user notifications endpoint to include system notifications (admin@system.local) for admins
  - Added team approval notifications sent to all team members when admin approves
- **Impact**: Admins now receive proper notifications for team requests in both dashboard and bell icon

### Manager Integration in User Management (July 2025)
Integrated manager request workflow into admin user management:
- **UI Enhancement**: Added pending manager request section in user edit modal
- **Smart Role Changes**: 
  - Approving manager request also changes user role to "manager"
  - Changing role from manager automatically clears managed team
  - Changing role to manager with pending request auto-approves it
- **API Updates**: 
  - `GET /api/admin/users` now includes pending manager request details
  - `PUT /api/admin/users/<email>` handles role changes intelligently
  - Manager approval endpoint also updates user role
- **Streamlined Workflow**: Admins can manage everything from one interface
- **Deprecated**: Removed separate `/admin/manager-requests` page in favor of integrated approach

### My Team Page Data Display Fix (July 2025)
Fixed missing data and charts on the My Team page:
- **API Response Mismatch**: Updated JavaScript to use correct field names from API (`total_members` instead of `member_count`, etc.)
- **Chart Data Paths**: Fixed nested data structure access (`teamStats.breakdowns.submitted_status` instead of `teamStats.submitted_by_status`)
- **Member Data**: Added role and skills fields to member activity API response
- **Team Ideas Section**: Replaced broken loader with link to Browse Ideas page

### Admin Team Member Edit Access (July 2025)
Fixed admin access to team member editing:
- **API Authorization**: Updated `/api/team/members/<email>` endpoints to check for both manager role and admin access
- **Teams Endpoint**: Modified `/api/teams/<team_id>/members` to allow admin access
- **Session Checks**: Added `is_admin` session check alongside manager role verification

### JavaScript Utils Consolidation (July 2025)
Fixed duplicate utils definitions causing conflicts:
- **Removed Duplicate**: Deleted local utils object from `my_team.html` template
- **Global Utils**: All pages now use the shared utils from `/static/js/main.js`
- **Date Formatting**: Consistent date formatting across all pages using timezone-aware parser
- **HTML Escaping**: Unified XSS protection through single escapeHtml implementation

### My Ideas Page Formatting Fix (July 2025)
Fixed empty state and error message formatting:
- **Empty State**: Properly styled "No ideas found" message with grid-spanning div and centered layout
- **Error Messages**: Consistent styling for error states with red color indicator
- **Grid Layout**: Messages now properly integrate with CSS grid structure

### All Teams Overview Data Fix (July 2025)
Fixed "All Teams (Overview)" selection returning no data in admin My Team page:
- **API Response Structure**: Changed from `{teams: ...}` to `{teams_overview: ...}` to match frontend expectations
- **Field Names**: Updated API to return consistent field names (`member_count`, `submitted_count`, `claimed_count`)
- **Display Control**: Added logic to hide individual team stats cards when viewing all teams overview

### Team-Based Submit Form Enhancement (July 2025)
Implemented automatic team assignment for users submitting ideas:
- **Pre-filled Teams**: Users with assigned teams see their team pre-filled and read-only on submit form
- **Disabled Selection**: Team dropdown and custom input are hidden for users with assigned teams
- **Session Integration**: Submit route now passes `user_team` from session to template
- **Visual Indicators**: Read-only fields have gray background with explanatory text
- **Conditional JavaScript**: Event listeners only attach when team selection is available

### Skill Persistence Clarification (July 2025)
Updated messaging about skill persistence on submit form:
- **Clear Messaging**: Skills field now states "Skills are required for this idea only and will not be saved to your profile"
- **Team-Only Persistence**: Moved "Clear saved data" link to team field only
- **Correct Behavior**: Verified that idea skills and user profile skills remain separate as intended

### Chart Color Consistency (July 2025)
Implemented consistent color mapping across all charts in My Team page:
- **Structured Color System**: Created category-based color mappings for status, priority, size, skills, and team claims
- **Context-Aware Colors**: "medium" shows as orange in priority charts and blue in size charts
- **Auto-Detection**: Chart type is automatically determined based on label content
- **Visual Consistency**: Same categories now use identical colors across all chart types
- **Color Scheme**:
  - Status: open=green, claimed=yellow, complete=gray
  - Priority: high=red, medium=orange, low=green  
  - Size: small=teal, medium=blue, large=purple, extra_large=pink
  - Team Claims: Own Team=blue, Other Teams=orange
  - Skills: Distinct colors for each skill type (SQL=blue, Python=brown, Java=pink, etc.)

### Team Skills Chart Fix (July 2025)
Fixed data processing error in team skills chart:
- **API Data Format**: API returns `team_skills` as array of objects with `skill` and `count` properties
- **Frontend Processing**: Updated to correctly extract skill names and counts from API response
- **Color Assignment**: Added 'skills' category to COLOR_MAPPINGS with distinct colors for each skill
- **Chart Type Parameter**: Updated createBarChart to accept chartType parameter for proper color mapping

### My Team Role Display Fix (July 2025)
Fixed roles not displaying correctly in My Team users table:
- **Issue**: Only "Developer" and "Citizen Developer" roles were shown, managers and idea submitters displayed as "Developer"
- **Fix**: Updated role display logic to handle all four role types: Manager, Idea Submitter, Citizen Developer, Developer
- **Filter Update**: Added all role options to the role filter dropdown
- **API**: Confirmed API was already returning correct role data, issue was only in frontend display

### My Team Skills Gap Analysis Feature (July 2025)
Added skills gap analysis to help teams identify training and hiring needs:
- **New Chart**: "Skills Needed for Team Ideas" positioned next to "My Team's Skills" chart
- **API Enhancement**: Added `skills_needed` field to team stats API response
  - Aggregates all skills required by ideas submitted by team members
  - Returns top 10 most needed skills with counts
- **Gap Highlighting**: Skills the team lacks are highlighted in light red (#ffcccc) with red border
- **Interactive Tooltips**: Shows "Gap: Team lacks this skill" for missing skills
- **Use Case**: Helps managers identify skill gaps for training or recruitment planning

### My Team UI Improvements (July 2025)
Streamlined the My Team page interface:
- **Removed**: Team Claims pie chart (Own vs Other Teams)
  - Information still available in team members table columns
- **Added**: Column totals row at top of team members table
  - Bold "TOTALS" label
  - Sums for all numeric columns (submitted, claimed, completed, etc.)
  - Maintains column background colors (light blue/orange)
  - Updates dynamically with filters

### Team Request Notification Fix (July 2025)
Fixed missing notifications when users submit custom team requests:
- **Issue**: Admin dashboard showed pending teams but no notifications were created, bell icon didn't show team requests
- **Fix**: 
  - Create notification for `admin@system.local` when new team is created with `is_approved=false`
  - Update user notifications endpoint to include system notifications for admins
  - Create notifications for team members when their team is approved
- **Implementation**:
  - New team creation triggers admin notification in `auth.py`
  - Admin bell icon now shows team approval requests via system notifications
  - Team approval sends notifications to all team members
- **Result**: Admins are properly notified of new team requests and users are notified when their teams are approved

### Profile Update Error Fix (December 2024)
Fixed "Failed to update profile" error when saving profile changes:
- **SQLAlchemy Compatibility**: Replaced deprecated `db.query(Model).get(id)` with `db.query(Model).filter_by(id=id).first()`
- **Error Handling**: Added proper exception handling in profile update endpoint to catch and report database errors
- **Transaction Management**: Added explicit rollback on errors to prevent database transaction issues

### Profile Page Styling Consistency (December 2024)
Fixed button sizing and form styling inconsistencies on the My Profile page:
- **Button Uniformity**: Removed custom button styles that were overriding global design system
- **Form Labels**: Added consistent `form-label` class with uppercase styling to all form fields
- **Alert Styling**: Updated alerts to match global design system with proper colors and borders
- **Badge Updates**: Changed badges to use soft backgrounds consistent with status indicators
- **Typography**: Standardized h1 size to 1.75rem and form group spacing to 20px
- **Help Text**: Consistent 12px gray text for all help messages

### Bulk Upload User Profile Update Fix (December 2024)
Fixed "Failed to update profile" error for bulk uploaded users:
- **Root Cause**: Bulk uploaded users were marked as verified but hadn't gone through the email verification flow, so their session wasn't properly initialized
- **Session Initialization**: Added `update_session_from_db()` call in the profile route to ensure session is populated with user data
- **Enhanced Logging**: Added detailed error logging with traceback and form data to help diagnose profile update failures
- **Manager Request Fix**: Added null check for pending manager request team relationship to prevent errors
- **Python Scoping Fix**: Resolved `UnboundLocalError` in `update_user_profile` function caused by local imports shadowing module-level imports
  - Moved all model imports (`UserProfile`, `VerificationCode`, `Skill`, `Team`, `Notification`, `ManagerRequest`) to top of file
  - Removed all `from models import ...` statements inside functions
  - This fixed the "cannot access local variable 'UserProfile'" error
- **Impact**: All users, including bulk uploaded ones, can now successfully update their profiles

### Admin Notification Persistence Fix (July 2025)
Fixed admin bell notifications not displaying despite being in database:
- **Problem**: Admin notifications existed in database but bell icon showed "0" with display:none
- **Root Cause**: JavaScript initialization timing issues on complex admin pages
- **Solution**: Implemented multiple initialization strategies:
  - DOMContentLoaded event listener for standard page loads
  - Immediate initialization check if DOM already loaded
  - 500ms fallback timer for general pages
  - 1000ms special fallback for admin pages with complex initialization
- **Debugging Enhancements**:
  - Added comprehensive console logging throughout notification loading process
  - Created `window.debugNotifications()` function for manual testing
  - Added debug output to API endpoint to track notification queries
- **Verification**: API correctly returns notifications, multiple initialization paths ensure bell updates

### Cache Busting Implementation (July 2025)
Added cache busting to prevent stale JavaScript and CSS files:
- **JavaScript**: Added `?v={{ range(1000, 9999) | random }}` to main.js in base.html
- **CSS**: Added same cache busting pattern to styles.css in base.html
- **Coverage**: Since all templates extend base.html, cache busting works on every page
- **Purpose**: Ensures browsers fetch fresh copies of assets after updates, preventing issues from cached files

### Admin Bell Notification Display Fix (July 2025)
Fixed admin bell notifications not displaying despite API returning correct data:
- **Problem**: Bell icon showed "0" with display:none even though API returned unread_count: 3
- **Root Cause**: Duplicate CSS definition in admin dashboard template was missing critical positioning properties
- **Solutions Implemented**:
  - Removed conflicting `.notification-badge` CSS from admin/dashboard.html that was overriding global styles
  - Enhanced JavaScript to use `!important` flags to force visibility: `display: inline-block !important`
  - Added additional 1.5s fallback specifically for admin pages to fix inline style issues
  - Implemented force reflow with `offsetHeight` to ensure browser updates
- **Debug Tools Added**:
  - `window.debugNotifications()` - Shows current state and forces reload
  - `window.fixNotificationBadge()` - Manually fixes badge visibility
- **Result**: Admin bell notifications now properly display the unread count

### Notification Click Routing Implementation (July 2025)
Implemented intelligent routing when users click on bell notifications:
- **Feature**: Clicking notifications now takes users to the relevant area based on notification type
- **Implementation**:
  - Modified notification HTML to pass notification type to click handler
  - Updated `handleNotificationClick` to route based on type
  - Added comprehensive routing logic for all notification types
- **Routing Map**:
  - `team_approval_request` → `/admin/teams` (admin team approval page)
  - `team_approved/team_denied` → `/profile` (user profile to see team status)
  - `manager_approved/manager_denied` → `/profile` (user profile to see manager status)
  - `new_manager/new_team_member` → `/my-team` (team page to see members)
  - `claim_request` → `/my-ideas` (to approve/deny claims)
  - `claim_approved/claim_denied` → `/idea/{id}` or `/my-ideas`
  - `status_change/idea_completed/assigned` → `/idea/{id}` (specific idea page)
- **Enhanced Display**: Updated `formatNotificationType` to show user-friendly labels for all types
- **Result**: Users can now click any notification to navigate directly to the relevant page

### Notification Delete Feature (July 2025)
Added ability to delete notifications for cleanliness:
- **Feature**: Clickable X button in top-right corner of each notification
- **Implementation**:
  - Added delete button to notification HTML with proper event handling
  - Created DELETE endpoint at `/api/user/notifications/<id>`
  - Implemented JavaScript handler to delete and refresh notifications
- **Styling**:
  - Delete button positioned absolutely in top-right corner
  - Gray color that turns red on hover
  - Subtle hover effects with background color change
- **Security**: Users can only delete their own notifications; admins can delete any
- **User Experience**: No confirmation dialog for smooth, quick deletion
- **Result**: Users can easily clean up their notification list by removing old or irrelevant notifications

### My Team Page Fixes (July 2025)
Fixed My Team page showing blank and team ideas not loading:
- **File Corruption Issue**: My Team page template was corrupted (reduced to 1 byte)
  - Fixed by restoring from git: `git restore backend/templates/my_team.html`
  - Re-implemented the loadTeamIdeas function
- **API Response Structure**: JavaScript expected `teamStats.teamName` but API didn't include it
  - Updated `/api/team-stats` to include `teamId` and `teamName` fields
  - Updated `/api/admin/team-stats` to use consistent field names
  - Team ideas section now properly loads ideas filtered by team name
- **Card Layout Update**: Updated `createIdeaCard` function to match Browse Ideas modern layout
  - Stacked priority/size badges
  - Description tooltips for truncated text
  - Consistent styling with rest of application
- **Team Ideas Filtering**: Fixed issue where team ideas showed all ideas instead of team-specific
  - Added missing `benefactor_team` filter to `/api/ideas` endpoint
  - API now properly filters when `?benefactor_team=TeamName` parameter is provided
  - Both admin and manager views now show only the selected team's ideas
- **Team Ideas Styling**: Updated to match Browse Ideas page exactly
  - Implemented identical card structure with idea-header containing title and status badge
  - Added skills tags display
  - Included bounty field display (was previously showing as "reward")
  - Added clickable cards with View Details link
  - Consistent hover effects and interactions

### Bounty System Implementation (July 2025)
Added comprehensive monetary bounty tracking system:
- **Database Changes**: Added `Bounty` model to track monetary bounties with approval workflow
- **UI Enhancement**: Added monetary bounty section to submit form with:
  - "Is monetary?" checkbox
  - "Is expensed?" checkbox (shown when monetary is checked)
  - Amount input field with $ formatting (shown when expensed is checked)
  - Automatic notification for amounts over $50 requiring manager/admin approval
- **Approval Workflow**: Bounties over $50 create notifications for managers and admins
- **Terminology Update**: Replaced all references to "reward" with "bounty" throughout codebase
  - Updated database column from `reward` to `bounty`
  - Changed all UI labels and API responses
  - Modified CSV templates and bulk upload functionality

### Skills Gap Analysis for Teams (July 2025)
Enhanced My Team page with skills gap visualization:
- **Skills Needed Chart**: Added chart showing skills required by team's submitted ideas
- **Gap Highlighting**: Skills the team lacks are highlighted in light red (#ffcccc)
- **Visual Comparison**: Side-by-side display with team's actual skills for easy gap identification
- **API Enhancement**: Added `skills_needed` field to team-stats endpoint

### Team Performance Enhancements (July 2025)
- **Removed Redundancy**: Removed team claims pie chart from My Team page (data available in table)
- **Column Totals**: Added bold totals row at top of team members table for quick summaries

### Interactive SVG GANTT Implementation (July 2025)
Replaced Canvas-based GANTT chart with interactive SVG implementation:
- **Technology Migration**: Converted from HTML5 Canvas to SVG for enhanced interactivity
- **Interactive Features**:
  - Hover tooltips displaying phase name, dates, duration, and progress
  - Shows count of linked items (comments, external links) when hovering over phases
  - Click on phases to open stage-specific data modal with relevant fields
- **Visual Consistency**: Maintained exact visual design from Canvas implementation
- **Export Functionality**: SVG to PNG export preserves full chart quality
- **Implementation Details**:
  - Created `svg-gantt.js` module with SVGGanttChart class
  - Uses SVG groups and rects for phase rendering
  - Event delegation for efficient mouse interaction
  - Tooltip positioning adjusts to prevent edge overflow
- **Browser Compatibility**: Works in all modern browsers supporting SVG
- **Performance**: Lightweight implementation with no external dependencies