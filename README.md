# Citizen Developer Posting Board

A web application for posting and claiming citizen developer ideas with skill matching, team management, and comprehensive workflow features.

## Overview

The Citizen Developer Posting Board enables teams to post development needs and allows developers to browse and claim ideas they can work on. It features a complete authentication system, approval workflows, and team management capabilities.

## Key Features

### Core Functionality
- **Post Ideas**: Submit development ideas with required skills, priority, size, and team assignment
- **Browse & Filter**: Search ideas by skills, priority, status, and team with dynamic filtering
- **Claim Ideas**: Developers can claim ideas with dual approval workflow
- **My Ideas**: Track both submitted and claimed ideas in one place
- **Email Authentication**: Secure email-based verification system (no passwords)

### Advanced Features
- **Dual Approval Workflow**: Claims require approval from both idea owner and claimer's manager
- **Team Management**: Managers can view team performance, assign ideas, and approve claims
- **Notification System**: Real-time notifications for claims, approvals, and status changes
- **Admin Portal**: Comprehensive admin dashboard for managing ideas, skills, teams, and users
- **Bulk Import**: Upload ideas and users via CSV files
- **Version Tracking**: Dynamic git commit hash display for deployment tracking

### User Roles
- **Manager**: Can submit ideas, manage team members, approve claims
- **Idea Submitter**: Can submit ideas only
- **Developer/Citizen Developer**: Can submit and claim ideas
- **Admin**: Full system access via hidden portal

## Tech Stack

- **Backend**: Flask (Python 3.8+), SQLAlchemy, SQLite
- **Frontend**: Server-side rendering with Jinja2 templates
- **Styling**: Custom CSS with modern, professional design
- **Session Management**: Flask-Session for user persistence
- **Deployment**: Docker support with docker-compose

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd postingboard

# Start with Docker
./start-flask.sh

# Access the application
open http://localhost:9094
```

### Native Installation

```bash
# Requires Python 3.8 or newer
./start-flask.sh native

# Or manually:
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Configuration

### Port Configuration
The application runs on port **9094** by default. To change:
```bash
PORT=8080 ./start-flask.sh
```

### Email Configuration
For email notifications, configure SMTP settings in the admin portal or set environment variables:
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### Proxy Configuration
For corporate environments:
```bash
HTTP_PROXY=http://proxy:8080 HTTPS_PROXY=http://proxy:8080 ./start-flask.sh
```

## User Guide

### Getting Started
1. Navigate to http://localhost:9094
2. Browse ideas on the home page
3. Click "Login" to verify your email
4. Complete your profile with role, team, and skills
5. Start submitting or claiming ideas

### For Idea Submitters
1. Click "Submit Idea" from the navigation
2. Fill in idea details including team, priority, and required skills
3. Track your submissions in "My Ideas"
4. Approve/deny claim requests from developers

### For Developers
1. Browse available ideas on the home page
2. Filter by your skills or team
3. Click "Claim This Idea" on ideas you want to work on
4. Wait for dual approval (idea owner + your manager)
5. Track your claims in "My Ideas"

### For Managers
1. Access "My Ideas" to see team performance dashboard
2. View comprehensive KPIs and team statistics
3. Approve/deny team members' claim requests
4. Assign open ideas to specific team members
5. Monitor team activity and completion rates

## Admin Access

The admin portal is accessed by clicking the version indicator (e.g., "v.446f372") in the bottom right corner of any page.

**Default Password**: `2929arch`

### Admin Features
- Dashboard with statistics and charts
- Manage ideas, skills, teams, and users
- Approve custom teams and manager requests
- Bulk upload ideas and users via CSV
- Configure email settings
- View all pending approvals

## Database Schema

### Main Tables
- **ideas**: Core idea information with status tracking
- **user_profiles**: User accounts with email verification
- **teams**: Team definitions with approval status
- **skills**: Available skills for tagging
- **claims**: Finalized idea claims
- **claim_approvals**: Pending claim requests
- **notifications**: User notification system
- **manager_requests**: Pending manager role requests

## API Documentation

### Public Endpoints
- `GET /api/ideas` - List ideas with filters
- `GET /api/my-ideas` - Get user's ideas (requires auth)
- `GET /api/skills` - List all skills
- `GET /api/teams` - List approved teams
- `POST /idea/<id>/claim` - Request to claim an idea

### Authentication Endpoints
- `POST /request-code` - Request email verification code
- `POST /verify-code` - Verify email with code
- `GET /profile` - View/update user profile
- `POST /logout` - Clear session

### Admin Endpoints
- `GET /api/admin/stats` - Dashboard statistics
- `POST /api/teams` - Create team
- `POST /api/skills` - Create skill
- `GET /api/admin/users` - Manage users
- `POST /api/admin/bulk-upload` - Import CSV data

## Development

### Project Structure
```
postingboard/
├── backend/
│   ├── app.py              # Flask application
│   ├── blueprints/         # Route handlers
│   ├── models/             # Database models
│   ├── templates/          # Jinja2 templates
│   ├── static/             # CSS and JavaScript
│   └── requirements.txt    # Python dependencies
├── docker-compose-flask.yml # Docker configuration
├── start-flask.sh          # Startup script
└── README.md              # This file
```

### Running Tests
```bash
# Currently, manual testing is recommended
# Automated tests can be added in the future
```

### Contributing
1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## Deployment

### Docker Deployment
```bash
# Build and run with Docker
docker compose -f docker-compose-flask.yml up -d --build

# View logs
docker logs postingboard-flask-app-1

# Stop services
docker compose -f docker-compose-flask.yml down
```

### Production Considerations
- Use environment variables for sensitive configuration
- Enable HTTPS with a reverse proxy (nginx/Apache)
- Configure proper email service for notifications
- Set up regular database backups
- Monitor application logs and performance

## Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find and kill process using port 9094
lsof -ti:9094 | xargs kill -9
```

**Database Not Initialized**
```bash
cd backend
python database.py
```

**Email Not Sending**
- Check SMTP configuration in admin portal
- Verify firewall allows outbound SMTP
- Check application logs for errors

**Version Indicator Shows "unknown"**
- This is normal in Docker (git not installed)
- In native mode, ensure you're in a git repository

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review application logs
3. Contact your system administrator

## License

This project is proprietary software. All rights reserved.