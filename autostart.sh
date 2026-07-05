#!/usr/bin/env bash
# Auto-restart script for OpenClaw Bot
# Usage: ./autostart.sh
# Restarts the bot automatically if it crashes.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOT_SCRIPT="$SCRIPT_DIR/bot.py"
RESTART_DELAY=5    # seconds between restarts
MAX_FAILURES=10    # consecutive failures before cooldown
COOLDOWN=60        # cooldown seconds after MAX_FAILURES consecutive crashes

failures=0

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "OpenClaw Bot auto-restart wrapper starting..."

while true; do
    log "Starting bot (attempt after $failures consecutive failure(s))..."
    if python3 "$BOT_SCRIPT"; then
        # Clean exit
        log "Bot exited cleanly."
        failures=0
    else
        failures=$((failures + 1))
        log "Bot crashed (exit code $?). Failure #$failures."
    fi

    if [ "$failures" -ge "$MAX_FAILURES" ]; then
        log "Too many failures ($failures). Cooling down for ${COOLDOWN}s..."
        sleep "$COOLDOWN"
        failures=0
    else
        log "Restarting in ${RESTART_DELAY}s..."
        sleep "$RESTART_DELAY"
    fi
done
