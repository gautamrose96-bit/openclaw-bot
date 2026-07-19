"""Multi-provider AI client with automatic fallback and rate-limit rotation."""

import time

from openai import AsyncOpenAI

import config
from services.memory import JSONMemory
from utils.logger import get_logger

logger = get_logger("ai_client")

_PROVIDER_COOLDOWN = 60


class AIClient:
    """Routes chat requests across multiple AI providers with auto-fallback."""

    def __init__(self) -> None:
        self._clients: dict[str, AsyncOpenAI] = {}
        self._memory = JSONMemory(config.MEMORY_PATH)
        self._histories: dict[int, list[dict[str, str]]] = self._memory.load_all()
        if self._histories:
            logger.info("Loaded memory for %d chats", len(self._histories))
        self._chat_provider: dict[int, str] = {}
        self._chat_model: dict[int, str] = {}
        self._provider_failures: dict[str, float] = {}
        self._provider_requests: dict[str, int] = {}
        # Track per-model failures within a provider
        self._model_failures: dict[str, float] = {}

        for prov_name, prov in config.PROVIDERS.items():
            if not prov["key"]:
                continue
            self._clients[prov_name] = AsyncOpenAI(
                api_key=prov["key"],
                base_url=prov["base_url"],
            )
            self._provider_requests[prov_name] = 0
            logger.info("Enabled provider: %s (%s)", prov["name"], prov_name)

    def _get_provider_order(self, preferred: str) -> list[str]:
        """Return providers sorted: preferred first, then healthy, failed last."""
        now = time.time()
        healthy = []
        cooldown = []
        for name in self._clients:
            if name == preferred:
                continue
            last_fail = self._provider_failures.get(name, 0)
            if now - last_fail > _PROVIDER_COOLDOWN:
                healthy.append(name)
            else:
                cooldown.append(name)
        result = []
        if preferred in self._clients:
            result.append(preferred)
        result.extend(healthy)
        result.extend(cooldown)
        return result

    def _get_models_for_provider(self, provider: str, preferred_model: str) -> list[str]:
        """Return model IDs for a provider, preferred first, skip recently failed ones."""
        now = time.time()
        prov_models = config.PROVIDERS[provider]["models"]
        all_ids = [info["id"] for info in prov_models.values()]
        # Put preferred model first if it belongs to this provider
        ordered = []
        if preferred_model in all_ids:
            ordered.append(preferred_model)
        for mid in all_ids:
            if mid == preferred_model:
                continue
            # Skip models that failed in the last 5 minutes
            if now - self._model_failures.get(mid, 0) < 300:
                continue
            ordered.append(mid)
        return ordered

    def _get_default_model(self, provider: str) -> str:
        models = config.PROVIDERS[provider]["models"]
        return next(iter(models.values()))["id"]

    def _get_history(self, chat_id: int) -> list[dict[str, str]]:
        if chat_id not in self._histories:
            self._histories[chat_id] = []
        return self._histories[chat_id]

    def get_provider(self, chat_id: int) -> str:
        return self._chat_provider.get(chat_id, config.DEFAULT_PROVIDER)

    def get_model_id(self, chat_id: int) -> str:
        return self._chat_model.get(chat_id, config.DEFAULT_MODEL)

    def set_model(self, chat_id: int, provider: str, model_id: str) -> None:
        self._chat_provider[chat_id] = provider
        self._chat_model[chat_id] = model_id

    def clear_history(self, chat_id: int) -> None:
        self._histories.pop(chat_id, None)
        self._memory.save_all(self._histories)

    def get_stats(self) -> dict[str, int]:
        return dict(self._provider_requests)

    def get_healthy_providers(self) -> list[str]:
        now = time.time()
        return [
            n for n in self._clients
            if now - self._provider_failures.get(n, 0) > _PROVIDER_COOLDOWN
        ]

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        max_msgs = config.MAX_CONTEXT_MESSAGES * 2
        while len(history) > max_msgs:
            history.pop(0)

    async def _generate(self, chat_id: int, messages: list[dict[str, str]]) -> str:
        """Run one completion across providers/models with auto-fallback."""
        preferred_provider = self.get_provider(chat_id)
        preferred_model = self.get_model_id(chat_id)
        providers_to_try = self._get_provider_order(preferred_provider)

        last_error = None
        for prov_name in providers_to_try:
            # Try all models in this provider (preferred first, then others)
            models_to_try = self._get_models_for_provider(prov_name, preferred_model)
            if not models_to_try:
                models_to_try = [self._get_default_model(prov_name)]

            for model in models_to_try:
                try:
                    reply = await self._call_provider(prov_name, model, messages)
                    if prov_name != preferred_provider or model != preferred_model:
                        logger.info(
                            "Used %s/%s for chat %s (preferred: %s/%s)",
                            prov_name, model, chat_id, preferred_provider, preferred_model,
                        )
                    return reply
                except Exception as exc:
                    last_error = exc
                    err_str = str(exc)
                    if "rate_limit" in err_str or "429" in err_str:
                        self._model_failures[model] = time.time()
                        logger.warning("Model %s rate-limited, trying next", model)
                    else:
                        self._provider_failures[prov_name] = time.time()
                        logger.warning("Provider %s failed: %s", prov_name, exc)
                        break  # Non-rate-limit error: skip entire provider

        logger.error("All providers/models failed for chat %s", chat_id)
        raise last_error  # type: ignore[misc]

    async def chat(self, chat_id: int, user_message: str) -> str:
        history = self._get_history(chat_id)
        history.append({"role": "user", "content": user_message})
        self._trim_history(history)

        messages = [{"role": "system", "content": config.SYSTEM_PROMPT}, *history]
        try:
            reply = await self._generate(chat_id, messages)
        except Exception:
            history.pop()  # roll back the user message on total failure
            raise
        history.append({"role": "assistant", "content": reply})
        self._memory.save_all(self._histories)
        return reply

    async def complete(self, chat_id: int, prompt: str, system: str | None = None) -> str:
        """One-off completion that does NOT touch conversation memory."""
        messages = [
            {"role": "system", "content": system or config.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        return await self._generate(chat_id, messages)

    def _get_model_max_tokens(self, provider: str, model: str) -> int:
        """Return the model-specific max_completion_tokens, falling back to the global default."""
        prov = config.PROVIDERS.get(provider, {})
        for info in prov.get("models", {}).values():
            if info["id"] == model:
                return info.get("max_completion_tokens", config.MAX_RESPONSE_TOKENS)
        return config.MAX_RESPONSE_TOKENS

    async def _call_provider(self, provider: str, model: str, messages: list[dict]) -> str:
        client = self._clients[provider]
        max_tokens = self._get_model_max_tokens(provider, model)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        self._provider_requests[provider] = self._provider_requests.get(provider, 0) + 1
        self._provider_failures.pop(provider, None)
        self._model_failures.pop(model, None)
        content = response.choices[0].message.content
        return content or ""
