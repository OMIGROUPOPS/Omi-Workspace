# OMI Bot Server Deployment Guide

## Quick Deploy

### Step 1: Deploy to DigitalOcean

From Git Bash on Windows:
```bash
cd /c/Users/liamm/Omi-Workspace/arb-executor
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

Or manually:
```bash
# SSH to server
ssh root@104.131.191.95

# Create directory
mkdir -p /opt/omi-bot

# Exit and copy files from Windows
scp arb-executor/bot_server.py root@104.131.191.95:/opt/omi-bot/
scp arb-executor/arb_executor_v7.py root@104.131.191.95:/opt/omi-bot/
scp arb-executor/kalshi.pem root@104.131.191.95:/opt/omi-bot/
scp arb-executor/deploy/* root@104.131.191.95:/opt/omi-bot/deploy/

# SSH back and run setup
ssh root@104.131.191.95
cd /opt/omi-bot
chmod +x deploy/setup-server.sh
./deploy/setup-server.sh
```

### Step 2: Update Vercel Environment

1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
   - Name: `NEXT_PUBLIC_BOT_SERVER_URL`
   - Value: `https://104.131.191.95`
5. Redeploy the project

### Step 3: Verify

1. Check bot server: `curl https://104.131.191.95/status`
2. Open your Vercel dashboard at `/edge/trading`
3. Should show "Connected" status

## Server Management

```bash
# Check status
systemctl status omi-bot

# Restart bot
systemctl restart omi-bot

# View logs
tail -f /var/log/omi-bot/server.log
journalctl -u omi-bot -f

# Stop bot
systemctl stop omi-bot
```

## Files Deployed

| File | Purpose |
|------|---------|
| bot_server.py | FastAPI WebSocket server |
| arb_executor_v7.py | Main trading bot |
| kalshi.pem | Kalshi API credentials |

## Ports

- 8001: Bot server (internal)
- 443: HTTPS/WSS (nginx proxy)
- 80: HTTP redirect to HTTPS

## Security Notes

- SSL enabled via self-signed cert (for IP access)
- For production, set up `bot.omi.com` subdomain and use Let's Encrypt
- Consider adding API key auth to bot_server.py endpoints
