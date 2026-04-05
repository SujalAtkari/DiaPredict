"""
WSGI entry point for running the Flask application.
This file is used by production servers like Gunicorn.

Usage:
    gunicorn wsgi:app
"""

import os
import sys

# Add app directory to path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

from app import app

if __name__ == "__main__":
    app.run()
