@echo off
chcp 65001 > nul
REM Daily data collection script

cd /d %~dp0..
call .venv\Scripts\activate.bat
if not exist logs mkdir logs
python scripts/collect_data.py >> logs/collect.log 2>&1
