#!/usr/bin/env python3
"""OpenClaw Telegram Bot - Multi-provider AI with auto-fallback and self-healing."""

import asyncio
import os
import time

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

import config
from handlers import (
    help_command,
    message_handler,
    model_command,
    models_command,
    reset_command,
    restart_command,
    start_command,
    status_command,
    tokens_command,
)
from services import AIClient, start_health_server, self_ping_loop
from utils import get_logger
from utils.error_handler import handle_error

logger = get_logger("bot")


async def post_init(app) -> None:
    """Start the self-ping keep-alive loop after the bot is initialized."""
    asyncio.create_task(self_ping_loop())


def _build_app(ai_client: AIClient):
    app = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )
    app.bot_data["ai_client"] = ai_client

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("model", model_command))
    app.add_handler(CommandHandler("models", models_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("tokens", tokens_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("restart", restart_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.add_error_handler(handle_error)
    return app


def main() -> None:
    config.validate()
    config.BOT_START_TIME = time.time()

    ai_client = AIClient()

    providers = config.get_enabled_providers()
    models = config.get_all_models()
    logger.info(
        "Starting with %d providers, %d models: %s",
        len(providers), len(models), ", ".join(providers),
    )

    app = _build_app(ai_client)

    webhook_url = os.getenv("WEBHOOK_URL", "")
    port = int(os.getenv("WEBHOOK_PORT", str(config.HEALTH_PORT)))

    if webhook_url:
        logger.info("Starting in WEBHOOK mode: %s", webhook_url)
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook",
            webhook_url=f"{webhook_url}/webhook",
            drop_pending_updates=True,
        )
    else:
        start_health_server(ai_client)
        logger.info("Starting in POLLING mode")
        while True:
            try:
                app = _build_app(ai_client)
                app.run_polling(drop_pending_updates=True)
                break
            except Exception:
                logger.exception("Bot error. Restarting in 10s...")
                time.sleep(10)


if __name__ == "__main__":
    main()
