from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import numpy as np
import pickle
import os
from dotenv import load_dotenv

# Import database and utilities
import sys
sys.path.insert(0, os.path.dirname(__file__))

from database import (
    init_database, create_user, get_user_by_email, get_user_by_id,
    get_user_by_verification_token, verify_user, update_last_login,
    record_login_attempt, save_prediction, get_user_predictions,
    get_user_statistics, get_user_predictions_for_charts, get_prediction_by_id
)
from utils.auth import hash_password, verify_password, generate_verification_token, is_password_strong
from utils.email import send_verification_email, send_welcome_email
from utils.stats import get_chart_data, format_for_json

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=int(os.getenv('SESSION_TIMEOUT', 1800)))

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize database
init_database()

# Load ML model and scaler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "hybrid_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(SCALER_PATH, "rb") as f:
    scaler = pickle.load(f)

FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]


# ==================== USER CLASS ====================

class User(UserMixin):
    def __init__(self, user_id, email, username, is_verified):
        self.id = user_id
        self.email = email
        self.username = username
        self.is_verified = is_verified


@login_manager.user_loader
def load_user(user_id):
    user_data = get_user_by_id(user_id)
    if user_data:
        return User(str(user_data['_id']), user_data['email'], user_data['username'], user_data['is_verified'])
    return None


# ==================== HELPER FUNCTIONS ====================

def check_rate_limit(email, max_attempts=5, window_seconds=300):
    """Check if user has exceeded login attempt limits"""
    user = get_user_by_email(email)
    if not user:
        return True

    if user.get('login_attempts', 0) >= max_attempts:
        if user.get('last_login_attempt'):
            time_since_attempt = datetime.utcnow() - user['last_login_attempt']
            if time_since_attempt.total_seconds() < window_seconds:
                return False
    return True


def send_verification_link(email, username, verification_token):
    """Send verification link to user"""
    verification_link = url_for('verify_email', token=verification_token, _external=True)
    return send_verification_email(email, username, verification_link)


# ==================== HOME & STATIC ROUTES ====================

@app.route('/')
def home():
    """Home page - redirect based on login status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not email or not username or not password:
            flash('All fields are required.', 'error')
            return render_template('signup.html')

        # Check password strength
        is_strong, message = is_password_strong(password)
        if not is_strong:
            flash(message, 'error')
            return render_template('signup.html')

        # Check password match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        # Check if email already exists
        if get_user_by_email(email):
            flash('Email already registered. Please log in or use a different email.', 'error')
            return render_template('signup.html')

        try:
            # Create user
            password_hash = hash_password(password)
            verification_token = generate_verification_token()

            user_id = create_user(email, username, password_hash, verification_token)

            # Send verification email
            if send_verification_link(email, username, verification_token):
                flash('Registration successful! Check your email to verify your account.', 'success')
            else:
                flash('Registration successful, but email verification could not be sent. Please contact support.', 'warning')

            return redirect(url_for('login'))

        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/verify/<token>')
def verify_email(token):
    """Verify email with token"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    user = get_user_by_verification_token(token)

    if not user:
        flash('Invalid or expired verification link.', 'error')
        return redirect(url_for('login'))

    email = user['email']
    username = user['username']

    if verify_user(email):
        # Send welcome email
        send_welcome_email(email, username)
        flash('Email verified successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    else:
        flash('Error verifying email. Please try again.', 'error')
        return redirect(url_for('signup'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Check rate limiting
        if not check_rate_limit(email):
            flash('Too many login attempts. Please try again later.', 'error')
            return render_template('login.html')

        # Get user
        user_data = get_user_by_email(email)

        if not user_data:
            record_login_attempt(email, success=False)
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

        # Check if verified
        if not user_data.get('is_verified', False):
            flash('Please verify your email first.', 'error')
            return render_template('login.html')

        # Verify password
        if not verify_password(user_data['password_hash'], password):
            record_login_attempt(email, success=False)
            flash('Invalid email or password.', 'error')
            return render_template('login.html')

        # Successful login
        record_login_attempt(email, success=True)
        update_last_login(str(user_data['_id']))

        user = User(str(user_data['_id']), user_data['email'], user_data['username'], user_data['is_verified'])
        login_user(user, remember=True)

        flash(f'Welcome back, {user_data["username"]}!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    flash(f'Goodbye, {username}! You have been logged out.', 'info')
    return redirect(url_for('login'))


# ==================== PREDICTION ROUTES ====================

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Make a diabetes prediction"""
    if request.method == 'GET':
        return render_template('index.html', username=current_user.username)

    if request.method == 'POST':
        try:
            values = []
            health_data = {}

            for name in FEATURE_NAMES:
                raw = request.form.get(name)
                if raw is None or raw.strip() == "":
                    return render_template(
                        'result.html',
                        prediction_text="Please fill in all fields.",
                        username=current_user.username
                    )
                float_val = float(raw)
                values.append(float_val)
                health_data[name] = raw

            # Make prediction
            input_array = np.array([values])
            scaled_input = scaler.transform(input_array)
            prediction = model.predict(scaled_input)[0]

            if int(prediction) == 1:
                prediction_text = "The model predicts: Diabetes Positive"
            else:
                prediction_text = "The model predicts: Diabetes Negative"

            # Save to database
            prediction_id = save_prediction(current_user.id, health_data, prediction, prediction_text)

            return render_template(
                'result.html',
                prediction_text=prediction_text,
                username=current_user.username,
                prediction_id=prediction_id
            )

        except ValueError:
            return render_template(
                'result.html',
                prediction_text="Error: Please enter valid numbers for all fields.",
                username=current_user.username
            )
        except Exception as e:
            return render_template(
                'result.html',
                prediction_text=f"Error while making prediction: {str(e)}",
                username=current_user.username
            )


# ==================== DASHBOARD ROUTES ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with statistics"""
    predictions = get_user_predictions(current_user.id, limit=100)
    stats = get_user_statistics(current_user.id)

    return render_template(
        'dashboard.html',
        username=current_user.username,
        stats=stats,
        prediction_count=len(predictions)
    )


@app.route('/dashboard/api/chart-data')
@login_required
def get_chart_data_api():
    """API endpoint for chart data"""
    try:
        predictions = get_user_predictions(current_user.id, limit=100)
        chart_data = get_chart_data(predictions)

        # Format datetime objects for JSON
        chart_data = format_for_json(chart_data)

        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predictions')
@login_required
def predictions_history():
    """View all predictions history"""
    predictions = get_user_predictions(current_user.id, limit=1000)

    # Format for display
    for pred in predictions:
        pred['created_at_str'] = datetime.fromisoformat(pred['created_at']).strftime("%Y-%m-%d %H:%M:%S") if isinstance(pred['created_at'], str) else pred['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        pred['risk_label'] = "⚠️ Positive" if pred['prediction'] == 1 else "✓ Negative"

    return render_template(
        'predictions_history.html',
        predictions=predictions,
        username=current_user.username,
        total_count=len(predictions)
    )


@app.route('/predictions/<prediction_id>')
@login_required
def view_prediction(prediction_id):
    """View a specific prediction"""
    pred = get_prediction_by_id(prediction_id)

    if not pred or str(pred['user_id']) != current_user.id:
        flash('Prediction not found or access denied.', 'error')
        return redirect(url_for('predictions_history'))

    return render_template(
        'prediction_detail.html',
        prediction=pred,
        username=current_user.username
    )


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403


# ==================== CONTEXT PROCESSORS ====================

@app.context_processor
def inject_user():
    """Make current_user available in all templates"""
    return {'current_user': current_user}


# ==================== RUN APP ====================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
