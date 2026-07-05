from telegram import Update
from telegram.ext import ContextTypes

from services.ai_client import AIClient
from utils import get_logger, safe_reply
from utils.error_handler import USER_ERROR_MESSAGE

logger = get_logger("messages")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    if not user_text:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    logger.info("Message from user %s in chat %s", user_id, chat_id)

    ai_client: AIClient = context.bot_data["ai_client"]

    try:
        reply = await ai_client.chat(chat_id, user_text)
        if not reply:
            reply = "I received an empty response. Please try again."
        await safe_reply(update, reply)
    except Exception:
        logger.exception("All providers failed for chat %s", chat_id)
        await safe_reply(
            update,
            f"{USER_ERROR_MESSAGE}\n\n"
            "All AI providers are temporarily unavailable. "
            "The bot will auto-retry shortly.",
        )
