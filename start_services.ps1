# Start Trading System Services
Write-Host "Starting Trading System..." -ForegroundColor Green

# Kill any existing Python processes
Write-Host "Stopping existing services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 1

# Start Trading Server
Write-Host "Starting Trading Server..." -ForegroundColor Cyan
$serverPath = Join-Path $PSScriptRoot "trading-server"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$serverPath'; .\venv\Scripts\Activate.ps1; python server.py"

# Wait for server to be ready
Write-Host "Waiting for Trading Server to start..." -ForegroundColor Cyan
$maxAttempts = 15
$attempt = 0
$serverReady = $false

while ($attempt -lt $maxAttempts -and -not $serverReady) {
    Start-Sleep -Seconds 1
    $attempt++
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            Write-Host "Trading Server is ready!" -ForegroundColor Green
        }
    } catch {
        Write-Host "." -NoNewline
    }
}

if (-not $serverReady) {
    Write-Host ""
    Write-Host "Trading Server failed to start!" -ForegroundColor Red
    exit 1
}

# Start Discord Bot
Write-Host "Starting Discord Bot..." -ForegroundColor Cyan
$botPath = Join-Path $PSScriptRoot "discord-bot"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$botPath'; .\venv\Scripts\Activate.ps1; python bot.py"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Both services started successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Trading Server: http://localhost:8000" -ForegroundColor White
Write-Host "Discord Channel: 1451667836417347728" -ForegroundColor White
Write-Host ""
Write-Host "Check the two PowerShell windows for service logs." -ForegroundColor Yellow
