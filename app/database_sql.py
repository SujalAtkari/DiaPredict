from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Optional, List
import os
import atexit

# Load environment variables from .env file in current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')
load_dotenv(ENV_PATH)

db = SQLAlchemy()

# Auto-cleanup: Close database connections on exit
def cleanup_db():
    """Close database connections on application shutdown"""
    try:
        db.engine.dispose()
    except:
        pass

atexit.register(cleanup_db)

# SQLAlchemy models
class User(UserMixin, db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False, default='other')
    password_hash = db.Column(db.String(128))
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(128))
    verification_token_expiry = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    login_attempts = db.Column(db.Integer, default=0)
    last_login_attempt = db.Column(db.DateTime)
    predictions = db.relationship('Prediction', foreign_keys='Prediction.userid', backref='user', lazy=True)
    
    @property
    def id(self):
        """Property for Flask-Login compatibility (expects 'id' attribute)"""
        return self.userid
    
    def get_id(self):
        """Required by Flask-Login: return user id as string"""
        return str(self.userid)

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    username = db.Column(db.String(80), nullable=False)  # Store username as data, not FK
    pregnancies = db.Column(db.Float)
    glucose = db.Column(db.Float)
    blood_pressure = db.Column(db.Float)
    skin_thickness = db.Column(db.Float)
    insulin = db.Column(db.Float)
    bmi = db.Column(db.Float)
    diabetes_pedigree_function = db.Column(db.Float)
    age = db.Column(db.Float)
    outcome = db.Column(db.Integer)  # 0 = not diabetic, 1 = diabetic
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Track prediction timestamp

# ==================== USER MANAGEMENT ====================

def create_user(email: str, username: str, gender: str, password_hash: str, verification_token: Optional[str]) -> int:
    user = User(
        email=email.lower(),
        username=username,
        gender=gender,
        password_hash=password_hash,
        verification_token=verification_token,
        verification_token_expiry=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(user)
    db.session.commit()
    return user.userid

def get_user_by_email(email: str) -> Optional[User]:
    return User.query.filter_by(email=email.lower()).first()

def get_user_by_userid(userid: int) -> Optional[User]:
    return User.query.get(userid)

def verify_user(email: str) -> bool:
    user = User.query.filter_by(email=email.lower()).first()
    if user:
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expiry = None
        user.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    return False

def get_user_by_verification_token(token: str) -> Optional[User]:
    return User.query.filter_by(verification_token=token).filter(
        User.verification_token_expiry > datetime.utcnow()
    ).first()

def update_user_login(userid: int) -> None:
    user = User.query.get(userid)
    if user:
        user.last_login = datetime.utcnow()
        user.login_attempts = 0
        db.session.commit()

def increment_login_attempts(userid: int) -> None:
    """Track failed login attempts for rate limiting"""
    user = User.query.get(userid)
    if user:
        user.login_attempts += 1
        user.last_login_attempt = datetime.utcnow()
        db.session.commit()


def is_account_locked(userid: int, max_attempts: int = 5, lockout_minutes: int = 15) -> bool:
    """
    Check if account is locked due to too many failed login attempts.
    Returns True if locked, False otherwise.
    """
    user = User.query.get(userid)
    if not user:
        return False
    
    # No lockout if no failed attempts
    if user.login_attempts < max_attempts:
        return False
    
    # Check if lockout period has expired
    if user.last_login_attempt:
        lockout_expiry = user.last_login_attempt + timedelta(minutes=lockout_minutes)
        if datetime.utcnow() > lockout_expiry:
            # Lockout period expired, reset attempts
            user.login_attempts = 0
            db.session.commit()
            return False
    
    # Account is locked
    return True

# ==================== PREDICTION MANAGEMENT ====================

def save_prediction(userid: int, username: str, prediction_data: dict) -> int:
    prediction = Prediction(
        userid=userid,
        username=username,
        pregnancies=prediction_data.get('pregnancies'),
        glucose=prediction_data.get('glucose'),
        blood_pressure=prediction_data.get('blood_pressure'),
        skin_thickness=prediction_data.get('skin_thickness'),
        insulin=prediction_data.get('insulin'),
        bmi=prediction_data.get('bmi'),
        diabetes_pedigree_function=prediction_data.get('diabetes_pedigree_function'),
        age=prediction_data.get('age'),
        outcome=prediction_data.get('prediction')  # 0 or 1
    )
    db.session.add(prediction)
    db.session.commit()
    return prediction.id

def get_user_predictions(userid: int, username: Optional[str] = None, limit: Optional[int] = None, ascending: bool = True) -> List[Prediction]:
    """
    Fetch user predictions.
    
    Args:
        userid: User ID
        username: Optional username filter to avoid showing stale records if user IDs are reused
        limit: Maximum number of predictions to return
        ascending: If True, return oldest first (for charts). If False, newest first (for history).
    """
    query = Prediction.query.filter_by(userid=userid)
    if username:
        query = query.filter_by(username=username)
    
    if ascending:
        query = query.order_by(Prediction.created_at.asc())  # Oldest first for charts
    else:
        query = query.order_by(Prediction.created_at.desc())  # Newest first for history
    
    if limit:
        query = query.limit(limit)
    
    return query.all()
