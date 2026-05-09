@echo off
REM Start CredsCore Orchestrator Service
REM Port: 8005

set "SCRIPT_DIR=%~dp0"
set "SERVICE_DIR=%SCRIPT_DIR%..\services\orchestrator"

echo Starting Orchestrator Service...
echo URL: http://localhost:8005
echo Health: http://localhost:8005/health
echo Docs: http://localhost:8005/docs
echo.

cd /d "%SERVICE_DIR%"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
