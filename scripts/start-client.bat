@echo off
REM Start CredsCore Client (Next.js Frontend)
REM Port: 3000

set "SCRIPT_DIR=%~dp0"
set "CLIENT_DIR=%SCRIPT_DIR%..\client"

echo Starting CredsCore Client...
echo URL: http://localhost:3000
echo.

cd /d "%CLIENT_DIR%"
npm run dev
