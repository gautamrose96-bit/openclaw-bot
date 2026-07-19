from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from handlers.commands import search_answer
from services import tools
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

    # Current-events questions: search the web first, then let the AI answer.
    if tools.needs_web_search(user_text):
        try:
            await context.bot.send_chat_action(chat_id, ChatAction.TYPING)
            reply = await search_answer(ai_client, chat_id, user_text)
            await safe_reply(update, reply)
            return
        except Exception:
            logger.exception("Auto-search failed for chat %s; falling back to chat", chat_id)

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
            "All AI providers are temporarily unavailable (rate-limited).\n"
            "These commands still work — they don't need AI:\n"
            "/weather <city> · /calculate <expr> · /search <query> · "
            "/news <topic> · /imagine <prompt>",
        )
