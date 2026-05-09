@echo off
REM Start CredsCore Fraud Detection Service
REM Port: 8002

set "SCRIPT_DIR=%~dp0"
set "SERVICE_DIR=%SCRIPT_DIR%..\services\fraud_detection"

echo Starting Fraud Detection Service...
echo URL: http://localhost:8002
echo Health: http://localhost:8002/health
echo Docs: http://localhost:8002/docs
echo.

cd /d "%SERVICE_DIR%"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
