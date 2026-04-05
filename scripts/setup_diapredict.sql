-- ==============================================================================
-- DiaPredict Database Setup Script
-- Run this in MySQL Workbench to create fresh database
-- ==============================================================================

-- Drop existing database if it exists
DROP DATABASE IF EXISTS diapredict;

-- Create fresh database
CREATE DATABASE diapredict;
USE diapredict;

-- Create user table
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
);

-- Create prediction table with CORRECT constraints
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
);

-- Create indexes for performance
CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_username ON user(username);
CREATE INDEX idx_prediction_userid ON prediction(userid);
CREATE INDEX idx_prediction_created_at ON prediction(created_at);

-- Verify schema
SHOW TABLES;
DESCRIBE user;
DESCRIBE prediction;

-- ==============================================================================
-- Setup complete! You can now see the tables above.
-- ==============================================================================
