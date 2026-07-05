"""Multi-provider AI client with automatic fallback and rate-limit rotation."""

import time

from openai import AsyncOpenAI

import config
from utils.logger import get_logger

logger = get_logger("ai_client")

# Cooldown (seconds) after a provider fails before retrying it
_PROVIDER_COOLDOWN = 60


class AIClient:
    """Routes chat requests across multiple AI providers with auto-fallback."""

    def __init__(self) -> None:
        self._clients: dict[str, AsyncOpenAI] = {}
        self._histories: dict[int, list[dict[str, str]]] = {}
        self._chat_provider: dict[int, str] = {}
        self._chat_model: dict[int, str] = {}
        self._provider_failures: dict[str, float] = {}
        self._provider_requests: dict[str, int] = {}

        for prov_name, prov in config.PROVIDERS.items():
            if not prov["key"]:
                continue
            self._clients[prov_name] = AsyncOpenAI(
                api_key=prov["key"],
                base_url=prov["base_url"],
            )
            self._provider_requests[prov_name] = 0
            logger.info("Enabled provider: %s (%s)", prov["name"], prov_name)

    # ── Provider ordering ──

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

    def _get_default_model(self, provider: str) -> str:
        models = config.PROVIDERS[provider]["models"]
        return next(iter(models.values()))["id"]

    # ── Per-chat state ──

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

    def get_stats(self) -> dict[str, int]:
        return dict(self._provider_requests)

    def get_healthy_providers(self) -> list[str]:
        now = time.time()
        return [
            n for n in self._clients
            if now - self._provider_failures.get(n, 0) > _PROVIDER_COOLDOWN
        ]

    # ── Chat ──

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        max_msgs = config.MAX_CONTEXT_MESSAGES * 2
        while len(history) > max_msgs:
            history.pop(0)

    async def chat(self, chat_id: int, user_message: str) -> str:
        history = self._get_history(chat_id)
        history.append({"role": "user", "content": user_message})
        self._trim_history(history)

        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            *history,
        ]

        preferred_provider = self.get_provider(chat_id)
        preferred_model = self.get_model_id(chat_id)
        providers_to_try = self._get_provider_order(preferred_provider)

        last_error = None
        for prov_name in providers_to_try:
            model = preferred_model if prov_name == preferred_provider else self._get_default_model(prov_name)
            try:
                reply = await self._call_provider(prov_name, model, messages)
                history.append({"role": "assistant", "content": reply})
                if prov_name != preferred_provider:
                    logger.info(
                        "Fallback: %s -> %s for chat %s",
                        preferred_provider, prov_name, chat_id,
                    )
                return reply
            except Exception as exc:
                self._provider_failures[prov_name] = time.time()
                last_error = exc
                logger.warning(
                    "Provider %s failed (model=%s): %s", prov_name, model, exc,
                )

        history.pop()
        logger.error("All providers failed for chat %s", chat_id)
        raise last_error  # type: ignore[misc]

    async def _call_provider(self, provider: str, model: str, messages: list[dict]) -> str:
        client = self._clients[provider]
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=config.MAX_RESPONSE_TOKENS,
            temperature=0.7,
        )
        self._provider_requests[provider] = self._provider_requests.get(provider, 0) + 1
        self._provider_failures.pop(provider, None)
        content = response.choices[0].message.content
        return content or ""
