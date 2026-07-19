"""Simple per-chat conversation memory backed by a JSON file.

Free, no database. Note: on ephemeral hosts (e.g. GitHub Actions runners) the
file is wiped on each restart, so memory only persists within a single run.
On a persistent host (VPS/Docker volume) it survives restarts.
"""

import json
import os
import threading

from utils.logger import get_logger

logger = get_logger("memory")


class JSONMemory:
    """Thread-safe JSON-file store of {chat_id: [ {role, content}, ... ]}."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._lock = threading.Lock()

    def load_all(self) -> dict[int, list[dict[str, str]]]:
        try:
            with open(self.path, encoding="utf-8") as f:
                raw = json.load(f)
            return {int(k): v for k, v in raw.items()}
        except FileNotFoundError:
            return {}
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Could not read memory file %s: %s", self.path, exc)
            return {}

    def save_all(self, data: dict[int, list[dict[str, str]]]) -> None:
        with self._lock:
            directory = os.path.dirname(self.path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            tmp = f"{self.path}.tmp"
            try:
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump({str(k): v for k, v in data.items()}, f)
                os.replace(tmp, self.path)
            except OSError as exc:
                logger.warning("Could not write memory file %s: %s", self.path, exc)
