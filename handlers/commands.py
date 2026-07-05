from telegram import Update
from telegram.ext import ContextTypes

import config
from services import GroqClient
from utils import get_logger, safe_reply

logger = get_logger("commands")

HELP_TEXT = (
    "Available commands:\n"
    "/start  - Start the bot\n"
    "/help   - Show this help message\n"
    "/model  - Switch AI model\n"
    "/models - List all available models\n"
    "/reset  - Clear conversation history\n\n"
    "Just send me any message and I'll reply using AI!"
)


def _format_model_list(current_model_id: str) -> str:
    lines = ["Available AI models:\n"]
    for key, info in config.AVAILABLE_MODELS.items():
        marker = " (current)" if info["id"] == current_model_id else ""
        lines.append(f"  /{key}{marker}\n  {info['name']} - {info['description']}\n")
    lines.append("\nSwitch with: /model <name>")
    lines.append("Example: /model gemma2-9b")
    return "\n".join(lines)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User %s started the bot", update.effective_user.id)
    await safe_reply(
        update,
        "Hello! I'm OpenClaw Bot, an AI assistant powered by Groq.\n"
        "Send me any message and I'll respond.\n\n"
        "Type /help for commands or /models to see available AI models.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_reply(update, HELP_TEXT)


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groq_client: GroqClient = context.bot_data["groq_client"]
    chat_id = update.effective_chat.id
    current = groq_client.get_model(chat_id)
    await safe_reply(update, _format_model_list(current))


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groq_client: GroqClient = context.bot_data["groq_client"]
    chat_id = update.effective_chat.id

    if not context.args:
        current = groq_client.get_model(chat_id)
        await safe_reply(update, _format_model_list(current))
        return

    model_key = context.args[0].lower().strip("/")
    if model_key not in config.AVAILABLE_MODELS:
        available = ", ".join(config.AVAILABLE_MODELS.keys())
        await safe_reply(
            update,
            f"Unknown model: {model_key}\n\nAvailable: {available}\n"
            f"Example: /model gemma2-9b",
        )
        return

    model_info = config.AVAILABLE_MODELS[model_key]
    groq_client.set_model(chat_id, model_info["id"])
    logger.info("Chat %s switched to model %s", chat_id, model_info["id"])
    await safe_reply(
        update,
        f"Switched to {model_info['name']}!\n{model_info['description']}",
    )


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groq_client: GroqClient = context.bot_data["groq_client"]
    chat_id = update.effective_chat.id
    groq_client.clear_history(chat_id)
    logger.info("Conversation reset for chat %s", chat_id)
    await safe_reply(update, "Conversation history cleared. Send a new message to start fresh!")
