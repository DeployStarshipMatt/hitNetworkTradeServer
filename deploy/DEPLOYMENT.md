# Digital Ocean Droplet Deployment Guide

## Prerequisites
- Digital Ocean droplet created (Ubuntu 22.04 LTS recommended)
- SSH access configured
- Droplet IP address

## Quick Deployment Steps

### 1. Connect to your droplet
```bash
ssh root@YOUR_DROPLET_IP
```

### 2. Upload the setup script
From your local machine (in PowerShell):
```powershell
scp deploy/setup_droplet.sh root@YOUR_DROPLET_IP:/root/
```

### 3. Upload your project files
Option A - Using Git (recommended):
```bash
# On droplet
cd /opt
git clone YOUR_REPO_URL hitNetworkAutomation
cd hitNetworkAutomation
```

Option B - Using SCP from local machine:
```powershell
# From your Windows machine
scp -r C:\Users\yahke\CodeSpace\hitNetworkAutomation root@YOUR_DROPLET_IP:/opt/hitNetworkAutomation
```

### 4. Run the setup script
```bash
# On droplet
chmod +x /root/setup_droplet.sh
/root/setup_droplet.sh
```

### 5. Configure environment variables
```bash
nano /opt/hitNetworkAutomation/.env
```

Add your actual credentials:
```env
DISCORD_TOKEN=your_actual_discord_token
DISCORD_CHANNEL_ID=your_actual_channel_id
BLOFIN_API_KEY=your_actual_api_key
BLOFIN_SECRET_KEY=your_actual_secret_key
BLOFIN_PASSPHRASE=your_actual_passphrase
BLOFIN_BASE_URL=https://openapi.blofin.com
```

Save and exit (Ctrl+X, then Y, then Enter)

### 6. Start the services
```bash
# Start both services
systemctl start trading-bot
systemctl start trading-server

# Enable auto-start on reboot
systemctl enable trading-bot
systemctl enable trading-server

# Check status
systemctl status trading-bot
systemctl status trading-server
```

### 7. Monitor logs
```bash
# Follow Discord bot logs
journalctl -u trading-bot -f

# Follow trading server logs
journalctl -u trading-server -f

# View last 50 lines
journalctl -u trading-bot -n 50
journalctl -u trading-server -n 50
```

## Useful Commands

### Service Management
```bash
# Restart services
systemctl restart trading-bot
systemctl restart trading-server

# Stop services
systemctl stop trading-bot
systemctl stop trading-server

# Check if running
systemctl is-active trading-bot
systemctl is-active trading-server
```

### Troubleshooting
```bash
# Check service status
systemctl status trading-bot --no-pager -l

# View error logs
journalctl -u trading-bot --since "10 minutes ago"

# Test Python environment
cd /opt/hitNetworkAutomation
source venv/bin/activate
python3 discord-bot/bot.py  # Test manually
```

### Updating Code
```bash
# If using git
cd /opt/hitNetworkAutomation
git pull

# Restart services to apply changes
systemctl restart trading-bot
systemctl restart trading-server
```

### Security (Optional but Recommended)
```bash
# Create dedicated user instead of running as root
useradd -r -s /bin/false tradingbot
chown -R tradingbot:tradingbot /opt/hitNetworkAutomation

# Update service files to use User=tradingbot instead of User=root
nano /etc/systemd/system/trading-bot.service
nano /etc/systemd/system/trading-server.service
systemctl daemon-reload
systemctl restart trading-bot trading-server
```

## Files Created on Droplet

- `/opt/hitNetworkAutomation/` - Application directory
- `/opt/hitNetworkAutomation/venv/` - Python virtual environment
- `/opt/hitNetworkAutomation/.env` - Environment variables (KEEP SECRET!)
- `/etc/systemd/system/trading-bot.service` - Discord bot service
- `/etc/systemd/system/trading-server.service` - Trading server service

## Firewall (Optional)

If you need to access trading server from outside:
```bash
# Allow SSH
ufw allow 22/tcp

# Allow trading server port if needed externally
ufw allow 8000/tcp

# Enable firewall
ufw enable
```

**Note:** For this bot, you typically don't need external access - everything runs locally on the droplet.

## Quick Reference

| Task | Command |
|------|---------|
| View bot logs | `journalctl -u trading-bot -f` |
| View server logs | `journalctl -u trading-server -f` |
| Restart bot | `systemctl restart trading-bot` |
| Restart server | `systemctl restart trading-server` |
| Check status | `systemctl status trading-bot trading-server` |
| Stop all | `systemctl stop trading-bot trading-server` |
| Start all | `systemctl start trading-bot trading-server` |
