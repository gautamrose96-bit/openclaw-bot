#!/usr/bin/env bash
# Oracle Cloud Always Free VPS Setup Script for OpenClaw Bot
# Tested on: Ubuntu 22.04 / 24.04 (Always Free ARM or AMD instances)
#
# Usage:
#   1. Create an Always Free instance on Oracle Cloud (ARM Ampere A1 or AMD E2.1.Micro)
#   2. SSH into the instance
#   3. Run: curl -sSL <raw-url-of-this-script> | bash
#      Or: chmod +x setup-oracle-vps.sh && ./setup-oracle-vps.sh

set -euo pipefail

APP_DIR="/opt/openclaw-bot"
REPO_URL="https://github.com/gautamrose96-bit/openclaw-bot.git"
SERVICE_USER="openclaw"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ──────────────────────────────────────────────
# 1. System updates & dependencies
# ──────────────────────────────────────────────
log "Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv git curl ufw

# ──────────────────────────────────────────────
# 2. Firewall (only SSH needed; bot uses outbound HTTPS)
# ──────────────────────────────────────────────
log "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
echo "y" | sudo ufw enable

# ──────────────────────────────────────────────
# 3. Create service user
# ──────────────────────────────────────────────
if ! id "$SERVICE_USER" &>/dev/null; then
    log "Creating service user: $SERVICE_USER"
    sudo useradd --system --shell /usr/sbin/nologin --home-dir "$APP_DIR" "$SERVICE_USER"
fi

# ──────────────────────────────────────────────
# 4. Clone / update the repo
# ──────────────────────────────────────────────
if [ -d "$APP_DIR/.git" ]; then
    log "Updating existing installation..."
    cd "$APP_DIR" && sudo -u "$SERVICE_USER" git pull --ff-only
else
    log "Cloning repository..."
    sudo git clone "$REPO_URL" "$APP_DIR"
    sudo chown -R "$SERVICE_USER:$SERVICE_USER" "$APP_DIR"
fi

# ──────────────────────────────────────────────
# 5. Python virtual environment & dependencies
# ──────────────────────────────────────────────
log "Setting up Python virtual environment..."
cd "$APP_DIR"
sudo -u "$SERVICE_USER" python3 -m venv venv
sudo -u "$SERVICE_USER" venv/bin/pip install --upgrade pip
sudo -u "$SERVICE_USER" venv/bin/pip install -r requirements.txt

# ──────────────────────────────────────────────
# 6. Environment file
# ──────────────────────────────────────────────
if [ ! -f "$APP_DIR/.env" ]; then
    log "Creating .env from template..."
    sudo -u "$SERVICE_USER" cp "$APP_DIR/.env.example" "$APP_DIR/.env"
    sudo chmod 600 "$APP_DIR/.env"
    echo ""
    echo "============================================="
    echo "  IMPORTANT: Edit $APP_DIR/.env and add your"
    echo "  TELEGRAM_BOT_TOKEN and GROQ_API_KEY"
    echo "============================================="
    echo ""
fi

# ──────────────────────────────────────────────
# 7. Create logs directory
# ──────────────────────────────────────────────
sudo -u "$SERVICE_USER" mkdir -p "$APP_DIR/logs"

# ──────────────────────────────────────────────
# 8. Install systemd service
# ──────────────────────────────────────────────
log "Installing systemd service..."
sudo cp "$APP_DIR/openclaw-bot.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable openclaw-bot

# ──────────────────────────────────────────────
# 9. Swap file (useful for Always Free 1GB RAM instances)
# ──────────────────────────────────────────────
if [ ! -f /swapfile ]; then
    log "Creating 2GB swap file..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# ──────────────────────────────────────────────
# 10. Automatic security updates
# ──────────────────────────────────────────────
log "Enabling automatic security updates..."
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades 2>/dev/null || true

log ""
log "=========================================="
log "  Setup complete!"
log "=========================================="
log ""
log "Next steps:"
log "  1. Edit secrets:  sudo nano $APP_DIR/.env"
log "  2. Start the bot: sudo systemctl start openclaw-bot"
log "  3. Check status:  sudo systemctl status openclaw-bot"
log "  4. View logs:     sudo journalctl -u openclaw-bot -f"
log ""
