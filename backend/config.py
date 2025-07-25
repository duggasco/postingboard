import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    # This is not used - database.py handles the database URL
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///data/posting_board_uuid.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = './flask_session'
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Email configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    
    # Admin password
    ADMIN_PASSWORD = '2929arch'
    
    # Pagination
    IDEAS_PER_PAGE = 20
    
    # Auto-refresh intervals (in seconds)
    HOME_REFRESH_INTERVAL = 30
    ADMIN_IDEAS_REFRESH_INTERVAL = 5
    ADMIN_SKILLS_REFRESH_INTERVAL = 2