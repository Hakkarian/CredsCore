# Start CredsCore API Gateway
# Port: 4000

$gatewayPath = Join-Path $PSScriptRoot "..\services\api_gateway"

Write-Host "Starting API Gateway..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:4000" -ForegroundColor Green
Write-Host "Health: http://localhost:4000/health" -ForegroundColor Green
Write-Host ""

Set-Location $gatewayPath
python -m uvicorn main:app --host 0.0.0.0 --port 4000 --reload
