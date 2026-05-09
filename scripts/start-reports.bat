@echo off
REM Start CredsCore Report Generator Service
REM Port: 8004

set "SCRIPT_DIR=%~dp0"
set "SERVICE_DIR=%SCRIPT_DIR%..\services\report-generator"

echo Starting Report Generator Service...
echo URL: http://localhost:8004
echo Health: http://localhost:8004/health
echo Docs: http://localhost:8004/docs
echo.

cd /d "%SERVICE_DIR%"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
