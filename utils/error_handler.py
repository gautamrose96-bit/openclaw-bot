from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import get_logger

logger = get_logger("error_handler")

USER_ERROR_MESSAGE = (
    "Sorry, something went wrong while processing your request. "
    "Please try again in a moment."
)


async def safe_reply(update: Update, text: str) -> None:
    """Send a reply, suppressing any Telegram API errors."""
    try:
        if update.effective_message:
            await update.effective_message.reply_text(text)
    except Exception as exc:
        logger.error("Failed to send reply: %s", exc)


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler registered with the Application."""
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)
    if isinstance(update, Update):
        await safe_reply(update, USER_ERROR_MESSAGE)
