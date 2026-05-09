@echo off
REM CredsCore - Kill Services by Port (Windows Command Prompt)
REM This script kills processes running on CredsCore service ports

echo ========================================
echo   CredsCore - Stopping All Services
echo ========================================
echo.

REM Ports used by CredsCore services
set ports=3000 4000 8000 8001 8002 8003 8004 8005 8006 8090 9092 6379

set killedCount=0

for %%p in (%ports%) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%%p') do (
        echo Stopping process on port %%p (PID: %%a)...
        taskkill /PID %%a /F > nul 2>&1
        if !errorlevel! equ 0 (
            echo Killed process on port %%p
            set /a killedCount+=1
        )
    )
)

echo.
if %killedCount% gtr 0 (
    echo ========================================
    echo   Stopped %killedCount% service(s)
    echo ========================================
) else (
    echo No active services found on CredsCore ports.
)
echo.
pause
