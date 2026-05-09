# Start CredsCore Data Enrichment Service
# Port: 8006

$servicePath = Join-Path $PSScriptRoot "..\services\data-enrichment\src"

Write-Host "Starting Data Enrichment Service..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:8006" -ForegroundColor Green
Write-Host "Health: http://localhost:8006/health" -ForegroundColor Green
Write-Host "Docs: http://localhost:8006/docs" -ForegroundColor Green
Write-Host ""

Set-Location $servicePath
python -m uvicorn main:app --host 0.0.0.0 --port 8006 --reload
