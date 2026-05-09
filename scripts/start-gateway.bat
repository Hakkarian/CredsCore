@echo off
REM Start CredsCore API Gateway
REM Port: 4000

set "SCRIPT_DIR=%~dp0"
set "GATEWAY_DIR=%SCRIPT_DIR%..\services\api_gateway"

echo Starting API Gateway...
echo URL: http://localhost:4000
echo Health: http://localhost:4000/health
echo.

cd /d "%GATEWAY_DIR%"
python -m uvicorn main:app --host 0.0.0.0 --port 4000 --reload
