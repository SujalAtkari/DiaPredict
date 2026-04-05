"""
Development server entry point.
Run the Flask application in development mode.

Usage:
    python run.py
"""

import os
import sys

# Add app directory to path so we can import from it
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Change to app directory for relative paths to work correctly
os.chdir(app_dir)

# Import the app from app.py in the app directory
from app import app

if __name__ == "__main__":
    # For development
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    # Disable use_reloader to avoid issues with debug mode
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
