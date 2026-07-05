"""Lightweight HTTP health check server for keep-alive pings."""

import asyncio
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

import config
from utils.logger import get_logger

logger = get_logger("health")

_start_time = 0.0
_status = "starting"
_ai_client = None


def _uptime() -> str:
    secs = int(time.time() - _start_time)
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


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health" or self.path == "/":
            body = (
                f'{{"status":"{_status}",'
                f'"uptime":"{_uptime()}",'
                f'"providers":{len(config.get_enabled_providers())}}}'
            )
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.write(body.encode())
        elif self.path == "/ping":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.write(b"pong")
        else:
            self.send_response(404)
            self.end_headers()

    def write(self, data: bytes):
        self.wfile.write(data)

    def log_message(self, format, *args):
        pass  # suppress request logs


def start_health_server(ai_client=None) -> None:
    global _start_time, _status, _ai_client
    _start_time = time.time()
    _status = "running"
    _ai_client = ai_client
    port = config.HEALTH_PORT

    def _run():
        server = HTTPServer(("0.0.0.0", port), _Handler)
        server.allow_reuse_address = True
        logger.info("Health server on port %s", port)
        server.serve_forever()

    thread = Thread(target=_run, daemon=True)
    thread.start()


async def self_ping_loop() -> None:
    """Periodically ping our own health endpoint to keep free-tier services awake."""
    import aiohttp
    port = config.HEALTH_PORT
    url = f"http://127.0.0.1:{port}/ping"
    while True:
        await asyncio.sleep(240)  # every 4 minutes
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)):
                    pass
        except Exception:
            pass
