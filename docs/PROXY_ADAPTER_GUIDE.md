# Proxy Adapter Configuration & Architecture

## Overview

The proxy adapter (`proxy_adapter.py`) intercepts all Cursor AI calls and routes them to your local ZombieCoder Agent.

```
┌─────────────────────────────────────────────────────────────┐
│ Cursor AI                                                   │
│   (Request to http://127.0.0.1:5010/v1/chat/completions)   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Proxy Adapter (Port 5010)                                   │
│   • Intercepts requests                                     │
│   • Validates API key                                       │
│   • Strips suspicious headers                               │
│   • Supports streaming (SSE)                                │
│   • Implements retry logic (60 attempts with backoff)       │
│   • Logs all requests                                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ ZombieCoder Agent (Port 8001)                               │
│   • /v1/chat/completions                                    │
│   • /chat (native endpoint)                                 │
│   • /status, /health, /memory                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│ Model Server (Port 8155)                                    │
│   • /api/generate                                           │
│   • Model: deepseek-coder-1.3b                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Configuration Files

### 1. config/proxy_config.json
```json
{
  "api_key": "DUMMY_API_KEY_FOR_LOCAL",
  "port": 5010,
  "bind_host": "127.0.0.1",
  "target_base": "http://127.0.0.1:8001",
  "log_file": "logs/proxy_adapter.log",
  "log_max_bytes": 5242880,
  "log_backup_count": 3
}
```

**Keys Explanation:**
- `api_key`: Authorization token (checked against Bearer token in Authorization header)
- `port` / `proxy_port`: Listen port (default 5010)
- `bind_host`: Bind address (default 127.0.0.1)
- `target_base`: Upstream ZombieCoder Agent URL
- `log_file`: Rotating log file location
- `log_max_bytes`: Max log file size before rotation (5MB default)
- `log_backup_count`: Number of backup logs to keep (3 default)

### 2. Environment Variables (Optional)
The proxy supports environment variable overrides:
```powershell
$env:PROXY_PORT = "5010"
$env:PROXY_BIND_HOST = "127.0.0.1"
$env:PROXY_TARGET_BASE = "http://127.0.0.1:8001"
$env:PROXY_API_KEY = "DUMMY_API_KEY_FOR_LOCAL"
```

Priority: Environment Variables > Config File > Defaults

---

## Features

### ✅ Request Forwarding
- ✓ Forwards GET, POST, HEAD requests
- ✓ Preserves request headers (strips suspicious ones)
- ✓ Handles binary and JSON payloads
- ✓ Supports streaming responses (SSE format)

### ✅ Security
- ✓ API key validation (Bearer token)
- ✓ Blocks suspicious headers:
  - `host`, `connection`, `keep-alive`
  - `proxy-authenticate`, `te`, `trailers`, `upgrade`
  - `x-cursor-client-*`, `x-hellozombie-*`
- ✓ Prevents self-targeting

### ✅ Streaming Support
- ✓ Detects `"stream": true` in request body
- ✓ Forwards as Server-Sent Events (SSE)
- ✓ Fallback to non-stream if upstream streaming fails
- ✓ Properly formats SSE lines: `data: <content>\n\n`

### ✅ Reliability
- ✓ Retry logic (60 attempts with exponential backoff)
- ✓ Connection error handling
- ✓ Timeout handling (60s default, 120s for fallback)
- ✓ CORS headers on all responses
- ✓ Rotating file logs

### ✅ CORS Support
All responses include CORS headers:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS, HEAD
Access-Control-Allow-Headers: Content-Type, Authorization, X-Session-Id, ...
```

---

## Usage

### Start Proxy (PowerShell)
```powershell
# First terminal - Start Agent
./full_auto_install.ps1

# Second terminal - Start Proxy
.\scripts\start_proxy.ps1

# Optional: Force restart
.\scripts\start_proxy.ps1 -Force
```

### Start Proxy (Python)
```bash
python scripts/start_proxy.py
```

### Test Proxy
```bash
python scripts/test_proxy.py
```

---

## Request Flow Examples

### Example 1: Chat Completion
**Cursor AI sends:**
```http
POST http://127.0.0.1:5010/v1/chat/completions
Authorization: Bearer DUMMY_API_KEY_FOR_LOCAL
Content-Type: application/json

{
  "model": "deepseek-coder-1.3b",
  "messages": [{"role": "user", "content": "Hello"}],
  "stream": false
}
```

**Proxy:**
1. Validates API key ✓
2. Strips suspicious headers ✓
3. Forwards to http://127.0.0.1:8001/v1/chat/completions
4. Returns response as-is

**Cursor AI receives:**
```json
{
  "model": "deepseek-coder-1.3b",
  "choices": [...],
  "usage": {...}
}
```

### Example 2: Streaming Request
**Cursor AI sends:**
```http
POST http://127.0.0.1:5010/v1/chat/completions
Authorization: Bearer DUMMY_API_KEY_FOR_LOCAL
Content-Type: application/json

{
  "model": "deepseek-coder-1.3b",
  "messages": [{"role": "user", "content": "Stream me a response"}],
  "stream": true
}
```

**Proxy:**
1. Detects `"stream": true` in body
2. Makes upstream request with `stream=True`
3. Returns response as `text/event-stream` (SSE)
4. Forwards each line as `data: <line>\n\n`

**Cursor AI receives:**
```
data: Hello, this is
data:  a streaming
data:  response from
data:  the model
data: [DONE]
```

---

## Logging

### Log Format
```
2025-11-11 15:30:45,123 INFO 127.0.0.1 GET /health -> 200
2025-11-11 15:30:46,456 INFO 127.0.0.1 POST /v1/chat/completions -> 200
2025-11-11 15:30:47,789 WARNING Upstream connection failed (attempt 1/60) to http://127.0.0.1:8001/v1/chat/completions: Connection refused
```

### Log File Location
```
logs/proxy_adapter.log
```

### Viewing Logs
```powershell
# Real-time tail
Get-Content logs/proxy_adapter.log -Wait

# Last 20 lines
Get-Content logs/proxy_adapter.log -Tail 20

# Search for errors
Select-String "ERROR|WARNING" logs/proxy_adapter.log
```

---

## Troubleshooting

### Issue: "Connection refused"
**Check if proxy is running:**
```powershell
netstat -ano | findstr ":5010"
```

**Solution:**
```powershell
.\scripts\start_proxy.ps1
```

### Issue: "Unauthorized"
**Check API key:**
- Cursor AI headers must include: `Authorization: Bearer DUMMY_API_KEY_FOR_LOCAL`
- Or environment variable `PROXY_API_KEY` must be set

### Issue: Upstream connection fails
**Check if Agent is running:**
```powershell
netstat -ano | findstr ":8001"
curl http://127.0.0.1:8001/health
```

### Issue: Logs show header blocking
**This is normal** - proxy strips suspicious headers for security:
```
[BLOCK] Stripping suspicious header: x-cursor-client-version
```

This is intentional and doesn't affect functionality.

### Issue: Streaming stops mid-response
**Check logs** for upstream timeout:
```
Upstream streaming read failure: ReadTimeout
```

Proxy will attempt non-stream fallback automatically.

---

## Performance Tuning

### Increase Retry Attempts
Edit `proxy_adapter.py` line ~180:
```python
max_attempts = 120  # Default is 60
```

### Increase Timeout
Edit `proxy_adapter.py` line ~195:
```python
timeout=120  # Default is 60 seconds
```

### Rotate Logs More Frequently
Edit `config/proxy_config.json`:
```json
{
  "log_max_bytes": 1048576,  // 1MB instead of 5MB
  "log_backup_count": 10     // Keep more backups
}
```

---

## Integration with Cursor AI

### Step 1: Configure Cursor Settings
```json
{
  "cursor.chat.customModel": {
    "title": "ZombieCoder Agent (Proxy)",
    "url": "http://127.0.0.1:5010/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "deepseek-coder-1.3b"
  }
}
```

### Step 2: Start Proxy
```powershell
.\scripts\start_proxy.ps1
```

### Step 3: Use in Cursor
- Open Cursor
- `Ctrl+L` (Chat)
- Start chatting!

---

## Monitoring

### Health Check Endpoint
```bash
curl http://127.0.0.1:5010/health
```

Expected response:
```json
{
  "status": "running",
  "target": "http://127.0.0.1:8001",
  "uptime": 3600,
  "requests_handled": 125
}
```

### Check Log File
```bash
# Last 50 lines
tail -50 logs/proxy_adapter.log

# Watch real-time
tail -f logs/proxy_adapter.log
```

---

## Advanced Configuration

### Custom Target Base
Edit `config/proxy_config.json`:
```json
{
  "target_base": "http://192.168.1.100:8001"  // Different machine
}
```

### Disable API Key
Edit `config/proxy_config.json`:
```json
{
  "api_key": null  // or remove the line entirely
}
```

### Different Log Path
Edit `config/proxy_config.json`:
```json
{
  "log_file": "C:/custom/path/proxy.log"
}
```

---

## FAQ

**Q: Why do I need a proxy? Can't Cursor AI just call the agent?**
A: The proxy intercepts calls to provide:
- Centralized logging
- Security (API key validation, header filtering)
- Streaming support with fallback
- Retry logic for reliability
- Header manipulation

**Q: Can I run multiple proxies?**
A: Yes, use different ports in config files.

**Q: Does the proxy modify responses?**
A: No, responses are forwarded as-is (except for streaming format).

**Q: What if the agent goes down?**
A: Proxy will retry 60 times with exponential backoff (30 seconds max wait).

**Q: Can I use this with a remote agent?**
A: Yes, change `target_base` in `config/proxy_config.json`.

---

## Security Notes

⚠️ **WARNING**: This proxy is designed for **LOCAL DEVELOPMENT ONLY**.

- API key is hardcoded (`DUMMY_API_KEY_FOR_LOCAL`)
- No SSL/TLS encryption
- No rate limiting
- No DDoS protection
- All traffic is unencrypted

**Do NOT expose this on the public internet.**

For production use:
1. Generate secure API keys
2. Use HTTPS/SSL
3. Implement rate limiting
4. Deploy behind a proper API gateway
5. Use network isolation/firewall

---

## Support

For issues:
1. Check `logs/proxy_adapter.log`
2. Verify config in `config/proxy_config.json`
3. Test connectivity: `curl http://127.0.0.1:5010/health`
4. Check if upstream is running: `curl http://127.0.0.1:8001/health`
