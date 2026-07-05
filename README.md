# OpenClaw Bot

AI Telegram bot with **6 free AI providers**, **15+ models**, and **5 free hosting platforms**. Runs **24/7 forever at $0 cost**.

```
User  -->  Telegram  -->  OpenClaw Bot  -->  Groq (primary)
                               |              |-- Gemini (fallback 1)
                               |              |-- Mistral (fallback 2)
                               |              |-- Cohere (fallback 3)
                               |              |-- HuggingFace (fallback 4)
                               |              |-- OpenRouter (fallback 5)
                               |
                          Health Server  <--  UptimeRobot / GitHub Actions
                               |
          Oracle Cloud (primary)  |  GCP (backup)  |  Railway  |  Render  |  Fly.io
```

## Features

- **6 AI Providers** with automatic fallback - never run out of tokens
- **15+ Free Models** - LLaMA, Gemini, Mixtral, Gemma, Command R, Mistral
- **5 Free Hosting Platforms** - Oracle, GCP, Railway, Render, Fly.io
- **Self-healing** - auto-restart, watchdog, health checks
- **Auto-deploy** - push to GitHub and all platforms update
- **Zero cost forever** - uses only free tiers

## Quick Start (2 minutes)

```bash
git clone https://github.com/gautamrose96-bit/openclaw-bot.git
cd openclaw-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add TELEGRAM_BOT_TOKEN and at least one AI provider key
python3 bot.py
```

## Free API Keys (all free, no credit card)

| Provider | Get Free Key | Free Limit |
|----------|-------------|------------|
| Groq | [console.groq.com/keys](https://console.groq.com/keys) | 30 req/min |
| Google Gemini | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | 15 req/min |
| Mistral | [console.mistral.ai](https://console.mistral.ai/api-keys) | Free tier |
| Cohere | [dashboard.cohere.com](https://dashboard.cohere.com/api-keys) | 20 req/min |
| HuggingFace | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) | Free inference |
| OpenRouter | [openrouter.ai/keys](https://openrouter.ai/keys) | Free models |
| Telegram Bot | [@BotFather](https://t.me/BotFather) | Unlimited |

**Tip**: Add ALL providers for maximum reliability. If one hits rate limits, the bot automatically switches to the next.

## Available Models

| Model | Command | Provider |
|-------|---------|----------|
| LLaMA 3.3 70B | `/model llama-3.3-70b` | Groq |
| LLaMA 3.1 8B | `/model llama-3.1-8b` | Groq |
| LLaMA 3 70B | `/model llama3-70b` | Groq |
| LLaMA 3 8B | `/model llama3-8b` | Groq |
| Gemma 2 9B | `/model gemma2-9b` | Groq |
| Mixtral 8x7B | `/model mixtral-8x7b` | Groq |
| Gemini 2.0 Flash | `/model gemini-flash` | Google |
| Gemini 2.0 Flash Lite | `/model gemini-flash-lite` | Google |
| Mistral Small | `/model mistral-small` | Mistral |
| Command R | `/model command-r` | Cohere |
| HF LLaMA 3.1 8B | `/model hf-llama` | HuggingFace |
| OR LLaMA 3.3 70B | `/model or-llama` | OpenRouter |
| OR Gemma 2 9B | `/model or-gemma` | OpenRouter |
| OR Mistral 7B | `/model or-mistral` | OpenRouter |

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/model <name>` | Switch AI model |
| `/models` | List all available models |
| `/status` | Bot health, uptime, provider status |
| `/tokens` | Provider usage stats and limits |
| `/reset` | Clear conversation history |
| `/restart` | Restart the bot |

## Free 24/7 Hosting (5 Platforms)

### 1. Oracle Cloud Always Free (Recommended - Primary)

**Free forever**: ARM Ampere A1 (4 OCPU, 24 GB RAM) or AMD E2.1.Micro

```bash
# One-command setup:
curl -sSL https://raw.githubusercontent.com/gautamrose96-bit/openclaw-bot/main/setup-oracle-vps.sh | bash
sudo nano /opt/openclaw-bot/.env
sudo systemctl start openclaw-bot
```

Sign up: [cloud.oracle.com](https://cloud.oracle.com/) (credit card for verification, never charged)

Includes: systemd service, watchdog cron (5 min), daily auto-update, swap, security updates.

### 2. Google Cloud Free Tier (Backup)

**Free forever**: 1x e2-micro instance in us-central1/us-west1/us-east1

```bash
chmod +x setup-gcp.sh && ./setup-gcp.sh
gcloud compute ssh openclaw-bot --zone=us-central1-a
sudo nano /opt/openclaw-bot/.env
sudo systemctl enable --now openclaw-bot
```

Sign up: [cloud.google.com](https://cloud.google.com/)

### 3. Railway.app (Backup)

**Free**: $5 monthly credit (enough for a bot running 24/7)

1. Go to [railway.app](https://railway.app/) and connect your GitHub repo
2. Add env vars: `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`
3. Auto-deploys on every push

### 4. Render.com (Backup)

**Free**: Worker service

1. Go to [render.com](https://render.com/) and create a "Worker" service
2. Connect your GitHub repo
3. Add env vars in the dashboard
4. Auto-deploys on every push

### 5. Fly.io (Backup)

**Free**: 3 shared VMs

```bash
flyctl launch --copy-config
flyctl secrets set TELEGRAM_BOT_TOKEN=... GROQ_API_KEY=...
flyctl deploy
```

Sign up: [fly.io](https://fly.io/)

## Self-Healing System

The bot has multiple layers of auto-recovery:

1. **Python error handler** - catches all exceptions, sends user-friendly message
2. **Provider auto-fallback** - if one AI provider fails, instantly tries the next
3. **systemd auto-restart** - RestartSec=5, restarts on any crash
4. **Watchdog cron** - checks every 5 minutes, restarts if dead
5. **Health endpoint** - `/health` returns JSON status for monitoring
6. **Self-ping loop** - keeps free-tier services awake (pings every 4 min)
7. **GitHub Actions health check** - runs every 5 minutes, auto-restarts VPS
8. **Auto-rollback** - if deploy fails, reverts to previous version
9. **Daily auto-update** - pulls latest code from GitHub at 4 AM UTC

## Keep-Alive System

Free-tier services often sleep after inactivity. The bot prevents this with:

- **Self-ping**: Internal loop pings `/health` every 4 minutes
- **UptimeRobot**: Free external monitoring (set up at [uptimerobot.com](https://uptimerobot.com/))
  - Add HTTP monitor: `http://YOUR_SERVER_IP:8080/health`
  - Check interval: 5 minutes
  - Get alerts if bot goes down
- **GitHub Actions**: Health check workflow runs every 5 minutes

## CI/CD (GitHub Actions)

### Auto-Deploy (`deploy.yml`)
- Lint + test on every push
- Deploy to VPS, Railway, and Fly.io in parallel
- Auto-rollback on VPS if deploy fails

### Health Check (`health-check.yml`)
- Runs every 5 minutes
- Checks all platform health endpoints
- Auto-restarts VPS if down

### Required Secrets (Settings > Secrets > Actions)

| Secret | Description | Required |
|--------|-------------|----------|
| `VPS_HOST` | Oracle/GCP server IP | For VPS deploy |
| `VPS_USER` | SSH username | For VPS deploy |
| `VPS_SSH_KEY` | SSH private key | For VPS deploy |
| `VPS_HEALTH_URL` | `http://IP:8080/health` | For health checks |
| `RAILWAY_TOKEN` | Railway deploy token | For Railway |
| `FLY_API_TOKEN` | Fly.io API token | For Fly.io |

## Project Structure

```
openclaw-bot/
├── bot.py                      # Entry point
├── config.py                   # Multi-provider config + model registry
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container build (Railway, Fly.io, Render)
├── Procfile                    # Railway/Render process
├── handlers/
│   ├── commands.py             # /start /help /model /status /tokens /restart
│   └── messages.py             # AI chat with auto-fallback
├── services/
│   ├── ai_client.py            # Multi-provider AI with fallback rotation
│   └── health.py               # HTTP health server + self-ping
├── utils/
│   ├── error_handler.py        # Global error handler
│   └── logger.py               # Shared logger
├── ecosystem.config.js         # PM2 config
├── openclaw-bot.service        # systemd service
├── autostart.sh                # Shell auto-restart wrapper
├── setup-oracle-vps.sh         # Oracle Cloud one-command setup
├── setup-gcp.sh                # Google Cloud setup
├── fly.toml                    # Fly.io config
├── render.yaml                 # Render.com config
├── railway.json                # Railway config
├── nixpacks.toml               # Railway/Nixpacks build
└── .github/workflows/
    ├── deploy.yml              # Multi-platform auto-deploy
    └── health-check.yml        # 5-minute health checks
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Conflict: terminated by other getUpdates" | Only one bot instance can run per token. Stop other instances. |
| Bot not responding | Check `/status`. If all providers show COOLDOWN, wait 60s or add more provider keys. |
| Rate limited | Add more AI provider API keys. The bot auto-rotates between them. |
| Server sleeping (Render/Railway) | Set up UptimeRobot to ping `/health` every 5 min. |
| Deploy failed | Check GitHub Actions logs. The VPS auto-rolls back on failure. |
| Out of free credits (Railway) | Bot continues on other platforms. Railway resets monthly. |

## Security

- All secrets in `.env`, never hardcoded or committed
- `.env` is in `.gitignore`
- systemd runs as dedicated user with filesystem hardening
- Firewall allows only SSH inbound
- Automatic OS security updates

## Zero Cost Guarantee

Every component is free tier:
- **AI**: Groq, Gemini, Mistral, Cohere, HuggingFace, OpenRouter (all free)
- **Hosting**: Oracle Always Free, GCP Free, Railway $5/mo credit, Render Free, Fly.io Free
- **Monitoring**: UptimeRobot Free, GitHub Actions (2000 min/mo)
- **CI/CD**: GitHub Actions Free
- **Domain**: Not needed (Telegram bot uses polling)

**Total lifetime cost: $0**

## License

MIT
