"""
Temporary test route for creating authenticated sessions for documentation screenshots
This file should be removed in production
"""

from flask import Blueprint, session, redirect, url_for
from database import get_session
from models import UserProfile, Team, Skill
import uuid

test_auth_bp = Blueprint('test_auth', __name__)

@test_auth_bp.route('/test-auth-documentation')
def create_test_session():
    """Create a test authenticated session for documentation screenshots"""
    # Only enable in development mode
    import os
    if os.environ.get('FLASK_ENV') != 'development':
        return "Not available in production", 403
    
    db = get_session()
    try:
        # Create or get test user in database
        test_email = 'demo@example.com'
        user = db.query(UserProfile).filter_by(email=test_email).first()
        
        if not user:
            # Get team
            team = db.query(Team).filter_by(name='SL - Tech').first()
            if not team:
                # Get first available team
                team = db.query(Team).first()
            
            # Create user
            user = UserProfile(
                email=test_email,
                name='Demo User',
                role='developer',
                team_uuid=team.uuid if team else None,
                is_verified=True
            )
            db.add(user)
            db.commit()
            
            # Add skills
            skill_names = ['Python', 'JavaScript', 'SQL']
            for skill_name in skill_names:
                skill = db.query(Skill).filter_by(name=skill_name).first()
                if skill:
                    user.skills.append(skill)
            db.commit()
        
        # Update session from database
        from decorators import update_session_from_db
        update_session_from_db(test_email)
        
        # Add submitted/claimed ideas
        session['submitted_ideas'] = []
        session['claimed_ideas'] = []
        
        return redirect(url_for('main.home'))
        
    finally:
        db.close()