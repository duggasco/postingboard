# Citizen Developer Posting Board - Claude Development Notes

## Project Context
This is a full-stack web application for posting and claiming citizen developer ideas. It allows teams to post development needs with required skills, and developers to browse and claim ideas they can work on.

## Key Technical Decisions

### Backend Architecture
- **Flask over Django**: Chose Flask for its simplicity and lightweight nature, perfect for this focused API
- **SQLAlchemy ORM**: Provides good abstraction while keeping flexibility
- **SQLite for Development**: Easy setup, file-based, perfect for development and small deployments
- **Enum Types**: Used Python enums for priority, size, and status to ensure data consistency

### Frontend Architecture
- **Create React App**: Quick setup with good defaults
- **React Router**: Client-side routing for SPA experience
- **Axios over Fetch**: Better error handling and interceptor support
- **Custom CSS**: No CSS framework to keep bundle size small and have full control

### Skill Selection UI
- **Dropdown + Custom Input**: Dual approach for skill selection
  - Dropdown shows predefined skills from database (SQL/Databases, Frontend/UI variants, Python, Java, Platform, Regulatory)
  - Custom input field allows adding skills not in the predefined list
- **Tag-based Display**: Selected skills shown as removable tags with × buttons
- **Duplicate Prevention**: Dropdown filters out already-selected skills
- **Responsive Design**: Mobile-friendly with stacked layout on small screens
- **Controlled Component**: Dropdown uses `value=""` prop to ensure it always shows default text after selection
  - Avoid manually resetting select value with `e.target.value = ''` - doesn't work properly with React
  - Instead, use controlled component pattern with fixed empty value

### Idea Detail View
- **Click-to-Navigate**: All idea cards are now clickable, navigating to a detailed view
- **Visual Feedback**: Cards show hover effects (blue border, elevation) to indicate clickability
- **Comprehensive Details**: Detail page shows full description, all metadata, skills, and claim history
- **Reward Display**: Rewards are prominently displayed on both list cards and detail view
- **Default Reward Text**: Placeholder changed from "$100 gift card" to "BLK swag, lunch, etc."
- **Navigation**: Back button allows easy return to idea list
- **Claim Integration**: Claim modal accessible from detail view for open ideas

### Database Design
- **Many-to-Many Skills**: Allows flexible skill assignment without duplication
- **Separate Claims Table**: Tracks claim history and allows multiple claims if needed
- **Email in Ideas**: Stores owner contact for notifications without user management

### Admin Portal
- **Password Protection**: Admin portal accessible at `/admin` with hardcoded password "2929arch"
- **Session-Based Authentication**: Uses Flask sessions with HttpOnly cookies for security
- **Admin Dashboard**: Shows statistics (total/open/claimed/completed ideas, total skills) at `/admin/dashboard`
- **Idea Management**: 
  - Full CRUD operations on ideas
  - Inline editing with immediate save
  - Status changes via dropdown (open/claimed/complete)
  - Bulk operations support
- **Skill Management**:
  - Add new skills to the predefined list
  - Edit existing skill names
  - Delete unused skills (protected if in use)
- **API Endpoints**:
  - Authentication: `/api/auth/login`, `/api/auth/logout`, `/api/auth/check`
  - Ideas: `/api/admin/ideas/<id>` (PUT/DELETE)
  - Skills: `/api/admin/skills` (POST), `/api/admin/skills/<id>` (PUT/DELETE)
- **Security**: All admin endpoints protected with `@require_admin` decorator

## API Design Patterns

### RESTful Conventions
- GET for reading data
- POST for creating resources
- Nested routes for related resources (e.g., `/ideas/:id/claim`)
- Consistent JSON response format

### Query Parameters
- Filtering: `?skill=Python&urgency=urgent`
- Sorting: `?sort_by=date_submitted&order=desc`
- All optional with sensible defaults

## Code Organization

### Backend
```
models/      # All database models in one file for simplicity
routes/      # Separated by resource type
utils/       # Reusable utilities (email)
```

### Frontend
```
api/         # Centralized API communication
components/  # One component per file
```

## State Management
- Local component state for forms
- Props for passing data down
- Callbacks for child-to-parent communication
- No global state management (Redux/Context) to keep it simple

## Security Considerations
- Input validation on both frontend and backend
- SQL injection prevention via ORM
- CORS configuration for production
- Email addresses visible (consider in production)

## Performance Optimizations
- Database indexes on foreign keys (automatic in SQLAlchemy)
- Eager loading of relationships where needed
- Frontend bundle splitting (React default)
- Pagination ready to add when needed

## Development Workflow
1. Backend first approach - API design drives frontend
2. Test with curl before building UI
3. Incremental feature development
4. Database migrations handled by recreating in development

## Error Handling
- Backend returns consistent error format
- Frontend shows user-friendly messages
- Email failures don't break claim process
- Form validation before submission

## Styling Approach
- Mobile-first responsive design
- CSS Grid for layouts
- Flexbox for component layouts
- CSS variables for theming (easy to add)
- BEM-style naming convention

## Testing Strategy
- Manual API testing with curl
- Frontend testing through UI interaction
- Database state verification
- Would add pytest and Jest for production

## Deployment Considerations
- Environment variables for configuration
- Docker support for easy deployment
- Docker Compose for multi-container orchestration
- Nginx for static file serving
- Gunicorn for production WSGI
- Database migrations needed for production

## Docker Development
The project includes Docker support with the following structure:
- `docker-compose.yml`: Orchestrates backend and frontend services
- `backend/Dockerfile`: Flask API container
- `frontend/Dockerfile`: React app served via nginx
- `./start-dev.sh`: Unified script for both native and Docker development

Docker Compose configuration:
- Backend runs on port 5000
- Frontend runs on port 3000 (nginx on port 80 internally)
- SQLite database persisted via volume mount
- Auto-restart enabled for both services
- **Nginx reverse proxy**: Frontend nginx proxies `/api` requests to backend container
- **Relative API URLs**: Uses `/api` instead of hardcoded URLs for portability

### Docker Networking Troubleshooting
When frontend cannot reach backend ("failed to create idea" errors):
1. **Check API URL configuration**: Ensure `REACT_APP_API_URL=/api` (relative, not absolute)
2. **Verify nginx proxy config**: Check `frontend/nginx.conf` has proxy_pass to `http://backend:5000`
3. **Debug with console logging**: Add `console.log('Submitting:', formData)` in frontend
4. **Test API directly**: `curl -X POST http://localhost:3000/api/ideas -H "Content-Type: application/json" -d '{...}'`
5. **Check backend logs**: `docker logs postingboard-backend-1` for errors
6. **Common issues**:
   - Frontend sending wrong field names (e.g., `required_skills` vs `skills`)
   - Invalid enum values (e.g., `medium` vs `not_urgent`, check `models/__init__.py`)
   - Missing required fields in form data

### Docker Script Improvements (Fixed Issues)
The `start-dev.sh` script has been enhanced to handle common Docker issues:

1. **Port Checking Timeouts**: Added `timeout 2` to all `lsof` commands to prevent hanging when checking for port conflicts
2. **Container Status Display**: Shows container status after `docker compose up -d` to confirm successful startup
3. **Docker Compose Version**: Removed obsolete `version: '3.8'` field from docker-compose.yml to eliminate warnings
4. **Improved Feedback**: Added 2-second delay and status display to show containers are actually running

Common issues resolved:
- Script appearing to do nothing when running `./start-dev.sh up`
- `lsof` command hanging indefinitely when checking ports
- No visual confirmation that containers started successfully

## Future Improvements Priority
1. User authentication system
2. Pagination for large datasets
3. Real-time updates (WebSocket)
4. Advanced search functionality
5. File attachments
6. Admin interface
7. API versioning
8. Automated testing
9. CI/CD pipeline
10. Monitoring and analytics

## Common Commands

### Development
```bash
# Native development (default)
./start-dev.sh              # Start native services
./start-dev.sh native-down  # Stop native services

# Docker development
./start-dev.sh up      # Start services
./start-dev.sh down    # Stop services
./start-dev.sh logs    # View logs
./start-dev.sh build   # Build images
./start-dev.sh rebuild # Rebuild without cache
./start-dev.sh clean   # Remove all Docker resources

# Manual native commands
# Backend
source venv/bin/activate
python app.py

# Frontend  
npm start

# Database reset
rm backend/posting_board.db
python backend/database.py
```

### Native Service Management
The `start-dev.sh` script now supports stopping native services:
- PIDs are stored in `/tmp/.postingboard_pids` when services start
- `./start-dev.sh native-down` stops services using stored PIDs
- If PID file is missing, it falls back to finding processes on ports 5000 (backend) and 3000 (frontend)
- Uses `ss` command as primary method for finding processes by port (more robust than `lsof`)
- Falls back to `lsof` if `ss` is not available or doesn't return results
- Handles multiple PIDs on the same port gracefully
- The PID file is automatically cleaned up after stopping services

### Port Conflict Resolution
When encountering "address already in use" errors with Docker:
1. **Automatic handling**: The `./start-dev.sh up` command now automatically detects port conflicts
2. **Interactive prompt**: If ports 5000 or 3000 are in use, the script will:
   - Show which processes are using the ports
   - Ask if you want to stop them
   - Allow you to abort if you prefer to handle it manually
3. **Manual resolution**: Use `./start-dev.sh native-down` to stop all native servers
4. **Direct commands**: 
   - Use `ss -tlnp | grep <port>` to identify processes using the port
   - Kill the processes: `kill <PID>`

### Testing
```bash
# Create idea (example with all required fields and correct enum values)
curl -X POST http://localhost:3000/api/ideas -H "Content-Type: application/json" -d '{
  "title": "Test Idea",
  "description": "Test Description",
  "skills": ["Python"],
  "urgency": "not_urgent",
  "size": "small",
  "email": "test@example.com",
  "benefactor_team": "Test Team",
  "needed_by": "2025-12-31"
}'

# Valid enum values:
# - priority: "low", "medium", "high"
# - size: "small", "medium", "large", "extra_large"
# - status: "open", "claimed", "complete"

# Claim idea
curl -X POST http://localhost:3000/api/ideas/1/claim -H "Content-Type: application/json" -d '{
  "claimer_name": "John Doe",
  "claimer_email": "john@example.com",
  "claimer_skills": "Python, JavaScript",
  "claimer_team": "Dev Team"
}'

# Admin login
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d '{"password": "2929arch"}' -c cookies.txt

# Update idea as admin
curl -X PUT http://localhost:5000/api/admin/ideas/1 -H "Content-Type: application/json" -b cookies.txt -d '{
  "title": "Updated Title",
  "status": "complete"
}'

# Add new skill as admin
curl -X POST http://localhost:5000/api/admin/skills -H "Content-Type: application/json" -b cookies.txt -d '{"name": "Machine Learning"}'
```

### Production
```bash
# Build frontend
npm run build

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## Known Limitations
- Admin authentication is basic (single hardcoded password)
- Email configuration required for notifications
- No data validation for dates (can be in past)
- No rate limiting
- No audit trail
- Single-tenant design

## Debug Tips
- Check browser console for frontend errors
- Flask debug mode shows detailed errors
- SQLAlchemy echo=True shows SQL queries
- Network tab for API debugging
- React Developer Tools for component state

## React Hooks Best Practices
- **useEffect Dependencies**: Always include all variables used inside useEffect in the dependency array
- **useCallback for Functions**: When passing functions as dependencies to useEffect, wrap them with useCallback to prevent infinite re-renders
- **Example Fix**: In IdeaList.js, the fetchData function is wrapped with useCallback and includes filters as a dependency, then useEffect depends on fetchData

This project demonstrates a clean, extensible architecture suitable for citizen developer tools while keeping complexity manageable.