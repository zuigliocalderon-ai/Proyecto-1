import os
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from auth import init_auth, require_login
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
    return jsonify({'status': 'ok', 'authentication': 'enabled', 'espn_api': 'active', 'nba_api': 'active', 'odds_api': 'ready'}), 200

@app.route('/api/user')
@require_login
def get_user():
    return jsonify({'email': session.get('user_email'), 'name': session.get('user_name')}), 200

@app.route('/api/teams')
@require_login
def get_teams():
    return jsonify({'teams': [{'id': 1, 'name': 'Miami Heat'}, {'id': 2, 'name': 'Boston Celtics'}]}), 200

@app.route('/api/live-matches')
@require_login
def get_live_matches():
    return jsonify([{'id': 101, 'team1': 'Boston Celtics', 'team2': 'Miami Heat', 'score1': 58, 'score2': 52, 'quarter': 2, 'time': '5:30', 'status': 'live', 'date': datetime.now().strftime('%Y-%m-%d'), 'start_time': '19:30'}]), 200

@app.route('/api/upcoming-matches')
@require_login
def get_upcoming_matches():
    return jsonify([{'id': 1, 'team1': 'Miami Heat', 'team2': 'Boston Celtics', 'date': datetime.now().strftime('%Y-%m-%d'), 'time': '19:30', 'league': 'NBA', 'prediction': {'winner': 'Miami Heat', 'confidence': 72, 'odds': {'home': 1.85, 'away': 2.05}}, 'stats': {'team1_avg_points': 108.5, 'team2_avg_points': 107.2, 'team1_win_pct': 56, 'team2_win_pct': 60}}]), 200

@app.route('/api/metrics')
@require_login
def get_metrics():
    return jsonify({'win_rate': 65, 'current_balance': 4750, 'starting_balance': 3500, 'total_profit': 1250, 'roi': 35, 'total_bets': 20, 'successful_bets': 13}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
