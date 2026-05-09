# CredsCore - Kill Services by Port (PowerShell)
# This script kills processes running on CredsCore service ports

$ErrorActionPreference = "Continue"

# Colors for output
$Green = "`e[32m"
$Yellow = "`e[33m"
$Red = "`e[31m"
$Reset = "`e[0m"

Write-Host "$Red========================================$Reset"
Write-Host "$Red  CredsCore - Stopping All Services$Reset"
Write-Host "$Red========================================$Reset"
Write-Host ""

# Ports used by CredsCore services
$ports = @(3000, 4000, 8000, 8001, 8002, 8003, 8004, 8005, 8006, 8007, 8008, 8009, 8090, 9092, 6379)

$killedCount = 0

foreach ($port in $ports) {
    try {
        $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
        if ($connection) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "$YellowStopping process on port $port (PID: $($process.Id), Name: $($process.ProcessName))...$Reset"
                Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                $killedCount++
                Write-Host "$Green✓ Killed process on port $port$Reset"
            }
        }
    } catch {
        # Port not in use or error
    }
}

Write-Host ""
if ($killedCount -gt 0) {
    Write-Host "$Green========================================$Reset"
    Write-Host "$Green  Stopped $killedCount service(s)$Reset"
    Write-Host "$Green========================================$Reset"
} else {
    Write-Host "$YellowNo active services found on CredsCore ports.$Reset"
}
Write-Host ""
