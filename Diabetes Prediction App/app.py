from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
import numpy as np
import pickle
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'demo-secret-key-change-in-production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Load ML model and scaler
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "hybrid_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "scaler.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    print("✓ Model loaded successfully")
except Exception as e:
    print(f"✗ Error loading model: {e}")
    model = None
    scaler = None

FEATURE_NAMES = [
    "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
    "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
]

# ==================== MOCK USER CLASS ====================

class User(UserMixin):
    def __init__(self, user_id, email, username):
        self.id = user_id
        self.email = email
        self.username = username

# Store demo users in memory
demo_users = {}

@login_manager.user_loader
def load_user(user_id):
    return demo_users.get(user_id)

# ==================== HELPER FUNCTIONS ====================

def create_demo_user(email, username):
    """Create a demo user in memory"""
    user_id = f"user_{len(demo_users) + 1}"
    user = User(user_id, email, username)
    demo_users[user_id] = user
    return user

# ==================== HOME & STATIC ROUTES ====================

@app.route('/')
def home():
    """Home page - redirect based on login status"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ==================== AUTHENTICATION ROUTES ====================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration (DEMO - no data saved)"""
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
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('signup.html')

        if not any(c.isupper() for c in password):
            flash('Password must contain at least one uppercase letter.', 'error')
            return render_template('signup.html')

        if not any(c.islower() for c in password):
            flash('Password must contain at least one lowercase letter.', 'error')
            return render_template('signup.html')

        if not any(c.isdigit() for c in password):
            flash('Password must contain at least one digit.', 'error')
            return render_template('signup.html')

        # Check password match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        try:
            # Create demo user (no database)
            user = create_demo_user(email, username)

            # Flash message
            flash(f'✓ Account created successfully! Logging you in...', 'success')

            # Auto-login
            login_user(user, remember=True)

            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f'Error during registration: {str(e)}', 'error')
            return render_template('signup.html')

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login (DEMO - any credentials work)"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Validation
        if not email or not password:
            flash('Email and password are required.', 'error')
            return render_template('login.html')

        # DEMO MODE: Accept any login credentials
        user_id = f"user_{hash(email) % 10000}"
        username = email.split('@')[0]

        user = User(user_id, email, username)
        demo_users[user_id] = user

        login_user(user, remember=True)
        flash(f'Welcome, {username}! 🎉', 'success')

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

            # Make prediction if model is loaded
            if model and scaler:
                input_array = np.array([values])
                scaled_input = scaler.transform(input_array)
                prediction = model.predict(scaled_input)[0]

                if int(prediction) == 1:
                    prediction_text = "The model predicts: Diabetes Positive"
                else:
                    prediction_text = "The model predicts: Diabetes Negative"
            else:
                prediction_text = "The model predicts: Diabetes Negative (Demo Mode)"

            return render_template(
                'result.html',
                prediction_text=prediction_text,
                username=current_user.username
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
    """User dashboard with demo data"""
    # Generate demo data for visualization
    demo_stats = {
        "total_predictions": 5,
        "positive_count": 2,
        "negative_count": 3,
        "positive_percentage": 40.0,
        "negative_percentage": 60.0,
        "avg_glucose": 125.5,
        "avg_bmi": 27.8,
        "avg_blood_pressure": 82.4,
        "avg_insulin": 95.3,
        "last_prediction_date": datetime.now().isoformat()
    }

    return render_template(
        'dashboard.html',
        username=current_user.username,
        stats=demo_stats,
        prediction_count=demo_stats["total_predictions"]
    )


@app.route('/dashboard/api/chart-data')
@login_required
def get_chart_data_api():
    """API endpoint for chart data (DEMO)"""
    try:
        # Generate demo chart data
        demo_data = {
            "timeline": [
                {"index": 1, "date": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d"), "time": "10:30:00", "risk": 0, "risk_label": "Negative ✓", "glucose": 88.5, "bmi": 23.2, "blood_pressure": 75.0, "insulin": 42.5},
                {"index": 2, "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "time": "14:15:00", "risk": 0, "risk_label": "Negative ✓", "glucose": 105.2, "bmi": 24.8, "blood_pressure": 78.5, "insulin": 68.2},
                {"index": 3, "date": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "time": "11:45:00", "risk": 1, "risk_label": "Positive ⚠️", "glucose": 145.8, "bmi": 28.5, "blood_pressure": 85.2, "insulin": 125.3},
                {"index": 4, "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "time": "09:20:00", "risk": 0, "risk_label": "Negative ✓", "glucose": 92.1, "bmi": 25.5, "blood_pressure": 76.8, "insulin": 55.7},
                {"index": 5, "date": datetime.now().strftime("%Y-%m-%d"), "time": "15:30:00", "risk": 1, "risk_label": "Positive ⚠️", "glucose": 165.5, "bmi": 32.1, "blood_pressure": 88.9, "insulin": 142.6},
            ],
            "risk_distribution": {
                "positive": 2,
                "negative": 3,
                "total": 5,
                "positive_percentage": 40.0,
                "negative_percentage": 60.0
            },
            "health_metrics": [
                {
                    "period": "all_time",
                    "glucose": 119.42,
                    "bmi": 26.82,
                    "blood_pressure": 80.88,
                    "insulin": 86.86
                }
            ],
            "summary": {
                "total_tests": 5,
                "positive_count": 2,
                "negative_count": 3,
                "positive_percentage": 40.0,
                "negative_percentage": 60.0
            }
        }

        return jsonify(demo_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/predictions')
@login_required
def predictions_history():
    """View all predictions history (DEMO)"""
    # Demo prediction history
    demo_predictions = [
        {
            'created_at_str': (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
            'glucose': 88.5,
            'bmi': 23.2,
            'blood_pressure': 75.0,
            'insulin': 42.5,
            'prediction': 0,
            'risk_label': "✓ Negative"
        },
        {
            'created_at_str': (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
            'glucose': 105.2,
            'bmi': 24.8,
            'blood_pressure': 78.5,
            'insulin': 68.2,
            'prediction': 0,
            'risk_label': "✓ Negative"
        },
        {
            'created_at_str': (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
            'glucose': 145.8,
            'bmi': 28.5,
            'blood_pressure': 85.2,
            'insulin': 125.3,
            'prediction': 1,
            'risk_label': "⚠️ Positive"
        },
        {
            'created_at_str': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
            'glucose': 92.1,
            'bmi': 25.5,
            'blood_pressure': 76.8,
            'insulin': 55.7,
            'prediction': 0,
            'risk_label': "✓ Negative"
        },
        {
            'created_at_str': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'glucose': 165.5,
            'bmi': 32.1,
            'blood_pressure': 88.9,
            'insulin': 142.6,
            'prediction': 1,
            'risk_label': "⚠️ Positive"
        },
    ]

    return render_template(
        'predictions_history.html',
        predictions=demo_predictions,
        username=current_user.username,
        total_count=len(demo_predictions)
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
    print("🚀 Starting DiaPredict Demo...")
    print("✓ No database required - DEMO MODE")
    print("✓ Access at: http://localhost:5000")
    print("✓ Any email/password will work for login")
    app.run(debug=True, host="0.0.0.0", port=5000)
