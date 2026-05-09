@echo off
REM Start CredsCore Policy Service
REM Port: 8003

set "SCRIPT_DIR=%~dp0"
set "SERVICE_DIR=%SCRIPT_DIR%..\services\policy"

echo Starting Policy Service...
echo URL: http://localhost:8003
echo Health: http://localhost:8003/health
echo Docs: http://localhost:8003/docs
echo.

cd /d "%SERVICE_DIR%"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
