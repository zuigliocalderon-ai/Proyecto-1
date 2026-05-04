import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from auth import init_auth, require_login
from predictions import get_enhanced_predictions, get_live_scores
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

init_auth(app)

@app.route('/')
def index():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user_name=session.get('user_name'))

@app.route('/api/health')
def api_health():
    return jsonify({'status': 'ok', 'authentication': 'enabled', 'api_integration': 'active'}), 200

@app.route('/api/user')
@require_login
def get_user():
    return jsonify({'email': session.get('user_email'), 'name': session.get('user_name')}), 200

@app.route('/api/live-matches')
@require_login
def get_live_matches():
    try:
        matches = get_live_scores()
        return jsonify(matches), 200
    except Exception as e:
        print(f'Error fetching live matches: {e}')
        return jsonify({'error': 'Failed to fetch live matches'}), 500

@app.route('/api/upcoming-matches')
@require_login
def get_upcoming_matches():
    try:
        matches = get_enhanced_predictions()
        return jsonify(matches), 200
    except Exception as e:
        print(f'Error fetching upcoming matches: {e}')
        return jsonify({'error': 'Failed to fetch predictions'}), 500

@app.route('/api/metrics')
@require_login
def get_metrics():
    return jsonify({'win_rate': 65, 'current_balance': 4750, 'starting_balance': 3500, 'total_profit': 1250, 'roi': 35, 'total_bets': 20, 'successful_bets': 13}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
