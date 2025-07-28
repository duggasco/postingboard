# Screenshot Instructions for Documentation

The documentation requires proper screenshots of the application with JavaScript fully loaded. The screenshots showing blank pages are due to JavaScript components not being rendered.

## Required Screenshots

The following screenshots need to be captured with the application running and all JavaScript components loaded:

1. **home_page.png** - Browse Ideas page showing:
   - Idea cards with full content
   - Filter options
   - Navigation bar
   - Statistics if visible

2. **submit_page.png** - Submit Idea form showing:
   - All form fields
   - Skill selection
   - Team dropdown
   - Bounty options

3. **my_ideas_page.png** - My Ideas dashboard showing:
   - Personal statistics cards
   - Submitted ideas list
   - Claimed ideas list
   - Pending approvals section

4. **my_team_page.png** - Team Analytics page showing:
   - Team performance metrics
   - Charts and graphs
   - Team member table
   - Skills gap analysis

5. **idea_detail_page.png** - Individual idea detail showing:
   - Full idea information
   - Status and progress
   - Comments section
   - GANTT chart if claimed

6. **profile_page.png** - User Profile page showing:
   - Profile form
   - Role selection
   - Team assignment
   - Skills selection

7. **verify_email_page.png** - Email Verification showing:
   - Email input field
   - Verification code entry
   - Instructions

8. **admin_dashboard.png** (optional) - Admin Dashboard showing:
   - Statistics cards
   - Charts
   - Pending notifications

## How to Capture Proper Screenshots

1. **Start the Application**:
   ```bash
   ./start-flask.sh
   ```

2. **Wait for Full Load**:
   - Navigate to each page
   - Wait 2-3 seconds for all JavaScript to load
   - Ensure charts, forms, and dynamic content are visible

3. **Browser Settings**:
   - Use 1920x1080 resolution or similar
   - Disable ad blockers
   - Enable JavaScript
   - Use Chrome/Firefox developer tools for full-page capture

4. **Save Screenshots**:
   - Save to `/root/postingboard/documentation_screenshots/`
   - Use exact filenames listed above
   - PNG format preferred

## Alternative: Text Descriptions

If screenshots cannot be properly captured, the documentation can use detailed text descriptions of each page's functionality instead of visual screenshots.