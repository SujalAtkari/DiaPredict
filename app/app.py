from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.wrappers import Response
from datetime import datetime, timedelta
from typing import Union, Dict, List, Tuple, Optional
from sqlalchemy import inspect
import numpy as np
import pandas as pd
import joblib
import os
import logging
from dotenv import load_dotenv
from database_sql import db, User, Prediction, create_user, get_user_by_email, get_user_by_userid, verify_user, save_prediction, get_user_predictions, update_user_login, increment_login_attempts, is_account_locked
from utils.stats import get_chart_data, calculate_risk_distribution
from utils.auth import hash_password, verify_password, validate_email, is_password_strong

# Load environment variables from .env file in current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

# ==================== LOGGING CONFIGURATION ====================
# Get parent directory (project root)
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
LOGS_DIR = os.path.join(PROJECT_ROOT, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'diabetes_app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_DIR = APP_DIR
SQLITE_PATH = os.path.join(PROJECT_ROOT, 'data', 'diapredict.db')
DEFAULT_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

# ==================== PARAMETER VALIDATION RANGES ====================
# Medical ranges for the 8 health parameters
PARAMETER_RANGES = {
    "Pregnancies": (0, 20.4, "Number of pregnancies (0-17 in dataset)"),
    "Glucose": (13, 230, "Fasting blood glucose in mg/dL (44-199 in dataset)"),
    "BloodPressure": (4.4, 141.6, "Diastolic blood pressure in mmHg (24-122 in dataset)"),
    "SkinThickness": (0, 117.4, "Triceps skin fold thickness in mm (7-99 in dataset)"),
    "Insulin": (0, 1012.4, "2-Hour serum insulin in mU/mL (14-846 in dataset)"),
    "BMI": (8.42, 76.88, "Body Mass Index in kg/m² (18.2-67.1 in dataset)"),
    "DiabetesPedigreeFunction": (0, 2.89, "Diabetes pedigree function (0.08-2.42 in dataset)"),
    "Age": (9, 93, "Age in years (21-81 in dataset)"),
}

# ==================== ENVIRONMENT VALIDATION ====================
def validate_environment() -> Dict[str, Union[bool, str]]:
    """
    Validate all required environment variables at startup.
    Returns a dict with validation status and messages.
    """
    required_vars = {
        'SECRET_KEY': 'Flask secret key for session encryption',
    }
    
    optional_vars = {
        'DATABASE_URL': 'Database connection URL (defaults to SQLite)',
        'SMTP_SERVER': 'SMTP server for email (defaults to smtp.gmail.com)',
        'SMTP_PORT': 'SMTP port (defaults to 587)',
        'SENDER_EMAIL': 'Email address for sending notifications',
        'SENDER_PASSWORD': 'Email password for SMTP authentication',
    }
    
    validation_status = {
        'is_production': False,
        'warnings': [],
        'errors': []
    }
    
    # Check required variables
    for var, description in required_vars.items():
        if not os.getenv(var):
            if var == 'SECRET_KEY':
                msg = f"⚠️  {var} not set. Using insecure default. Set {var} in .env for production."
                validation_status['warnings'].append(msg)
                logger.warning(msg)
            else:
                validation_status['errors'].append(f"Missing required: {var} ({description})")
                logger.error(f"Missing required: {var}")
    
    # Check optional variables
    for var, description in optional_vars.items():
        if not os.getenv(var):
            msg = f"Optional {var} not configured ({description})"
            validation_status['warnings'].append(msg)
            logger.info(msg)
    
    # Check if production-ready
    if os.getenv('SECRET_KEY') and os.getenv('SENDER_EMAIL') and os.getenv('DATABASE_URL'):
        validation_status['is_production'] = True
    
    return validation_status

def validate_health_parameter(name: str, value: float) -> Tuple[bool, Optional[str]]:
    """Validate a single health parameter against acceptable ranges"""
    if name not in PARAMETER_RANGES:
        return False, f"Unknown parameter: {name}"
    
    min_val, max_val, description = PARAMETER_RANGES[name]
    
    if value < min_val or value > max_val:
        return False, f"{name} must be between {min_val} and {max_val}. {description}"
    
    return True, None

# ==================== ENVIRONMENT VALIDATION STARTUP ====================
env_validation = validate_environment()
if env_validation['errors']:
    logger.critical(f"Environment validation failed: {env_validation['errors']}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', DEFAULT_DATABASE_URL)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV', 'development') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['WTF_CSRF_CHECK_DEFAULT'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF token never expires
app.config['SESSION_PERMANENT'] = True  # Make session permanent for CSRF

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize SQLAlchemy and Flask-Login
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# ==================== MODEL LOADING (LAZY LOAD) ====================

MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')

MODEL_PATHS = [
    os.path.join(MODELS_DIR, "final_diabetes_model.pkl")
]

IMPUTER_PATHS = [
    os.path.join(MODELS_DIR, "diabetes_imputer.pkl")
]

model = None
imputer = None
models_loaded = False

def load_models() -> None:
    """Lazy load ML models on first use (avoids Flask reload issues)"""
    global model, imputer, models_loaded
    
    if models_loaded:
        return
    
    # Try to load model from multiple possible paths
    for model_path in MODEL_PATHS:
        if os.path.exists(model_path):
            try:
                model = joblib.load(model_path)
                logger.info(f"[OK] Model loaded successfully from: {model_path}")
                break
            except Exception as e:
                logger.error(f"[FAIL] Failed to load model from {model_path}: {e}")
    
    # Try to load imputer from multiple possible paths
    for imputer_path in IMPUTER_PATHS:
        if os.path.exists(imputer_path):
            try:
                imputer = joblib.load(imputer_path)
                logger.info(f"[OK] Imputer loaded successfully from: {imputer_path}")
                break
            except Exception as e:
                logger.error(f"[FAIL] Failed to load imputer from {imputer_path}: {e}")
    
    if model is None:
        logger.warning("[WARN] Model not loaded. Predictions will fail.")
    if imputer is None:
        logger.warning("[WARN] Imputer not loaded. Predictions will fail.")
    
    models_loaded = True

FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]

@app.after_request
def add_security_headers(response):
    """Add comprehensive security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com https://fonts.googleapis.com https://fonts.gstatic.com; connect-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https:;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

@login_manager.user_loader
def load_user(user_id):
    try:
        user = get_user_by_userid(int(user_id))
        return user
    except (ValueError, TypeError) as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None

@app.context_processor
def inject_csrf_token():
    """Inject CSRF token into template context"""
    return {'csrf_token': lambda: generate_csrf()}

@app.before_request
def before_request():
    """Initialize session before each request for CSRF protection"""
    session.permanent = True
    session.modified = True

# ==================== ROUTES ====================

@app.route('/')
def home() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup() -> Union[str, Response]:
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            # Validate all fields present and length
            if not email or not username or not password:
                flash("All fields are required.", "error")
                logger.warning(f"Signup: Missing required fields")
                return redirect(url_for('signup'))
            
            if len(email) > 254:
                flash("Email is too long (max 254 characters).", "error")
                logger.warning(f"Signup: Email too long")
                return redirect(url_for('signup'))
            
            if len(username) > 80:
                flash("Username is too long (max 80 characters).", "error")
                logger.warning(f"Signup: Username too long")
                return redirect(url_for('signup'))
            
            if len(password) > 256:
                flash("Password is too long (max 256 characters).", "error")
                logger.warning(f"Signup: Password too long")
                return redirect(url_for('signup'))

            # Email validation with email-validator library
            email_valid, email_error = validate_email(email)
            if not email_valid:
                flash(email_error, "error")
                logger.info(f"Signup: Invalid email format - {email}")
                return redirect(url_for('signup'))
            
            # Username validation (alphanumeric and underscore only, 3-30 chars)
            if not (3 <= len(username) <= 30 and all(c.isalnum() or c in '_-' for c in username)):
                flash("Username must be 3-30 characters (letters, numbers, underscore, hyphen only).", "error")
                logger.info(f"Signup: Invalid username format")
                return redirect(url_for('signup'))
            
            # Password strength validation
            is_strong, strength_msg = is_password_strong(password)
            if not is_strong:
                flash(strength_msg, "error")
                logger.info(f"Signup: Weak password provided")
                return redirect(url_for('signup'))

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                logger.info(f"Signup: Password confirmation mismatch")
                return redirect(url_for('signup'))

            # Check if user exists
            if get_user_by_email(email):
                flash("Email already registered.", "error")
                logger.info(f"Signup: Email already registered - {email}")
                return redirect(url_for('signup'))

            # Hash password and create user
            hashed_password = hash_password(password)
            user_id = create_user(email, username, hashed_password, None)
            user = get_user_by_userid(user_id)
            
            if user:
                login_user(user, remember=True)
                logger.info(f"User signup successful: {email}")
                flash(f"Welcome {username}! Account created successfully.", "success")
                return redirect(url_for('dashboard'))
            else:
                logger.error(f"Signup: Failed to create user for {email}")
                flash("An error occurred during signup. Please try again.", "error")
                return redirect(url_for('signup'))
                
        except Exception as e:
            logger.error(f"Signup error: {str(e)}", exc_info=True)
            flash("An error occurred during signup. Please try again.", "error")
            return redirect(url_for('signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')

            # Input validation
            if not email or len(email) > 254:
                logger.warning(f"Login: Invalid email format provided")
                flash("Invalid email or password.", "error")
                return redirect(url_for('login'))

            user = get_user_by_email(email)
            
            # Check if account is locked due to failed attempts
            if user and is_account_locked(user.userid):
                logger.warning(f"Login: Attempt on locked account - {email}")
                flash("Account temporarily locked due to too many failed login attempts. Please try again after 15 minutes.", "error")
                return redirect(url_for('login'))
            
            if user and verify_password(user.password_hash, password):
                update_user_login(user.userid)
                login_user(user, remember=True)
                logger.info(f"User login successful: {email}")
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(url_for('dashboard'))
            else:
                if user:
                    increment_login_attempts(user.userid)
                    remaining_attempts = 5 - user.login_attempts
                    if remaining_attempts > 0:
                        logger.warning(f"Login: Failed attempt for {email} ({5 - remaining_attempts}/5)")
                        flash(f"Invalid email or password. {remaining_attempts} attempts remaining.", "error")
                    else:
                        logger.warning(f"Login: Account locked after failed attempts - {email}")
                        flash("Too many failed login attempts. Account is temporarily locked for 15 minutes.", "error")
                else:
                    # Don't reveal if email doesn't exist (security best practice)
                    logger.info(f"Login: Attempt with non-existent email - {email}")
                    flash("Invalid email or password.", "error")
                return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Login error: {str(e)}", exc_info=True)
            flash("An error occurred during login. Please try again.", "error")
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard() -> Union[str, Response]:
    """Dashboard with user statistics and prediction history"""
    try:
        # Get predictions in ascending order (oldest first) for timeline chart
        predictions = get_user_predictions(current_user.userid, ascending=True)
        
        # Convert predictions to dictionaries for chart calculations
        pred_dicts = []
        for pred in predictions:
            pred_dicts.append({
                'id': pred.id,
                'userid': pred.userid,
                'pregnancies': pred.pregnancies,
                'glucose': pred.glucose,
                'blood_pressure': pred.blood_pressure,
                'skin_thickness': pred.skin_thickness,
                'insulin': pred.insulin,
                'bmi': pred.bmi,
                'diabetes_pedigree_function': pred.diabetes_pedigree_function,
                'age': pred.age,
                'prediction': pred.outcome,
                'created_at': pred.created_at if pred.created_at else datetime.utcnow()
            })
        
        # Get chart data and statistics
        if pred_dicts:
            chart_data = get_chart_data(pred_dicts)
            risk_dist = calculate_risk_distribution(pred_dicts)
            
            stats = {
                'total_tests': len(pred_dicts),
                'total_predictions': len(pred_dicts),  # For template compatibility
                'positive_count': risk_dist.get('positive', 0),
                'negative_count': risk_dist.get('negative', 0),
                'positive_percentage': round(risk_dist.get('positive_percentage', 0), 1),
                'negative_percentage': round(risk_dist.get('negative_percentage', 0), 1)
            }
            # Get 5 most recent predictions (reverse order)
            recent_predictions = get_user_predictions(current_user.userid, limit=5, ascending=False)
        else:
            chart_data = {
                'timeline': [],
                'risk_distribution': {'positive': 0, 'negative': 0},
                'health_metrics': [],
                'summary': {}
            }
            stats = {
                'total_tests': 0,
                'total_predictions': 0,  # For template compatibility
                'positive_count': 0,
                'negative_count': 0,
                'positive_percentage': 0,
                'negative_percentage': 0
            }
            recent_predictions = []
        
        logger.info(f"Dashboard loaded for user {current_user.userid}")
        return render_template(
            'dashboard.html',
            username=current_user.username,
            stats=stats,
            recent_predictions=recent_predictions,
            chart_data=chart_data
        )
    except Exception as e:
        logger.error(f"Dashboard error for user {current_user.userid}: {str(e)}", exc_info=True)
        flash("Error loading dashboard.", "error")
        return redirect(url_for('predict'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict() -> Union[str, Response]:
    if request.method == 'GET':
        return render_template('index.html', username=current_user.username)

    # POST request
    try:
        # Load models on first use (lazy loading)
        load_models()
        
        # 1. Extract and validate values from form
        raw_values = []
        for i, name in enumerate(FEATURE_NAMES):
            value_str = request.form.get(name, '').strip()
            if not value_str:
                logger.warning(f"Predict: Missing field {name} for user {current_user.userid}")
                flash(f"Missing required field: {name}", "error")
                return redirect(url_for('predict'))
            try:
                value = float(value_str)
                
                # Validate against parameter ranges
                is_valid, error_msg = validate_health_parameter(name, value)
                if not is_valid:
                    logger.warning(f"Predict: {error_msg} for user {current_user.userid}")
                    flash(error_msg, "error")
                    return redirect(url_for('predict'))
                
                raw_values.append(value)
            except ValueError:
                logger.warning(f"Predict: Invalid value for {name}: '{value_str}' for user {current_user.userid}")
                flash(f"Invalid value for {name}: must be a number", "error")
                return redirect(url_for('predict'))
        
        if model is None or imputer is None:
            logger.error(f"Predict: Models not loaded for user {current_user.userid}")
            flash("Models not available. Predictions unavailable.", "error")
            return redirect(url_for('predict'))
        
        # 2. Convert to DataFrame (so feature names match)
        input_df = pd.DataFrame([raw_values], columns=FEATURE_NAMES)
        
        # 3. Apply Imputer
        imputed_data = imputer.transform(input_df)
        
        # 4. Generate Prediction and Probability
        prediction = int(model.predict(imputed_data)[0])
        probability = float(model.predict_proba(imputed_data)[0][1] * 100)

        # 5. Format Output
        if prediction == 1:
            result_label = "Diabetic (Positive)"
            risk_class = "danger"
        else:
            result_label = "Non-Diabetic (Negative)"
            risk_class = "success"

        # Generate tailored advice based on parameters
        advice = []
        if raw_values[5] > 30:  # BMI
            advice.append("Consult a doctor if BMI > 30 - indicates obesity risk.")
        if raw_values[1] > 140:  # Glucose
            advice.append("High glucose levels detected. Monitor blood sugar regularly.")
        if raw_values[2] > 90:  # BloodPressure
            advice.append("Elevated blood pressure. Consider lifestyle changes or medical advice.")
        if raw_values[4] > 166:  # Insulin
            advice.append("High insulin levels. Consult an endocrinologist.")
        if raw_values[0] > 5:  # Pregnancies
            advice.append("Multiple pregnancies may increase diabetes risk. Regular check-ups recommended.")
        if raw_values[7] > 45:  # Age
            advice.append("Age over 45 increases diabetes risk. Annual screenings advised.")
        if raw_values[6] > 0.5:  # DiabetesPedigreeFunction
            advice.append("Family history suggests higher risk. Genetic counseling may help.")

        # Save prediction to database
        prediction_data = {
            "pregnancies": float(raw_values[0]),
            "glucose": float(raw_values[1]),
            "blood_pressure": float(raw_values[2]),
            "skin_thickness": float(raw_values[3]),
            "insulin": float(raw_values[4]),
            "bmi": float(raw_values[5]),
            "diabetes_pedigree_function": float(raw_values[6]),
            "age": float(raw_values[7]),
            "prediction": prediction,
        }
        prediction_id = save_prediction(current_user.userid, current_user.username, prediction_data)
        logger.info(f"Prediction saved: ID {prediction_id} for user {current_user.userid}")

        return render_template(
            'result.html',
            prediction_text=result_label,
            confidence=f"{probability:.2f}%",
            risk_class=risk_class,
            username=current_user.username,
            advice=advice
        )

    except Exception as e:
        logger.error(f"Prediction error for user {current_user.userid}: {str(e)}", exc_info=True)
        flash(f"An error occurred during prediction. Please try again.", "error")
        return redirect(url_for('predict'))

@app.route('/predictions_history')
@login_required
def predictions_history() -> Union[str, Response]:
    """View all user predictions in reverse chronological order"""
    try:
        # Get predictions in descending order (newest first) for history view
        predictions = get_user_predictions(current_user.userid, ascending=False)
        total_count = len(predictions)
        logger.info(f"Predictions history accessed for user {current_user.userid}")
        return render_template(
            'predictions_history.html',
            predictions=predictions,
            total_count=total_count,
            username=current_user.username
        )
    except Exception as e:
        logger.error(f"Predictions history error for user {current_user.userid}: {str(e)}", exc_info=True)
        flash("Error loading predictions history.", "error")
        return redirect(url_for('dashboard'))

@app.route('/logout')
@login_required
def logout() -> Response:
    logger.info(f"User logout: {current_user.userid}")
    logout_user()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(400)
def bad_request(error) -> tuple[str, int]:
    """Handle 400 Bad Request errors"""
    logger.warning(f"400 Bad Request: {error}")
    return render_template('400.html' if os.path.exists(os.path.join(BASE_DIR, 'Templates', '400.html')) else '404.html'), 400

@app.errorhandler(403)
def forbidden(error) -> tuple[str, int]:
    """Handle 403 Forbidden errors"""
    logger.warning(f"403 Forbidden: {error}")
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(error) -> tuple[str, int]:
    """Handle 404 Not Found errors"""
    logger.warning(f"404 Not Found: {error}")
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error) -> tuple[str, int]:
    """Handle 500 Internal Server errors"""
    logger.error(f"500 Internal Server Error: {error}", exc_info=True)
    return render_template('500.html'), 500

@app.errorhandler(Exception)
def handle_exception(e) -> tuple[str, int]:
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return render_template('500.html'), 500

# ==================== DATABASE INITIALIZATION ====================

def initialize_database():
    """Initialize Flask app context and create database tables"""
    try:
        with app.app_context():
            # Ensure data directory exists
            os.makedirs(os.path.dirname(SQLITE_PATH), exist_ok=True)

            # Check if database file exists and is empty
            if os.path.exists(SQLITE_PATH):
                if os.path.getsize(SQLITE_PATH) == 0:
                    logger.warning(f"Database file is empty, removing: {SQLITE_PATH}")
                    try:
                        os.remove(SQLITE_PATH)
                    except Exception as e:
                        logger.warning(f"Could not remove empty DB file: {e}")

            logger.info("Creating database tables...")
            db.create_all()
            logger.info(f"[OK] Database initialized successfully: {app.config['SQLALCHEMY_DATABASE_URI']}")

            # Verify tables were created
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"Database tables: {tables}")

    except Exception as e:
        logger.error(f"[ERROR] Database initialization error: {e}", exc_info=True)
        # Try SQLite fallback if using MySQL/other DB
        if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite://'):
            logger.warning("Attempting SQLite fallback...")
            app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{SQLITE_PATH}"
            try:
                with app.app_context():
                    db.engine.dispose()
                    logger.info("Creating database tables (fallback)...")
                    db.create_all()
                logger.info(f"[OK] Fallback database initialized: {app.config['SQLALCHEMY_DATABASE_URI']}")
            except Exception as fallback_error:
                logger.critical(f"[ERROR] Fallback initialization failed: {fallback_error}", exc_info=True)
                raise

    # Load ML models on startup
    logger.info("Loading ML models at startup...")
    load_models()

if __name__ == "__main__":
    initialize_database()
    logger.info("=" * 60)
    logger.info("Starting DiaPredict Flask Application")
    logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    logger.info(f"Debug Mode: {os.getenv('FLASK_DEBUG', 'False')}")
    logger.info(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    logger.info(">>> Flask app running on http://0.0.0.0:5000")
    logger.info("=" * 60)
    # Disable auto-reloader to prevent model reloading issues
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
