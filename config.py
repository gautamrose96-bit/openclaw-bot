import os
from dotenv import load_dotenv

load_dotenv()

# ── Core ──
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_START_TIME = 0.0  # set at runtime

# ── API Keys (all optional; providers with keys get enabled) ──
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# ── Defaults ──
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "groq")
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "2048"))
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are OpenClaw Bot, a helpful AI assistant. "
    "Answer questions clearly and concisely.",
)

# ── Health check ──
HEALTH_PORT = int(os.getenv("HEALTH_PORT", "8080"))

# ── Provider registry ──
# Each provider: {key_env, models: {short_name: {id, name, description}}}
PROVIDERS = {
    "groq": {
        "name": "Groq",
        "key": GROQ_API_KEY,
        "base_url": "https://api.groq.com/openai/v1",
        "models": {
            "llama-3.1-8b": {
                "id": "llama-3.1-8b-instant",
                "name": "LLaMA 3.1 8B",
                "description": "Fast, efficient, default model",
            },
            "llama-3.3-70b": {
                "id": "llama-3.3-70b-versatile",
                "name": "LLaMA 3.3 70B",
                "description": "Most capable, best for complex tasks",
            },
            "qwen3-32b": {
                "id": "qwen/qwen3-32b",
                "name": "Qwen 3 32B",
                "description": "Strong reasoning and coding",
            },
            "llama4-scout": {
                "id": "meta-llama/llama-4-scout-17b-16e-instruct",
                "name": "LLaMA 4 Scout 17B",
                "description": "Latest LLaMA 4, multimodal",
            },
        },
    },
    "gemini": {
        "name": "Google Gemini",
        "key": GEMINI_API_KEY,
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": {
            "gemini-flash": {
                "id": "gemini-2.0-flash",
                "name": "Gemini 2.0 Flash",
                "description": "Fast, free Google AI",
            },
            "gemini-flash-lite": {
                "id": "gemini-2.0-flash-lite",
                "name": "Gemini 2.0 Flash Lite",
                "description": "Lightest, fastest Gemini",
            },
        },
    },
    "mistral": {
        "name": "Mistral",
        "key": MISTRAL_API_KEY,
        "base_url": "https://api.mistral.ai/v1",
        "models": {
            "mistral-small": {
                "id": "mistral-small-latest",
                "name": "Mistral Small",
                "description": "Efficient Mistral model",
            },
        },
    },
    "cohere": {
        "name": "Cohere",
        "key": COHERE_API_KEY,
        "base_url": "https://api.cohere.com/v2",
        "models": {
            "command-r": {
                "id": "command-r",
                "name": "Command R",
                "description": "Cohere's conversational model",
            },
        },
    },
    "huggingface": {
        "name": "HuggingFace",
        "key": HF_API_KEY,
        "base_url": "https://api-inference.huggingface.co/v1",
        "models": {
            "hf-llama": {
                "id": "meta-llama/Llama-3.1-8B-Instruct",
                "name": "HF LLaMA 3.1 8B",
                "description": "Free HuggingFace inference",
            },
        },
    },
    "openrouter": {
        "name": "OpenRouter",
        "key": OPENROUTER_API_KEY,
        "base_url": "https://openrouter.ai/api/v1",
        "models": {
            "or-llama": {
                "id": "meta-llama/llama-3.3-70b-instruct:free",
                "name": "OR LLaMA 3.3 70B",
                "description": "Free via OpenRouter",
            },
            "or-gemma": {
                "id": "google/gemma-2-9b-it:free",
                "name": "OR Gemma 2 9B",
                "description": "Free via OpenRouter",
            },
            "or-mistral": {
                "id": "mistralai/mistral-7b-instruct:free",
                "name": "OR Mistral 7B",
                "description": "Free via OpenRouter",
            },
        },
    },
}


def get_enabled_providers() -> list[str]:
    return [name for name, p in PROVIDERS.items() if p["key"]]


def get_all_models() -> dict[str, dict]:
    """Flat map of short_name -> {id, name, description, provider}."""
    models = {}
    for prov_name, prov in PROVIDERS.items():
        if not prov["key"]:
            continue
        for short, info in prov["models"].items():
            models[short] = {**info, "provider": prov_name}
    return models


def validate():
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required. See .env.example.")
    enabled = get_enabled_providers()
    if not enabled:
        raise RuntimeError(
            "No AI provider configured. Add at least one API key "
            "(GROQ_API_KEY, GEMINI_API_KEY, etc.) to .env."
        )
