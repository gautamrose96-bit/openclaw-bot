#!/usr/bin/env python3
"""Discover the latest free chat models from provider /models APIs and record
any new ones in discovered_models.json. Run weekly by the update workflow.

- Groq: needs GROQ_API_KEY (fetches https://api.groq.com/openai/v1/models).
- OpenRouter: no key needed for the public /models list; only :free models kept.

Never fails the build: missing keys / network errors just skip that provider.
Exits 0 always; prints a summary. Only writes files when something changed.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config  # noqa: E402

DISCOVERED_PATH = os.path.join(ROOT, "discovered_models.json")
CHANGELOG_PATH = os.path.join(ROOT, "CHANGELOG.md")

# Groq model ids that are NOT chat completion models.
_GROQ_EXCLUDE = ("whisper", "tts", "guard", "prompt-guard", "distil")


def _http_json(url: str, token: str | None = None) -> dict:
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _static_ids(provider: str) -> set[str]:
    prov = config.PROVIDERS.get(provider, {})
    return {m["id"] for m in prov.get("models", {}).values()}


def discover_groq() -> list[dict]:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        print("Groq: no GROQ_API_KEY, skipping")
        return []
    try:
        data = _http_json("https://api.groq.com/openai/v1/models", key)
    except Exception as exc:
        print(f"Groq: fetch failed: {exc}")
        return []
    known = _static_ids("groq")
    out = []
    for m in data.get("data", []):
        mid = m.get("id", "")
        low = mid.lower()
        if not mid or mid in known:
            continue
        if any(x in low for x in _GROQ_EXCLUDE):
            continue
        out.append({
            "id": mid,
            "name": mid,
            "description": "Auto-discovered Groq model",
            "max_completion_tokens": m.get("max_completion_tokens", 8192),
        })
    print(f"Groq: {len(out)} new chat model(s)")
    return out


def discover_openrouter() -> list[dict]:
    try:
        data = _http_json("https://openrouter.ai/api/v1/models")
    except Exception as exc:
        print(f"OpenRouter: fetch failed: {exc}")
        return []
    known = _static_ids("openrouter")
    out = []
    for m in data.get("data", []):
        mid = m.get("id", "")
        if not mid.endswith(":free") or mid in known:
            continue
        out.append({
            "id": mid,
            "name": m.get("name", mid),
            "description": "Free via OpenRouter (auto-discovered)",
        })
    print(f"OpenRouter: {len(out)} new free model(s)")
    return out


def main() -> int:
    try:
        with open(DISCOVERED_PATH) as f:
            current = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        current = {"updated": "", "providers": {}}

    providers = {
        "groq": discover_groq(),
        "openrouter": discover_openrouter(),
    }
    # Merge with anything already discovered (keep old, add new by id).
    changed = False
    merged = current.get("providers", {})
    added_names: list[str] = []
    for prov, models in providers.items():
        existing = {m["id"] for m in merged.get(prov, [])}
        keep = list(merged.get(prov, []))
        for m in models:
            if m["id"] not in existing:
                keep.append(m)
                added_names.append(f"{prov}:{m['id']}")
                changed = True
        merged[prov] = keep

    if not changed:
        print("No new models. Nothing to write.")
        return 0

    today = dt.date.today().isoformat()
    current["updated"] = today
    current["providers"] = merged
    with open(DISCOVERED_PATH, "w") as f:
        json.dump(current, f, indent=2)
        f.write("\n")

    entry = f"## {today}\n" + "\n".join(f"- Added model `{n}`" for n in added_names) + "\n\n"
    try:
        with open(CHANGELOG_PATH) as f:
            existing_log = f.read()
    except FileNotFoundError:
        existing_log = "# Changelog\n\n"
    head, _, rest = existing_log.partition("\n\n")
    with open(CHANGELOG_PATH, "w") as f:
        f.write(head + "\n\n" + entry + rest)

    print(f"Wrote {len(added_names)} new model(s): {', '.join(added_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
