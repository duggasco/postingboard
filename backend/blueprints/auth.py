from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from database import get_session
from auth_utils import create_verification_code, verify_code, get_user_profile, update_user_profile
from decorators import update_session_from_db
from models import Skill

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
        
        # Get all available skills
        skills = db.query(Skill).order_by(Skill.name).all()
        
        return render_template('auth/profile.html', user=user, skills=skills)
    finally:
        db.close()

@auth.route('/profile/update', methods=['POST'])
def update_profile():
    """Update user profile."""
    if not session.get('user_email'):
        return jsonify({'success': False, 'error': 'Authentication required.'}), 401
    
    name = request.form.get('name', '').strip()
    role = request.form.get('role', '').strip()
    skill_ids = request.form.getlist('skills[]')
    
    if not name:
        return jsonify({'success': False, 'error': 'Name is required.'}), 400
    
    if not role:
        return jsonify({'success': False, 'error': 'Role is required.'}), 400
    
    # Only require skills for developers
    if role in ['citizen_developer', 'developer'] and not skill_ids:
        return jsonify({'success': False, 'error': 'Please select at least one skill.'}), 400
    
    db = get_session()
    try:
        # Convert skill IDs to integers
        skill_ids = [int(sid) for sid in skill_ids if sid.isdigit()] if skill_ids else []
        
        # Clear skills for non-developer roles
        if role not in ['citizen_developer', 'developer']:
            skill_ids = []
        
        user = update_user_profile(db, session['user_email'], name=name, role=role, skill_ids=skill_ids)
        
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
    finally:
        db.close()

@auth.route('/logout')
def logout():
    """Log out the current user."""
    # Clear all session data
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))