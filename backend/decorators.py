from functools import wraps
from flask import session, redirect, url_for, jsonify, flash, request
from database import get_session
from auth_utils import is_user_verified

def require_verified_email(f):
    """Decorator to require email verification for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = session.get('user_email')
        
        if not user_email:
            if hasattr(f, '__name__') and 'api' in f.__module__:
                # API endpoint
                return jsonify({'error': 'Authentication required. Please verify your email.'}), 401
            else:
                # Regular route
                flash('Please verify your email to access this feature.', 'warning')
                return redirect(url_for('auth.verify_email'))
        
        # Check if user is verified in database
        db = get_session()
        try:
            if not is_user_verified(db, user_email):
                if hasattr(f, '__name__') and 'api' in f.__module__:
                    return jsonify({'error': 'Email verification required.'}), 401
                else:
                    flash('Please verify your email to access this feature.', 'warning')
                    return redirect(url_for('auth.verify_email'))
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

def require_profile_complete(f):
    """Decorator to require a complete profile (name and skills)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_email = session.get('user_email')
        
        if not user_email:
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Authentication required.'}), 401
            else:
                flash('Please verify your email first.', 'warning')
                return redirect(url_for('auth.verify_email'))
        
        # Check if profile is complete
        db = get_session()
        try:
            from auth_utils import get_user_profile
            user = get_user_profile(db, user_email)
            
            if not user or not user.is_verified:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Email verification required.'}), 401
                else:
                    flash('Please verify your email first.', 'warning')
                    return redirect(url_for('auth.verify_email'))
            
            if not user.name or not user.skills:
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'error': 'Please complete your profile with name and skills.'}), 401
                else:
                    flash('Please complete your profile before proceeding.', 'info')
                    return redirect(url_for('main.profile'))
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

def update_session_from_db(email):
    """Update session with user data from database."""
    db = get_session()
    try:
        from auth_utils import get_user_profile
        user = get_user_profile(db, email)
        
        if user:
            session['user_email'] = user.email
            session['user_name'] = user.name
            session['user_verified'] = user.is_verified
            session['user_skills'] = [skill.name for skill in user.skills]
            session.permanent = True
            return True
        return False
    finally:
        db.close()