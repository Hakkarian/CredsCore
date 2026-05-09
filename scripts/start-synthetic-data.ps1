# Synthetic Data Service Startup Script
# Port: 8007

$ErrorActionPreference = "Stop"

$serviceName = "Synthetic Data Service"
$port = 8007
$serviceDir = Join-Path $PSScriptRoot "..\services\synthetic-data"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Starting $serviceName" -ForegroundColor Cyan
Write-Host "  Port: $port" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if virtual environment exists
$venvPath = Join-Path $serviceDir ".venv"
$pythonPath = if (Test-Path $venvPath) {
    Join-Path $venvPath "Scripts\python.exe"
} else {
    "python"
}

Write-Host "Using Python: $pythonPath" -ForegroundColor Gray

# Check if port is already in use
$portInUse = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "Warning: Port $port is already in use!" -ForegroundColor Yellow
    $process = Get-Process -Id $portInUse.OwningProcess -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "Process using port: $($process.ProcessName) (PID: $($process.Id))" -ForegroundColor Yellow
    }
}

# Set environment variables
$env:PORT = $port
$env:SERVICE_NAME = "synthetic-data"
$env:PYTHONPATH = $serviceDir

# Create models directory if it doesn't exist
$modelsDir = Join-Path $serviceDir "models"
if (-not (Test-Path $modelsDir)) {
    New-Item -ItemType Directory -Force -Path $modelsDir | Out-Null
    Write-Host "Created models directory: $modelsDir" -ForegroundColor Gray
}

# Change to service directory
Set-Location $serviceDir

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Gray
try {
    & $pythonPath -c "import fastapi, ctgan, pandas, torch; print('All dependencies found')"
} catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & $pythonPath -m pip install -r requirements.txt
}

# Start the service
Write-Host "Starting $serviceName on port $port..." -ForegroundColor Green
try {
    & $pythonPath -m uvicorn app.main:app --host 0.0.0.0 --port $port --reload
} catch {
    Write-Host "Error starting service: $_" -ForegroundColor Red
    exit 1
}
