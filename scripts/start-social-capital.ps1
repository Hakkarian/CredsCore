# Start CredsCore Social Capital Service
# Port: 8009

$ServicePath = Join-Path $PSScriptRoot "..\services\social_capital"

Write-Host "Starting Social Capital Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8009" -ForegroundColor Green
Write-Host "Health: http://localhost:8009/health" -ForegroundColor Green
Write-Host ""

Set-Location $ServicePath
python -m uvicorn app.main:app --host 0.0.0.0 --port 8009 --reload
