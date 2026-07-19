"""Free, no-API-key tools: web search, weather, news, image gen, calculator."""

import ast
import operator
import urllib.parse
import xml.etree.ElementTree as ET

import aiohttp

from utils.logger import get_logger

logger = get_logger("tools")

_TIMEOUT = aiohttp.ClientTimeout(total=15)
_UA = {"User-Agent": "OpenClawBot/1.0 (+https://github.com/gautamrose96-bit/openclaw-bot)"}


async def _get_json(url: str) -> dict:
    async with aiohttp.ClientSession(timeout=_TIMEOUT, headers=_UA) as s:
        async with s.get(url) as r:
            return await r.json(content_type=None)


async def _get_text(url: str) -> str:
    async with aiohttp.ClientSession(timeout=_TIMEOUT, headers=_UA) as s:
        async with s.get(url) as r:
            return await r.text()


async def ddg_search(query: str) -> str:
    """Search via DuckDuckGo's free Instant Answer API (no key)."""
    url = (
        "https://api.duckduckgo.com/?q="
        + urllib.parse.quote(query)
        + "&format=json&no_html=1&skip_disambig=1"
    )
    try:
        data = await _get_json(url)
    except Exception as exc:
        logger.warning("DDG search failed: %s", exc)
        return "Search failed. Please try again."

    if data.get("AbstractText"):
        out = data["AbstractText"]
        if data.get("AbstractURL"):
            out += f"\n\nSource: {data['AbstractURL']}"
        return out

    topics = []
    for t in data.get("RelatedTopics", []):
        text = t.get("Text")
        if text:
            topics.append(f"- {text}")
        if len(topics) >= 5:
            break
    if topics:
        return "Top results:\n" + "\n".join(topics)
    return f"No instant answer found for '{query}'. Try rephrasing."


async def get_weather(city: str) -> str:
    """Current weather via wttr.in (no key)."""
    fmt = urllib.parse.quote("%l: %c %t (feels %f), humidity %h, wind %w")
    url = f"https://wttr.in/{urllib.parse.quote(city)}?format={fmt}&m"
    try:
        text = (await _get_text(url)).strip()
    except Exception as exc:
        logger.warning("Weather failed: %s", exc)
        return "Could not fetch weather. Please try again."
    if not text or "Unknown location" in text or "sorry" in text.lower():
        return f"Could not find weather for '{city}'."
    return text


async def get_news(topic: str, limit: int = 5) -> str:
    """Latest headlines via Google News RSS (no key)."""
    url = (
        "https://news.google.com/rss/search?q="
        + urllib.parse.quote(topic)
        + "&hl=en-US&gl=US&ceid=US:en"
    )
    try:
        xml = await _get_text(url)
        root = ET.fromstring(xml)
    except Exception as exc:
        logger.warning("News failed: %s", exc)
        return "Could not fetch news. Please try again."

    items = root.findall(".//item")[:limit]
    if not items:
        return f"No news found for '{topic}'."
    lines = [f"Latest news on '{topic}':\n"]
    for it in items:
        title = it.findtext("title") or "(no title)"
        link = it.findtext("link") or ""
        lines.append(f"- {title}\n  {link}")
    return "\n".join(lines)


def image_url(prompt: str) -> str:
    """Build a Pollinations.ai image URL (no key)."""
    return (
        "https://image.pollinations.ai/prompt/"
        + urllib.parse.quote(prompt)
        + "?width=1024&height=1024&nologo=true"
    )


# Pollinations generation can take a while, so allow a generous timeout.
_IMAGE_TIMEOUT = aiohttp.ClientTimeout(total=90)


async def fetch_image(prompt: str, attempts: int = 3) -> bytes | None:
    """Download a generated image from Pollinations as raw bytes (no key).

    Returns the image bytes, or None if generation failed after retries.
    """
    url = image_url(prompt)
    for attempt in range(1, attempts + 1):
        try:
            async with aiohttp.ClientSession(timeout=_IMAGE_TIMEOUT, headers=_UA) as s:
                async with s.get(url) as r:
                    data = await r.read()
                    ctype = r.headers.get("Content-Type", "")
                    if r.status == 200 and ctype.startswith("image/") and data:
                        return data
                    logger.warning(
                        "Pollinations attempt %d: status=%s type=%s len=%d",
                        attempt, r.status, ctype, len(data),
                    )
        except Exception as exc:
            logger.warning("Pollinations attempt %d failed: %s", attempt, exc)
    return None


# ── Safe calculator ──
_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval_node(node.operand))
    raise ValueError("Unsupported expression")


def calculate(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression (no names/calls)."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _eval_node(tree.body)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception:
        return "Invalid expression. Use numbers and + - * / // % ** ( )."
    if isinstance(result, float) and result.is_integer():
        result = int(result)
    return f"{expression} = {result}"
