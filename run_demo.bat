@echo off
REM DiaPredict - Demo Mode Startup Script

echo.
echo ====================================
echo       DiaPredict - Demo Mode
echo ====================================
echo.

REM Change to Diabetes Prediction App directory
cd "Diabetes Prediction App"

REM Check if app.py exists
if not exist "app.py" (
    echo ERROR: app.py not found!
    echo Please make sure you run this from the project root directory.
    pause
    exit /b 1
)

REM Run the Flask app
echo Starting DiaPredict...
echo.
echo Web App: http://localhost:5000
echo Press Ctrl+C to stop
echo.

python app.py

pause
