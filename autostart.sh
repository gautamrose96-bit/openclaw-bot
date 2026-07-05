#!/usr/bin/env bash
# Auto-restart wrapper for OpenClaw Bot
# Restarts automatically on crash with exponential backoff.
# Usage: ./autostart.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOT_SCRIPT="$SCRIPT_DIR/bot.py"
RESTART_DELAY=5
MAX_FAILURES=10
COOLDOWN=60

failures=0

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }

log "OpenClaw Bot auto-restart wrapper starting..."

while true; do
    log "Starting bot (failures: $failures)..."
    if python3 "$BOT_SCRIPT"; then
        log "Bot exited cleanly."
        failures=0
    else
        failures=$((failures + 1))
        log "Bot crashed (exit $?). Failure #$failures."
    fi

    if [ "$failures" -ge "$MAX_FAILURES" ]; then
        log "Too many failures. Cooling down ${COOLDOWN}s..."
        sleep "$COOLDOWN"
        failures=0
    else
        log "Restarting in ${RESTART_DELAY}s..."
        sleep "$RESTART_DELAY"
    fi
done
