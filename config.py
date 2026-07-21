import json
import os

from dotenv import load_dotenv

load_dotenv()

# ── Core ──
def _read_version() -> str:
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")) as f:
            return f.read().strip() or "0.0.0"
    except OSError:
        return "0.0.0"


VERSION = _read_version()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_START_TIME = 0.0  # set at runtime
# Optional chat ID that receives crash alerts (see /version, self-healing).
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID", "")

# Models auto-discovered by the weekly update workflow (scripts/sync_models.py).
DISCOVERED_MODELS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "discovered_models.json"
)

# ── API Keys (all optional; providers with keys get enabled) ──
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# GitHub Models (free with a GitHub Personal Access Token). Accepts either a
# dedicated GITHUB_MODELS_API_KEY or a standard GITHUB_TOKEN / GH_TOKEN.
GITHUB_MODELS_API_KEY = (
    os.getenv("GITHUB_MODELS_API_KEY", "")
    or os.getenv("GITHUB_TOKEN", "")
    or os.getenv("GH_TOKEN", "")
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "") or os.getenv("DASHSCOPE_API_KEY", "")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")

# ── Optional Google Custom Search (100 free searches/day) ──
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

# ── Defaults ──
DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "groq")
DEFAULT_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
MAX_CONTEXT_MESSAGES = int(os.getenv("MAX_CONTEXT_MESSAGES", "20"))
MAX_RESPONSE_TOKENS = int(os.getenv("MAX_RESPONSE_TOKENS", "700"))
# Per-request timeout (seconds). If a model is slower, fall back to a faster one.
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are OpenClaw Bot, a helpful AI assistant. "
    "Answer clearly and concisely, keeping responses under 500 words.",
)

# ── Health check ──
HEALTH_PORT = int(os.getenv("HEALTH_PORT", "8080"))

# ── Conversation memory (JSON file) ──
MEMORY_PATH = os.getenv("MEMORY_PATH", "data/memory.json")

# ── Provider registry ──
# Each provider: {key_env, models: {short_name: {id, name, description}}}
PROVIDERS = {
    # GitHub Models: free AI (GPT-4o, Llama, Mistral, DeepSeek) using just a
    # GitHub Personal Access Token. OpenAI-compatible endpoint.
    "github": {
        "name": "GitHub Models",
        "key": GITHUB_MODELS_API_KEY,
        "base_url": "https://models.github.ai/inference",
        "models": {
            "gpt-4o-mini": {
                "id": "openai/gpt-4o-mini",
                "name": "GPT-4o mini (GitHub)",
                "description": "Fast free GPT-4o mini via GitHub",
            },
            "gpt-4o": {
                "id": "openai/gpt-4o",
                "name": "GPT-4o (GitHub)",
                "description": "Most capable OpenAI model, free via GitHub",
            },
            "github-llama-70b": {
                "id": "meta/Llama-3.3-70B-Instruct",
                "name": "Llama 3.3 70B (GitHub)",
                "description": "Meta Llama 3.3 70B, free via GitHub",
            },
            "github-mistral": {
                "id": "mistral-ai/Mistral-Nemo",
                "name": "Mistral Nemo (GitHub)",
                "description": "Mistral Nemo, free via GitHub",
            },
        },
    },
    "groq": {
        "name": "Groq",
        "key": GROQ_API_KEY,
        "base_url": "https://api.groq.com/openai/v1",
        "models": {
            "llama-3.1-8b": {
                "id": "llama-3.1-8b-instant",
                "name": "LLaMA 3.1 8B",
                "description": "Fastest, default model",
                "max_completion_tokens": 8192,
            },
            "llama-3.3-70b": {
                "id": "llama-3.3-70b-versatile",
                "name": "LLaMA 3.3 70B",
                "description": "Most capable, slower",
                "max_completion_tokens": 8192,
            },
            "qwen3-32b": {
                "id": "qwen/qwen3-32b",
                "name": "Qwen 3 32B",
                "description": "Strong reasoning and coding",
                "max_completion_tokens": 8192,
            },
            "llama4-scout": {
                "id": "meta-llama/llama-4-scout-17b-16e-instruct",
                "name": "LLaMA 4 Scout 17B",
                "description": "Latest LLaMA 4, multimodal",
                "max_completion_tokens": 8192,
            },
        },
    },
    "gemini": {
        "name": "Google Gemini",
        "key": GEMINI_API_KEY,
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "litellm_prefix": "gemini",
        "models": {
            "gemini-flash": {
                "id": "gemini-1.5-flash",
                "name": "Gemini 1.5 Flash",
                "description": "Fast, free Google AI",
            },
        },
    },
    "mistral": {
        "name": "Mistral",
        "key": MISTRAL_API_KEY,
        "base_url": "https://api.mistral.ai/v1",
        "models": {
            "mistral-large": {
                "id": "mistral-large-latest",
                "name": "Mistral Large",
                "description": "Most capable Mistral model",
            },
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
        # Cohere's OpenAI-compatible endpoint (works with the openai SDK).
        "base_url": "https://api.cohere.ai/compatibility/v1",
        "models": {
            "command-r-plus": {
                "id": "command-r-plus",
                "name": "Command R+",
                "description": "Cohere's most capable model",
            },
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
        # HuggingFace's OpenAI-compatible inference router.
        "base_url": "https://router.huggingface.co/v1",
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
            "or-llama-8b": {
                "id": "meta-llama/llama-3.1-8b-instruct:free",
                "name": "OR LLaMA 3.1 8B",
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
            "or-phi3": {
                "id": "microsoft/phi-3-mini-128k-instruct:free",
                "name": "OR Phi-3 Mini 128k",
                "description": "Free via OpenRouter",
            },
            "or-hermes-405b": {
                "id": "nousresearch/hermes-3-llama-3.1-405b:free",
                "name": "OR Hermes 3 405B",
                "description": "Free via OpenRouter",
            },
        },
    },
    "deepseek": {
        "name": "DeepSeek",
        "key": DEEPSEEK_API_KEY,
        "base_url": "https://api.deepseek.com",
        "models": {
            "deepseek-chat": {
                "id": "deepseek-chat",
                "name": "DeepSeek V3",
                "description": "Very capable general chat model",
            },
            "deepseek-reasoner": {
                "id": "deepseek-reasoner",
                "name": "DeepSeek R1",
                "description": "Strong reasoning model",
            },
        },
    },
    "cerebras": {
        "name": "Cerebras",
        "key": CEREBRAS_API_KEY,
        "base_url": "https://api.cerebras.ai/v1",
        "models": {
            "cerebras-llama-8b": {
                "id": "llama3.1-8b",
                "name": "Cerebras LLaMA 3.1 8B",
                "description": "Extremely fast inference",
            },
        },
    },
    "qwen": {
        "name": "Qwen (DashScope)",
        "key": QWEN_API_KEY,
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "models": {
            "qwen-turbo": {
                "id": "qwen-turbo",
                "name": "Qwen Turbo",
                "description": "Fast and free",
            },
            "qwen-plus": {
                "id": "qwen-plus",
                "name": "Qwen Plus",
                "description": "More capable",
            },
            "qwen-max": {
                "id": "qwen-max",
                "name": "Qwen Max",
                "description": "Best quality",
            },
        },
    },
    "together": {
        "name": "Together AI",
        "key": TOGETHER_API_KEY,
        "base_url": "https://api.together.xyz/v1",
        "models": {
            "together-llama-8b": {
                "id": "meta-llama/Llama-3-8b-chat-hf",
                "name": "Together LLaMA 3 8B",
                "description": "Free tier LLaMA 3",
            },
            "together-mistral-7b": {
                "id": "mistralai/Mistral-7B-Instruct-v0.1",
                "name": "Together Mistral 7B",
                "description": "Free tier Mistral",
            },
        },
    },
    "moonshot": {
        "name": "Moonshot (Kimi)",
        "key": MOONSHOT_API_KEY,
        "base_url": "https://api.moonshot.cn/v1",
        "models": {
            "kimi-k3": {
                "id": "kimi-k3",
                "name": "Kimi K3",
                "description": "Latest large Kimi model",
            },
            "moonshot-v1-8k": {
                "id": "moonshot-v1-8k",
                "name": "Moonshot v1 8k",
                "description": "Fast Chinese/English model",
            },
        },
    },
    "zhipu": {
        "name": "Zhipu AI (GLM)",
        "key": ZHIPU_API_KEY,
        "base_url": "https://open.bigmodel.cn/api/paas/v4",
        "models": {
            "glm-4-flash": {
                "id": "glm-4-flash",
                "name": "GLM-4 Flash",
                "description": "Completely free GLM model",
            },
        },
    },
    "siliconflow": {
        "name": "SiliconFlow",
        "key": SILICONFLOW_API_KEY,
        "base_url": "https://api.siliconflow.cn/v1",
        "models": {
            "sf-qwen-7b": {
                "id": "Qwen/Qwen2.5-7B-Instruct",
                "name": "SF Qwen2.5 7B",
                "description": "Free tier Qwen",
            },
            "sf-deepseek": {
                "id": "deepseek-ai/DeepSeek-V2.5",
                "name": "SF DeepSeek V2.5",
                "description": "Free tier DeepSeek",
            },
        },
    },
    # Keyless, always-on last-resort fallback so chat never fully goes down.
    "pollinations": {
        "name": "Pollinations",
        "key": os.getenv("POLLINATIONS_API_KEY", "keyless"),
        "base_url": "https://text.pollinations.ai/openai",
        "models": {
            "pollinations-openai": {
                "id": "openai",
                "name": "Pollinations (keyless)",
                "description": "Free text AI, no API key required",
            },
            "pollinations-mistral": {
                "id": "mistral",
                "name": "Pollinations Mistral (keyless)",
                "description": "Free Mistral via Pollinations, no key",
            },
        },
    },
}


# Fallback priority: try fastest/best first, keyless Pollinations always last.
PROVIDER_PRIORITY = [
    "groq",
    "github",
    "cerebras",
    "deepseek",
    "openrouter",
    "qwen",
    "together",
    "moonshot",
    "zhipu",
    "siliconflow",
    "gemini",
    "mistral",
    "cohere",
    "huggingface",
    "pollinations",
]

LAST_UPDATE = "unknown"


def _load_discovered() -> dict:
    try:
        with open(DISCOVERED_MODELS_PATH) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def _merge_discovered_models() -> None:
    """Merge models auto-discovered by the weekly workflow into the registry."""
    global LAST_UPDATE
    data = _load_discovered()
    LAST_UPDATE = data.get("updated", "unknown")
    for prov_name, models in data.get("providers", {}).items():
        prov = PROVIDERS.get(prov_name)
        if not prov:
            continue
        existing_ids = {m["id"] for m in prov["models"].values()}
        for m in models:
            mid = m.get("id")
            if not mid or mid in existing_ids:
                continue
            short = mid.split("/")[-1][:40]
            prov["models"][short] = {
                "id": mid,
                "name": m.get("name", mid),
                "description": m.get("description", "Auto-discovered model"),
                "max_completion_tokens": m.get("max_completion_tokens", 8192),
            }
            existing_ids.add(mid)


_merge_discovered_models()


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
