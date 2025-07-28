"""
Test routes for documentation screenshot generation
Only available in development mode
"""

from flask import Blueprint, session, redirect, url_for, current_app
from models import UserProfile, Team, Skill, UserSkill, get_session as get_db_session
import os

test_bp = Blueprint('test', __name__)

@test_bp.route('/test-auth-docs/<email>')
def create_test_session_docs(email):
    """
    Create an authenticated session for documentation screenshots
    Only works in development mode
    """
    # Only allow in development
    if not (os.environ.get('FLASK_ENV') == 'development' or 
            current_app.config.get('ENV') == 'development' or
            current_app.debug):
        return "Not available in production", 403
    
    db = get_db_session()
    
    try:
        # Check if user exists
        user = db.query(UserProfile).filter_by(email=email).first()
        
        if not user:
            # Create user
            team = db.query(Team).filter_by(name='Cash - GPP').first()
            if not team:
                team = db.query(Team).first()  # Get any team
            
            user = UserProfile(
                email=email,
                name=f"Test User {email.split('@')[0]}",
                is_verified=True,
                role='developer',
                team_uuid=team.uuid if team else None
            )
            db.add(user)
            db.commit()
            
            # Add some skills
            skills = db.query(Skill).filter(
                Skill.name.in_(['Python', 'JavaScript', 'React', 'SQL', 'Data Analytics'])
            ).all()
            
            for skill in skills:
                user_skill = UserSkill(
                    user_email=user.email,
                    skill_uuid=skill.uuid
                )
                db.add(user_skill)
            
            db.commit()
        
        # Create session
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['user_verified'] = True
        session['user_role'] = user.role
        session['user_team'] = db.query(Team).filter_by(uuid=user.team_uuid).first().name if user.team_uuid else None
        session['user_team_uuid'] = user.team_uuid
        session['user_skills'] = [
            skill.name for skill in 
            db.query(Skill).join(UserSkill).filter(UserSkill.user_email == user.email).all()
        ]
        session['pending_manager_request'] = False
        session.permanent = True
        
        return redirect(url_for('main.home'))
        
    except Exception as e:
        db.rollback()
        return f"Error creating test session: {str(e)}", 500
    finally:
        db.close()