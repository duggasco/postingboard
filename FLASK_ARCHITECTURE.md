# Flask Architecture Design

## File Structure
```
backend/
├── app.py                  # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models (unchanged)
├── database.py            # Database setup (unchanged)
├── email_utils.py         # Email functionality (unchanged)
├── blueprints/
│   ├── __init__.py
│   ├── main.py           # Main routes (home, ideas, submit)
│   ├── admin.py          # Admin routes
│   └── api.py            # API endpoints for AJAX
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── home.html         # Browse ideas page
│   ├── submit.html       # Submit idea form
│   ├── my_ideas.html     # User's ideas
│   ├── idea_detail.html  # Individual idea view
│   ├── admin/
│   │   ├── login.html    # Admin login
│   │   ├── dashboard.html # Admin dashboard
│   │   ├── ideas.html    # Manage ideas
│   │   └── skills.html   # Manage skills
│   └── components/
│       ├── idea_card.html # Reusable idea card
│       └── claim_modal.html # Claim modal component
└── static/
    ├── css/
    │   └── styles.css     # Main stylesheet
    └── js/
        ├── main.js        # Common JavaScript
        ├── home.js        # Home page interactions
        ├── submit.js      # Submit form logic
        ├── admin.js       # Admin functionality
        └── claim.js       # Claim modal logic
```

## Routes Structure

### Main Blueprint (`/`)
- `GET /` - Home page with filters
- `GET /submit` - Submit idea form
- `POST /submit` - Process idea submission
- `GET /my-ideas` - User's submitted ideas
- `GET /idea/<int:idea_id>` - Individual idea detail
- `POST /idea/<int:idea_id>/claim` - Claim an idea

### Admin Blueprint (`/admin`)
- `GET /admin` - Redirect based on auth status
- `GET /admin/login` - Login page
- `POST /admin/login` - Process login
- `GET /admin/logout` - Logout
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/ideas` - Manage ideas
- `GET /admin/skills` - Manage skills

### API Blueprint (`/api`)
- `GET /api/ideas` - Get filtered ideas (JSON)
- `GET /api/skills` - Get all skills
- `POST /api/skills` - Add new skill
- `PUT /api/skills/<int:id>` - Update skill
- `DELETE /api/skills/<int:id>` - Delete skill
- `PUT /api/ideas/<int:id>` - Update idea (admin)
- `DELETE /api/ideas/<int:id>` - Delete idea (admin)
- `GET /api/stats` - Get dashboard statistics

## Template Design

### Base Template Features
- Navigation bar with active page highlighting
- Flash message support
- Meta tags and responsive viewport
- Common CSS/JS includes
- Block structure for content and scripts

### JavaScript Approach
- Vanilla JavaScript for core functionality
- AJAX calls using Fetch API
- Event delegation for dynamic content
- Form validation and error handling
- Auto-refresh using setInterval
- Modular design with separate files

### Session Management
- Flask-Session with filesystem backend
- Session variables:
  - `is_admin` - Admin authentication
  - `submitted_ideas` - List of idea IDs
  - `user_email` - Remembered email

## Key Implementation Notes

1. **Maintain Dash Functionality**: All interactive features will use JavaScript and AJAX instead of Dash callbacks

2. **Database**: Keep existing SQLAlchemy models and database structure

3. **Styling**: Reuse existing CSS with minor adjustments for Flask templates

4. **Email**: Keep existing email functionality

5. **Auto-refresh**: Implement with JavaScript setInterval on relevant pages

6. **Form Handling**: Use Flask-WTF for CSRF protection and validation

7. **Error Handling**: Proper error pages and JSON error responses for API

8. **Security**: 
   - CSRF protection on forms
   - Input validation
   - SQL injection prevention (SQLAlchemy)
   - XSS prevention (Jinja2 auto-escaping)