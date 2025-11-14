# Hello Zombie - OpenAI Compatible Local Server

Hello Zombie হল একটি লোকাল OpenAI-compatible ব্যাকএন্ড যা আধুনিক AI এডিটর (VS Code Copilot, Cursor ইত্যাদি) এর সাথে সরাসরি কাজ করতে ডিজাইন করা।

## Core Capabilities
- OpenAI API compatible endpoints: `/v1/chat/completions`, `/v1/models`
- Native endpoints: `/health`, `/models`, `/chat`, `/conversations/{agent}`
- Streaming (SSE) support
- Session-based JSON memory + SQLite system memory
- Persona prefix (ভাইয়া) ও বাংলা-প্রাধান্যযুক্ত উত্তর

## Quick Start
1) Python 3.11 venv
```bash
py -3.11 -m venv .venv311
.\\.venv311\\Scripts\\activate
pip install -r requirements.txt
```
2) Run server
```bash
python -m uvicorn main_server:app --host 127.0.0.1 --port 12346 --log-level info
```
3) Health check
```bash
curl http://127.0.0.1:12346/health
```

## Editor Integration
- Cursor/VS Code Copilot সহ যেকোনো OpenAI-compatible ক্লায়েন্টে Base URL দিন: `http://127.0.0.1:8001/v1`
- উদাহরণ settings কনফিগ: `doc/cursor_settings.json`
- বিস্তারিত: `doc/extensions.md`

## Endpoints
- `POST /v1/chat/completions` (OpenAI) — stream/non-stream
- `GET /v1/models`
- `POST /chat` (session_id, stream)
- `GET /health`

## Tests
- Smoke: `python test/integration_test.py`
- Final E2E: `python test/final_integration_test.py`

## Logs & Config
- Logs: `log/main_server.log`
- Agent config: `agents/hello_zombie.yaml`
- JSON memory: `memory/hello_zombie_memory.json`
- Lock file: `data/server.lock`

