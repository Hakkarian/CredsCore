@echo off
REM Start CredsCore Data Enrichment Service
REM Port: 8006

set "SCRIPT_DIR=%~dp0"
set "SERVICE_DIR=%SCRIPT_DIR%..\services\data-enrichment\src"

echo Starting Data Enrichment Service...
echo URL: http://localhost:8006
echo Health: http://localhost:8006/health
echo Docs: http://localhost:8006/docs
echo.

cd /d "%SERVICE_DIR%"
python -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload
