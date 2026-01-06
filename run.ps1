# Run Script for HIT Network Automation
# Starts both Trading Server and Discord Bot

Write-Host "🚀 HIT Network Automation - Starting Services" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

$rootDir = $PSScriptRoot

# Function to check if .env exists
function Test-EnvFile {
    param (
        [string]$ServicePath,
        [string]$ServiceName
    )
    
    if (-not (Test-Path "$ServicePath\.env")) {
        Write-Host "❌ $ServiceName .env file not found!" -ForegroundColor Red
        Write-Host "   Please configure $ServicePath\.env before running" -ForegroundColor Yellow
        return $false
    }
    return $true
}

# Check configurations
Write-Host "Checking configurations..." -ForegroundColor Yellow
$server_ok = Test-EnvFile -ServicePath "$rootDir\trading-server" -ServiceName "Trading Server"
$bot_ok = Test-EnvFile -ServicePath "$rootDir\discord-bot" -ServiceName "Discord Bot"

if (-not ($server_ok -and $bot_ok)) {
    Write-Host ""
    Write-Host "⚠️  Please run setup.ps1 first and configure .env files" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host "✅ Configuration files found" -ForegroundColor Green
Write-Host ""

# Start Trading Server in new window
Write-Host "🔧 Starting Trading Server..." -ForegroundColor Cyan
$serverScript = @"
Set-Location '$rootDir\trading-server'
.\venv\Scripts\Activate.ps1
Write-Host '🚀 Trading Server Starting...' -ForegroundColor Green
python server.py
"@

$serverScriptPath = "$rootDir\trading-server\start_server_temp.ps1"
$serverScript | Out-File -FilePath $serverScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $serverScriptPath

Write-Host "✅ Trading Server started in new window" -ForegroundColor Green

# Wait a bit for server to start
Write-Host "⏳ Waiting 5 seconds for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Discord Bot in new window
Write-Host "🤖 Starting Discord Bot..." -ForegroundColor Cyan
$botScript = @"
Set-Location '$rootDir\discord-bot'
.\venv\Scripts\Activate.ps1
Write-Host '🤖 Discord Bot Starting...' -ForegroundColor Green
python bot.py
"@

$botScriptPath = "$rootDir\discord-bot\start_bot_temp.ps1"
$botScript | Out-File -FilePath $botScriptPath -Encoding UTF8

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $botScriptPath

Write-Host "✅ Discord Bot started in new window" -ForegroundColor Green
Write-Host ""
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "✅ Both services are running!" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Monitoring:" -ForegroundColor Yellow
Write-Host "  • Trading Server: http://localhost:8000/health" -ForegroundColor White
Write-Host "  • Check the separate windows for logs" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop: Close the service windows or press Ctrl+C in each" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Cleanup temp scripts
Remove-Item $serverScriptPath -ErrorAction SilentlyContinue
Remove-Item $botScriptPath -ErrorAction SilentlyContinue
