# Check if credit scoring server is running
Write-Host "Checking server status..." -ForegroundColor Cyan

# Check port 8000
$connection = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($connection) {
    $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
    Write-Host "Server is RUNNING on port 8000" -ForegroundColor Green
    Write-Host "  Process: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor White
    Write-Host "  CPU Time: $($process.TotalProcessorTime)" -ForegroundColor White
    Write-Host "  Memory: $([math]::Round($process.WorkingSet64 / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "  URL: http://localhost:8000" -ForegroundColor Yellow
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
} else {
    Write-Host "Server is NOT running on port 8000" -ForegroundColor Red
}

# Check for Python/uvicorn processes
Write-Host ""
Write-Host "Python processes found:" -ForegroundColor Cyan
$pythonProcs = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcs) {
    $pythonProcs | Select-Object Id, ProcessName, @{Name="Memory(MB)";Expression={[math]::Round($_.WorkingSet64 / 1MB, 2)}}, @{Name="Runtime";Expression={(Get-Date) - $_.StartTime}} | Format-Table -AutoSize
} else {
    Write-Host "  None" -ForegroundColor Gray
}
