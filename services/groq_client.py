from groq import Groq

import config
from utils.logger import get_logger

logger = get_logger("groq_client")


class GroqClient:
    """Thin wrapper around the Groq SDK that manages per-chat context and models."""

    def __init__(self) -> None:
        self._client = Groq(api_key=config.GROQ_API_KEY)
        self._histories: dict[int, list[dict[str, str]]] = {}
        self._models: dict[int, str] = {}

    def _get_history(self, chat_id: int) -> list[dict[str, str]]:
        if chat_id not in self._histories:
            self._histories[chat_id] = []
        return self._histories[chat_id]

    def get_model(self, chat_id: int) -> str:
        return self._models.get(chat_id, config.DEFAULT_MODEL)

    def set_model(self, chat_id: int, model_id: str) -> None:
        self._models[chat_id] = model_id

    def clear_history(self, chat_id: int) -> None:
        self._histories.pop(chat_id, None)

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        max_msgs = config.MAX_CONTEXT_MESSAGES * 2
        while len(history) > max_msgs:
            history.pop(0)

    async def chat(self, chat_id: int, user_message: str) -> str:
        history = self._get_history(chat_id)
        history.append({"role": "user", "content": user_message})
        self._trim_history(history)

        model = self.get_model(chat_id)
        messages = [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            *history,
        ]

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=config.MAX_RESPONSE_TOKENS,
                temperature=0.7,
            )
            reply = response.choices[0].message.content or ""
            history.append({"role": "assistant", "content": reply})
            return reply
        except Exception:
            history.pop()
            logger.exception("Groq API call failed (model=%s, chat=%s)", model, chat_id)
            raise
