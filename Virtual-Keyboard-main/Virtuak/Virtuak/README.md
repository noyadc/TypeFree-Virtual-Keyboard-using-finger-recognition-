# TypeFree - Touchless Typing Website with Flask Backend

A modern, responsive website featuring login and registration pages with a sophisticated dark theme, textured brown background design, and a complete Flask backend with SQLite database.

## 🎨 Design Features

- **Dark Theme**: Clean brown gradient background with white text for optimal contrast
- **Split Layout**: Hero content on the left, forms on the right
- **Modern UI**: Glassmorphism effects with backdrop blur and subtle animations
- **Responsive Design**: Fully responsive across all device sizes
- **Interactive Forms**: Real-time validation and user feedback
- **Backend Integration**: Complete Flask backend with SQLite database

## 🚀 Backend Features

- **User Authentication**: Secure login and registration system
- **SQLite Database**: Local database for user management
- **Session Management**: Secure user sessions
- **Profile Management**: Edit profile and change password
- **Dashboard**: User dashboard with account information
- **API Endpoints**: RESTful API for user data

## 📁 File Structure

```
TypeFree/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── virtuak.db            # SQLite database (created automatically)
├── templates/            # HTML templates
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── dashboard.html    # User dashboard
│   └── profile.html      # User profile
├── static/               # Static files
│   ├── styles.css        # Main stylesheet
│   └── script.js         # JavaScript functionality
└── README.md             # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application
```bash
python app.py
```

### Step 3: Access the Website
Open your browser and go to: `http://localhost:5000`

## 🎯 Pages Overview

### Home Page (`/`)
- Hero section with the "Join us now" message
- Navigation menu with login/register buttons
- Call-to-action buttons for getting started

### Login Page (`/login`)
- Email and password fields
- Remember me checkbox
- Form validation with real-time feedback
- Flash messages for errors/success

### Register Page (`/register`)
- First name and last name fields
- Email and password fields
- Password confirmation
- Comprehensive form validation
- Flash messages for errors/success

### Dashboard (`/dashboard`)
- User account information
- Quick action buttons
- Statistics display
- Navigation to other sections

### Profile (`/profile`)
- Edit profile information
- Change password functionality
- Account information display
- AJAX form submissions

## ✨ Features

### Backend Features
- **User Registration**: Secure user account creation
- **User Login**: Authentication with session management
- **Password Hashing**: Secure password storage using Werkzeug
- **Database Management**: SQLite database with SQLAlchemy ORM
- **Profile Updates**: Edit user information
- **Password Changes**: Secure password update functionality
- **Session Security**: Protected routes and session management

### Frontend Features
- **Form Validation**: Real-time email format checking
- **Required Fields**: All necessary fields are validated
- **Password Matching**: Confirmation password must match
- **Loading States**: Visual feedback during form submission
- **Success Messages**: Confirmation messages after successful actions
- **Error Handling**: Clear error messages for validation failures
- **Smooth Animations**: Subtle animations for better UX
- **Responsive Design**: Works perfectly on mobile and desktop

### Visual Design
- **Glassmorphism**: Modern glass-like card effects
- **Golden Accents**: Elegant gold (#d4af37) color scheme
- **Brown Gradient**: Sophisticated brown background pattern
- **Typography**: Clean Inter font family
- **Hover Effects**: Interactive button and link animations

## 🎨 Color Scheme

- **Primary Background**: Brown gradient (#2d1810 → #5d4037 → #a1887f)
- **Accent Color**: #d4af37 (Golden)
- **Text Color**: #ffffff (White)
- **Error Color**: #ff6b6b (Red)
- **Success Color**: #4caf50 (Green)

## 📱 Responsive Breakpoints

- **Desktop**: 1200px and above
- **Tablet**: 768px - 1199px
- **Mobile**: 480px - 767px
- **Small Mobile**: Below 480px

## 🔧 API Endpoints

### Authentication
- `POST /login` - User login
- `POST /register` - User registration
- `GET /logout` - User logout

### User Management
- `GET /dashboard` - User dashboard
- `GET /profile` - User profile page
- `POST /update_profile` - Update user profile
- `POST /change_password` - Change user password

### API
- `GET /api/users` - Get all users (requires authentication)

## 🌐 Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

## 🔒 Security Features

- **Password Hashing**: Secure password storage
- **Session Management**: Secure user sessions
- **CSRF Protection**: Built-in Flask CSRF protection
- **Input Validation**: Server-side form validation
- **SQL Injection Protection**: SQLAlchemy ORM protection

## 📝 Database Schema

### User Table
- `id` (Primary Key)
- `first_name` (String, 50 chars)
- `last_name` (String, 50 chars)
- `email` (String, 120 chars, unique)
- `password_hash` (String, 255 chars)
- `created_at` (DateTime)
- `last_login` (DateTime)
- `is_active` (Boolean)

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. Set `FLASK_ENV=production`
2. Change the secret key in `app.py`
3. Use a production WSGI server (Gunicorn, uWSGI)
4. Set up a proper database (PostgreSQL, MySQL)

### Example with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🤝 Contributing

Feel free to modify and enhance this website:
- Add more pages
- Implement additional backend functionality
- Enhance animations and interactions
- Add more form validation rules
- Improve accessibility features
- Add user roles and permissions
- Implement email verification
- Add password reset functionality

## 🐛 Troubleshooting

### Common Issues

1. **Database not created**: The database is created automatically when you first run the app
2. **Port already in use**: Change the port in `app.py` or kill the process using the port
3. **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Database Reset
To reset the database, delete `virtuak.db` and restart the application.

---

**Enjoy your touchless typing journey with TypeFree!** 🎯
