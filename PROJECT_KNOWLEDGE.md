# Citizen Developer Posting Board - Project Knowledge

## Overview
A full-stack web application that serves as a posting board for citizen developer ideas, allowing users to post development needs and developers to claim and work on them.

## Architecture

### Backend (Python Flask)
- **Framework**: Flask 2.3.3 with Flask-CORS for cross-origin support
- **Database**: SQLite with SQLAlchemy ORM
- **Email**: SMTP integration for notifications (configurable)
- **API**: RESTful endpoints under `/api` prefix

### Frontend (React)
- **Framework**: React 18 with React Router for navigation
- **HTTP Client**: Axios for API communication
- **Styling**: Custom CSS with responsive design
- **State Management**: React hooks (useState, useEffect)

### Database Schema

#### Tables
1. **ideas**
   - id (Primary Key)
   - title (String, required)
   - description (Text, required)
   - email (String, required - idea owner)
   - benefactor_team (String, required)
   - size (Enum: small, medium, large, extra_large)
   - reward (String, optional)
   - needed_by (DateTime, required)
   - urgency (Enum: not_urgent, urgent, very_urgent)
   - status (Enum: open, claimed, complete)
   - date_submitted (DateTime, auto-generated)

2. **skills**
   - id (Primary Key)
   - name (String, unique)

3. **claims**
   - id (Primary Key)
   - idea_id (Foreign Key to ideas)
   - claimer_name (String, required)
   - claimer_email (String, required)
   - claimer_skills (Text, optional)
   - claimer_team (String, optional)
   - claim_date (DateTime, auto-generated)

4. **idea_skills** (Many-to-Many junction table)
   - idea_id (Foreign Key to ideas)
   - skill_id (Foreign Key to skills)

## API Endpoints

### Ideas
- `GET /api/ideas` - List all ideas
  - Query params: skill, urgency, team, status, sort_by, order
- `POST /api/ideas` - Create new idea
- `GET /api/ideas/:id` - Get specific idea details
- `POST /api/ideas/:id/claim` - Claim an idea
- `POST /api/ideas/:id/complete` - Mark idea as complete

### Skills
- `GET /api/skills` - List all available skills

### Health
- `GET /api/health` - API health check

## Key Features

### Skill Management
- 9 predefined skills loaded on initialization:
  - SQL/Databases
  - Frontend/UI - Tableau
  - Frontend/UI - Streamlit
  - Frontend/UI - Web
  - Frontend/UI - PowerBI
  - Python
  - Java
  - Platform
  - Regulatory
- Users can add custom skills when posting ideas

### Email Notifications
- Triggered when an idea is claimed
- Sends details to idea owner including:
  - Claimer's name
  - Claimer's team
  - Claimer's skills
- Configurable SMTP settings via environment variables

### Filtering & Sorting
- Filter by: skill, urgency, team, status
- Sort by: date submitted, needed by date, urgency
- Order: ascending or descending

### Status Workflow
1. **Open**: Initial state when idea is posted
2. **Claimed**: When a developer claims the idea
3. **Complete**: When the work is finished

## Frontend Components

### Main Components
1. **App.js** - Main router and layout
2. **Navigation.js** - Top navigation bar
3. **IdeaList.js** - Homepage with idea grid and filters
4. **IdeaCard.js** - Individual idea display card
5. **IdeaForm.js** - Form for posting new ideas
6. **ClaimModal.js** - Modal for claiming ideas

### Routing
- `/` - Home page with idea list
- `/new-idea` - Form to post new idea

## Configuration

### Backend Environment Variables
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string
- `MAIL_SERVER` - SMTP server address
- `MAIL_PORT` - SMTP port (default: 25)
- `MAIL_USE_TLS` - Enable TLS (true/false)
- `MAIL_USERNAME` - SMTP username
- `MAIL_PASSWORD` - SMTP password
- `MAIL_DEFAULT_SENDER` - Default sender email

### Frontend Environment Variables
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:5000/api)

## Development Setup

### Quick Start
```bash
./start-dev.sh
```

### Manual Setup
1. Backend:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python database.py  # Initialize database
   python app.py       # Start server
   ```

2. Frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Deployment

### Docker Deployment
```bash
docker compose up -d
```

### Production Considerations
1. Use production WSGI server (Gunicorn) instead of Flask dev server
2. Set secure SECRET_KEY
3. Configure proper SMTP credentials
4. Use PostgreSQL or MySQL for production database
5. Enable HTTPS
6. Set up proper CORS origins
7. Implement rate limiting
8. Add authentication/authorization if needed

## Testing

### Backend Testing
```bash
# Health check
curl http://localhost:5000/api/health

# Get skills
curl http://localhost:5000/api/skills

# Create idea
curl -X POST http://localhost:5000/api/ideas \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "description": "Test desc", ...}'
```

### Frontend Testing
- Visit http://localhost:3000
- Test idea creation flow
- Test filtering and sorting
- Test claiming process

## File Structure
```
postingboard/
├── backend/
│   ├── models/
│   │   └── __init__.py      # Database models
│   ├── routes/
│   │   ├── ideas.py         # Ideas endpoints
│   │   ├── claims.py        # Claims endpoints
│   │   └── skills.py        # Skills endpoints
│   ├── utils/
│   │   └── email.py         # Email utilities
│   ├── app.py               # Flask application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── api.js       # API client
│   │   ├── components/      # React components
│   │   ├── App.js           # Main app
│   │   └── App.css          # Styles
│   └── package.json         # Node dependencies
├── docker-compose.yml       # Docker configuration
├── start-dev.sh            # Development startup script
└── README.md               # Project documentation
```

## Common Issues & Solutions

1. **Email not sending**: Check SMTP configuration, use localhost for development
2. **CORS errors**: Ensure Flask-CORS is installed and frontend URL is correct
3. **Database not found**: Run `python database.py` to initialize
4. **Port conflicts**: Change ports in configuration files
5. **Dependencies issues**: Use virtual environment for Python, delete node_modules and reinstall for React

## Future Enhancements
- User authentication and authorization
- File attachments for ideas
- Comments/discussion on ideas
- Progress tracking for claimed ideas
- Analytics dashboard
- Notification preferences
- API rate limiting
- Search functionality
- Tags/categories for ideas