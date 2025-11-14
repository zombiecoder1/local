# Editor Integration (Cursor, VS Code Copilot)

এই ডকুমেন্টে জানানো হলো কীভাবে Hello Zombie সার্ভারকে কোনো এক্সটেনশন না বানিয়েও OpenAI-compatible ক্লায়েন্টে সংযুক্ত করবেন।

## OpenAI Compatibility
- Base URL: `http://127.0.0.1:8001/v1`
- Endpoints:
  - `POST /chat/completions`
  - `GET /models`
- API Key: লোকাল সেটাপে ডামি কী ব্যবহার করতে পারেন (যেমন: `hello-zombie-local`).

## Cursor Settings উদাহরণ
`doc/cursor_settings.json` থেকে কনফিগ কপি করে Cursor settings এ যোগ করুন।
```json
{
  "cursor.chat.customModel": {
    "url": "http://127.0.0.1:8001/v1/chat/completions",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL"
  },
  "cursor.telemetry.enabled": false
}
```

## Without Extension (Generic OpenAI Client)
```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi-2-gguf",
    "messages": [
      {"role": "user", "content": "Hello Zombie!"}
    ]
  }'
```

## Features
- **Streaming (SSE)**: `stream: true` পাঠালে OpenAI chunk format-এ ইভেন্ট আসে।
- **Session Memory**: নেটিভ `/chat` এ `session_id` দিলে আগের কথোপকথন context হিসেবে ব্যবহৃত হয়।
- **Language & Prefix**: উত্তর বাংলা-প্রাধান্য এবং `ভাইয়া` প্রিফিক্স কনফিগারেবল (দেখুন `agents/hello_zombie.yaml`).
