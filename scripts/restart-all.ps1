# Restart all CredsCore services
# Requires: PowerShell 5.1 or later

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Colors
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Cyan = "Cyan"
$Gray = "DarkGray"

Write-Host "==========================================" -ForegroundColor $Cyan
Write-Host " CredsCore - Restart All Services" -ForegroundColor $Cyan
Write-Host "==========================================" -ForegroundColor $Cyan
Write-Host ""

# Step 1: Kill existing processes
Write-Host "Step 1: Killing existing processes..." -ForegroundColor $Yellow

# Run kill-ports script
$KillPortsScript = Join-Path $ScriptDir "kill-ports.ps1"
if (Test-Path $KillPortsScript) {
    & $KillPortsScript
}

# Also kill any Python processes matching our services
$ports = @(3000, 4000, 8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009)
foreach ($port in $ports) {
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "  Killing process on port $port (PID: $($process.Id))" -ForegroundColor $Gray
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
            }
        }
    } catch { }
}

Write-Host ""
Write-Host "Processes killed." -ForegroundColor $Green
Write-Host ""

# Step 2: Start all services
Write-Host "Step 2: Starting all services..." -ForegroundColor $Yellow
Write-Host ""

$StartAllScript = Join-Path $ScriptDir "start-all.ps1"
if (Test-Path $StartAllScript) {
    & $StartAllScript
} else {
    Write-Host "Error: start-all.ps1 not found at $StartAllScript" -ForegroundColor $Red
}
