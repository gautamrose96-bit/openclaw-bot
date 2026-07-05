# OpenClaw Bot

AI-powered Telegram bot using [Groq](https://groq.com/) (LLaMA 3.3 70B). Runs 24/7 for free on Oracle Cloud Always Free tier.

## Features

- Chat with LLaMA 3.3 70B via Groq's ultra-fast inference
- Per-chat conversation memory with `/reset` to clear
- Structured codebase: handlers, services, and shared utilities (no code duplication)
- Production-ready error handling and logging
- Multiple deployment options: systemd, PM2, or plain script

## Project Structure

```
openclaw-bot/
├── bot.py                     # Entry point
├── config.py                  # Env-based configuration
├── handlers/
│   ├── commands.py            # /start, /help, /reset
│   └── messages.py            # Free-text message handler
├── services/
│   └── groq_client.py         # Groq API wrapper with chat history
├── utils/
│   ├── error_handler.py       # Global error handler + safe_reply
│   └── logger.py              # Shared logger factory
├── ecosystem.config.js        # PM2 config
├── autostart.sh               # Auto-restart shell script
├── openclaw-bot.service       # systemd unit file
├── setup-oracle-vps.sh        # One-command Oracle Cloud VPS setup
└── .github/workflows/
    └── deploy.yml             # CI/CD: lint + SSH deploy
```

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/gautamrose96-bit/openclaw-bot.git
cd openclaw-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your keys:
#   TELEGRAM_BOT_TOKEN=...
#   GROQ_API_KEY=...
```

Get your keys:
- **Telegram token**: message [@BotFather](https://t.me/BotFather) on Telegram
- **Groq API key**: [console.groq.com/keys](https://console.groq.com/keys)

### 3. Run

```bash
python3 bot.py
```

## Deployment (Free 24/7)

### Option A: Oracle Cloud Always Free VPS (Recommended)

Oracle Cloud offers **Always Free** ARM instances (4 OCPU, 24 GB RAM) that never expire.

1. Sign up at [cloud.oracle.com](https://cloud.oracle.com/) (credit card required for verification, never charged)
2. Create an **Always Free** Ampere A1 or E2.1.Micro compute instance (Ubuntu 22.04)
3. SSH in and run:

```bash
curl -sSL https://raw.githubusercontent.com/gautamrose96-bit/openclaw-bot/main/setup-oracle-vps.sh | bash
sudo nano /opt/openclaw-bot/.env   # add your keys
sudo systemctl start openclaw-bot
```

### Option B: PM2 (any VPS)

```bash
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup   # follow the printed command to enable on boot
```

### Option C: systemd (manual)

```bash
sudo cp openclaw-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-bot
```

### Option D: Auto-restart script

```bash
./autostart.sh
```

## CI/CD (GitHub Actions)

The included workflow (`.github/workflows/deploy.yml`) automatically:
1. Lints on every push
2. Deploys to your VPS via SSH on pushes to `main`

Add these secrets in your repo settings (`Settings > Secrets > Actions`):
- `VPS_HOST` - your server IP
- `VPS_USER` - SSH username (e.g. `ubuntu`)
- `VPS_SSH_KEY` - private SSH key for the server

## Bot Commands

| Command  | Description                    |
|----------|--------------------------------|
| `/start` | Welcome message                |
| `/help`  | Show available commands        |
| `/reset` | Clear conversation history     |

## Security

- All secrets are loaded from `.env` (never hardcoded)
- `.env` is in `.gitignore` and will never be committed
- systemd service runs as a dedicated `openclaw` user with filesystem hardening
- Firewall configured to allow only SSH (outbound HTTPS for Telegram/Groq APIs)

## License

MIT
