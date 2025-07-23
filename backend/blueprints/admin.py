from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from config import Config

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
def index():
    """Redirect to appropriate admin page."""
    if session.get('is_admin'):
        return redirect(url_for('admin.dashboard'))
    else:
        return redirect(url_for('admin.login'))

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == Config.ADMIN_PASSWORD:
            session['is_admin'] = True
            session.permanent = True
            flash('Successfully logged in as admin', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid password', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout."""
    session.pop('is_admin', None)
    flash('Successfully logged out', 'success')
    return redirect(url_for('main.home'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with statistics."""
    return render_template('admin/dashboard.html')

@admin_bp.route('/ideas')
@admin_required
def ideas():
    """Manage ideas page."""
    return render_template('admin/ideas.html')

@admin_bp.route('/skills')
@admin_required
def skills():
    """Manage skills page."""
    return render_template('admin/skills.html')