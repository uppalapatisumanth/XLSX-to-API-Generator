@echo off
echo ==========================================
echo       API GENERATOR - STARTUP SCRIPT
echo ==========================================

echo [1/3] Installing dependencies...
cd backend
pip install fastapi uvicorn python-multipart pandas openpyxl jinja2 requests
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

echo [2/3] Starting Backend Server (Port 8000)...
start "Backend API" cmd /k "python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo [3/3] Starting Frontend Server...
cd ../frontend
start "Frontend UI" cmd /k "npm run dev"

echo ==========================================
echo Servers are launching...
echo Backend: http://localhost:8000/api/template
echo Frontend: http://localhost:5173
echo ==========================================
pause
