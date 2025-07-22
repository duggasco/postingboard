from flask import Flask
from flask_cors import CORS
from config import Config
from routes.ideas import ideas_bp
from routes.claims import claims_bp
from routes.skills import skills_bp
from routes.auth import auth_bp
from database import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app, supports_credentials=True)
    
    app.register_blueprint(ideas_bp)
    app.register_blueprint(claims_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(auth_bp)
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app

if __name__ == '__main__':
    init_db()
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)