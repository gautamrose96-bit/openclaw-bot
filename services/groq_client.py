from groq import Groq

import config
from utils.logger import get_logger

logger = get_logger("groq_client")


class GroqClient:
    """Thin wrapper around the Groq SDK that manages per-chat context."""

    def __init__(self) -> None:
        self._client = Groq(api_key=config.GROQ_API_KEY)
        self._histories: dict[int, list[dict[str, str]]] = {}

    def _get_history(self, chat_id: int) -> list[dict[str, str]]:
        if chat_id not in self._histories:
            self._histories[chat_id] = []
        return self._histories[chat_id]

    def clear_history(self, chat_id: int) -> None:
        self._histories.pop(chat_id, None)

    def _trim_history(self, history: list[dict[str, str]]) -> None:
        max_msgs = config.MAX_CONTEXT_MESSAGES * 2  # pairs of user+assistant
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

        try:
            response = self._client.chat.completions.create(
                model=config.GROQ_MODEL,
                messages=messages,
                max_tokens=config.MAX_RESPONSE_TOKENS,
                temperature=0.7,
            )
            reply = response.choices[0].message.content or ""
            history.append({"role": "assistant", "content": reply})
            return reply
        except Exception:
            # Remove the failed user message so context stays clean
            history.pop()
            logger.exception("Groq API call failed for chat %s", chat_id)
            raise
