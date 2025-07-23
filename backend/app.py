from flask import Flask, render_template, redirect, url_for, session, request
from flask_session import Session
from dotenv import load_dotenv
import os
from config import Config

# Load environment variables
load_dotenv()

# Import blueprints
from blueprints.main import main_bp
from blueprints.admin import admin_bp
from blueprints.api import api_bp
from blueprints.auth import auth

def create_app():
    app = Flask(__name__)
    
    # Load configuration from Config class
    app.config.from_object(Config)
    
    # Initialize extensions
    Session(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth)
    
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