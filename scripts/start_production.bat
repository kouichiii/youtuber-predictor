@echo off
chcp 65001 > nul
REM Production mode startup script

cd /d %~dp0..

REM Start Backend
start "Backend API" cmd /k "cd backend && .venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM Wait 5 seconds
timeout /t 5 /nobreak

REM Start Frontend Public (port 3000)
start "Frontend Public" cmd /k "cd frontend && npm run start -- -p 3000"

REM Start Frontend Admin (port 3001)
start "Frontend Admin" cmd /k "cd frontend-admin && npm run start -- -p 3001"

echo.
echo All services started:
echo   Backend:  http://localhost:8000
echo   Public:   http://localhost:3000
echo   Admin:    http://localhost:3001
