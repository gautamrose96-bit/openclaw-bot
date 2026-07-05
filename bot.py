#!/usr/bin/env python3
"""OpenClaw Telegram Bot - AI assistant powered by Groq."""

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

import config
from handlers import help_command, message_handler, reset_command, start_command
from services import GroqClient
from utils import get_logger
from utils.error_handler import handle_error

logger = get_logger("bot")


def main() -> None:
    config.validate()

    groq_client = GroqClient()

    app = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).build()
    app.bot_data["groq_client"] = groq_client

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    app.add_error_handler(handle_error)

    logger.info("OpenClaw Bot starting (model: %s)...", config.GROQ_MODEL)
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
