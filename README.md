# OpenClaw Bot

AI-powered Telegram bot with **6 free AI models** via [Groq](https://groq.com/). Runs **24/7 for free** on Oracle Cloud Always Free tier.

## Features

- **6 AI models** - switch anytime with `/model` (LLaMA 3.3 70B, LLaMA 3.1 8B, LLaMA 3 70B/8B, Gemma 2 9B, Mixtral 8x7B)
- Per-chat conversation memory with `/reset`
- Zero-cost 24/7 hosting on Oracle Cloud Always Free
- Auto-restart, watchdog, and daily auto-updates
- Modular codebase with shared utilities (no code duplication)

## Available Models (all free via Groq)

| Model | Command | Best For |
|-------|---------|----------|
| LLaMA 3.3 70B | `/model llama-3.3-70b` | Complex tasks (default) |
| LLaMA 3.1 8B | `/model llama-3.1-8b` | Fast simple tasks |
| LLaMA 3 70B | `/model llama3-70b` | Large 8K context |
| LLaMA 3 8B | `/model llama3-8b` | Fastest responses |
| Gemma 2 9B | `/model gemma2-9b` | Good all-rounder |
| Mixtral 8x7B | `/model mixtral-8x7b` | 32K context window |

## Quick Start

```bash
git clone https://github.com/gautamrose96-bit/openclaw-bot.git
cd openclaw-bot
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: add TELEGRAM_BOT_TOKEN and GROQ_API_KEY
python3 bot.py
```

Get your keys:
- **Telegram**: [@BotFather](https://t.me/BotFather)
- **Groq**: [console.groq.com/keys](https://console.groq.com/keys)

## Free 24/7 Deployment (Oracle Cloud)

Oracle Cloud Always Free tier gives you a **lifetime free** VPS:
- ARM Ampere A1: up to 4 OCPUs + 24 GB RAM
- AMD E2.1.Micro: 1 OCPU + 1 GB RAM
- 200 GB storage, 10 TB/month bandwidth

### Setup Steps

1. **Create account**: [cloud.oracle.com](https://cloud.oracle.com/) (credit card for verification only, never charged for Always Free)
2. **Create instance**: Compute > Create Instance > Always Free eligible shape (Ampere A1 or E2.1.Micro) > Ubuntu 22.04/24.04
3. **SSH in** and run one command:

```bash
curl -sSL https://raw.githubusercontent.com/gautamrose96-bit/openclaw-bot/main/setup-oracle-vps.sh | bash
```

4. **Add your keys**:
```bash
sudo nano /opt/openclaw-bot/.env
```

5. **Start**:
```bash
sudo systemctl start openclaw-bot
```

### What the setup script does automatically

- Installs Python, creates virtualenv, installs dependencies
- Creates dedicated `openclaw` service user (security)
- Configures UFW firewall (SSH only)
- Installs systemd service with auto-restart
- Creates watchdog cron (checks every 5 min)
- Daily auto-update from GitHub (4 AM UTC)
- 2 GB swap file (essential for 1 GB RAM instances)
- Automatic OS security updates
- Weekly old log cleanup

## Other Deployment Options

### PM2
```bash
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save && pm2 startup
```

### systemd (manual)
```bash
sudo cp openclaw-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-bot
```

### Auto-restart script
```bash
./autostart.sh
```

## CI/CD

GitHub Actions workflow (`.github/workflows/deploy.yml`) auto-deploys on push to `main`. Add these repo secrets:
- `VPS_HOST` - server IP
- `VPS_USER` - SSH user
- `VPS_SSH_KEY` - SSH private key

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Show commands |
| `/model <name>` | Switch AI model |
| `/models` | List available models |
| `/reset` | Clear conversation history |

## Project Structure

```
├── bot.py                  # Entry point
├── config.py               # Env config + model registry
├── handlers/
│   ├── commands.py         # /start, /help, /model, /reset
│   └── messages.py         # Free-text message handler
├── services/
│   └── groq_client.py      # Groq API + per-chat history & model
├── utils/
│   ├── error_handler.py    # Global error handler + safe_reply
│   └── logger.py           # Shared logger factory
├── ecosystem.config.js     # PM2 config
├── openclaw-bot.service    # systemd service
├── setup-oracle-vps.sh     # One-command Oracle Cloud setup
├── autostart.sh            # Auto-restart wrapper
└── .github/workflows/
    └── deploy.yml          # CI/CD pipeline
```

## Security

- All secrets in `.env` (never hardcoded, never committed)
- systemd runs as dedicated user with filesystem hardening
- Firewall allows only SSH inbound
- Automatic OS security updates enabled

## License

MIT
