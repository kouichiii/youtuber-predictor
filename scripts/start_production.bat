@echo off
REM 本番モードで全サービスを起動
REM 事前に npm run build を実行しておくこと

cd /d %~dp0..

REM バックエンド起動
start "Backend API" cmd /k "cd backend && .venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM 少し待機
timeout /t 5 /nobreak

REM フロントエンド（公開用）起動 - ポート3000
start "Frontend Public" cmd /k "cd frontend && npm run start -- -p 3000"

REM フロントエンド（管理用）起動 - ポート3001
start "Frontend Admin" cmd /k "cd frontend-admin && npm run start -- -p 3001"

echo 全サービスを起動しました
echo.
echo   Backend:  http://localhost:8000
echo   Public:   http://localhost:3000
echo   Admin:    http://localhost:3001
