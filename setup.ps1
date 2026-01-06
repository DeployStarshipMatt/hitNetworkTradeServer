# Setup Script for HIT Network Automation
# Run this to set up both services

Write-Host "🚀 HIT Network Automation - Setup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Function to setup a service
function Setup-Service {
    param (
        [string]$ServiceName,
        [string]$ServicePath
    )
    
    Write-Host ""
    Write-Host "📦 Setting up $ServiceName..." -ForegroundColor Cyan
    Write-Host "-----------------------------------" -ForegroundColor Cyan
    
    # Navigate to service directory
    Set-Location $ServicePath
    
    # Create virtual environment
    if (Test-Path "venv") {
        Write-Host "⚠️  Virtual environment already exists, skipping..." -ForegroundColor Yellow
    } else {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
    }
    
    # Activate and install dependencies
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
    pip install --upgrade pip | Out-Null
    pip install -r requirements.txt
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        return $false
    }
    
    # Create .env from example if not exists
    if (Test-Path ".env") {
        Write-Host "⚠️  .env file already exists, skipping..." -ForegroundColor Yellow
    } else {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env file (please configure it!)" -ForegroundColor Green
    }
    
    deactivate
    
    return $true
}

# Get root directory
$rootDir = $PSScriptRoot

# Setup Discord Bot
$success1 = Setup-Service -ServiceName "Discord Bot" -ServicePath "$rootDir\discord-bot"

# Setup Trading Server
Set-Location $rootDir
$success2 = Setup-Service -ServiceName "Trading Server" -ServicePath "$rootDir\trading-server"

# Return to root
Set-Location $rootDir

# Summary
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($success1 -and $success2) {
    Write-Host "✅ Both services set up successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next Steps:" -ForegroundColor Yellow
    Write-Host "1. Configure discord-bot\.env with your Discord bot token and channel ID" -ForegroundColor White
    Write-Host "2. Configure trading-server\.env with your BloFin API credentials" -ForegroundColor White
    Write-Host "3. Start Trading Server: cd trading-server; .\venv\Scripts\Activate.ps1; python server.py" -ForegroundColor White
    Write-Host "4. Start Discord Bot: cd discord-bot; .\venv\Scripts\Activate.ps1; python bot.py" -ForegroundColor White
    Write-Host ""
    Write-Host "📚 See README.md in each service folder for detailed instructions" -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Some services failed to set up. Check errors above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
