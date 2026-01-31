#!/bin/bash
# Deploy OMI Bot to DigitalOcean
# Run from your local machine (Windows: use Git Bash)

SERVER="104.131.191.95"
DEPLOY_DIR="/opt/omi-bot"

echo "=== Deploying OMI Bot to $SERVER ==="

# Files to deploy
FILES=(
    "bot_server.py"
    "arb_executor_v7.py"
    "kalshi.pem"
    "deploy/requirements-server.txt"
    "deploy/omi-bot.service"
    "deploy/nginx-omi-bot.conf"
    "deploy/setup-server.sh"
)

# Create deploy directory on server
echo "[1/4] Creating remote directory..."
ssh root@$SERVER "mkdir -p $DEPLOY_DIR/deploy"

# Copy files
echo "[2/4] Copying files..."
for file in "${FILES[@]}"; do
    echo "  -> $file"
    scp "$(dirname "$0")/../$file" root@$SERVER:$DEPLOY_DIR/$file
done

# Copy .env if exists
if [ -f "$(dirname "$0")/../.env" ]; then
    echo "  -> .env"
    scp "$(dirname "$0")/../.env" root@$SERVER:$DEPLOY_DIR/.env
fi

# Run setup script
echo "[3/4] Running setup script..."
ssh root@$SERVER "cd $DEPLOY_DIR && chmod +x deploy/setup-server.sh && ./deploy/setup-server.sh"

echo "[4/4] Verifying deployment..."
ssh root@$SERVER "systemctl status omi-bot --no-pager"

echo ""
echo "=== Deployment Complete ==="
echo "Dashboard should connect to: https://$SERVER"
