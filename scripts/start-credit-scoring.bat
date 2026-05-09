@echo off
REM Start CredsCore Credit Scoring Service
REM Port: 8000

set "SCRIPT_DIR=%~dp0"
set "SERVICE_DIR=%SCRIPT_DIR%..\services\credit_scoring"

echo Starting Credit Scoring Service...
echo URL: http://localhost:8000
echo Health: http://localhost:8000/health
echo Docs: http://localhost:8000/docs
echo.

cd /d "%SERVICE_DIR%"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
