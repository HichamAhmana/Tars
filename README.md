# TARS — Voice-Controlled PC Assistant (v2)

TARS is a Jarvis-inspired, modular voice assistant. It pairs a plugin-based Python
engine with a Django REST + WebSocket backend and a glassmorphic Next.js dashboard,
so you get hands-free PC control **and** a realtime view of everything that is
happening on your machine.

![TARS Banner](https://img.shields.io/badge/TARS-v2-00d2ff?style=for-the-badge)

## ✨ What's new in v2

| Pillar | v1                                       | v2                                                                           |
| ------ | ---------------------------------------- | ---------------------------------------------------------------------------- |
| Brain  | Hardcoded keyword matcher                | Plugin-based skill registry + optional LLM intent parser (OpenAI/Groq/Ollama) with rule-based fallback, plus short-term conversational memory |
| Voice  | Google STT + pyttsx3                      | Pluggable pipeline: **Porcupine** wake word, **faster-whisper** STT, **edge-tts** TTS — all optional via env vars, falls back to v1 stack |
| OS     | Windows-only                              | Cross-platform abstraction layer (Windows / macOS / Linux) behind `engine/platform/` |
| API    | Unauthenticated REST                      | API-token auth (`TARS_REQUIRE_AUTH=1`), WebSocket stream for realtime engine events, `/skills/`, `/engine/speak/`, `/tokens/` |
| Dash   | 3s polling, no realtime                   | Live WebSocket log, **push-to-talk** from the browser, skills browser, theme toggle, provider pickers |
| Polish | Empty `tests/`, no CI                     | Pytest suite for skills / brain / platform / API, GitHub Actions CI, cross-platform `start.sh` / `start.bat` |

## 🏗️ Architecture

```
┌────────────┐   WS + REST    ┌─────────────┐   pub/sub events   ┌─────────────┐
│ Dashboard  │◄──────────────►│ Django +    │◄──────────────────►│  Engine     │
│ Next.js 16 │                │ Channels    │                    │  (skills,   │
│ (React 19) │                │ REST API    │                    │  brain, OS) │
└────────────┘                └─────────────┘                    └─────────────┘
                                    ▲                                    ▲
                                    │ TokenAuth                          │ platform/*
                                    │                                    ▼
                                 SQLite                           Windows / macOS / Linux
```

- **`engine/`** — plugin-based skill registry (`engine/skills/*.py`), brain
  (`engine/brain.py`), audio pipeline (`engine/wake.py`, `stt.py`, `tts.py`) and
  OS driver (`engine/platform/{windows,macos,linux}.py`).
- **`backend/`** — ASGI Django app with HTTP **and** WebSocket routing
  (Channels in-memory layer by default).
- **`api/`** — DRF views, serializers, token auth, `events.publish()` helper
  that broadcasts to WebSocket subscribers.
- **`dashboard/`** — Next.js 16 / React 19 UI with live log, push-to-talk, skills
  browser, settings panel, dark/light theme.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (the dashboard is built with Next.js 16)
- Windows, macOS, or Linux

### 1. Clone & install

```bash
git clone https://github.com/HichamAhmana/Tars.git
cd Tars
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt   # optional: tests + linters
python manage.py migrate

cd dashboard && npm install && cd ..
```

### 2. Configure (optional)

Copy `.env.example` to `.env` and set any integration you want to opt into.
**Nothing is required** — if you skip every env var, TARS uses the built-in
rule router, Google STT, and pyttsx3 TTS.

```bash
cp .env.example .env
```

### 3. Run everything

```bash
# macOS / Linux
./start.sh

# Windows
start.bat
```

This boots Django (ASGI via daphne) on `:8000`, the dashboard on `:3000`, and
the voice engine in the foreground. Open `http://localhost:3000` and hit
**Start Tars**.

## 🧩 Skills — add a new one in 20 lines

Every skill lives in its own file under `engine/skills/` and registers itself
with the `@skill` decorator:

```python
# engine/skills/weather.py
from . import skill, SkillContext

@skill(name="weather.current", triggers=("weather", "what's the weather"), priority=4)
def current_weather(text: str, ctx: SkillContext) -> bool:
    ctx.speak("It's 22 degrees and sunny.")
    return True
```

Drop the file in and it's live next time you run `python -m engine.main` — no
router changes, no imports to update.

## 🧠 Optional LLM brain

Set `BRAIN_PROVIDER=openai|groq|ollama` plus a key in `.env` to enable
free-form Q&A ("what's 15% of 240?", "summarize gravity"). When the rule
router recognises a skill trigger it still takes priority — the LLM only
answers when nothing matches.

## 🎙️ Optional voice upgrades

| Variable             | Effect                                                          |
| -------------------- | --------------------------------------------------------------- |
| `PORCUPINE_ACCESS_KEY` | Offline wake-word detection (install `pvporcupine pvrecorder`). |
| `STT_PROVIDER=whisper` | Local, private STT via `faster-whisper`.                        |
| `TTS_PROVIDER=edge`    | Neural voices via `edge-tts`.                                   |

All three are optional — if the libraries aren't installed, TARS falls back
to the built-in defaults.

## 🔒 Auth

Set `TARS_REQUIRE_AUTH=1` to lock down the REST + WebSocket API. Generate a
token via the dashboard or:

```bash
python manage.py shell -c "from api.models import APIToken; print(APIToken.create('my-laptop').key)"
```

The engine reads `TARS_API_TOKEN` and attaches it automatically; the dashboard
reads it from `localStorage.TARS_API_TOKEN` or `NEXT_PUBLIC_TARS_API_TOKEN`.

## 🧪 Tests

```bash
pytest                      # engine + backend
cd dashboard && npm run lint && npm run build
```

The same commands run on every push / PR via GitHub Actions
(`.github/workflows/ci.yml`).

## 📁 Project layout

```
Tars/
├── engine/
│   ├── skills/          # plugin-based skills (@skill decorator)
│   ├── platform/        # OS abstraction (windows, macos, linux)
│   ├── brain.py         # intent router + optional LLM
│   ├── wake.py / stt.py / tts.py
│   ├── memory.py        # short-term conversational state
│   └── main.py          # entry point
├── api/                 # DRF views, serializers, auth, events, consumers
├── backend/             # Django settings, ASGI app
├── dashboard/           # Next.js 16 / React 19 UI
├── start.sh / start.bat # cross-platform launcher
├── .env.example
└── .github/workflows/ci.yml
```

---
*Built with ❤️ for productivity.*
