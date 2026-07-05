#!/usr/bin/env bash
# ============================================================
# Oracle Cloud Always Free VPS Setup - OpenClaw Bot
# ============================================================
# Runs the bot 24/7 for FREE, forever.
#
# Oracle Always Free tier includes:
#   - ARM Ampere A1: up to 4 OCPUs + 24 GB RAM (lifetime free)
#   - AMD E2.1.Micro: 1 OCPU + 1 GB RAM (lifetime free)
#   - 200 GB block storage, 10 TB/month outbound data
#
# Usage:
#   1. Create Oracle Cloud account: https://cloud.oracle.com/
#   2. Create Always Free compute instance (Ubuntu 22.04/24.04)
#   3. SSH in and run:
#      curl -sSL https://raw.githubusercontent.com/gautamrose96-bit/openclaw-bot/main/setup-oracle-vps.sh | bash
#
# After setup, edit /opt/openclaw-bot/.env with your keys, then:
#   sudo systemctl start openclaw-bot
# ============================================================

set -euo pipefail

APP_DIR="/opt/openclaw-bot"
REPO_URL="https://github.com/gautamrose96-bit/openclaw-bot.git"
SERVICE_USER="openclaw"
WATCHDOG_SCRIPT="$APP_DIR/watchdog.sh"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

# ──────────────────────────────────────────────
# 1. System updates & dependencies
# ──────────────────────────────────────────────
log "Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y
sudo apt-get install -y python3 python3-pip python3-venv git curl ufw cron

# ──────────────────────────────────────────────
# 2. Firewall (only SSH needed; bot uses outbound HTTPS)
# ──────────────────────────────────────────────
log "Configuring firewall..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
echo "y" | sudo ufw enable || true

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
    cd "$APP_DIR"
    sudo -u "$SERVICE_USER" git pull --ff-only || {
        log "Pull failed, resetting to origin/main..."
        sudo -u "$SERVICE_USER" git fetch origin
        sudo -u "$SERVICE_USER" git reset --hard origin/main
    }
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
    echo "  Command: sudo nano $APP_DIR/.env"
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
# 9. Swap file (essential for Always Free 1GB RAM instances)
# ──────────────────────────────────────────────
if [ ! -f /swapfile ]; then
    log "Creating 2GB swap file (important for 1GB RAM instances)..."
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# ──────────────────────────────────────────────
# 10. Watchdog script (extra reliability layer)
# ──────────────────────────────────────────────
log "Creating watchdog script..."
sudo tee "$WATCHDOG_SCRIPT" > /dev/null << 'WATCHDOG'
#!/usr/bin/env bash
# Watchdog: ensures openclaw-bot is running, restarts if dead
SERVICE="openclaw-bot"
if ! systemctl is-active --quiet "$SERVICE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Watchdog: $SERVICE is down, restarting..." >> /opt/openclaw-bot/logs/watchdog.log
    systemctl restart "$SERVICE"
fi
WATCHDOG
sudo chmod +x "$WATCHDOG_SCRIPT"

# ──────────────────────────────────────────────
# 11. Cron jobs for auto-recovery and auto-update
# ──────────────────────────────────────────────
log "Setting up cron jobs..."

# Watchdog every 5 minutes
CRON_WATCHDOG="*/5 * * * * $WATCHDOG_SCRIPT"
# Auto-update daily at 4 AM UTC
CRON_UPDATE="0 4 * * * cd $APP_DIR && git pull --ff-only && $APP_DIR/venv/bin/pip install -r requirements.txt -q && systemctl restart openclaw-bot"
# Clear old logs weekly
CRON_LOGCLEAN="0 3 * * 0 find $APP_DIR/logs -name '*.log' -mtime +30 -delete"

(sudo crontab -l 2>/dev/null | grep -v "openclaw" || true; echo "$CRON_WATCHDOG"; echo "$CRON_UPDATE"; echo "$CRON_LOGCLEAN") | sudo crontab -

# ──────────────────────────────────────────────
# 12. Automatic security updates
# ──────────────────────────────────────────────
log "Enabling automatic security updates..."
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades 2>/dev/null || true

# ──────────────────────────────────────────────
# 13. Optimize for low-memory (Always Free tier)
# ──────────────────────────────────────────────
log "Optimizing for low-memory operation..."
# Reduce swappiness for better performance
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.d/99-openclaw.conf
sudo sysctl -p /etc/sysctl.d/99-openclaw.conf 2>/dev/null || true

log ""
log "=========================================="
log "  Setup complete! Bot will run 24/7 FREE"
log "=========================================="
log ""
log "Next steps:"
log "  1. Edit secrets:    sudo nano $APP_DIR/.env"
log "  2. Start the bot:   sudo systemctl start openclaw-bot"
log "  3. Check status:    sudo systemctl status openclaw-bot"
log "  4. View logs:       sudo journalctl -u openclaw-bot -f"
log ""
log "Automatic features enabled:"
log "  - Auto-restart on crash (systemd)"
log "  - Watchdog check every 5 minutes (cron)"
log "  - Auto-update from GitHub daily at 4 AM UTC"
log "  - Auto security updates (unattended-upgrades)"
log "  - 2GB swap for stability on 1GB RAM instances"
log "  - Old log cleanup weekly"
log ""
