#!/usr/bin/env python3
"""Test script to verify Flask app functionality."""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import get_session
from models import Idea, Skill, IdeaStatus

def test_app_creation():
    """Test Flask app creation."""
    print("Testing Flask app creation...")
    app = create_app()
    assert app is not None
    print("✓ Flask app created successfully")
    return app

def test_routes(app):
    """Test that all routes are registered."""
    print("\nTesting routes...")
    
    expected_routes = [
        '/',
        '/submit',
        '/my-ideas',
        '/idea/<int:idea_id>',
        '/admin/',
        '/admin/login',
        '/admin/dashboard',
        '/admin/ideas',
        '/admin/skills',
        '/api/ideas',
        '/api/skills',
        '/api/stats',
        '/api/my-ideas'
    ]
    
    # Get all registered routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(str(rule))
    
    # Check main routes exist
    for route in expected_routes:
        found = any(route in r for r in routes)
        if found:
            print(f"✓ Route {route} registered")
        else:
            print(f"✗ Route {route} NOT found")

def test_database():
    """Test database connection."""
    print("\nTesting database connection...")
    try:
        db = get_session()
        
        # Count records
        idea_count = db.query(Idea).count()
        skill_count = db.query(Skill).count()
        open_ideas = db.query(Idea).filter_by(status=IdeaStatus.open).count()
        
        print(f"✓ Database connected")
        print(f"  - Total ideas: {idea_count}")
        print(f"  - Total skills: {skill_count}")
        print(f"  - Open ideas: {open_ideas}")
        
        db.close()
    except Exception as e:
        print(f"✗ Database error: {e}")

def test_templates():
    """Test that all templates exist."""
    print("\nTesting templates...")
    
    templates = [
        'base.html',
        'home.html',
        'submit.html',
        'my_ideas.html',
        'idea_detail.html',
        'admin/login.html',
        'admin/dashboard.html',
        'admin/ideas.html',
        'admin/skills.html',
        '404.html',
        '500.html'
    ]
    
    for template in templates:
        path = os.path.join('templates', template)
        if os.path.exists(path):
            print(f"✓ Template {template} exists")
        else:
            print(f"✗ Template {template} NOT found")

def test_static_files():
    """Test that static files exist."""
    print("\nTesting static files...")
    
    static_files = [
        'css/styles.css',
        'js/main.js',
        'js/home.js',
        'js/submit.js'
    ]
    
    for file in static_files:
        path = os.path.join('static', file)
        if os.path.exists(path):
            print(f"✓ Static file {file} exists")
        else:
            print(f"✗ Static file {file} NOT found")

def main():
    """Run all tests."""
    print("=" * 50)
    print("Flask App Test Suite")
    print("=" * 50)
    
    app = test_app_creation()
    test_routes(app)
    test_database()
    test_templates()
    test_static_files()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")
    print("=" * 50)

if __name__ == '__main__':
    main()