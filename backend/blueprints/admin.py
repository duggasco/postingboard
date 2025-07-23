from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from functools import wraps
from config import Config
import os

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
            # Set admin user credentials for regular features
            session['user_email'] = 'admin@system.local'
            session['user_name'] = 'Admin'
            session['user_verified'] = True
            session['user_skills'] = []  # Admin has access to all skills
            flash('Successfully logged in as admin', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid password', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout."""
    session.pop('is_admin', None)
    # Clear admin user credentials
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_verified', None)
    session.pop('user_skills', None)
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

@admin_bp.route('/teams')
@admin_required
def teams():
    """Manage teams page."""
    return render_template('admin/teams.html')

@admin_bp.route('/manager-requests')
@admin_required
def manager_requests():
    """Manage manager requests page."""
    return render_template('admin/manager_requests.html')

@admin_bp.route('/email-settings')
@admin_required
def email_settings():
    """Manage email settings page."""
    return render_template('admin/email_settings.html')

@admin_bp.route('/bulk-upload')
@admin_required
def bulk_upload():
    """Bulk upload page for importing ideas and users."""
    return render_template('admin/bulk_upload.html')

@admin_bp.route('/users')
@admin_required
def users():
    """Manage users page."""
    return render_template('admin/users.html')

@admin_bp.route('/download-template/<template_type>')
@admin_required
def download_template(template_type):
    """Download CSV template for bulk upload."""
    if template_type == 'ideas':
        filepath = os.path.join(os.path.dirname(__file__), '..', 'templates', 'csv', 'ideas_template.csv')
        return send_file(filepath, as_attachment=True, download_name='ideas_template.csv', mimetype='text/csv')
    elif template_type == 'users':
        filepath = os.path.join(os.path.dirname(__file__), '..', 'templates', 'csv', 'users_template.csv')
        return send_file(filepath, as_attachment=True, download_name='users_template.csv', mimetype='text/csv')
    else:
        flash('Invalid template type', 'error')
        return redirect(url_for('admin.bulk_upload'))