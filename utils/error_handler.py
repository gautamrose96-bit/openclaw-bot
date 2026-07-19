from telegram import Update
from telegram.ext import ContextTypes

from utils.logger import get_logger

logger = get_logger("error_handler")

USER_ERROR_MESSAGE = (
    "Sorry, something went wrong while processing your request. "
    "Please try again in a moment."
)

# Telegram rejects messages longer than 4096 characters.
TELEGRAM_MAX_MESSAGE_LEN = 4096


def split_message(text: str, limit: int = TELEGRAM_MAX_MESSAGE_LEN) -> list[str]:
    """Split text into chunks no longer than `limit`, preferring to break on
    newlines and then whitespace so words and lines stay intact."""
    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        window = remaining[:limit]
        # Prefer the last newline, then the last space, within the window.
        split_at = window.rfind("\n")
        if split_at <= 0:
            split_at = window.rfind(" ")
        if split_at <= 0:
            split_at = limit  # no natural break: hard-split
        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:].lstrip("\n ")
    if remaining:
        chunks.append(remaining)
    return chunks


async def safe_reply(update: Update, text: str) -> None:
    """Send a reply, splitting long text into multiple messages and
    suppressing any Telegram API errors."""
    message = update.effective_message
    if not message:
        return
    try:
        for chunk in split_message(text) or [""]:
            await message.reply_text(chunk)
    except Exception as exc:
        logger.error("Failed to send reply: %s", exc)


async def handle_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler registered with the Application."""
    logger.error("Unhandled exception: %s", context.error, exc_info=context.error)
    if isinstance(update, Update):
        await safe_reply(update, USER_ERROR_MESSAGE)
