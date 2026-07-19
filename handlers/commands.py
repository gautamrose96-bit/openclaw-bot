import os
import sys
import time

from telegram import Update
from telegram.ext import ContextTypes

import config
from services import tools
from services.ai_client import AIClient
from utils import get_logger, safe_reply

logger = get_logger("commands")

HELP_TEXT = (
    "OpenClaw Bot Commands:\n\n"
    "/start   - Start the bot\n"
    "/help    - Show this help\n"
    "/model   - Switch AI model\n"
    "/models  - List all available models\n"
    "/status  - Bot health and uptime\n"
    "/tokens  - Show provider usage stats\n"
    "/reset   - Clear conversation history\n"
    "/restart - Restart the bot\n\n"
    "Smart tools:\n"
    "/search [query]     - Web search (DuckDuckGo)\n"
    "/weather [city]     - Current weather\n"
    "/news [topic]       - Latest headlines\n"
    "/translate [text]   - Translate to English\n"
    "/summarize [text]   - Summarize text\n"
    "/calculate [expr]   - Evaluate math\n"
    "/imagine [prompt]   - Generate an image\n\n"
    "Send any message to chat with AI!"
)


def _uptime_str() -> str:
    secs = int(time.time() - config.BOT_START_TIME)
    days, secs = divmod(secs, 86400)
    hours, secs = divmod(secs, 3600)
    mins, secs = divmod(secs, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def _format_model_list(ai_client: AIClient, chat_id: int) -> str:
    all_models = config.get_all_models()
    current_model = ai_client.get_model_id(chat_id)
    lines = ["Available AI models:\n"]
    current_provider = ""
    for short, info in all_models.items():
        prov = info["provider"]
        if prov != current_provider:
            prov_name = config.PROVIDERS[prov]["name"]
            lines.append(f"\n[{prov_name}]")
            current_provider = prov
        marker = " << current" if info["id"] == current_model else ""
        lines.append(f"  /model {short}{marker}")
        lines.append(f"    {info['name']} - {info['description']}")
    lines.append("\nUsage: /model <name>")
    return "\n".join(lines)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("User %s started the bot", update.effective_user.id)
    providers = config.get_enabled_providers()
    models = config.get_all_models()
    await safe_reply(
        update,
        f"Hello! I'm OpenClaw Bot with {len(models)} AI models "
        f"across {len(providers)} providers.\n\n"
        "Send me any message and I'll respond using AI!\n"
        "Type /help for commands or /models to see all models.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_reply(update, HELP_TEXT)


async def models_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_client: AIClient = context.bot_data["ai_client"]
    chat_id = update.effective_chat.id
    await safe_reply(update, _format_model_list(ai_client, chat_id))


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_client: AIClient = context.bot_data["ai_client"]
    chat_id = update.effective_chat.id

    if not context.args:
        await safe_reply(update, _format_model_list(ai_client, chat_id))
        return

    model_key = context.args[0].lower().strip("/")
    all_models = config.get_all_models()

    if model_key not in all_models:
        available = ", ".join(all_models.keys())
        await safe_reply(
            update,
            f"Unknown model: {model_key}\n\nAvailable: {available}",
        )
        return

    info = all_models[model_key]
    ai_client.set_model(chat_id, info["provider"], info["id"])
    prov_name = config.PROVIDERS[info["provider"]]["name"]
    logger.info("Chat %s -> %s (%s)", chat_id, info["id"], info["provider"])
    await safe_reply(
        update,
        f"Switched to {info['name']} ({prov_name})!\n{info['description']}",
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_client: AIClient = context.bot_data["ai_client"]
    healthy = ai_client.get_healthy_providers()
    all_prov = config.get_enabled_providers()
    stats = ai_client.get_stats()
    total_reqs = sum(stats.values())

    lines = [
        "Bot Status",
        f"  Uptime: {_uptime_str()}",
        f"  Providers: {len(healthy)}/{len(all_prov)} healthy",
        f"  Total requests: {total_reqs}",
        "",
        "Providers:",
    ]
    for prov in all_prov:
        status = "OK" if prov in healthy else "COOLDOWN"
        reqs = stats.get(prov, 0)
        name = config.PROVIDERS[prov]["name"]
        lines.append(f"  {name}: {status} ({reqs} reqs)")

    await safe_reply(update, "\n".join(lines))


async def tokens_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_client: AIClient = context.bot_data["ai_client"]
    stats = ai_client.get_stats()
    healthy = ai_client.get_healthy_providers()

    lines = ["Provider Usage (all free tiers):\n"]
    for prov_name in config.get_enabled_providers():
        name = config.PROVIDERS[prov_name]["name"]
        reqs = stats.get(prov_name, 0)
        status = "Active" if prov_name in healthy else "Rate-limited (auto-retry in 60s)"
        lines.append(f"{name}")
        lines.append(f"  Requests: {reqs}")
        lines.append(f"  Status: {status}")
        lines.append("  Cost: $0 (free tier)")
        lines.append("")

    lines.append("Auto-fallback is ON: if one provider hits limits,")
    lines.append("the bot automatically switches to the next one.")
    await safe_reply(update, "\n".join(lines))


async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ai_client: AIClient = context.bot_data["ai_client"]
    chat_id = update.effective_chat.id
    ai_client.clear_history(chat_id)
    logger.info("Conversation reset for chat %s", chat_id)
    await safe_reply(update, "Conversation history cleared!")


async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Restart requested by user %s", update.effective_user.id)
    await safe_reply(update, "Restarting bot... I'll be back in a few seconds!")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def _arg_text(context: ContextTypes.DEFAULT_TYPE) -> str:
    return " ".join(context.args).strip() if context.args else ""


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = _arg_text(context)
    if not query:
        await safe_reply(update, "Usage: /search <query>")
        return
    await safe_reply(update, await tools.ddg_search(query))


async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    city = _arg_text(context)
    if not city:
        await safe_reply(update, "Usage: /weather <city>")
        return
    await safe_reply(update, await tools.get_weather(city))


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    topic = _arg_text(context)
    if not topic:
        await safe_reply(update, "Usage: /news <topic>")
        return
    await safe_reply(update, await tools.get_news(topic))


async def calculate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    expr = _arg_text(context)
    if not expr:
        await safe_reply(update, "Usage: /calculate <expression>  e.g. /calculate 2*(3+4)")
        return
    await safe_reply(update, tools.calculate(expr))


async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = _arg_text(context)
    if not text:
        await safe_reply(update, "Usage: /translate <text>")
        return
    ai_client: AIClient = context.bot_data["ai_client"]
    chat_id = update.effective_chat.id
    reply = await ai_client.complete(
        chat_id,
        text,
        system="You are a translator. Translate the user's text to English. "
        "If it is already English, translate it to Spanish. Reply with only the translation.",
    )
    await safe_reply(update, reply)


async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = _arg_text(context)
    if not text:
        await safe_reply(update, "Usage: /summarize <text>")
        return
    ai_client: AIClient = context.bot_data["ai_client"]
    chat_id = update.effective_chat.id
    reply = await ai_client.complete(
        chat_id,
        text,
        system="Summarize the user's text concisely in a few bullet points.",
    )
    await safe_reply(update, reply)


async def imagine_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prompt = _arg_text(context)
    if not prompt:
        await safe_reply(update, "Usage: /imagine <prompt>")
        return
    url = tools.image_url(prompt)
    message = update.effective_message
    try:
        await message.reply_photo(photo=url, caption=f"/imagine {prompt}")
    except Exception as exc:
        logger.error("Image send failed: %s", exc)
        await safe_reply(update, f"Could not generate image. Direct link:\n{url}")
