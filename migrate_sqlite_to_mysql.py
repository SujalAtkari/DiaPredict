#!/usr/bin/env python3
"""
Migrate data from SQLite to MySQL database
Run this before switching DATABASE_URL to MySQL in .env
"""

import sqlite3
import sys
import os
from datetime import datetime

# Add app directory to path
app_dir = r"c:\Academic Projects\DIABETES-DETECTION\Diabetes Prediction App"
sys.path.insert(0, app_dir)

from database_sql import db, User, Prediction
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(app_dir, '.env'))

# Verify MySQL is configured
if 'mysql' not in os.getenv('DATABASE_URL', '').lower():
    print("ERROR: DATABASE_URL in .env must point to MySQL!")
    print("Current value:", os.getenv('DATABASE_URL'))
    sys.exit(1)

# Initialize Flask app with MySQL config
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 
    'mysql+pymysql://root:password@localhost:3306/diapredict')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

print("=" * 80)
print("SQLite to MySQL Migration Tool")
print("=" * 80)

sqlite_path = os.path.join(app_dir, 'diapredict.db')

if not os.path.exists(sqlite_path):
    print("ERROR: SQLite database not found at:", sqlite_path)
    sys.exit(1)

print(f"\n[1] Reading data from SQLite: {sqlite_path}")

# Connect to SQLite
sqlite_conn = sqlite3.connect(sqlite_path)
sqlite_conn.row_factory = sqlite3.Row
sqlite_cursor = sqlite_conn.cursor()

# Read users
sqlite_cursor.execute("SELECT * FROM user")
users = sqlite_cursor.fetchall()
print(f"  Found {len(users)} users")

# Read predictions
sqlite_cursor.execute("SELECT * FROM prediction")
predictions = sqlite_cursor.fetchall()
print(f"  Found {len(predictions)} predictions")

sqlite_conn.close()

print(f"\n[2] Creating MySQL tables...")

with app.app_context():
    try:
        db.create_all()
        print("  ✓ MySQL tables created successfully")
    except Exception as e:
        print(f"  ERROR creating tables: {e}")
        sys.exit(1)

print(f"\n[3] Migrating users to MySQL...")

with app.app_context():
    try:
        for user_row in users:
            user = User(
                userid=user_row['userid'],
                email=user_row['email'],
                username=user_row['username'],
                password_hash=user_row['password_hash'],
                is_verified=user_row['is_verified'],
                verification_token=user_row['verification_token'],
                verification_token_expiry=user_row['verification_token_expiry'],
                created_at=user_row['created_at'],
                updated_at=user_row['updated_at'],
                last_login=user_row['last_login'],
                login_attempts=user_row['login_attempts'],
                last_login_attempt=user_row['last_login_attempt']
            )
            db.session.merge(user)
        
        db.session.commit()
        print(f"  ✓ {len(users)} users migrated")
    except Exception as e:
        db.session.rollback()
        print(f"  ERROR migrating users: {e}")
        sys.exit(1)

print(f"\n[4] Migrating predictions to MySQL...")

with app.app_context():
    try:
        for pred_row in predictions:
            prediction = Prediction(
                id=pred_row['id'],
                userid=pred_row['userid'],
                username=pred_row['username'],
                pregnancies=pred_row['pregnancies'],
                glucose=pred_row['glucose'],
                blood_pressure=pred_row['blood_pressure'],
                skin_thickness=pred_row['skin_thickness'],
                insulin=pred_row['insulin'],
                bmi=pred_row['bmi'],
                diabetes_pedigree_function=pred_row['diabetes_pedigree_function'],
                age=pred_row['age'],
                outcome=pred_row['outcome'],
                created_at=pred_row['created_at']
            )
            db.session.merge(prediction)
        
        db.session.commit()
        print(f"  ✓ {len(predictions)} predictions migrated")
    except Exception as e:
        db.session.rollback()
        print(f"  ERROR migrating predictions: {e}")
        sys.exit(1)

print("\n" + "=" * 80)
print("MIGRATION COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("1. Verify data in MySQL:")
print("   SELECT * FROM diapredict.user;")
print("   SELECT * FROM diapredict.prediction;")
print("\n2. Restart Flask app with: python app.py")
print("=" * 80)
