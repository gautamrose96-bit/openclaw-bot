from telegram import Update
from telegram.ext import ContextTypes

from services import GroqClient
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

    groq_client: GroqClient = context.bot_data["groq_client"]

    try:
        reply = await groq_client.chat(chat_id, user_text)
        if not reply:
            reply = "I received an empty response. Please try again."
        await safe_reply(update, reply)
    except Exception:
        logger.exception("Failed to generate response for chat %s", chat_id)
        await safe_reply(update, USER_ERROR_MESSAGE)
