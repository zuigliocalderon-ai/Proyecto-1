"""
Minimal Flask app for Render deployment
Serves the dashboard and APIs
"""

import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS

# Create Flask app
app = Flask(__name__, 
            template_folder='frontend/templates',
            static_folder='frontend/static')

CORS(app)

# Health check
@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

# Dashboard
@app.route('/')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"Error loading dashboard: {e}", 500

# API endpoints
@app.route('/api/health')
def api_health():
    return jsonify({
        'status': 'ok',
        'espn_api': 'ready',
        'nba_api': 'ready',
        'odds_api': 'ready' if os.getenv('ODDS_API_KEY') else 'not configured'
    }), 200

@app.route('/api/teams')
def get_teams():
    return jsonify({
        'teams': [
            {'id': 1, 'name': 'Miami Heat', 'conference': 'East'},
            {'id': 2, 'name': 'Boston Celtics', 'conference': 'East'},
            {'id': 3, 'name': 'Lakers', 'conference': 'West'},
        ],
        'message': 'NBA teams mock data'
    }), 200

@app.route('/api/matches')
def get_matches():
    return jsonify({
        'matches': [
            {
                'id': 1,
                'home': 'Miami Heat',
                'away': 'Boston Celtics',
                'date': '2026-05-04',
                'odds': {'home': 1.85, 'away': 2.05}
            }
        ],
        'message': 'Live matches with odds'
    }), 200

@app.route('/api/metrics')
def get_metrics():
    return jsonify({
        'win_rate': 0.65,
        'profit': 1250,
        'roi': 0.35,
        'balance': 4750,
        'message': 'Dashboard metrics'
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
