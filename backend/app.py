from flask import Flask, render_template, redirect, url_for, session, request
from flask_session import Session
from dotenv import load_dotenv
import os
import subprocess
from config import Config

# Load environment variables
load_dotenv()

# Import blueprints
from blueprints.main import main_bp
from blueprints.admin import admin_bp
from blueprints.api import api_bp
from blueprints.auth import auth

def get_git_revision_short_hash():
    """Get the short git commit hash for version tracking"""
    # First check if we have it as an environment variable (from Docker build)
    git_commit = os.getenv('GIT_COMMIT')
    if git_commit and git_commit != 'unknown':
        return git_commit
    
    # Otherwise try to get it from git command
    try:
        return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
    except:
        return 'unknown'

def create_app():
    app = Flask(__name__)
    
    # Load configuration from Config class
    app.config.from_object(Config)
    
    # Initialize extensions
    Session(app)
    
    # Ensure database tables exist and teams are initialized
    from database import init_db
    init_db()
    
    # Ensure predefined teams exist
    from initialize_teams import ensure_teams_exist
    ensure_teams_exist()
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth)
    
    # Make git commit hash available to all templates
    @app.context_processor
    def inject_git_commit():
        return {'git_commit': get_git_revision_short_hash()}
    
    # Add cache control headers for admin pages
    @app.after_request
    def after_request(response):
        # Prevent caching for admin pages
        if request.path.startswith('/admin'):
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 9094))
    app.run(host='0.0.0.0', port=port, debug=True)