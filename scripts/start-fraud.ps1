# Start CredsCore Fraud Detection Service
# Port: 8002

$servicePath = Join-Path $PSScriptRoot "..\services\fraud_detection"

Write-Host "Starting Fraud Detection Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8002" -ForegroundColor Green
Write-Host "Health: http://localhost:8002/health" -ForegroundColor Green
Write-Host "Docs: http://localhost:8002/docs" -ForegroundColor Green
Write-Host ""

Set-Location $servicePath
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
