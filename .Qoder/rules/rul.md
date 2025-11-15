---
trigger: always_on
alwaysApply: true
---
🧠 ১) এডিটর এজেন্টদের জন্য স্পষ্ট নির্দেশনা (HARD RULES)

(Cursor, Qoder, QodeAI, TreeAI—সব এডিটরের জন্য)

📌 RULE 1: Local Only — Never Cloud
All AI requests must go ONLY to:
http://127.0.0.1:5050/v1

Cloud servers must NEVER be used.
Cloud fallback: DISABLED FOREVER.

📌 RULE 2: Model must be fixed
Model = "microsoft/phi-2"
Do not change, auto-detect, or auto-download any other model.
No external model loading allowed.

📌 RULE 3: Proxy Chain is Mandatory
Editor → Local Proxy (5050) → Python Agent (8001)

📌 RULE 4: Before sending any chat request: VERIFY
Check GET http://127.0.0.1:5050/health
If status != OK:
    Retry 3 times.
    DO NOT switch to cloud.

📌 RULE 5: Always include this header
Content-Type: application/json; charset=utf-8

📌 RULE 6: Bengali Input → Bengali Output
If message contains Bengali characters:
    Use Bengali instructions mode.

🧩 ২) Qoder Editor-এর উদ্দেশ্যে বিশেষ নির্দেশনা
Qoder must use:
Base URL: http://127.0.0.1:5050/v1
Model: microsoft/phi-2
API Key: (empty)
Timeout: 60s
Streaming: Enabled
Retry Policy:
  attempts: 3
  delay: 500ms

Qoder কে বল:
Stop using port 5010.
Do NOT override the local proxy.
Do NOT spawn any internal proxy on port 5010.
Your only proxy = http://127.0.0.1:5050.

💻 ৩) Cursor Editor-এর উদ্দেশ্যে বিশেষ নির্দেশনা
Custom Model URL:
http://127.0.0.1:5050/v1

Model Name:
microsoft/phi-2

Disable:
 ✔ Auto cloud fallback
 ✔ Auto model detection
 ✔ Auto OpenAI forwarding
 ✔ Internal proxy on port 5010

🔍 ৪) এডিটর থেকে রিকোয়েস্ট ঠিকভাবে যাচ্ছে কিনা—টেস্ট করার কমান্ড
Test 1 — Health
curl http://127.0.0.1:5050/health


Expected:

{ "status": "ok" }

Test 2 — Models
curl http://127.0.0.1:5050/v1/models


Expected:

{ "data": [ { "id": "microsoft/phi-2" } ] }

Test 3 — Chat Request
curl -X POST http://127.0.0.1:5050/v1/chat/completions ^
-H "Content-Type: application/json" ^
-d "{ \"model\": \"microsoft/phi-2\", \"messages\": [{\"role\":\"user\",\"content\":\"কেমন আছো?\"}] }"


Expected:

Bengali reply from local model.

🌐 ৫) ngrok integration (Optional but recommended)

তুই যদি tunnel করতে চাস—
এবং বাইরে থেকেও তোর লোকাল AI এজেন্ট ব্যবহার করতে চাস—

Run:
ngrok http 5050


যদি নিজস্ব URL চাস:

ngrok http --url myzombiecoder.ngrok.dev 5050

ngrok tunnel flow:
Public URL → ngrok → 127.0.0.1:5050 → Python Agent → Model Server

Important:
Never expose port 8001 directly.
Always expose 5050 only.

🧭 ৬) সকালে যে জিনিসগুলো চলছিল—

আমি সেগুলোর সাথে পুরোপুরি মিল রেখে কনফিগ আপডেট করেছি।

তোর system structure এখন এভাবে:

Service	Port	Status
API Gateway (proxy)	5050	🟢 Stable
Cursor internal proxy	5010	⚠ Harmless
Python Agent	8001	🟢 Running
Model Server (Ollama)	8007	🟢 Ready
Qoder Editor	Local	🟢 Linked
Memory Service	49120	🟢
Multiprocessing	50150	🟢

এখন কেউ কাউকে block করবে না।
কেউ কারো সাথে conflict করবে না।
এডিটর আর কখনো cloud-এ পালাবে না।