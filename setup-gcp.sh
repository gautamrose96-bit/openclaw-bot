#!/usr/bin/env bash
# ============================================================
# Google Cloud Free Tier Setup - OpenClaw Bot
# ============================================================
# GCP Always Free: 1 e2-micro instance (us-west1, us-central1, us-east1)
#
# Prerequisites:
#   1. Create GCP account: https://cloud.google.com/
#   2. Install gcloud CLI: https://cloud.google.com/sdk/docs/install
#   3. Run: gcloud auth login && gcloud config set project YOUR_PROJECT
#
# Usage:
#   chmod +x setup-gcp.sh && ./setup-gcp.sh
# ============================================================

set -euo pipefail

PROJECT=$(gcloud config get-value project 2>/dev/null)
ZONE="us-central1-a"  # Always Free eligible zone
INSTANCE="openclaw-bot"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "Project: $PROJECT"
log "Zone: $ZONE"

# ── Create e2-micro instance (Always Free) ──
log "Creating e2-micro instance..."
gcloud compute instances create "$INSTANCE" \
    --zone="$ZONE" \
    --machine-type=e2-micro \
    --image-family=ubuntu-2404-lts-amd64 \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --tags=openclaw-bot \
    --metadata=startup-script='#!/bin/bash
apt-get update -y
apt-get install -y python3 python3-pip python3-venv git
git clone https://github.com/gautamrose96-bit/openclaw-bot.git /opt/openclaw-bot
cd /opt/openclaw-bot
python3 -m venv venv
venv/bin/pip install -r requirements.txt
cp .env.example .env
echo "Setup complete. Edit /opt/openclaw-bot/.env with your API keys."
' \
    2>&1 || log "Instance may already exist, continuing..."

# ── Firewall rule for health checks ──
gcloud compute firewall-rules create allow-health-check \
    --allow=tcp:8080 \
    --target-tags=openclaw-bot \
    --description="OpenClaw Bot health check" \
    2>&1 || true

EXTERNAL_IP=$(gcloud compute instances describe "$INSTANCE" \
    --zone="$ZONE" \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)' 2>/dev/null)

log ""
log "=========================================="
log "  GCP Instance Created!"
log "=========================================="
log ""
log "Instance: $INSTANCE ($ZONE)"
log "IP: $EXTERNAL_IP"
log ""
log "Next steps:"
log "  1. SSH: gcloud compute ssh $INSTANCE --zone=$ZONE"
log "  2. Edit: sudo nano /opt/openclaw-bot/.env"
log "  3. Install service:"
log "     sudo cp /opt/openclaw-bot/openclaw-bot.service /etc/systemd/system/"
log "     sudo systemctl daemon-reload"
log "     sudo systemctl enable --now openclaw-bot"
log ""
log "Health check URL: http://$EXTERNAL_IP:8080/health"
log ""
