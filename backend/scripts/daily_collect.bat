@echo off
REM 毎日のデータ収集バッチファイル
REM タスクスケジューラから実行される

cd /d %~dp0..
call .venv\Scripts\activate.bat
python scripts\collect_data.py >> logs\collect_%date:~0,4%%date:~5,2%%date:~8,2%.log 2>&1
