# Start CredsCore Client (Next.js Frontend)
# Port: 3000

$clientPath = Join-Path $PSScriptRoot "..\client"

Write-Host "Starting CredsCore Client..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:3000" -ForegroundColor Green
Write-Host ""

Set-Location $clientPath
npm run dev
