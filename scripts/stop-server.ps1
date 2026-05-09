# Stop the credit scoring server
Write-Host "Stopping credit scoring server..." -ForegroundColor Yellow

# Try to get PID from file
if (Test-Path ".server.pid") {
    $pid = Get-Content ".server.pid"
    Write-Host "Found PID file: $pid"
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Remove-Item ".server.pid" -ErrorAction SilentlyContinue
    Write-Host "✓ Server stopped (PID: $pid)" -ForegroundColor Green
}

# Also kill any uvicorn or python processes on port 8000
$connection = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connection) {
    Stop-Process -Id $connection.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Killed process on port 8000" -ForegroundColor Green
}

# Clean up any orphaned uvicorn processes
Get-Process uvicorn* -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process python* -ErrorAction SilentlyContinue | Where-Object { $_.Parent.Id -eq 1 } | Stop-Process -Force

Write-Host "Done!" -ForegroundColor Green
