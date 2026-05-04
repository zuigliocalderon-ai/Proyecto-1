"""
WSGI entry point for Render deployment.
Imports and runs the Flask app from backend/src/api/app.py
"""

import os
import sys

# Add backend to Python path so imports work correctly
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Set environment for production
os.environ.setdefault('FLASK_ENV', 'production')

# Import the Flask app - this will initialize everything
try:
    from src.api.app import app
    print("✅ Flask app loaded successfully")
except Exception as e:
    print(f"❌ Error loading Flask app: {e}")
    import traceback
    traceback.print_exc()
    raise

# Gunicorn will use this app object
if __name__ == '__main__':
    # For local testing only
    app.run(debug=False)
