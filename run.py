#!/usr/bin/env python3
"""
HireFlow AI - Application Entry Point
Production-ready AI-powered Applicant Tracking System

Usage:
    python run.py              # Start development server
    python run.py --production  # Start production server
    gunicorn run:app           # Production deployment
"""

import os
import sys

# Fix Python path: add the backend directory so imports like 'from models.user import db' work
_project_root = os.path.dirname(os.path.abspath(__file__))
_backend_path = os.path.join(_project_root, 'backend')
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from backend import create_app

# Determine environment
config_name = os.getenv('FLASK_ENV', 'development')
if '--production' in sys.argv:
    config_name = 'production'

# Create application
app = create_app(config_name)

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = config_name == 'development'
    
    print("=" * 60)
    print("          HireFlow AI - Starting...")
    print("=" * 60)
    print(f"  Mode: {config_name}")
    print(f"  Host: {host}")
    print(f"  Port: {port}")
    print(f"  API:  http://{host}:{port}/api/")
    print("=" * 60)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
