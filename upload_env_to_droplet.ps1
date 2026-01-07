# Upload Environment Files to Digital Ocean Droplet
# This will copy your .env files to the droplet

$DROPLET_IP = "167.172.20.242"

Write-Host "📤 Uploading environment files to droplet..." -ForegroundColor Cyan

# Upload discord-bot .env
Write-Host "  → Uploading discord-bot/.env..." -ForegroundColor Yellow
scp discord-bot/.env root@${DROPLET_IP}:/opt/hitNetworkAutomation/discord-bot/.env

# Upload trading-server .env
Write-Host "  → Uploading trading-server/.env..." -ForegroundColor Yellow
scp trading-server/.env root@${DROPLET_IP}:/opt/hitNetworkAutomation/trading-server/.env

# Restart services
Write-Host "`n🔄 Restarting services..." -ForegroundColor Cyan
ssh root@$DROPLET_IP "systemctl restart trading-server; systemctl restart trading-bot"

Start-Sleep -Seconds 3

# Check status
Write-Host "`n📊 Checking service status..." -ForegroundColor Cyan
ssh root@$DROPLET_IP "systemctl status trading-server --no-pager -l | head -10; echo ''; systemctl status trading-bot --no-pager -l | head -10"

Write-Host "`n✅ Environment files uploaded and services restarted!" -ForegroundColor Green
