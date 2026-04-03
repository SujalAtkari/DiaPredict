# DiaPredict - Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB installed and running locally
- Gmail account (for email verification)

---

##Step 1: Install Dependencies

```bash
cd "Diabetes Prediction App"
pip install -r ../requirements.txt
```

---

## Step 2: Configure Environment Variables

1. **Create `.env` file** in the project root
2. **Copy contents from `.env.example`**:

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-change-this

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/diapredict

# Email Configuration (Gmail SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password_here

# Application Settings
SESSION_TIMEOUT=1800
EMAIL_VERIFICATION_TOKEN_EXPIRY=86400
MAX_LOGIN_ATTEMPTS=5
LOGIN_ATTEMPT_WINDOW=300
```

### 🔑 How to Get Gmail App Password:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" if not already enabled
3. Go to "App passwords"
4. Select Mail and Windows Computer
5. Copy the generated password (16 characters)
6. Paste into `.env` as `SENDER_PASSWORD`

---

## Step 3: Start MongoDB

**Windows (if MongoDB is installed as service):**
```bash
# Already running as a service, check by opening MongoDB Compass
# or using:
mongosh  # Opens MongoDB shell
```

**Windows (manual start):**
```bash
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe"
```

**Verify connection:**
```bash
mongosh --eval "db.adminCommand('ping')"
```

---

## Step 4: Run the Application

```bash
cd "Diabetes Prediction App"
python app.py
```

**Application will start at:**
```
http://localhost:5000
```

---

## 📋 Application Features

### Authentication Flow
1. **Signup** → Create account with email and password
2. **Email Verification** → Click link in email to verify
3. **Login** →  Access dashboard
4. **Dashboard** → View predictions and analytics
5. **New Test** → Take diabetes risk assessment
6. **View Results** → Immediate prediction feedback
7. **View History** → All past predictions with visualizations

### Dashboard Features
- 📊 **Statistics Cards**: Total tests, risk distribution
- 📈 **Risk Trend Chart**: Line graph of predictions over time
- 🥧 **Risk Distribution**: Pie chart showing positive vs negative
- 📊 **Health Metrics**: Bar chart of average values
- 📋 **Prediction History**: Table of all past tests

---

## 🧪 Testing the Application

### Test Account (After First Signup)
Email: `test@example.com`
Password: `TestPass123!`

### Test Prediction (Low Risk)
```
Age: 25
Pregnancies: 0
Glucose: 85
Blood Pressure: 70
Insulin: 40
Skin Thickness: 20
BMI: 22.5
Family History: 0.3
→ Result: ✅ Low Risk
```

### Test Prediction (High Risk)
```
Age: 55
Pregnancies: 3
Glucose: 180
Blood Pressure: 95
Insulin: 150
Skin Thickness: 40
BMI: 32.5
Family History: 1.2
→ Result: ⚠️ High Risk
```

---

## 🔍 Troubleshooting

### MongoDB Connection Error
```
Error: Database not connected
```
**Solution:**
- Install MongoDB from [mongodb.com](https://www.mongodb.com/try/download/community)
- Start MongoDB service
- Verify: `mongosh --eval "db.adminCommand('ping')"`

### Email Not Sending
```
SMTP Authentication Error
```
**Solution:**
- Check Gmail app password (not regular password)
- Enable "Less secure app access" in Gmail settings (legacy)
- For 2FA users, use App Password instead

### Port 5000 Already in Use
```
Address already in use
```
**Solution:**
```bash
# Change PORT in app.py, line ~15:
app.run(debug=True, host="0.0.0.0", port=5001)
```

### Password Validation Error
```
Password must contain uppercase, lowercase, and digits
```
**Solution:**
- Password must be at least 8 characters
- Include: A-Z, a-z, 0-9
- Example: `SecurePass123!`

---

## 📁 Project Structure

```
DiaPredict/
├── Diabetes Prediction App/
│   ├── app.py (MAIN FILE - Run this)
│   ├── database.py (MongoDB models)
│   ├── utils/
│   │   ├── auth.py (Authentication helpers)
│   │   ├── email.py (Email sending)
│   │   ├── stats.py (Statistics calculation)
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   ├── forms.css
│   │   │   └── dashboard.css
│   │   └── js/
│   │       ├── interactive.js
│   │       └── charts.js
│   ├── templates/
│   │   ├── base.html
│   │   ├── navbar.html
│   │   ├── signup.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── index.html (Prediction form)
│   │   └── result.html (Prediction result)
│   ├── hybrid_model.pkl
│   └── scaler.pkl
├── .env (Create this - don't commit)
├── .env.example (Template)
├── requirements.txt
└── diabetes.csv
```

---

## 🔐 Security Notes

1. **Never commit `.env`** - Contains sensitive credentials
2. **Change `SECRET_KEY`** in production
3. **Use HTTPS** in production (`SESSION_COOKIE_SECURE = True`)
4. **Rate limiting** implemented for login attempts
5. **Password hashing** using PBKDF2
6. **Email verification** required before login

---

## 📊 Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "user@example.com",
  "username": "username",
  "password_hash": "hashed_password",
  "is_verified": true,
  "verification_token": null,
  "verification_token_expiry": null,
  "created_at": "2024-04-03T10:00:00",
  "updated_at": "2024-04-03T10:00:00",
  "last_login": "2024-04-03T10:30:00"
}
```

### Predictions Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId (reference to users)",
  "pregnancies": 0,
  "glucose": 125.5,
  "blood_pressure": 80.2,
  "skin_thickness": 28.3,
  "insulin": 95.5,
  "bmi": 27.8,
  "diabetes_pedigree_function": 0.567,
  "age": 45,
  "prediction": 1,
  "prediction_text": "The model predicts: Diabetes Positive",
  "created_at": "2024-04-03T10:30:00"
}
```

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Configure `.env` file
3. ✅ Start MongoDB
4. ✅ Run application
5. ✅ Create account and verify email
6. ✅ Take a diabetes risk assessment
7. ✅ View dashboard and analytics

---

## 📧 Support

For issues or questions:
- Check troubleshooting section above
- Review app logs in console
- Verify MongoDB connection: `mongosh`
- Check Gmail app password configuration

---

## ✨ Features Implemented

✅ User Authentication (Signup/Login/Logout)
✅ Email Verification (Gmail SMTP)
✅ MongoDB Integration (Local database)
✅ Diabetes Risk Assessment (89.6% accuracy)
✅ Interactive Dashboard
✅ Multiple Visualizations (Charts.js)
✅ Prediction History
✅ Health Metrics Analytics
✅ Responsive Design (Mobile/Tablet/Desktop)
✅ Security (Hashed passwords, session management, rate limiting)

---

Happy diagnosing! 🏥💊
