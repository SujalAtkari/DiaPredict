from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/diapredict")

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Verify connection
    client.admin.command('ping')
    db = client.diapredict
    print("✓ Connected to MongoDB")
except ServerSelectionTimeoutError:
    print("✗ Failed to connect to MongoDB. Make sure MongoDB is running.")
    db = None

# Collections
users_collection = db.users if db else None
predictions_collection = db.predictions if db else None


# ==================== USER MANAGEMENT ====================

def create_user(email, username, password_hash, verification_token):
    """Create a new user in the database"""
    if not users_collection:
        raise Exception("Database not connected")

    user = {
        "email": email.lower(),
        "username": username,
        "password_hash": password_hash,
        "is_verified": False,
        "verification_token": verification_token,
        "verification_token_expiry": datetime.utcnow() + timedelta(hours=24),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_login": None,
        "login_attempts": 0,
        "last_login_attempt": None
    }

    result = users_collection.insert_one(user)
    return str(result.inserted_id)


def get_user_by_email(email):
    """Get user by email"""
    if not users_collection:
        return None
    return users_collection.find_one({"email": email.lower()})


def get_user_by_id(user_id):
    """Get user by ID"""
    if not users_collection:
        return None
    try:
        return users_collection.find_one({"_id": ObjectId(user_id)})
    except:
        return None


def verify_user(email):
    """Mark user as verified"""
    if not users_collection:
        return False

    result = users_collection.update_one(
        {"email": email.lower()},
        {
            "$set": {
                "is_verified": True,
                "verification_token": None,
                "verification_token_expiry": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    return result.modified_count > 0


def get_user_by_verification_token(token):
    """Get user by verification token"""
    if not users_collection:
        return None

    user = users_collection.find_one({
        "verification_token": token,
        "verification_token_expiry": {"$gt": datetime.utcnow()}
    })
    return user


def update_last_login(user_id):
    """Update user's last login time"""
    if not users_collection:
        return False

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "last_login": datetime.utcnow(),
                "login_attempts": 0,
                "last_login_attempt": None,
                "updated_at": datetime.utcnow()
            }
        }
    )
    return result.modified_count > 0


def record_login_attempt(email, success=False):
    """Record login attempt for rate limiting"""
    if not users_collection:
        return

    if success:
        users_collection.update_one(
            {"email": email.lower()},
            {
                "$set": {
                    "login_attempts": 0,
                    "last_login_attempt": None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
    else:
        users_collection.update_one(
            {"email": email.lower()},
            {
                "$inc": {"login_attempts": 1},
                "$set": {
                    "last_login_attempt": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )


# ==================== PREDICTION MANAGEMENT ====================

def save_prediction(user_id, health_data, prediction, prediction_text):
    """Save a prediction to the database"""
    if not predictions_collection:
        raise Exception("Database not connected")

    prediction_doc = {
        "user_id": ObjectId(user_id),
        "pregnancies": float(health_data.get("Pregnancies", 0)),
        "glucose": float(health_data.get("Glucose", 0)),
        "blood_pressure": float(health_data.get("BloodPressure", 0)),
        "skin_thickness": float(health_data.get("SkinThickness", 0)),
        "insulin": float(health_data.get("Insulin", 0)),
        "bmi": float(health_data.get("BMI", 0)),
        "diabetes_pedigree_function": float(health_data.get("DiabetesPedigreeFunction", 0)),
        "age": int(health_data.get("Age", 0)),
        "prediction": int(prediction),
        "prediction_text": prediction_text,
        "created_at": datetime.utcnow()
    }

    result = predictions_collection.insert_one(prediction_doc)
    return str(result.inserted_id)


def get_user_predictions(user_id, limit=100):
    """Get all predictions for a user"""
    if not predictions_collection:
        return []

    try:
        predictions = list(predictions_collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).limit(limit))

        # Convert ObjectId to string for JSON serialization
        for pred in predictions:
            pred["_id"] = str(pred["_id"])
            pred["user_id"] = str(pred["user_id"])

        return predictions
    except:
        return []


def get_prediction_by_id(prediction_id):
    """Get a specific prediction"""
    if not predictions_collection:
        return None

    try:
        pred = predictions_collection.find_one({"_id": ObjectId(prediction_id)})
        if pred:
            pred["_id"] = str(pred["_id"])
            pred["user_id"] = str(pred["user_id"])
        return pred
    except:
        return None


def delete_prediction(prediction_id, user_id):
    """Delete a prediction (only if it belongs to the user)"""
    if not predictions_collection:
        return False

    try:
        result = predictions_collection.delete_one({
            "_id": ObjectId(prediction_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0
    except:
        return False


def get_user_statistics(user_id):
    """Get statistics for a user's predictions"""
    if not predictions_collection:
        return {}

    try:
        predictions = list(predictions_collection.find({"user_id": ObjectId(user_id)}))

        if not predictions:
            return {
                "total_predictions": 0,
                "positive_count": 0,
                "negative_count": 0,
                "positive_percentage": 0,
                "negative_percentage": 0,
                "avg_glucose": 0,
                "avg_bmi": 0,
                "avg_blood_pressure": 0,
                "avg_insulin": 0,
                "last_prediction_date": None
            }

        total = len(predictions)
        positive = sum(1 for p in predictions if p["prediction"] == 1)
        negative = total - positive

        avg_glucose = sum(p["glucose"] for p in predictions) / total
        avg_bmi = sum(p["bmi"] for p in predictions) / total
        avg_bp = sum(p["blood_pressure"] for p in predictions) / total
        avg_insulin = sum(p["insulin"] for p in predictions) / total

        last_date = max(p["created_at"] for p in predictions) if predictions else None

        return {
            "total_predictions": total,
            "positive_count": positive,
            "negative_count": negative,
            "positive_percentage": round((positive / total) * 100, 2),
            "negative_percentage": round((negative / total) * 100, 2),
            "avg_glucose": round(avg_glucose, 2),
            "avg_bmi": round(avg_bmi, 2),
            "avg_blood_pressure": round(avg_bp, 2),
            "avg_insulin": round(avg_insulin, 2),
            "last_prediction_date": last_date.isoformat() if last_date else None
        }
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}


def get_user_predictions_for_charts(user_id, limit=30):
    """Get predictions formatted for chart display"""
    if not predictions_collection:
        return []

    try:
        predictions = list(predictions_collection.find(
            {"user_id": ObjectId(user_id)}
        ).sort("created_at", -1).limit(limit))

        # Reverse to show oldest first (for line charts)
        predictions.reverse()

        # Format for charts
        chart_data = []
        for pred in predictions:
            chart_data.append({
                "date": pred["created_at"].strftime("%Y-%m-%d %H:%M"),
                "risk": pred["prediction"],
                "glucose": pred["glucose"],
                "bmi": pred["bmi"],
                "blood_pressure": pred["blood_pressure"],
                "insulin": pred["insulin"]
            })

        return chart_data
    except Exception as e:
        print(f"Error getting chart data: {e}")
        return []


# ==================== DATABASE INITIALIZATION ====================

def init_database():
    """Initialize database indexes"""
    if not db:
        print("Database not connected, skipping initialization")
        return

    try:
        # Create indexes for faster queries
        users_collection.create_index("email", unique=True)
        users_collection.create_index("username", unique=True)
        users_collection.create_index("verification_token")

        predictions_collection.create_index("user_id")
        predictions_collection.create_index("created_at")
        predictions_collection.create_index([("user_id", 1), ("created_at", -1)])

        print("✓ Database indexes created")
    except Exception as e:
        print(f"Error creating indexes: {e}")
