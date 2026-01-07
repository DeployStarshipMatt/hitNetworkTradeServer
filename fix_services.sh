#!/bin/bash
# Fix systemd service files on droplet

# Create trading-server service
cat > /etc/systemd/system/trading-server.service << 'EOF'
[Unit]
Description=BloFin Trading Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hitNetworkAutomation/trading-server
Environment="PATH=/opt/hitNetworkAutomation/venv/bin"
EnvironmentFile=/opt/hitNetworkAutomation/trading-server/.env
ExecStart=/opt/hitNetworkAutomation/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create trading-bot service
cat > /etc/systemd/system/trading-bot.service << 'EOF'
[Unit]
Description=Discord Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hitNetworkAutomation/discord-bot
Environment="PATH=/opt/hitNetworkAutomation/venv/bin"
EnvironmentFile=/opt/hitNetworkAutomation/discord-bot/.env
ExecStart=/opt/hitNetworkAutomation/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and restart
systemctl daemon-reload
systemctl restart trading-server
systemctl restart trading-bot

echo "Services updated and restarted"
systemctl status trading-server --no-pager -l | head -15
echo ""
systemctl status trading-bot --no-pager -l | head -15
