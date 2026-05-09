@echo off
REM Synthetic Data Service Startup Script
REM Port: 8007

echo =========================================
echo Starting Synthetic Data Service
echo Port: 8007
echo =========================================

set "SERVICE_DIR=%~dp0..\services\synthetic-data"
set "PORT=8007"
set "SERVICE_NAME=synthetic-data"

REM Create models directory if it doesn't exist
if not exist "%SERVICE_DIR%\models" (
    mkdir "%SERVICE_DIR%\models"
    echo Created models directory
)

REM Change to service directory
cd /d "%SERVICE_DIR%"

REM Check dependencies and start
echo Checking dependencies...
python -c "import fastapi, ctgan, pandas, torch" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo Starting Synthetic Data Service on port %PORT%...
python -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload
