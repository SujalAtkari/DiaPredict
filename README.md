# 🏥 DiaPredict - Advanced Diabetes Detection Platform

> Early Diabetes Detection System with 89.6% Accuracy, Interactive Dashboard, and Multi-User Support

---

## ✨ **Major Features**

### 🔐 Authentication System
- User signup with email verification
- Secure login with session management
- Rate limiting & password hashing
- Gmail SMTP integration

### 📊 Interactive Dashboard
- Risk trend visualization (line chart)
- Risk distribution analysis (pie chart)
- Health metrics comparison (bar chart)
- Prediction history with details
- Real-time statistics cards

### 🔍 Diabetes Risk Assessment
- 8-parameter health evaluation
- 89.6% accuracy hybrid model
- Immediate predictions with recommendations
- Complete prediction history storage

### 💾 MongoDB Multi-User System
- User account management
- Prediction history per user
- Secure data isolation
- Indexed queries for performance

### 🎨 Modern UI/UX
- Purple gradient designer theme
- Fully responsive design
- Interactive charts (Chart.js)
- Toast notifications
- Form validation

---

## 🚀 **Quick Start**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
# Create .env from .env.example and add Gmail app password

# 3. Start MongoDB
mongosh

# 4. Run the application
cd "Diabetes Prediction App"
python app.py

# 5. Open browser
# Navigate to: http://localhost:5000
```

---

## 📋 **Input & Output**

### Input (8 Health Parameters)
- Age, Pregnancies, Glucose, Blood Pressure
- Insulin, Skin Thickness, BMI, Family History

### Output
- ✅ **Negative Risk**: "Low Diabetes Risk" (Green)
- ⚠️ **Positive Risk**: "Diabetes Risk Detected" (Red)
- Medical recommendations included

---

## 📊 **Dashboard Components**

1. **Statistics Cards**: Total tests, risk distribution percentages
2. **Risk Trend Chart**: Line graph showing predictions over time
3. **Risk Distribution**: Pie chart of positive vs negative results
4. **Health Metrics**: Bar chart of average health values
5. **Prediction History**: Detailed table of all tests

---

## 🔐 **Security Features**

✅ PBKDF2 password hashing
✅ Email verification tokens (24-hour expiry)
✅ Session management (30-minute timeout)
✅ Rate limiting (5 attempts per 5 minutes)
✅ User data isolation
✅ CSRF token support ready

---

## 📁 **Project Structure**

```
Diabetes Prediction App/
├── app.py (Main Flask + routes)
├── database.py (MongoDB models)
├── utils/ (auth, email, stats)
├── static/ (CSS + JavaScript)
├── templates/ (HTML templates)
├── hybrid_model.pkl (ML model)
└── scaler.pkl (Feature scaler)
```

---

## 🎯 **User Workflow**

Signup → Email Verification → Login → Dashboard → New Test → Results → History

---

## 📧 **Configuration**

Create `.env` file with:
- MongoDB connection string
- Gmail app password
- Flask secret key
- Session timeout settings

See `.env.example` for template.

---

## 🧪 **Testing**

Low Risk Test:
```
Age: 28, Glucose: 88, BMI: 23.5, Family: 0.25
→ Result: ✅ Low Risk
```

High Risk Test:
```
Age: 58, Glucose: 165, BMI: 33.1, Family: 1.35
→ Result: ⚠️ High Risk
```

---

## 📚 **Documentation**

- `SETUP_GUIDE.md` - Detailed setup instructions
- `UI_DOCUMENTATION.md` - UI specifications
- `INPUT_OUTPUT_GUIDE.md` - Input/output reference

---

## 🎓 **Model Info**

- **Type**: Hybrid Voting Ensemble
- **Accuracy**: 89.6%
- **Features**: 8 health parameters
- **Dataset**: Pima Indians Diabetes Dataset (768 samples)

---

## 🚀 **Features Implemented**

✅ Complete authentication system
✅ MongoDB local database
✅ Email verification (Gmail SMTP)
✅ Interactive dashboard
✅ Multiple chart visualizations
✅ Prediction history
✅ Responsive design (mobile/tablet/desktop)
✅ Form validation
✅ Session management
✅ Rate limiting
✅ Password hashing
✅ Toast notifications
✅ Multi-user support with data isolation

---

## 📞 **Support**

For setup issues, see `SETUP_GUIDE.md`
For API details, see documentation files
For model info, check notebooks

---

**Happy Diagnosing! 🏥💊**
