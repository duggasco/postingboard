from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database import get_session
from auth_utils import create_verification_code, verify_code, get_user_profile, update_user_profile
from decorators import update_session_from_db
from models import Skill, Team
from uuid_utils import is_valid_uuid

auth = Blueprint('auth', __name__)

@auth.route('/verify-email')
def verify_email():
    """Show email verification page."""
    return render_template('auth/verify_email.html')

@auth.route('/request-code', methods=['POST'])
def request_code():
    """Request a verification code."""
    email = request.form.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'error': 'Email is required.'}), 400
    
    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[1]:
        return jsonify({'success': False, 'error': 'Please enter a valid email address.'}), 400
    
    db = get_session()
    try:
        result = create_verification_code(db, email)
        
        if result['success']:
            # Store email in session temporarily
            session['pending_email'] = email
            session.permanent = True
            
            return jsonify({
                'success': True,
                'message': 'Verification code sent to your email.'
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 429  # Too Many Requests
    finally:
        db.close()

@auth.route('/verify-code', methods=['POST'])
def verify_code_route():
    """Verify the submitted code."""
    email = session.get('pending_email', '').strip().lower()
    code = request.form.get('code', '').strip()
    
    if not email:
        return jsonify({'success': False, 'error': 'No pending verification. Please request a new code.'}), 400
    
    if not code:
        return jsonify({'success': False, 'error': 'Verification code is required.'}), 400
    
    db = get_session()
    try:
        result = verify_code(db, email, code)
        
        if result['success']:
            # Update session with verified user data
            update_session_from_db(email)
            
            # Clear pending email
            session.pop('pending_email', None)
            
            # Check if user has completed profile
            user = result['user']
            if not user.name or not user.skills:
                return jsonify({
                    'success': True,
                    'redirect': url_for('auth.profile'),
                    'message': 'Email verified! Please complete your profile.'
                })
            else:
                return jsonify({
                    'success': True,
                    'redirect': url_for('main.home'),
                    'message': 'Email verified successfully!'
                })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
    finally:
        db.close()

@auth.route('/profile')
def profile():
    """Show user profile page."""
    if not session.get('user_email'):
        flash('Please verify your email first.', 'warning')
        return redirect(url_for('auth.verify_email'))
    
    db = get_session()
    try:
        user = get_user_profile(db, session['user_email'])
        if not user or not user.is_verified:
            flash('Please verify your email first.', 'warning')
            return redirect(url_for('auth.verify_email'))
        
        # Ensure session is properly initialized for bulk uploaded users
        update_session_from_db(user.email)
        
        # Get all available skills
        skills = db.query(Skill).order_by(Skill.name).all()
        
        # Get all approved teams
        teams = db.query(Team).filter(Team.is_approved == True).order_by(Team.name).all()
        
        return render_template('auth/profile.html', user=user, skills=skills, teams=teams)
    finally:
        db.close()

@auth.route('/profile/update', methods=['POST'])
def update_profile():
    """Update user profile."""
    if not session.get('user_email'):
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401
    
    name = request.form.get('name', '').strip()
    role = request.form.get('role', '').strip()
    team_uuid = request.form.get('team')
    custom_team = request.form.get('custom_team', '').strip()
    managed_team_uuid = request.form.get('managed_team')
    skill_ids = request.form.getlist('skills[]')
    custom_skill = request.form.get('custom_skill', '').strip()
    
    if not name:
        return jsonify({'success': False, 'error': 'Name is required.'}), 400
    
    if not role:
        return jsonify({'success': False, 'error': 'Role is required.'}), 400
    
    if not team_uuid and not custom_team:
        return jsonify({'success': False, 'error': 'Please select or enter a team.'}), 400
    
    # Skills are now optional for all roles - no validation needed
    
    # Require managed team for managers
    if role == 'manager' and not managed_team_uuid:
        return jsonify({'success': False, 'error': 'Please select a team to manage.'}), 400
    
    db = get_session()
    try:
        # Handle team selection
        if custom_team:
            # Create new team if custom team is provided
            existing_team = db.query(Team).filter_by(name=custom_team).first()
            if not existing_team:
                new_team = Team(name=custom_team, is_approved=False)  # Needs admin approval
                db.add(new_team)
                db.commit()
                team_uuid = new_team.uuid
                
                # Create notification for admins about new team request
                admin_notification = Notification(
                    user_email='admin@system.local',  # System notification for all admins
                    type='team_approval_request',
                    title='New team approval request',
                    message=f'User {user.name or user.email} has requested to create team "{custom_team}"',
                    related_user_email=user.email
                )
                db.add(admin_notification)
                db.commit()
            else:
                team_uuid = existing_team.uuid
        
        # Handle custom skill if provided
        if custom_skill and role in ['citizen_developer', 'developer']:
            # Check if skill already exists
            existing_skill = db.query(Skill).filter_by(name=custom_skill).first()
            if not existing_skill:
                # Create new skill
                new_skill = Skill(name=custom_skill)
                db.add(new_skill)
                db.commit()
                skill_ids.append(str(new_skill.uuid))
            else:
                # Add existing skill ID if not already selected
                if str(existing_skill.uuid) not in skill_ids:
                    skill_ids.append(str(existing_skill.uuid))
        
        # Filter valid skill UUIDs
        skill_ids = [sid for sid in skill_ids if is_valid_uuid(sid)] if skill_ids else []
        
        # Clear skills for non-developer roles
        if role not in ['citizen_developer', 'developer']:
            skill_ids = []
        
        # Clear managed team for non-manager roles
        if role != 'manager':
            managed_team_uuid = None
        
        user = update_user_profile(
            db, 
            session['user_email'], 
            name=name, 
            role=role, 
            team_uuid=team_uuid if team_uuid else None, 
            managed_team_uuid=managed_team_uuid if managed_team_uuid else None,
            skill_ids=skill_ids,
            create_manager_request=(role == 'manager' and managed_team_uuid is not None)
        )
        
        if user:
            # Update session data
            update_session_from_db(user.email)
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully!'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'User not found.'
            }), 404
    except Exception as e:
        db.rollback()
        import traceback
        error_details = f"Error updating profile for {session.get('user_email')}: {str(e)}"
        print(error_details)
        print(f"Traceback: {traceback.format_exc()}")
        print(f"Form data - name: {name}, role: {role}, team_uuid: {team_uuid}, skills: {skill_ids}")
        return jsonify({
            'success': False,
            'error': 'Failed to update profile. Please try again.'
        }), 500
    finally:
        db.close()

@auth.route('/logout')
def logout():
    """Log out the current user."""
    # Clear all session data
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))