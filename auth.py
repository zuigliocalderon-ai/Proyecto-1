import hashlib
from flask import redirect, url_for, render_template, request, session, jsonify
from functools import wraps

# User database
USERS = {
    'demo@example.com': {
        'password': hashlib.sha256('demo123'.encode()).hexdigest(),
        'name': 'Demo User'
    },
    'test@example.com': {
        'password': hashlib.sha256('test123'.encode()).hexdigest(),
        'name': 'Test User'
    }
}

def init_auth(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            if email in USERS:
                stored_hash = USERS[email]['password']
                provided_hash = hashlib.sha256(password.encode()).hexdigest()
                if stored_hash == provided_hash:
                    session['user_email'] = email
                    session['user_name'] = USERS[email]['name']
                    return redirect(url_for('dashboard'))
            return render_template('login.html', error='Invalid credentials'), 401
        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            name = request.form.get('name')
            if email in USERS:
                return render_template('signup.html', error='Email already exists'), 409
            USERS[email] = {
                'password': hashlib.sha256(password.encode()).hexdigest(),
                'name': name
            }
            session['user_email'] = email
            session['user_name'] = name
            return redirect(url_for('dashboard'))
        return render_template('signup.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function
