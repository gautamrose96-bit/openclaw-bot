# Changelog

## 1.1.0
- Auto-update system: weekly workflow discovers new free Groq/OpenRouter models
- `/version` and `/changelog` commands
- Keyless Pollinations text fallback so chat never fully goes down
- Real web search (DuckDuckGo + optional Google) with AI summaries and auto-search
- Speed: faster default model, typing indicator, per-request timeout, ~500-word cap
- Monthly keepalive workflow so scheduled Actions never auto-disable

## 1.0.0
- Multi-provider AI chat with automatic fallback (Groq, Mistral, Cohere, HF, OpenRouter, Gemini)
- Per-user JSON conversation memory
- Tools: /weather /news /translate /summarize /calculate /imagine /search
- Long-message splitting (>4096 chars)
- 24/7 hosting via GitHub Actions with crash-retry loop
