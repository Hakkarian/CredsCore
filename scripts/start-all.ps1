# Start all CredsCore services
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  CredsCore - Starting All Services" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$services = @(
    @{ Name = "Credit Scoring"; Script = "start-credit-scoring.ps1"; Port = 8001 },
    @{ Name = "Fraud Detection"; Script = "start-fraud.ps1"; Port = 8002 },
    @{ Name = "Orchestrator"; Script = "start-orchestrator.ps1"; Port = 8003 },
    @{ Name = "Data Enrichment"; Script = "start-enrichment.ps1"; Port = 8004 },
    @{ Name = "Policy Engine"; Script = "start-policy.ps1"; Port = 8005 },
    @{ Name = "Report Generator"; Script = "start-reports.ps1"; Port = 8006 },
    @{ Name = "Synthetic Data"; Script = "start-synthetic-data.ps1"; Port = 8007 },
    @{ Name = "Augmented Scoring"; Script = "start-augmented-scoring.ps1"; Port = 8008 },
    @{ Name = "API Gateway"; Script = "start-gateway.ps1"; Port = 8000 }
)

Write-Host "Step 1: Killing any existing processes on ports..." -ForegroundColor Yellow
& "$scriptDir\kill-ports.ps1"

Write-Host ""
Write-Host "Step 2: Starting services..." -ForegroundColor Yellow
Write-Host ""

$jobs = @()
foreach ($svc in $services) {
    Write-Host "  Starting $($svc.Name)..." -ForegroundColor Green
    $job = Start-Job -ScriptBlock {
        param($dir, $script)
        Set-Location $dir
        & ".\$script"
    } -ArgumentList $scriptDir, $svc.Script

    $jobs += [PSCustomObject]@{
        Job = $job
        Name = $svc.Name
        Port = $svc.Port
    }
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "Step 3: Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Service Status:" -ForegroundColor Cyan
Write-Host "------------------------------------------"
foreach ($jobInfo in $jobs) {
    $status = if ($jobInfo.Job.State -eq "Running") { "Starting" } else { $jobInfo.Job.State }
    Write-Host "  $($jobInfo.Name) (port $($jobInfo.Port)): $status" -ForegroundColor $(if ($status -eq "Starting") { "Green" } else { "Red" })
}

Write-Host ""
Write-Host "Step 4: Starting Next.js client..." -ForegroundColor Yellow
Write-Host ""

$clientJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location "$dir\..\client"
    npm run dev
} -ArgumentList $scriptDir

Start-Sleep -Seconds 3

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  All Services Started!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor White
Write-Host "  - Credit Scoring:  http://localhost:8001" -ForegroundColor Gray
Write-Host "  - Fraud Detection: http://localhost:8002" -ForegroundColor Gray
Write-Host "  - Orchestrator:    http://localhost:8003" -ForegroundColor Gray
Write-Host "  - Data Enrichment: http://localhost:8004" -ForegroundColor Gray
Write-Host "  - Policy Engine:   http://localhost:8005" -ForegroundColor Gray
Write-Host "  - Report Generator: http://localhost:8006" -ForegroundColor Gray
Write-Host "  - Synthetic Data:  http://localhost:8007" -ForegroundColor Gray
Write-Host "  - Augmented Scoring: http://localhost:8008" -ForegroundColor Yellow
Write-Host "  - API Gateway:     http://localhost:8000" -ForegroundColor Green
Write-Host "  - Next.js Client:  http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Enter to view logs, or Ctrl+C to stop all services..." -ForegroundColor Cyan

# Keep script running
while ($true) {
    $input = Read-Host
    if ($input -eq "logs") {
        Write-Host ""
        Write-Host "Recent logs:" -ForegroundColor Yellow
        foreach ($jobInfo in $jobs) {
            Write-Host "`n--- $($jobInfo.Name) ---" -ForegroundColor Cyan
            Receive-Job $jobInfo.Job -Keep | Select-Object -Last 10
        }
    } elseif ($input -eq "stop") {
        break
    }
}

# Cleanup
Write-Host "`nStopping all services..." -ForegroundColor Yellow
Get-Job | Stop-Job
Get-Job | Remove-Job
& "$scriptDir\kill-ports.ps1"
Write-Host "All services stopped." -ForegroundColor Green
