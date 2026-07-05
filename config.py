import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "2048"))
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are OpenClaw Bot, a helpful AI assistant powered by Groq. "
    "Answer questions clearly and concisely.",
)

# All free Groq models available for switching
AVAILABLE_MODELS = {
    "llama-3.3-70b": {
        "id": "llama-3.3-70b-versatile",
        "name": "LLaMA 3.3 70B",
        "description": "Most capable, best for complex tasks",
    },
    "llama-3.1-8b": {
        "id": "llama-3.1-8b-instant",
        "name": "LLaMA 3.1 8B",
        "description": "Fast and efficient for simple tasks",
    },
    "llama3-70b": {
        "id": "llama3-70b-8192",
        "name": "LLaMA 3 70B",
        "description": "Large context window (8192 tokens)",
    },
    "llama3-8b": {
        "id": "llama3-8b-8192",
        "name": "LLaMA 3 8B",
        "description": "Fastest, good for quick answers",
    },
    "gemma2-9b": {
        "id": "gemma2-9b-it",
        "name": "Gemma 2 9B",
        "description": "Google's Gemma 2, good all-rounder",
    },
    "mixtral-8x7b": {
        "id": "mixtral-8x7b-32768",
        "name": "Mixtral 8x7B",
        "description": "Mixture of experts, large 32K context",
    },
}


def validate():
    missing = []
    if not TELEGRAM_BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )
