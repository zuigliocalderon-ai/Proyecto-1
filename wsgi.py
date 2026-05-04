"""
WSGI entry point for Render deployment.
Imports and runs the Flask app from backend/src/api/app.py
"""

import os
import sys

# Add backend to Python path so imports work correctly
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the Flask app
from src.api.app import app

if __name__ == '__main__':
    app.run()
