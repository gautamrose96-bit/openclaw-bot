# Changelog

## 1.2.0
- Added free providers: DeepSeek, Cerebras, Qwen (DashScope), Moonshot/Kimi, Zhipu GLM, SiliconFlow, Together AI
- Added OpenRouter free models: Phi-3 Mini 128k, Hermes 3 405B
- Explicit fallback priority order (Groq → Cerebras → DeepSeek → OpenRouter → Qwen → Together → Kimi → … → Pollinations)
- `/version` now reads a `VERSION` file
- Auto key detection: only providers with a key set are enabled

## 2026-07-19
- Added model `openrouter:tencent/hy3:free`
- Added model `openrouter:poolside/laguna-xs-2.1:free`
- Added model `openrouter:cohere/north-mini-code:free`
- Added model `openrouter:nvidia/nemotron-3.5-content-safety:free`
- Added model `openrouter:nvidia/nemotron-3-ultra-550b-a55b:free`
- Added model `openrouter:nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free`
- Added model `openrouter:poolside/laguna-m.1:free`
- Added model `openrouter:google/gemma-4-26b-a4b-it:free`
- Added model `openrouter:google/gemma-4-31b-it:free`
- Added model `openrouter:nvidia/nemotron-3-super-120b-a12b:free`
- Added model `openrouter:nvidia/nemotron-3-nano-30b-a3b:free`
- Added model `openrouter:nvidia/nemotron-nano-12b-v2-vl:free`
- Added model `openrouter:nvidia/nemotron-nano-9b-v2:free`
- Added model `openrouter:openai/gpt-oss-20b:free`

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
