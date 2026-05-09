# Start CredsCore Policy Service
# Port: 8003

$servicePath = Join-Path $PSScriptRoot "..\services\policy"

Write-Host "Starting Policy Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8003" -ForegroundColor Green
Write-Host "Health: http://localhost:8003/health" -ForegroundColor Green
Write-Host "Docs: http://localhost:8003/docs" -ForegroundColor Green
Write-Host ""

Set-Location $servicePath
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
