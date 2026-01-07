# Update Digital Ocean Droplet with Latest Code
# Run this script to deploy the latest changes to your droplet

param(
    [Parameter(Mandatory=$true)]
    [string]$DropletIP
)

Write-Host "🚀 Updating Digital Ocean Droplet: $DropletIP" -ForegroundColor Cyan
Write-Host ""

# Create update commands
$updateCommands = @"
cd /opt/hitNetworkAutomation
echo '📥 Pulling latest code from GitHub...'
git pull
echo ''
echo '🔄 Restarting services...'
systemctl restart trading-server
systemctl restart trading-bot
echo ''
echo '✅ Services restarted. Checking status...'
echo ''
echo '--- Trading Server Status ---'
systemctl status trading-server --no-pager -l
echo ''
echo '--- Trading Bot Status ---'
systemctl status trading-bot --no-pager -l
echo ''
echo '✅ Update complete!'
"@

Write-Host "Connecting to droplet and updating..." -ForegroundColor Yellow
Write-Host ""

# Execute commands on droplet
ssh root@$DropletIP $updateCommands

Write-Host ""
Write-Host "✅ Droplet updated successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Cyan
Write-Host "  ssh root@$DropletIP 'journalctl -u trading-bot -n 50'" -ForegroundColor Gray
Write-Host "  ssh root@$DropletIP 'journalctl -u trading-server -n 50'" -ForegroundColor Gray
