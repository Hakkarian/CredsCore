# Start CredsCore Credit Scoring Service
# Port: 8000

$servicePath = Join-Path $PSScriptRoot "..\services\credit_scoring"

Write-Host "Starting Credit Scoring Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8000" -ForegroundColor Green
Write-Host "Health: http://localhost:8000/health" -ForegroundColor Green
Write-Host "Docs: http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

Set-Location $servicePath
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
