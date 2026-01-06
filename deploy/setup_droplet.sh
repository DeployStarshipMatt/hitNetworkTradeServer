#!/bin/bash
# Automated setup script for Digital Ocean droplet
# Run this on the droplet after SSH connection

set -e  # Exit on any error

echo "==================================="
echo "hitNetworkAutomation Droplet Setup"
echo "==================================="

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install Python and dependencies
echo "🐍 Installing Python 3.10+..."
apt-get install -y python3 python3-pip python3-venv git

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/hitNetworkAutomation
cd /opt/hitNetworkAutomation

# Clone repository (you'll need to set this up)
echo "⚠️  Manual step: Clone your repository or upload files"
echo "    Option 1: git clone <your-repo-url> ."
echo "    Option 2: scp files from local machine"
read -p "Press enter after files are in place..."

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r discord-bot/requirements.txt
pip install -r trading-server/requirements.txt
pip install -r shared/requirements.txt 2>/dev/null || echo "No shared requirements.txt"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file template..."
    cat > .env << 'EOF'
# Discord Configuration
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here

# Blofin API Configuration
BLOFIN_API_KEY=your_blofin_api_key_here
BLOFIN_SECRET_KEY=your_blofin_secret_key_here
BLOFIN_PASSPHRASE=your_blofin_passphrase_here
BLOFIN_BASE_URL=https://openapi.blofin.com

# Trading Server Configuration
TRADING_SERVER_HOST=localhost
TRADING_SERVER_PORT=8000
EOF
    echo "⚠️  IMPORTANT: Edit .env file with your actual credentials!"
    echo "    Run: nano /opt/hitNetworkAutomation/.env"
fi

# Create systemd service files
echo "🔧 Creating systemd service files..."

# Discord Bot Service
cat > /etc/systemd/system/trading-bot.service << 'EOF'
[Unit]
Description=Discord Trading Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hitNetworkAutomation
Environment="PATH=/opt/hitNetworkAutomation/venv/bin"
EnvironmentFile=/opt/hitNetworkAutomation/.env
ExecStart=/opt/hitNetworkAutomation/venv/bin/python3 discord-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Trading Server Service
cat > /etc/systemd/system/trading-server.service << 'EOF'
[Unit]
Description=Blofin Trading Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/hitNetworkAutomation
Environment="PATH=/opt/hitNetworkAutomation/venv/bin"
EnvironmentFile=/opt/hitNetworkAutomation/.env
ExecStart=/opt/hitNetworkAutomation/venv/bin/python3 trading-server/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials: nano /opt/hitNetworkAutomation/.env"
echo "2. Start services:"
echo "   systemctl start trading-bot"
echo "   systemctl start trading-server"
echo "3. Enable auto-start on boot:"
echo "   systemctl enable trading-bot"
echo "   systemctl enable trading-server"
echo "4. Check status:"
echo "   systemctl status trading-bot"
echo "   systemctl status trading-server"
echo "5. View logs:"
echo "   journalctl -u trading-bot -f"
echo "   journalctl -u trading-server -f"
echo ""
