# Start CredsCore Report Generator Service
# Port: 8004

$servicePath = Join-Path $PSScriptRoot "..\services\report-generator"

Write-Host "Starting Report Generator Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8004" -ForegroundColor Green
Write-Host "Health: http://localhost:8004/health" -ForegroundColor Green
Write-Host "Docs: http://localhost:8004/docs" -ForegroundColor Green
Write-Host ""

Set-Location $servicePath
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
