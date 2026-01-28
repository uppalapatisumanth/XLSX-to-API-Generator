@echo off
echo ========================================
echo      API SERVER REPAIR TOOL v2
echo ========================================

:: Change to the script's directory (D:\ais\api\)
cd /d "%~dp0"

:: Check if backend exists
if not exist "backend" (
    echo [ERROR] 'backend' folder not found in %cd%
    pause
    exit /b
)

cd backend
echo Working Directory: %cd%

echo [1/4] Stopping existing processes...
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1

echo [2/4] Creating Clean Virtual Environment...
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate

echo [3/4] Installing Dependencies...
if not exist "requirements.txt" (
    echo [ERROR] requirements.txt not found in %cd%
    pause
    exit /b
)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo FAILURE: Could not install dependencies.
    pause
    exit /b
)

echo [4/4] Starting Server...
echo API Documentation: http://localhost:8000/docs
echo Test Template: http://localhost:8000/api/template
echo.
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
