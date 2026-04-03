# INPUT & OUTPUT QUICK REFERENCE

## 📥 INPUT FORMAT

| Field | Type | Range | Unit | Example |
|-------|------|-------|------|---------|
| **Age** | Integer | 0-120 | Years | 45 |
| **Pregnancies** | Integer | 0-20 | Count | 2 |
| **Glucose** | Decimal | 0-300 | mg/dL | 125.5 |
| **Blood Pressure (Diastolic)** | Decimal | 0-150 | mmHg | 85.2 |
| **Insulin** | Decimal | 0-900 | µU/mL | 150.3 |
| **Skin Thickness** | Decimal | 0-100 | mm | 28.5 |
| **BMI** | Decimal | 10-70 | kg/m² | 27.8 |
| **Family History Index** | Decimal | 0-2.5 | Score | 0.567 |

---

## 📤 OUTPUT FORMAT

### Scenario 1: Negative (Low Risk)
```
Result Type: Negative Diabetes Risk ✅
Icon: ✅
Message: "The model predicts a negative diabetes risk."
Advice: "Maintain a healthy lifestyle and regular health checkups."
Color: Green (#4ade80)
```

### Scenario 2: Positive (High Risk)
```
Result Type: Positive Diabetes Risk ⚠️
Icon: ⚠️
Message: "The model predicts a positive diabetes risk."
Advice: "Please consult with a healthcare professional for further evaluation."
Color: Red (#ff6b6b)
```

### Scenario 3: Error
```
Result Type: Error ❌
Icon: ❌
Message: "Error message details"
Color: Orange (#f59e0b)
```

---

## 🎯 TYPICAL INPUT SCENARIOS

### Low Risk Profile
```
Age: 28, Pregnancies: 1, Glucose: 88, Blood Pressure: 72,
Insulin: 45, Skin Thickness: 22, BMI: 23.5, Family History: 0.25
→ Output: ✅ Low Diabetes Risk (Green)
```

### Borderline Profile
```
Age: 35, Pregnancies: 2, Glucose: 110, Blood Pressure: 78,
Insulin: 95, Skin Thickness: 30, BMI: 26.2, Family History: 0.45
→ Output: ✅ Low Diabetes Risk (Green) or ⚠️ High Risk (Red)
```

### High Risk Profile
```
Age: 58, Pregnancies: 4, Glucose: 165, Blood Pressure: 92,
Insulin: 200, Skin Thickness: 42, BMI: 33.1, Family History: 1.35
→ Output: ⚠️ Diabetes Risk Detected (Red)
```

---

## ✨ NEW UI FEATURES

✅ **Modern purple-blue gradient design**
✅ **Organized sections** (Personal, Clinical, Body Metrics)
✅ **Field hints** with units for each input
✅ **Clear validation** with error messages
✅ **Responsive design** for mobile/tablet/desktop
✅ **Colorful results** with icons and recommendations
✅ **Easy navigation** with "Take Another Test" button
✅ **Medical context** with realistic value ranges

---

## 🔄 DATA FLOW

```
User Input Form
    ↓
Client-side Validation
    ↓
Server Processing (Flask)
    ↓
Feature Scaling (Scaler)
    ↓
Hybrid Model Prediction
    ↓
Binary Output (0 or 1)
    ↓
Result Display Page
```

---

## 📱 RESPONSIVE BREAKPOINTS

- **Desktop**: Full 2-column grid layout
- **Tablet (600px - 1024px)**: Adaptive layout
- **Mobile (<600px)**: Single column layout, stacked buttons

