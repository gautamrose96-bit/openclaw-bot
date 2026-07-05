from telegram import Update
from telegram.ext import ContextTypes

from services import GroqClient
from utils import get_logger, safe_reply

logger = get_logger("commands")

HELP_TEXT = (
    "Available commands:\n"
    "/start  - Start the bot\n"
    "/help   - Show this help message\n"
    "/reset  - Clear conversation history\n\n"
    "Just send me any message and I'll reply using AI!"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User %s started the bot", update.effective_user.id)
    await safe_reply(
        update,
        "Hello! I'm OpenClaw Bot, an AI assistant powered by Groq.\n"
        "Send me any message and I'll respond.\n\n"
        "Type /help for more options.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_reply(update, HELP_TEXT)


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groq_client: GroqClient = context.bot_data["groq_client"]
    chat_id = update.effective_chat.id
    groq_client.clear_history(chat_id)
    logger.info("Conversation reset for chat %s", chat_id)
    await safe_reply(update, "Conversation history cleared. Send a new message to start fresh!")
