# Start CredsCore Orchestrator Service
# Port: 8005

$servicePath = Join-Path $PSScriptRoot "..\services\orchestrator"

Write-Host "Starting Orchestrator Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8005" -ForegroundColor Green
Write-Host "Health: http://localhost:8005/health" -ForegroundColor Green
Write-Host "Docs: http://localhost:8005/docs" -ForegroundColor Green
Write-Host ""

Set-Location $servicePath
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
