import json
import requests
import os
import time

CONFIG = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'proxy_config.json')
api_key = None
try:
    with open(CONFIG, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
        api_key = cfg.get('api_key')
except Exception as e:
    print('ERROR reading config:', e)

if not api_key:
    print('No API key found in config; aborting')
    raise SystemExit(1)

headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
url = 'http://127.0.0.1:5010/v1/chat/completions'

# Non-stream test
print('---NON-STREAM TEST---')
try:
    payload = {"model": "tinyllama-gguf", "messages": [{"role": "user", "content": "hello from automated test"}], "stream": False}
    r = requests.post(url, headers=headers, json=payload, timeout=30)
    print('status_code:', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print('non-json response:', r.text)
except Exception as e:
    print('NON-STREAM ERROR:', e)

# Small pause
time.sleep(1)

# Streaming test
print('\n---STREAMING TEST---')
try:
    payload = {"model": "tinyllama-gguf", "messages": [{"role": "user", "content": "Stream a short line"}], "stream": True}
    r = requests.post(url, headers=headers, json=payload, stream=True, timeout=600)
    print('status_code:', r.status_code)
    if r.status_code == 200:
        for raw in r.iter_lines(decode_unicode=True):
            if not raw:
                continue
            print('LINE:', raw)
    else:
        print('Streaming request returned non-200:', r.text)
except Exception as e:
    print('STREAM ERROR:', e)

print('\n---TESTS COMPLETE---')
