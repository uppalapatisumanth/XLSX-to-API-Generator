@echo off
echo Starting Frontend...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo Installing Frontend Dependencies...
    npm install
)
npm run dev
pause
