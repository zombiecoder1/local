import json
import requests
import time

payload = {
    "model": "deepseek-ai/deepseek-coder-1.3b-base",
    "stream": True,
    "max_tokens": 64,
    "messages": [
        {"role": "user", "content": "ভাইয়া, এই স্ট্রিমিং রেসপন্স পরীক্ষা করছি।"}
    ]
}

start = time.perf_counter()
try:
    resp = requests.post("http://127.0.0.1:8001/v1/chat/completions", json=payload, stream=True, timeout=60)
    print("status:", resp.status_code)
    if resp.status_code != 200:
        print(resp.text)
    else:
        chunks = []
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            chunks.append(line)
            if len(chunks) >= 5:
                break
        latency = time.perf_counter() - start
        print("initial_chunks:")
        for chunk in chunks:
            print(chunk)
        print("latency_ms:", round(latency * 1000, 2))
except Exception as e:
    print("Error:", e)
