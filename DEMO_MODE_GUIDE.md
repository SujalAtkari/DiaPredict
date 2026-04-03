# 🏥 DiaPredict - DEMO MODE (No Database Required)

> Run and test the UI immediately without MongoDB or any external setup!

---

## 🚀 **Quick Start (2 Steps)**

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the App

```bash
cd "Diabetes Prediction App"
python app.py
```

That's it! 🎉

---

## 🌐 **Access the Application**

Open your browser and go to:

```
http://localhost:5000
```

---

## 🧪 **What Works in DEMO MODE**

✅ **Signup Page** - Any email/password will work
✅ **Login Page** - Just enter any credentials
✅ **Dashboard** - Shows sample data with charts
✅ **Prediction Form** - Full form with all input fields
✅ **Results Page** - Shows predictions from ML model
✅ **Prediction History** - Demo data table
✅ **Charts & Visualizations** - All interactive charts work
✅ **Responsive Design** - Works on mobile, tablet, desktop

---

## 🎯 **Demo Credentials**

**Any email/password combination works!**

Example:
```
Email: test@example.com
Password: TestPass123!
```

Or:
```
Email: user@gmail.com
Password: Demo123456
```

---

## 📝 **What's NOT Saved**

⚠️ User accounts are NOT saved (memory only)
⚠️ Predictions are NOT stored (demo data only)
⚠️ Data clears when app restarts
⚠️ No email verification sent

**This is purely for UI/UX testing!**

---

## 🔄 **Test User Flow**

1. **Go to**: http://localhost:5000
2. **Click**: "Sign up here" link
3. **Fill in**:
   - Email: `test@example.com`
   - Username: `testuser`
   - Password: `TestPass123!` (must have uppercase, lowercase, number)
4. **Click**: "Create Account"
5. **Auto-redirected to Dashboard** ✓
6. **View demo charts and data** ✓

---

## 🔍 **Test Prediction Form**

1. **Go to**: http://localhost:5000
2. **Login** (any credentials)
3. **Click**: "🔍 New Test" in navbar
4. **Fill in sample values**:
   ```
   Age: 45
   Pregnancies: 2
   Glucose: 125
   Blood Pressure: 85
   Insulin: 95
   Skin Thickness: 28
   BMI: 27.5
   Family History: 0.5
   ```
5. **Click**: "🔍 Predict Diabetes Risk"
6. **See Result**: ✅ or ⚠️ (from actual ML model)

---

## 📊 **Dashboard Demo Data**

The dashboard shows:

- **5 sample predictions** with varied results
- **Risk Trend Chart**: Line graph over 5 days
- **Risk Distribution**: Pie chart (40% positive, 60% negative)
- **Health Metrics**: Bar chart with averages
- **Statistics Cards**: Total tests, risk percentages
- **Prediction History**: Table with demo data

---

## 📁 **.env File (Already Created)**

Location: `D:\College Pasara\Mini Project\Project\DiaPredict\.env`

Content:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=demo-secret-key-for-diapredict-change-in-production-12345
```

No MongoDB connection needed! ✓

---

## 🔄 **Stop the App**

Press **Ctrl + C** in your terminal

---

## 🚨 **Troubleshooting**

### Error: "No module named 'flask'"
```bash
# Install dependencies first
pip install -r requirements.txt
```

### Error: "Port 5000 already in use"
```bash
# Kill the process using port 5000 or change port in app.py
# Line: app.run(debug=True, host="0.0.0.0", port=5001)
```

### Error: "Template not found"
```bash
# Make sure you're running from:
cd "Diabetes Prediction App"
python app.py
```

### Charts not loading
- Refresh the page
- Clear browser cache
- Check console for errors

---

## 📝 **Testing Checklist**

- [ ] App runs without errors
- [ ] Can access http://localhost:5000
- [ ] Signup form works
- [ ] Auto-login redirects to dashboard
- [ ] Dashboard loads with charts
- [ ] Charts display correctly
- [ ] Can navigate between pages
- [ ] Prediction form accepts input
- [ ] Results page shows correctly
- [ ] History page displays demo data
- [ ] Navbar navigation works
- [ ] Logout button works
- [ ] Responsive design works on mobile

---

## 🎨 **Key Features to Test**

### 1. **UI Responsiveness**
Press F12 → Toggle device toolbar → Test on mobile/tablet

### 2. **Chart Interactivity**
- Hover over charts to see tooltips
- Charts should be animated and smooth

### 3. **Form Validation**
- Try submitting empty form
- Try invalid password (< 8 chars)
- Try mismatched passwords

### 4. **Navigation**
- Test all navbar links
- Test back buttons
- Test login redirects

---

## 📞 **Next Steps**

When ready to add real database:

1. **Set up MongoDB Atlas** (cloud)
   - Or install MongoDB locally

2. **Update `.env`** with:
   ```env
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/diapredict
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ```

3. **Update `app.py`** to use real database (provided separately)

---

## 🎉 **You're All Set!**

```bash
cd "Diabetes Prediction App"
python app.py

# Open: http://localhost:5000
```

**Enjoy exploring DiaPredict Demo! 🏥💊**

---

## 📊 **Demo Dashboard Stats**

The dashboard shows:
- **Total Tests**: 5
- **Positive Results**: 2 (40%)
- **Negative Results**: 3 (60%)
- **Average Glucose**: 119.42 mg/dL
- **Average BMI**: 26.82 kg/m²
- **Average BP**: 80.88 mmHg
- **Average Insulin**: 86.86 µU/mL

All data is simulated for demonstration purposes. ✨
