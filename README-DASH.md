# Citizen Developer Posting Board - Dash Version

This is a Dash (Python) implementation of the Citizen Developer Posting Board, converted from the original React/Flask architecture.

## Overview

The application has been completely rebuilt using Plotly Dash, providing:
- Single Python codebase (no separate frontend/backend)
- Server-side rendering with interactive components
- Built-in session management for admin authentication
- Simplified deployment with fewer moving parts

## Key Changes from React/Flask Version

### Architecture
- **Unified Application**: Single Dash app instead of separate React frontend and Flask API
- **Page-based Routing**: Uses Dash Pages for multi-page navigation
- **Server-side State**: Session management handled by Flask (which Dash runs on)
- **No API Endpoints**: Direct database queries in callbacks instead of REST API

### Features Maintained
- Browse and filter ideas by skill, priority, and status
- Submit new ideas with skill requirements
- Claim ideas with contact information
- Admin portal with password protection (password: "2929arch")
- Admin features: manage ideas and skills

### UI Components
- **DataTable**: For admin idea management with inline editing
- **Dropdowns**: For filtering and form inputs  
- **Modal-like Overlays**: Custom implementation for claim dialog
- **Responsive Design**: CSS Grid and Flexbox layouts

## Project Structure

```
backend/
├── dash_app.py          # Main Dash application
├── pages/               # Dash pages
│   ├── home.py         # Browse ideas (main page)
│   ├── submit.py       # Submit new idea form
│   ├── idea_detail.py  # Individual idea view
│   ├── admin_login.py  # Admin authentication
│   ├── admin_dashboard.py # Admin statistics
│   ├── admin_ideas.py  # Manage ideas
│   └── admin_skills.py # Manage skills
├── assets/             # CSS and static files
│   └── styles.css      # Application styles
├── models/             # SQLAlchemy models (unchanged)
├── database.py         # Database setup (unchanged)
├── config.py          # Configuration (unchanged)
└── utils/             # Utilities (unchanged)
```

## Getting Started

### Native Development

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Initialize database:
```bash
cd backend
python database.py
```

3. Run the Dash app:
```bash
python dash_app.py
# Or use the convenience script:
./start-dash.sh
```

### Docker Development

1. Build and run with Docker Compose:
```bash
./start-dash.sh up
```

2. View logs:
```bash
./start-dash.sh logs
```

3. Stop services:
```bash
./start-dash.sh down
```

## Usage

1. **Browse Ideas**: Visit http://localhost:5000
2. **Submit Idea**: Click "Submit Idea" in navigation
3. **View Details**: Click on any idea card
4. **Claim Idea**: Click "Claim This Idea" on detail page
5. **Admin Access**: Navigate to /admin (password: "2929arch")

## Development Notes

### Callbacks
- Callbacks handle all interactivity
- Use `prevent_initial_call=True` to avoid unnecessary calls
- Pattern-matching callbacks for dynamic components

### State Management
- Component state managed through callbacks
- Session state for authentication
- dcc.Store for client-side storage where needed

### Styling
- Custom CSS in `assets/styles.css`
- Inline styles for component-specific styling
- Responsive design with CSS Grid and Flexbox

### Performance
- DataTable pagination for large datasets
- Interval components for auto-refresh
- Efficient callback design to minimize updates

## Deployment

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 dash_app:server
```

### Docker Production
Update `docker-compose-dash.yml` for production settings and run:
```bash
docker compose -f docker-compose-dash.yml up -d
```

## Differences from React Version

1. **No Build Step**: Python code runs directly
2. **Server-side Rendering**: Initial page load is faster
3. **Simplified State**: No Redux or Context API needed
4. **Direct Database Access**: No API layer required
5. **Built-in Sessions**: Flask sessions for authentication

## Migration Notes

- All features from React version preserved
- Database schema unchanged - existing data works
- Admin password remains the same
- Email functionality maintained

## Troubleshooting

1. **Port conflicts**: Use `./start-dash.sh down` to stop services
2. **Module errors**: Ensure virtual environment is activated
3. **Database issues**: Delete `posting_board.db` and reinitialize
4. **Callback errors**: Check browser console and terminal output

## Future Enhancements

- WebSocket support for real-time updates
- Advanced filtering with date ranges
- Export functionality for admin
- User authentication system
- File upload capabilities