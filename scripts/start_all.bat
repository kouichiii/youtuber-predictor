@echo off
REM 全サービスを起動するバッチファイル
REM タスクスケジューラで「コンピューター起動時」に実行

cd /d %~dp0..

REM バックエンド起動
start "Backend API" cmd /k "cd backend && .venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM 少し待機
timeout /t 5 /nobreak

REM フロントエンド（公開用）起動
start "Frontend Public" cmd /k "cd frontend && npm run start"

REM フロントエンド（管理用）起動
start "Frontend Admin" cmd /k "cd frontend-admin && npm run start"

echo 全サービスを起動しました
