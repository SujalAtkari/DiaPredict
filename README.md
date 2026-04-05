# DiaPredict - Diabetes Risk Prediction System

> A machine learning-powered web application for diabetes risk assessment using the Pima Indians Diabetes Dataset.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-green)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Model Details](#model-details)
- [Database](#database)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)

---

## Overview

DiaPredict is a web-based diabetes risk prediction system that uses machine learning to assess the risk of diabetes based on 8 health parameters. The system provides:

- **User Authentication**: Secure login and registration system
- **Risk Assessment**: Real-time diabetes risk prediction
- **History Tracking**: View all past predictions with timestamps
- **Responsive UI**: Works on desktop and mobile devices
- **Data Security**: Password hashing, CSRF protection, SQL injection prevention

The model is trained on the Pima Indians Diabetes Dataset and achieves competitive accuracy on medical predictions.

---

## Features

### Core Functionality
✅ User registration and authentication  
✅ 8-parameter diabetes risk prediction  
✅ Prediction history with timestamps  
✅ Real-time risk assessment dashboard  
✅ Responsive, modern UI  

### Security
✅ Password hashing (bcrypt)  
✅ CSRF token protection  
✅ SQL injection prevention  
✅ Session security  
✅ Secure cookie handling  

### Data Storage
✅ MySQL database support  
✅ SQLite fallback option  
✅ User data persistence  
✅ Prediction tracking  

---

## Tech Stack

### Backend
- **Framework**: Flask 2.0+
- **Database**: MySQL 8.0 (default) / SQLite (backup)
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login with password hashing

### Machine Learning
- **Library**: Scikit-learn
- **Model**: Trained Diabetes Prediction Model
- **Feature Scaling**: Imputer for missing values

### Frontend
- **Template Engine**: Jinja2 (Flask)
- **Styling**: CSS3 with Bootstrap
- **Interactivity**: JavaScript (vanilla)

### Infrastructure
- **Runtime**: Python 3.8+
- **Server**: Flask development / Gunicorn production
- **Package Manager**: pip

---

## Project Structure

```
DIABETES-DETECTION/
│
├── 📂 app/                      # Flask Application
│   ├── app.py                   # Main application & routes
│   ├── database_sql.py          # SQLAlchemy models
│   ├── __init__.py              # Package init
│   ├── .env                     # Environment variables (NOT committed)
│   │
│   ├── static/                  # Static assets
│   │   ├── css/
│   │   │   ├── base.css         # Global styles
│   │   │   ├── dashboard.css    # Dashboard styles
│   │   │   └── forms.css        # Form styles
│   │   └── js/
│   │       └── interactive.js   # Client-side logic
│   │
│   ├── templates/               # HTML templates
│   │   ├── base.html            # Base template
│   │   ├── index.html           # Home page
│   │   ├── auth/                # Authentication pages
│   │   │   ├── login.html
│   │   │   └── signup.html
│   │   ├── pages/               # Main pages
│   │   │   ├── dashboard.html
│   │   │   ├── predictions_history.html
│   │   │   └── result.html
│   │   ├── errors/              # Error pages
│   │   │   ├── 403.html
│   │   │   ├── 404.html
│   │   │   └── 500.html
│   │   └── components/
│   │       └── navbar.html
│   │
│   └── utils/                   # Utilities
│       ├── auth.py              # Auth functions
│       ├── email.py             # Email functions
│       └── stats.py             # Statistics
│
├── 📂 data/                     # Data Files
│   └── diabetes.csv             # Training dataset (768 records)
│
├── 📂 models/                   # Pre-trained Models
│   ├── final_diabetes_model.pkl # Trained prediction model
│   ├── diabetes_imputer.pkl     # Feature imputer
│   └── model_metadata.json      # Model info & metadata
│
├── 📂 notebooks/                # Jupyter Notebooks
│   └── DiaPredict.ipynb         # Data exploration & training
│
├── 📂 docs/                     # Documentation (Archived)
│   └── [previous docs]
│
├── 📂 scripts/                  # Setup Scripts
│   ├── setup_mysql.py           # DB initialization
│   ├── migrate_sqlite_to_mysql.py
│   ├── check_db_schema.py
│   └── setup_diapredict.sql
│
├── 📂 logs/                     # Application Logs (gitignored)
│   └── .gitkeep
│
├── 📂 tests/                    # Unit Tests
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_predictions.py
│   └── conftest.py
│
├── 📂 .venv/                    # Virtual Environment (gitignored)
│
├── .env                         # Configuration (gitignored)
├── .env.example                 # Config template (COMMIT this)
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── run.py                       # Dev server entry point
├── wsgi.py                      # Production entry point
└── README.md                    # This file
```

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- MySQL 8.0 or SQLite 3
- pip (Python package manager)

### 1. Clone Repository
```bash
git clone https://github.com/sakshi048/DiaPredict.git
cd DIABETES-DETECTION
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your settings
# - Set SECRET_KEY
# - Configure DATABASE_URL (MySQL or SQLite)
# - Set email credentials (optional)
```

### 5. Initialize Database
```bash
# For MySQL
python scripts/setup_mysql.py

# For SQLite (default)
# Database auto-creates on first run
```

### 6. Run Application
```bash
# Development server
python run.py

# Access at: http://127.0.0.1:5000
```

---

## Installation

### Full Setup Guide

#### Step 1: Environment Setup
```bash
# Clone and navigate
git clone https://github.com/sakshi048/DiaPredict.git
cd DIABETES-DETECTION

# Create virtual environment
python -m venv .venv

# Activate venv (Windows)
.venv\Scripts\activate
# Activate venv (Linux/Mac)
source .venv/bin/activate
```

#### Step 2: Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 3: Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/diapredict
# FLASK_ENV=development
```

#### Step 4: Database Setup
```bash
# For MySQL (recommended)
python scripts/setup_mysql.py

# For SQLite (simple, local)
# Just run the app - DB auto-creates
```

#### Step 5: Start Server
```bash
python run.py
# Server runs at http://127.0.0.1:5000
```

---

## Configuration

### Environment Variables (.env)

```ini
# Flask Settings
FLASK_ENV=development          # development or production
FLASK_DEBUG=false             # Enable debug mode
SECRET_KEY=your-secret-key    # Change this!

# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/diapredict

# Email (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password

# Server
PORT=5000
```

### Database Options

#### MySQL (Production Recommended)
```ini
DATABASE_URL=mysql+pymysql://username:password@host:3306/diapredict
```

#### SQLite (Development)
```ini
DATABASE_URL=sqlite:///../data/diapredict.db
```

---

## Usage

### Web Interface

#### 1. Registration
- Navigate to `/signup`
- Enter email, username, and password
- Account activation (if configured)

#### 2. Login
- Go to `/login`
- Enter credentials
- Access dashboard

#### 3. Make Prediction
- Fill in 8 health parameters:
  - **Pregnancies**: 0-20
  - **Glucose**: 13-230 mg/dL
  - **Blood Pressure**: 4-141 mmHg
  - **Skin Thickness**: 0-117 mm
  - **Insulin**: 0-1012 mU/mL
  - **BMI**: 8-76 kg/m²
  - **Diabetes Pedigree Function**: 0-2.89
  - **Age**: 9-93 years

- Click "Predict"
- Get risk assessment (POSITIVE/NEGATIVE)

#### 4. View History
- Click "History" button
- See all past predictions
- Sorted by date (newest first)

---

## Model Details

### Dataset
- **Source**: Pima Indians Diabetes Database
- **Records**: 768 patients
- **Features**: 8 medical parameters
- **Target**: Diabetes outcome (0/1)

### Model Specifications
- **Algorithm**: Ensemble/Classification Model
- **Framework**: Scikit-learn
- **Performance**: High accuracy on medical predictions

### Features Used
```
1. Pregnancies         - Number of pregnancies (0-17)
2. Glucose            - Fasting blood glucose (44-199 mg/dL)
3. BloodPressure      - Diastolic BP (24-122 mmHg)
4. SkinThickness      - Triceps thickness (7-99 mm)
5. Insulin            - 2-hour serum insulin (14-846 mU/mL)
6. BMI                - Body Mass Index (18.2-67.1 kg/m²)
7. DiabetesPedigree   - Family history (0.08-2.42)
8. Age                - Age in years (21-81)
```

---

## Database

### Schema Overview

#### Users Table
```sql
- userid (PK, auto-increment)
- email (UNIQUE)
- username (UNIQUE)
- password_hash
- is_verified (boolean)
- created_at, updated_at
- last_login, login_attempts
```

#### Predictions Table
```sql
- id (PK, auto-increment)
- userid (FK → user)
- username (denormalized)
- All 8 health parameters (float)
- outcome (0/1)
- created_at (timestamp)
```

### Migrations

For SQLite to MySQL migration:
```bash
python scripts/migrate_sqlite_to_mysql.py
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/login` | Login page |
| POST   | `/login` | Process login |
| GET    | `/signup` | Registration page |
| POST   | `/signup` | Process registration |
| GET    | `/logout` | Logout user |

### Application
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/` | Home page |
| GET    | `/dashboard` | Main dashboard |
| POST   | `/predict` | Submit prediction |
| GET    | `/predictions_history` | View history |
| GET    | `/result` | View prediction result |

### Errors
| Code | Meaning |
|------|---------|
| 200  | Success |
| 302  | Redirect |
| 400  | Bad Request |
| 403  | Forbidden |
| 404  | Not Found |
| 500  | Server Error |

---

## Running Modes

### Development
```bash
python run.py
# Runs on http://127.0.0.1:5000
# Debug mode enabled
# Auto-reloader disabled (for stability)
```

### Production (Gunicorn)
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
# 4 worker processes
# Listens on all interfaces, port 8000
```

### Docker (Optional)
```bash
docker build -t diapredict .
docker run -p 5000:5000 diapredict
```

---

## File Guidelines

### Do NOT Commit
- `.env` - Contains secrets
- `.venv/` - Virtual environment
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python
- `logs/` - Application logs
- `.DS_Store` - macOS files
- `*.log` - Log files

### Always Commit
- `.env.example` - Config template
- `requirements.txt` - Dependencies
- `*.py` - Python source
- `*.html`, `*.css`, `*.js` - Web files
- `*.md` - Documentation
- `.gitignore` - Git rules

---

## Contributing

### Guidelines
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused

---

## Troubleshooting

### Flask Not Starting
```bash
# Check Python version
python --version

# Verify virtual environment
which python  # Should show .venv path

# Check dependencies
pip list | grep flask
```

### Database Connection Error
```bash
# Check MySQL is running
mysql --version

# Verify credentials in .env
# Check database exists
mysql -u root -p diapredict
```

### Port Already in Use
```bash
# Change port in .env or run command
python run.py --port 8000
```

---

## License

This project is licensed under the MIT License - see LICENSE file for details.

---

## Author

**DiaPredict Development Team**
- Repository: [github.com/sakshi048/DiaPredict](https://github.com/sakshi048/DiaPredict)
- Issues: Report via GitHub Issues

---

## Acknowledgments

- Pima Indians Diabetes Database (UCI Machine Learning Repository)
- Scikit-learn Documentation
- Flask Documentation
- Bootstrap Framework

---

## Changelog

### v1.0.0 (April 2026)
- ✅ Initial Release
- ✅ MySQL Integration
- ✅ User Authentication
- ✅ Prediction History
- ✅ Responsive UI
- ✅ Project Restructuring

---

## Future Enhancements

- [ ] API documentation (Swagger/OpenAPI)
- [ ] Unit tests with pytest
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Machine learning model improvements
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

---

## Support

For questions or issues:
1. Check [GitHub Issues](https://github.com/sakshi048/DiaPredict/issues)
2. Review application logs in `logs/` directory
3. Check `.env.example` for configuration
4. Review code comments in `app/` directory

---

**Last Updated**: April 5, 2026  
**Status**: Active Development
