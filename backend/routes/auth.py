from flask import Blueprint, request, jsonify, session
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Hardcoded admin password as specified
ADMIN_PASSWORD = "2929arch"

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')
    
    if password == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({'success': True, 'message': 'Admin login successful'})
    
    return jsonify({'success': False, 'message': 'Invalid password'}), 401

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/api/auth/check', methods=['GET'])
def check_auth():
    is_admin = session.get('is_admin', False)
    return jsonify({'is_admin': is_admin})