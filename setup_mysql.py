#!/usr/bin/env python3
"""
Setup MySQL Database for DiaPredict - Fresh Start
"""

import pymysql
import sys
import os

print("=" * 80)
print("DiaPredict MySQL Setup - Fresh Start")
print("=" * 80)

# Try both passwords
passwords = ["MyPass123!", "root@123", ""]
connection = None
used_password = None

for password in passwords:
    try:
        print(f"\n[1] Attempting MySQL connection with password: '{password if password else '(empty)'}'")
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=password,
            port=3306
        )
        used_password = password
        print(f"  [OK] Connected to MySQL successfully!")
        break
    except Exception as e:
        error_msg = str(e).replace(chr(10), " ")[:100]
        print(f"  [FAIL] {error_msg}")
        continue

if not connection:
    print("\n[ERROR] Could not connect with any password!")
    print("\nPlease check:")
    print("  - MySQL is running (check Services or MySQL Workbench)")
    print("  - Root password is correct")
    print("  - MySQL is listening on localhost:3306")
    sys.exit(1)

cursor = connection.cursor()

try:
    print(f"\n[2] Dropping existing database (if exists)...")
    try:
        cursor.execute("DROP DATABASE IF EXISTS diapredict")
        print(f"  [OK] Done")
    except Exception as e:
        print(f"  [OK] Database did not exist")
    
    print(f"\n[3] Creating fresh database...")
    cursor.execute("CREATE DATABASE diapredict")
    print(f"  [OK] Database created")
    
    print(f"\n[4] Using diapredict database...")
    cursor.execute("USE diapredict")
    print(f"  [OK] Selected")
    
    print(f"\n[5] Creating user table...")
    cursor.execute("""
    CREATE TABLE user (
        userid INT PRIMARY KEY AUTO_INCREMENT,
        email VARCHAR(120) UNIQUE NOT NULL,
        username VARCHAR(80) UNIQUE NOT NULL,
        password_hash VARCHAR(128),
        is_verified BOOLEAN DEFAULT FALSE,
        verification_token VARCHAR(128),
        verification_token_expiry DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        last_login DATETIME,
        login_attempts INT DEFAULT 0,
        last_login_attempt DATETIME
    )
    """)
    print(f"  [OK] user table created")
    
    print(f"\n[6] Creating prediction table...")
    cursor.execute("""
    CREATE TABLE prediction (
        id INT PRIMARY KEY AUTO_INCREMENT,
        userid INT NOT NULL,
        username VARCHAR(80) NOT NULL,
        pregnancies FLOAT NOT NULL,
        glucose FLOAT NOT NULL,
        blood_pressure FLOAT NOT NULL,
        skin_thickness FLOAT NOT NULL,
        insulin FLOAT NOT NULL,
        bmi FLOAT NOT NULL,
        diabetes_pedigree_function FLOAT NOT NULL,
        age FLOAT NOT NULL,
        outcome INT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE
    )
    """)
    print(f"  [OK] prediction table created")
    
    print(f"\n[7] Creating indexes...")
    cursor.execute("CREATE INDEX idx_user_email ON user(email)")
    cursor.execute("CREATE INDEX idx_user_username ON user(username)")
    cursor.execute("CREATE INDEX idx_prediction_userid ON prediction(userid)")
    cursor.execute("CREATE INDEX idx_prediction_created_at ON prediction(created_at)")
    print(f"  [OK] Indexes created")
    
    connection.commit()
    print(f"\n[8] Verifying database...")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"  [OK] Tables in diapredict: {[t[0] for t in tables]}")
    
    print(f"\n[9] Checking table structure...")
    cursor.execute("DESCRIBE user")
    user_cols = cursor.fetchall()
    print(f"  [OK] user table has {len(user_cols)} columns")
    
    cursor.execute("DESCRIBE prediction")
    pred_cols = cursor.fetchall()
    print(f"  [OK] prediction table has {len(pred_cols)} columns")
    
    print("\n" + "=" * 80)
    print("SUCCESS! MySQL database setup complete")
    print("=" * 80)
    
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
    connection.rollback()
    sys.exit(1)

finally:
    cursor.close()
    connection.close()

# Now update .env file
print(f"\n[10] Updating .env file...")
env_content = f"""# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development

# MySQL Database Configuration
DATABASE_URL=mysql+pymysql://root:{used_password}@localhost:3306/diapredict

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
"""

env_path = r"c:\Academic Projects\DIABETES-DETECTION\Diabetes Prediction App\.env"
with open(env_path, 'w') as f:
    f.write(env_content)

print(f"  [OK] .env file updated")
print(f"\n[NEXT STEPS]")
print(f"  1. MySQL is ready at localhost:3306/diapredict")
print(f"  2. Restart Flask: python app.py")
print(f"\nMySQL Connection String:")
print(f"  DATABASE_URL=mysql+pymysql://root:{used_password}@localhost:3306/diapredict")
print("=" * 80)

print("\nNext Steps:")
print("  1. Update .env file with DATABASE_URL above")
print("  2. Stop current Flask server")
print("  3. Restart Flask: python app.py")
print("=" * 80)
