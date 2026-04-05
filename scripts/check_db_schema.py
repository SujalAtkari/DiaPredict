#!/usr/bin/env python
import sqlite3
import os
import sys

db_path = 'diapredict.db'
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get prediction table schema
        cursor.execute("PRAGMA table_info(prediction)")
        columns = cursor.fetchall()
        
        print("PREDICTION TABLE SCHEMA:")
        print("-" * 60)
        for col in columns:
            print(f"  {col[1]:30s} {col[2]:15s} {'NOT NULL' if col[3] else 'NULLABLE':12s}")
        
        # Check if created_at exists
        col_names = [col[1] for col in columns]
        if 'created_at' in col_names:
            print("\n✓ created_at column EXISTS")
            sys.exit(0)
        else:
            print("\n✗ created_at column IS MISSING - NEED TO RECREATE DATABASE")
            sys.exit(1)
        
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")
        sys.exit(1)
else:
    print("Database file does not exist - will be created on startup")
    sys.exit(2)
