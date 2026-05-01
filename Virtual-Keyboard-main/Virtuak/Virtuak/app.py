from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import subprocess
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///virtuak.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<User {self.email}>'

# Create database tables
with app.app_context():
    db.create_all()

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
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = f"{user.first_name} {user.last_name}"
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
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
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password_hash=password_hash
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please login to access dashboard', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

def get_user_whiteboard_images():
    # Get all PNG files from instance folder that start with 'whiteboard_'
    instance_path = os.path.join(app.root_path, 'instance')
    image_files = []
    if os.path.exists(instance_path):
        for file in os.listdir(instance_path):
            if file.startswith('whiteboard_') and file.endswith('.png'):
                image_files.append({
                    'filename': file,
                    'path': url_for('serve_whiteboard_image', filename=file),
                    'date': datetime.fromtimestamp(os.path.getctime(os.path.join(instance_path, file))).strftime('%Y-%m-%d %H:%M:%S')
                })
    # Sort by date, newest first
    image_files.sort(key=lambda x: x['date'], reverse=True)
    return image_files

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to access profile', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    whiteboard_images = get_user_whiteboard_images()
    return render_template('profile.html', user=user, whiteboard_images=whiteboard_images)

@app.route('/whiteboard_image/<filename>')
def serve_whiteboard_image(filename):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    if not filename.startswith('whiteboard_') or not filename.endswith('.png'):
        return jsonify({'error': 'Invalid filename'}), 400
    return send_from_directory(os.path.join(app.root_path, 'instance'), filename)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    user = User.query.get(session['user_id'])
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    
    if not all([first_name, last_name, email]):
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    # Check if email is already taken by another user
    existing_user = User.query.filter_by(email=email).first()
    if existing_user and existing_user.id != user.id:
        return jsonify({'success': False, 'message': 'Email already taken'})
    
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    
    try:
        db.session.commit()
        session['user_email'] = email
        session['user_name'] = f"{first_name} {last_name}"
        return jsonify({'success': True, 'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Update failed'})

@app.route('/change_password', methods=['POST'])
def change_password():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    user = User.query.get(session['user_id'])
    current_password = request.form.get('currentPassword')
    new_password = request.form.get('newPassword')
    confirm_password = request.form.get('confirmPassword')
    
    if not check_password_hash(user.password_hash, current_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'})
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'})
    
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
    
    user.password_hash = generate_password_hash(new_password)
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Password change failed'})

# API Routes
@app.route('/api/users')
def api_users():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'created_at': user.created_at.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'is_active': user.is_active
        })
    
    return jsonify({'users': user_list})

# Additional informational pages referenced by templates
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/launch_keyboard', methods=['POST'])
def launch_keyboard():
    # Path to the provided virtual keyboard script (no gestures version by default)
    script_relative_path = os.path.join(
        "Virtual_keyboard(remove_gestures)",
        "Virtual keyboard",
        "virtual_keyboard_no_gestures.py"
    )
    script_path = os.path.join(app.root_path, script_relative_path)

    if not os.path.exists(script_path):
        flash('Virtual keyboard script not found.', 'error')
        return redirect(url_for('features'))

    try:
        subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path))
        flash('Virtual keyboard launching...', 'success')
    except Exception:
        flash('Failed to launch virtual keyboard.', 'error')

    return redirect(url_for('features'))

@app.route('/launch_whiteboard', methods=['POST'])
def launch_whiteboard():
    script_path = os.path.join(app.root_path, 'whiteboard.py')
    if not os.path.exists(script_path):
        flash('Whiteboard script not found.', 'error')
        return redirect(url_for('features'))
    try:
        subprocess.Popen([sys.executable, script_path], cwd=os.path.dirname(script_path))
        flash('Digital whiteboard launching...', 'success')
    except Exception:
        flash('Failed to launch digital whiteboard.', 'error')
    return redirect(url_for('features'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
