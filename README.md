# OpenClaw Bot

AI Telegram bot with **6 free AI providers**, **15+ models**, and **10 free hosting platforms**. Runs **24/7 forever at $0 cost**. No credit card needed.

## One-Click Deploy (Login with GitHub)

| Platform | Deploy | Free Tier | Credit Card |
|----------|--------|-----------|-------------|
| **Koyeb** | [![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?name=openclaw-bot&type=git&repository=github.com/gautamrose96-bit/openclaw-bot&branch=main&builder=dockerfile&instance_type=free&env[TELEGRAM_BOT_TOKEN]=&env[GROQ_API_KEY]=) | Free nano 24/7 | No |
| **Railway** | [![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template?template=https://github.com/gautamrose96-bit/openclaw-bot) | $5/month free | No |
| **Render** | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gautamrose96-bit/openclaw-bot) | Free worker | No |
| **Back4App** | [Deploy](https://www.back4app.com/docs-containers/deploy-from-github) | Free container | No |
| **Zeabur** | [Deploy](https://zeabur.com/templates) | Free tier | No |
| **HuggingFace** | [Deploy](https://huggingface.co/new-space) | Free Space | No |
| **Glitch** | [Import](https://glitch.com/edit/#!/import/github/gautamrose96-bit/openclaw-bot) | Free forever | No |
| **Fly.io** | `flyctl launch` | 3 free VMs | No |
| **Oracle Cloud** | [setup-oracle-vps.sh](#1-oracle-cloud-always-free-recommended) | Free forever | Yes (verify only) |
| **Google Cloud** | [setup-gcp.sh](#2-google-cloud-free-tier) | Free e2-micro | Yes (verify only) |

> **Quickest path**: Click the **Koyeb** button > Login with GitHub > Paste your API keys > Click Deploy. Done in 2 minutes.

```
Architecture:

User --> Telegram --> OpenClaw Bot --> Groq (primary)
                          |            |-- Gemini (fallback)
                          |            |-- Mistral (fallback)
                          |            |-- Cohere (fallback)
                          |            |-- HuggingFace (fallback)
                          |            |-- OpenRouter (fallback)
                          |
                     Health /ping <-- Self-ping + UptimeRobot + GitHub Actions
                          |
     Koyeb | Railway | Render | Glitch | Back4App | Zeabur | HF Spaces
     Oracle Cloud | Google Cloud | Fly.io
     (if one dies, deploy on another - bot never goes offline)
```

## Features

- **6 AI Providers** with automatic fallback - never run out of tokens
- **10+ Free Models** - LLaMA 3.3, LLaMA 4 Scout, Qwen 3, Gemini, Command R, Mistral
- **10 Free Hosting Platforms** - all no-credit-card (except Oracle/GCP verify)
- **Self-healing** - auto-restart, watchdog, health checks every 5 min
- **Auto-deploy** - push to GitHub, all platforms update
- **Keep-alive** - self-ping, UptimeRobot, GitHub Actions
- **Zero cost forever**

## Quick Start (Local)

```bash
git clone https://github.com/gautamrose96-bit/openclaw-bot.git
cd openclaw-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add TELEGRAM_BOT_TOKEN + at least one AI provider key
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

**Add ALL providers** for maximum reliability. If one hits rate limits, the bot automatically switches to the next.

## Available Models

| Model | Command | Provider |
|-------|---------|----------|
| LLaMA 3.1 8B (default) | `/model llama-3.1-8b` | Groq |
| LLaMA 3.3 70B | `/model llama-3.3-70b` | Groq |
| Qwen 3 32B | `/model qwen3-32b` | Groq |
| LLaMA 4 Scout 17B | `/model llama4-scout` | Groq |
| Gemini 2.0 Flash | `/model gemini-flash` | Google |
| Gemini 2.0 Flash Lite | `/model gemini-flash-lite` | Google |
| Mistral Small | `/model mistral-small` | Mistral |
| Command R | `/model command-r` | Cohere |
| HF LLaMA 3.1 8B | `/model hf-llama` | HuggingFace |
| OR LLaMA 3.3 70B | `/model or-llama` | OpenRouter |
| OR Gemma 2 9B | `/model or-gemma` | OpenRouter |
| OR Mistral 7B | `/model or-mistral` | OpenRouter |

> When a model is rate-limited, the bot automatically tries the next model in the same provider before falling back to another provider.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show all commands |
| `/model <name>` | Switch AI model |
| `/models` | List all available models |
| `/status` | Bot health, uptime, provider status |
| `/tokens` | Provider usage stats |
| `/reset` | Clear conversation history |
| `/restart` | Restart the bot |

## Free 24/7 Hosting (All Platforms)

### No Credit Card Platforms

#### Koyeb (Recommended - Easiest)
Free nano instance, runs 24/7, no credit card, login with GitHub.

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?name=openclaw-bot&type=git&repository=github.com/gautamrose96-bit/openclaw-bot&branch=main&builder=dockerfile&instance_type=free&env[TELEGRAM_BOT_TOKEN]=&env[GROQ_API_KEY]=)

1. Click button > Login with GitHub
2. Fill `TELEGRAM_BOT_TOKEN` and `GROQ_API_KEY`
3. Click Deploy. Done!

#### Railway
$5/month free credit (enough for 24/7 bot), GitHub login.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/template?template=https://github.com/gautamrose96-bit/openclaw-bot)

1. Click button > Login with GitHub
2. Add environment variables
3. Deploy

#### Render
Free worker service, auto-deploy from GitHub.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gautamrose96-bit/openclaw-bot)

1. Click button > Login with GitHub
2. Add env vars > Deploy

#### Glitch
Free forever, import from GitHub.

1. Go to [glitch.com/edit/#!/import/github/gautamrose96-bit/openclaw-bot](https://glitch.com/edit/#!/import/github/gautamrose96-bit/openclaw-bot)
2. Click `.env` in the editor
3. Add your keys
4. Bot starts automatically

#### Back4App Containers
Free Docker containers, deploy from GitHub.

1. Go to [back4app.com](https://www.back4app.com/) > Sign up with GitHub
2. Create new Container > Connect GitHub repo `openclaw-bot`
3. Add env vars > Deploy

#### Zeabur
Free tier, auto-deploy.

1. Go to [zeabur.com](https://zeabur.com/) > Login with GitHub
2. Create project > Deploy from GitHub > Select `openclaw-bot`
3. Add env vars > Deploy

#### HuggingFace Spaces
Free Docker Space, runs 24/7.

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Select Docker SDK, import from GitHub
3. Add secrets: `TELEGRAM_BOT_TOKEN`, `GROQ_API_KEY`
4. Space builds and runs automatically

#### Fly.io
3 free shared VMs.

```bash
flyctl launch --copy-config
flyctl secrets set TELEGRAM_BOT_TOKEN=... GROQ_API_KEY=...
flyctl deploy
```

### Credit Card Platforms (Free Forever After Verify)

#### 1. Oracle Cloud Always Free (Recommended)

ARM Ampere A1 (4 OCPU, 24 GB RAM) or AMD E2.1.Micro - free forever.

```bash
curl -sSL https://raw.githubusercontent.com/gautamrose96-bit/openclaw-bot/main/setup-oracle-vps.sh | bash
sudo nano /opt/openclaw-bot/.env
sudo systemctl start openclaw-bot
```

Sign up: [cloud.oracle.com](https://cloud.oracle.com/)

#### 2. Google Cloud Free Tier

1x e2-micro instance in us-central1 - free forever.

```bash
chmod +x setup-gcp.sh && ./setup-gcp.sh
```

Sign up: [cloud.google.com](https://cloud.google.com/)

## Self-Healing System (9 Layers)

| Layer | What It Does | Interval |
|-------|-------------|----------|
| Error Handler | Catches all exceptions, sends friendly message | Every request |
| Provider Fallback | If AI provider fails, tries next one instantly | Every request |
| systemd Restart | Restarts bot on crash | 5 seconds |
| Watchdog Cron | Checks if bot is alive, restarts if dead | 5 minutes |
| Self-Ping | Pings own health endpoint to prevent sleep | 4 minutes |
| Health Endpoint | `/health` and `/ping` for external monitoring | Always on |
| GitHub Actions | Checks all platforms, auto-restarts if down | 5 minutes |
| UptimeRobot | External monitor, alerts on downtime | 5 minutes |
| Auto-Rollback | If deploy fails on VPS, reverts to previous version | On deploy |

## Keep-Alive System

Free platforms may sleep after inactivity. The bot prevents this:

1. **Self-ping**: Internal loop hits `/health` every 4 minutes
2. **UptimeRobot** (free): [uptimerobot.com](https://uptimerobot.com/) - add HTTP monitor for your bot URL
3. **GitHub Actions**: Health check every 5 minutes with auto-restart

## CI/CD (GitHub Actions)

### Bot Runner (`run-bot.yml`)
Runs the bot directly on GitHub Actions - no external platform needed. Restarts every 5 hours via cron. Requires `TELEGRAM_BOT_TOKEN` and `GROQ_API_KEY` as repo secrets.

### Auto-Deploy (`deploy.yml`)
Deploys to all platforms on push to `main`: VPS, Railway, Fly.io, Koyeb, Render

### Health Check (`health-check.yml`)
Runs every 5 minutes. Checks all platforms. Auto-restarts any that are down.

### Optional Secrets (repo Settings > Secrets)

| Secret | For |
|--------|-----|
| `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` | Oracle/GCP VPS |
| `VPS_HEALTH_URL` | VPS health check |
| `RAILWAY_TOKEN` | Railway deploy |
| `FLY_API_TOKEN` | Fly.io deploy |
| `KOYEB_API_TOKEN` | Koyeb redeploy |
| `RENDER_DEPLOY_HOOK` | Render deploy |
| `*_HEALTH_URL` | Health check URLs |
| `TELEGRAM_BOT_TOKEN` | Bot runner (run-bot.yml) |
| `GROQ_API_KEY` | Bot runner (run-bot.yml) |

## Project Structure

```
openclaw-bot/
├── bot.py                       # Entry point
├── config.py                    # Multi-provider config + model registry
├── requirements.txt             # Python deps
├── Dockerfile                   # Container (Koyeb, Railway, Render, Fly, HF, Back4App)
├── Procfile                     # Railway/Render
├── runtime.txt                  # Python version
├── handlers/
│   ├── commands.py              # All bot commands
│   └── messages.py              # AI chat with auto-fallback
├── services/
│   ├── ai_client.py             # Multi-provider AI engine
│   └── health.py                # Health server + self-ping
├── utils/
│   ├── error_handler.py         # Global error handler
│   └── logger.py                # Shared logger
├── koyeb.yaml                   # Koyeb config
├── fly.toml                     # Fly.io config
├── render.yaml                  # Render config
├── railway.json                 # Railway config
├── nixpacks.toml                # Railway/Nixpacks
├── glitch.json                  # Glitch config
├── back4app.json                # Back4App config
├── zeabur.json                  # Zeabur config
├── ecosystem.config.js          # PM2 config
├── openclaw-bot.service         # systemd service
├── autostart.sh                 # Shell auto-restart
├── setup-oracle-vps.sh          # Oracle Cloud setup
├── setup-gcp.sh                 # Google Cloud setup
└── .github/workflows/
    ├── run-bot.yml               # Run bot on GitHub Actions
    ├── deploy.yml               # Multi-platform deploy
    └── health-check.yml         # 5-min health checks
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Conflict: terminated by other getUpdates" | Only one bot instance can run per token. Stop others first. |
| Bot not responding | Run `/status`. If providers show COOLDOWN, wait 60s or add more API keys. |
| Rate limited | Add more AI provider keys. Bot auto-rotates between them. |
| Server sleeping | Set up UptimeRobot to ping `/health` every 5 min. Self-ping is also built in. |
| Deploy failed | GitHub Actions auto-rolls back on VPS. Check Actions tab for logs. |
| Platform shut down | Deploy on another platform. 10 options available. |

## Dead Platforms (Don't Use)

These platforms from older guides are **shut down** as of 2026:
- ~~Deta.space / deta.sh~~ - Shut down
- ~~Cyclic.sh~~ - Shut down
- ~~Adaptable.io~~ - Shut down
- ~~Heroku Free~~ - Removed free tier in 2022

## Zero Cost Guarantee

| Component | Platform | Cost |
|-----------|----------|------|
| AI | Groq + Gemini + Mistral + Cohere + HF + OpenRouter | $0 |
| Hosting | Koyeb / Railway / Render / Glitch / Back4App / Zeabur / HF | $0 |
| VPS | Oracle Always Free / GCP Free | $0 |
| Monitoring | UptimeRobot + GitHub Actions | $0 |
| CI/CD | GitHub Actions (2000 min/mo) | $0 |
| Domain | Not needed (Telegram polling) | $0 |
| **Total** | | **$0 forever** |

## License

MIT
