# Citizen Developer Posting Board

A web application for posting and claiming citizen developer ideas/projects with skill matching and reward tracking.

> **Note**: This project now has two implementations:
> - **React/Flask version** (original) - See instructions below
> - **Dash version** (Python-only) - See [README-DASH.md](README-DASH.md)

## Features

- **Post Ideas**: Submit development ideas with required skills, priority, size, and rewards
- **Skill Matching**: Tag ideas with required skills (predefined or custom)
- **Claim Ideas**: Developers can claim ideas and notify the idea owner
- **Filtering & Sorting**: Filter by skills, priority, team, status and sort by date or priority
- **Email Notifications**: Automatic email notifications when ideas are claimed
- **Status Tracking**: Track ideas through open, claimed, and complete statuses

## Tech Stack

- **Backend**: Python Flask, SQLAlchemy, SQLite
- **Frontend**: React, React Router, Axios
- **Database**: SQLite

## Setup Instructions

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Initialize database:
   ```bash
   python database.py
   ```

5. Configure environment (optional):
   Create `.env` file with:
   ```
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@example.com
   MAIL_PASSWORD=your-password
   MAIL_DEFAULT_SENDER=noreply@example.com
   ```

6. Run backend:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure API endpoint (optional):
   Create `.env` file with:
   ```
   REACT_APP_API_URL=http://localhost:5000/api
   ```

4. Run frontend:
   ```bash
   npm start
   ```

## Usage

1. Access the application at `http://localhost:3000`
2. Click "Post New Idea" to submit an idea
3. Browse ideas on the home page
4. Use filters to find relevant ideas
5. Click "Claim This Idea" to work on an idea

## Database Schema

- **Ideas**: Store idea details including title, description, team, urgency, size, reward
- **Skills**: Predefined and custom skills
- **Claims**: Track who claimed which idea
- **IdeaSkills**: Many-to-many relationship between ideas and skills

## API Endpoints

- `GET /api/ideas` - Get all ideas with optional filters
- `POST /api/ideas` - Create new idea
- `GET /api/ideas/:id` - Get specific idea
- `POST /api/ideas/:id/claim` - Claim an idea
- `POST /api/ideas/:id/complete` - Mark idea as complete
- `GET /api/skills` - Get all available skills

## Deployment

### Production Backend

1. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
   ```

2. Set environment variables for production database and email configuration

### Production Frontend

1. Build the React app:
   ```bash
   npm run build
   ```

2. Serve the build directory with a web server like Nginx or Apache

## License

MIT