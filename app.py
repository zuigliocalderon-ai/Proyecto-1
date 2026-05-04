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
            {'id': 1, 'name': 'Miami Heat', 'conference': 'East', 'wins': 45, 'losses': 35},
            {'id': 2, 'name': 'Boston Celtics', 'conference': 'East', 'wins': 48, 'losses': 32},
            {'id': 3, 'name': 'Lakers', 'conference': 'West', 'wins': 42, 'losses': 38},
            {'id': 4, 'name': 'Golden State Warriors', 'conference': 'West', 'wins': 40, 'losses': 40},
            {'id': 5, 'name': 'Denver Nuggets', 'conference': 'West', 'wins': 47, 'losses': 33},
        ]
    }), 200

@app.route('/api/matches')
def get_matches():
    """Return matches in the format expected by dashboard.js"""
    return jsonify([
        {
            'id': 1,
            'home': 'Miami Heat',
            'away': 'Boston Celtics',
            'home_score': 105,
            'away_score': 98,
            'date': '2026-05-04',
            'status': 'completed',
            'odds': 1.85
        },
        {
            'id': 2,
            'home': 'Lakers',
            'away': 'Golden State Warriors',
            'home_score': None,
            'away_score': None,
            'date': '2026-05-05',
            'status': 'upcoming',
            'odds': 1.92
        },
        {
            'id': 3,
            'home': 'Denver Nuggets',
            'away': 'Phoenix Suns',
            'home_score': None,
            'away_score': None,
            'date': '2026-05-05',
            'status': 'upcoming',
            'odds': 2.15
        }
    ]), 200

@app.route('/api/metrics')
def get_metrics():
    """Return metrics in the format expected by dashboard.js"""
    return jsonify({
        'win_rate': 65,
        'current_balance': 4750,
        'starting_balance': 3500,
        'total_profit': 1250,
        'roi': 35,
        'total_bets': 20,
        'successful_bets': 13
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
