#!/bin/bash
# OMI Bot Server Setup Script
# Run this on the DigitalOcean droplet as root

set -e

echo "=== OMI Bot Server Setup ==="

# 1. Install dependencies
echo "[1/7] Installing system dependencies..."
apt-get update
apt-get install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx

# 2. Create directories
echo "[2/7] Creating directories..."
mkdir -p /opt/omi-bot
mkdir -p /var/log/omi-bot

# 3. Create Python virtual environment
echo "[3/7] Setting up Python environment..."
cd /opt/omi-bot
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-server.txt

# 4. Generate self-signed SSL cert (for IP-based access)
echo "[4/7] Generating SSL certificates..."
mkdir -p /etc/ssl/private
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/omi-bot.key \
    -out /etc/ssl/certs/omi-bot.crt \
    -subj "/CN=104.131.191.95"

# 5. Setup systemd service
echo "[5/7] Configuring systemd service..."
cp /opt/omi-bot/deploy/omi-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable omi-bot

# 6. Setup nginx
echo "[6/7] Configuring nginx..."
cp /opt/omi-bot/deploy/nginx-omi-bot.conf /etc/nginx/sites-available/omi-bot
ln -sf /etc/nginx/sites-available/omi-bot /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 7. Start the service
echo "[7/7] Starting OMI Bot Server..."
systemctl start omi-bot
systemctl status omi-bot

echo ""
echo "=== Setup Complete ==="
echo "Bot server running at: https://104.131.191.95"
echo "WebSocket endpoint: wss://104.131.191.95/ws"
echo ""
echo "Commands:"
echo "  systemctl status omi-bot   - Check status"
echo "  systemctl restart omi-bot  - Restart"
echo "  journalctl -u omi-bot -f   - View logs"
echo "  tail -f /var/log/omi-bot/server.log"
