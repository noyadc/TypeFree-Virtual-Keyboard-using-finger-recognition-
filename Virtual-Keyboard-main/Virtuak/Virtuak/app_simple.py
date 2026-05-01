from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'

# Database setup
def init_db():
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_email(email):
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(first_name, last_name, email, password_hash):
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (first_name, last_name, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (first_name, last_name, email, password_hash))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def update_last_login(user_id):
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def update_user_profile(user_id, first_name, last_name, email):
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET first_name = ?, last_name = ?, email = ?
        WHERE id = ?
    ''', (first_name, last_name, email, user_id))
    conn.commit()
    conn.close()

def update_password(user_id, password_hash):
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = get_user_by_email(email)
        print(f"Login attempt for email: {email}")
        print(f"User found: {user}")
        
        if user and user[4] == hash_password(password):  # password_hash is at index 4
            print(f"Login successful for user: {user[1]} {user[2]} (ID: {user[0]})")
            session['user_id'] = user[0]  # user id is at index 0
            session['user_email'] = user[3]  # email is at index 3
            session['user_name'] = f"{user[1]} {user[2]}"  # first_name and last_name
            
            print(f"Session data: {dict(session)}")
            
            # Update last login
            update_last_login(user[0])
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            print(f"Login failed - password check: {user and user[4] == hash_password(password)}")
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        
        # Validation
        if not all([first_name, last_name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = hash_password(password)
        try:
            print(f"Creating user: {first_name} {last_name} ({email})")
            user_id = create_user(first_name, last_name, email, password_hash)
            print(f"User created with ID: {user_id}")
            
            # Verify user was created
            created_user = get_user_by_id(user_id)
            print(f"Created user data: {created_user}")
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Registration error: {e}")
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # Debug: Print user data
    print(f"User data from database: {user}")
    print(f"User ID: {user[0]}, First Name: {user[1]}, Last Name: {user[2]}, Email: {user[3]}")
    
    # Convert tuple to dict for template
    user_dict = {
        'id': user[0],
        'first_name': user[1],
        'last_name': user[2],
        'email': user[3],
        'created_at': datetime.fromisoformat(user[5]) if user[5] else None,
        'last_login': datetime.fromisoformat(user[6]) if user[6] else None,
        'is_active': user[7]
    }
    
    print(f"User dict for template: {user_dict}")
    
    return render_template('dashboard.html', user=user_dict)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to access profile', 'error')
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    # Convert tuple to dict for template
    user_dict = {
        'id': user[0],
        'first_name': user[1],
        'last_name': user[2],
        'email': user[3],
        'created_at': datetime.fromisoformat(user[5]) if user[5] else None,
        'last_login': datetime.fromisoformat(user[6]) if user[6] else None,
        'is_active': user[7]
    }
    
    return render_template('profile.html', user=user_dict)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    
    if not all([first_name, last_name, email]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Check if email is already taken by another user
    existing_user = get_user_by_email(email)
    if existing_user and existing_user[0] != session['user_id']:
        return jsonify({'success': False, 'message': 'Email already taken'})
    
    try:
        update_user_profile(session['user_id'], first_name, last_name, email)
        session['user_email'] = email
        session['user_name'] = f"{first_name} {last_name}"
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Update failed'})

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    user = get_user_by_id(session['user_id'])
    if not user:
        return jsonify({'success': False, 'message': 'User not found'})
    
    current_password = request.form.get('currentPassword')
    new_password = request.form.get('newPassword')
    confirm_password = request.form.get('confirmPassword')
    
    if user[4] != hash_password(current_password):  # password_hash is at index 4
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
    
    try:
        new_password_hash = hash_password(new_password)
        update_password(session['user_id'], new_password_hash)
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Password change failed'})

# API Routes
@app.route('/api/users')
def api_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    
    user_list = []
    for user in users:
        user_list.append({
            'id': user[0],
            'first_name': user[1],
            'last_name': user[2],
            'email': user[3],
            'created_at': user[5],
            'last_login': user[6],
            'is_active': user[7]
        })
    
    return jsonify({'users': user_list})

# Additional Pages
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

# Debug route to check database
@app.route('/debug/users')
def debug_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    conn = sqlite3.connect('virtuak.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    
    current_user = get_user_by_id(session['user_id'])
    
    return jsonify({
        'all_users': [{'id': u[0], 'first_name': u[1], 'last_name': u[2], 'email': u[3]} for u in users],
        'current_user': {
            'id': current_user[0],
            'first_name': current_user[1],
            'last_name': current_user[2],
            'email': current_user[3]
        } if current_user else None,
        'session': dict(session)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
