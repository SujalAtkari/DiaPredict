#!/usr/bin/env python3
"""
Database reset script - Use this to reset the database when it's corrupted or empty.
Run this before starting the Flask app.
"""

import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'diapredict.db')
DATA_DIR = os.path.dirname(DB_PATH)

def reset_database():
    """Remove corrupted/empty database file and create fresh one"""
    try:
        # Ensure data directory exists
        os.makedirs(DATA_DIR, exist_ok=True)
        logger.info(f"Data directory: {DATA_DIR}")

        # Remove old database file if it exists
        if os.path.exists(DB_PATH):
            size = os.path.getsize(DB_PATH)
            logger.info(f"Found existing database file ({size} bytes): {DB_PATH}")
            try:
                os.remove(DB_PATH)
                logger.info("✓ Removed old database file")
            except Exception as e:
                logger.error(f"❌ Failed to remove database file: {e}")
                logger.info("The file may be locked by another process.")
                return False
        else:
            logger.info(f"No existing database file found at {DB_PATH}")

        # Initialize Flask app and create tables
        from app import app, db
        from database_sql import User, Prediction

        logger.info("Initializing Flask app context...")
        with app.app_context():
            logger.info("Creating database tables...")
            db.create_all()
            logger.info("✓ Database tables created")

            # Verify tables exist
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            logger.info(f"✓ Verified tables in database: {tables}")

            if 'user' in tables and 'prediction' in tables:
                logger.info("\n✅ Database reset successfully!")
                logger.info(f"Database location: {DB_PATH}")
                logger.info("\nYou can now start the Flask app with: python app.py")
                return True
            else:
                logger.error("❌ Tables were not created properly")
                return False

    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}", exc_info=True)
        return False

if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)
