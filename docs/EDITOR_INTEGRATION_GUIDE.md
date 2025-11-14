# Tree AI, Cursor AI, এবং Qoder Editor Integration Guide

**তারিখ:** ১৪ নভেম্বর, ২০২৫  
**সিস্টেম:** ZombieCoder Family Agent  
**Version:** 2.0.0

---

## 📋 Overview

এই সিস্টেমটি **Tree AI**, **Cursor AI**, এবং **Qoder** editor এর সাথে সম্পূর্ণ compatible। সব editor গুলো আপনার local ZombieCoder Agent ব্যবহার করতে পারবে।

### Supported Editors:
- ✅ **Cursor AI** - Full support (proxy + direct)
- ✅ **Qoder** - Full support (proxy + direct)
- ✅ **Tree AI** - Full support (proxy + direct)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Tree AI / Cursor AI / Qoder Editor                        │
│  (User Interface)                                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Proxy Server (Port 5010)                                   │
│  • Intercepts all API calls                                 │
│  • Validates API keys                                       │
│  • Routes to local agent                                    │
│  • Supports streaming (SSE)                                │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  ZombieCoder Agent (Port 8001)                             │
│  • /v1/chat/completions                                     │
│  • /v1/models                                              │
│  • Session management                                       │
│  • Memory systems (JSON + SQLite)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  Model Server (Port 8007/8080)                             │
│  • phi-2 model (default)                                   │
│  • Local LLM inference                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Start Agent Server
```powershell
# Terminal 1
.\venv\Scripts\python.exe unified_agent_system.py
```
✅ **Result:** Agent running on `http://127.0.0.1:8001`

### Step 2: Start Proxy Server
```powershell
# Terminal 2
.\venv\Scripts\python.exe proxy_cursor_enhanced.py
```
✅ **Result:** Proxy running on `http://127.0.0.1:5010`

### Step 3: Configure Your Editor
নিচে আপনার editor এর configuration দেখুন।

---

## 📝 Editor-Specific Configuration

### 1️⃣ Cursor AI Setup

#### Option A: Proxy ব্যবহার (Recommended)
```json
{
  "cursor.chat.customModel": {
    "title": "ZombieCoder Agent (Local)",
    "url": "http://127.0.0.1:5010/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "phi-2"
  }
}
```

#### Option B: Direct Connection
```json
{
  "cursor.chat.customModel": {
    "title": "ZombieCoder Agent (Direct)",
    "url": "http://127.0.0.1:8001/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "phi-2"
  }
}
```

#### Cursor Settings Location:
- **Windows:** `%APPDATA%\Cursor\User\settings.json`
- **macOS:** `~/Library/Application Support/Cursor/User/settings.json`
- **Linux:** `~/.config/Cursor/User/settings.json`

---

### 2️⃣ Qoder Editor Setup

#### Option A: Proxy ব্যবহার (Recommended)
Qoder settings এ যোগ করুন:
```json
{
  "qoder.ai.model": {
    "provider": "custom",
    "baseURL": "http://127.0.0.1:5010/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "phi-2"
  }
}
```

#### Option B: Direct Connection
```json
{
  "qoder.ai.model": {
    "provider": "custom",
    "baseURL": "http://127.0.0.1:8001/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "phi-2"
  }
}
```

#### Qoder Settings Location:
- **Windows:** `%APPDATA%\Qoder\User\settings.json`
- **macOS:** `~/Library/Application Support/Qoder/User/settings.json`
- **Linux:** `~/.config/Qoder/User/settings.json`

---

### 3️⃣ Tree AI Setup

#### Option A: Proxy ব্যবহার (Recommended)
Tree AI settings এ যোগ করুন:
```json
{
  "tree.ai.endpoint": "http://127.0.0.1:5010/v1",
  "tree.ai.apiKey": "DUMMY_API_KEY_FOR_LOCAL",
  "tree.ai.model": "phi-2"
}
```

#### Option B: Direct Connection
```json
{
  "tree.ai.endpoint": "http://127.0.0.1:8001/v1",
  "tree.ai.apiKey": "DUMMY_API_KEY_FOR_LOCAL",
  "tree.ai.model": "phi-2"
}
```

#### Tree AI Settings Location:
- **Windows:** `%APPDATA%\TreeAI\User\settings.json`
- **macOS:** `~/Library/Application Support/TreeAI/User/settings.json`
- **Linux:** `~/.config/TreeAI/User/settings.json`

---

## 🔧 Proxy Configuration

### Proxy Server Features:
- ✅ **Request Interception:** সব API calls intercept করে
- ✅ **API Key Validation:** Bearer token validation
- ✅ **Header Filtering:** Suspicious headers block করে
- ✅ **Streaming Support:** SSE (Server-Sent Events) format
- ✅ **Retry Logic:** 60 attempts with exponential backoff
- ✅ **Comprehensive Logging:** Rotating file logs
- ✅ **CORS Support:** Cross-origin requests support
- ✅ **Error Handling:** Fallback mechanisms

### Supported Hosts:
- `*.cursor.sh`, `*.cursor.com`, `*.cursorapi.com`
- `*.qoder.sh`, `*.qoder.com`
- `*.tree.ai` (Tree AI support added)
- `localhost`, `127.0.0.1` (local agent)

### Proxy Config File:
`config/proxy_config.json`:
```json
{
  "api_key": "DUMMY_API_KEY_FOR_LOCAL",
  "port": 5010,
  "bind_host": "127.0.0.1",
  "target_base": "http://127.0.0.1:8001",
  "log_file": "logs/proxy_adapter.log"
}
```

---

## 🧪 Testing Integration

### Test 1: Health Check
```powershell
# Agent Server
Invoke-WebRequest -Uri http://127.0.0.1:8001/health -UseBasicParsing

# Proxy Server
Invoke-WebRequest -Uri http://127.0.0.1:5010/health -UseBasicParsing
```

### Test 2: Chat Completions (via Proxy)
```powershell
$headers = @{
    'Authorization' = 'Bearer DUMMY_API_KEY_FOR_LOCAL'
    'Content-Type' = 'application/json'
    'X-Session-ID' = 'test-session-001'
}
$body = @{
    model = 'phi-2'
    messages = @(
        @{role='user'; content='হ্যালো, কেমন আছেন?'}
    )
    max_tokens = 100
} | ConvertTo-Json -Depth 10

$response = Invoke-WebRequest -Uri http://127.0.0.1:5010/v1/chat/completions -Method POST -Body $body -Headers $headers -UseBasicParsing
($response.Content | ConvertFrom-Json).choices[0].message.content
```

### Test 3: Direct Agent Connection
```powershell
$headers = @{
    'Authorization' = 'Bearer DUMMY_API_KEY_FOR_LOCAL'
    'Content-Type' = 'application/json'
    'X-Session-ID' = 'test-session-002'
}
$body = @{
    model = 'phi-2'
    messages = @(
        @{role='user'; content='হ্যালো'}
    )
    max_tokens = 50
} | ConvertTo-Json -Depth 10

$response = Invoke-WebRequest -Uri http://127.0.0.1:8001/v1/chat/completions -Method POST -Body $body -Headers $headers -UseBasicParsing
($response.Content | ConvertFrom-Json).choices[0].message.content
```

---

## 📊 API Endpoints

### Agent Server (Port 8001):
- `GET /health` - Health check
- `GET /` - Server info
- `POST /v1/chat/completions` - Chat completions
- `GET /v1/models` - Available models
- `GET /v1/agent/info` - Agent information
- `POST /api/ollama/completion` - Ollama completion

### Proxy Server (Port 5010):
- `GET /health` - Health check
- `POST /v1/chat/completions` - Chat completions (routed to agent)
- `GET /v1/models` - Available models (routed to agent)
- All other `/v1/*` endpoints routed to agent

---

## 🔍 Troubleshooting

### Issue 1: Editor cannot connect
**Solution:**
1. Check agent server running: `netstat -ano | findstr :8001`
2. Check proxy server running: `netstat -ano | findstr :5010`
3. Verify settings.json syntax (valid JSON)
4. Restart editor after configuration

### Issue 2: API key rejected
**Solution:**
- Use `DUMMY_API_KEY_FOR_LOCAL` as API key
- Check Authorization header format: `Bearer DUMMY_API_KEY_FOR_LOCAL`
- Verify proxy config has correct API key

### Issue 3: Model not found
**Solution:**
- Default model: `phi-2`
- Check model server running: `netstat -ano | findstr :8007`
- Verify model loaded in Ollama server

### Issue 4: Timeout errors
**Solution:**
- Model loading takes time (timeout: 120s)
- Check model server logs
- Verify model server has enough resources

### Issue 5: Bengali response not working
**Solution:**
- Prompt engineering ongoing
- Check agent logs for Bengali ratio warnings
- Response wrapper automatically adds Bengali context

---

## 📝 Configuration Examples

### Complete Cursor AI Settings:
```json
{
  "cursor.chat.customModel": {
    "title": "ZombieCoder Agent (Local)",
    "url": "http://127.0.0.1:5010/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "phi-2",
    "temperature": 0.7,
    "maxTokens": 220
  },
  "cursor.chat.defaultModel": "ZombieCoder Agent (Local)"
}
```

### Complete Qoder Settings:
```json
{
  "qoder.ai.model": {
    "provider": "custom",
    "baseURL": "http://127.0.0.1:5010/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "phi-2",
    "temperature": 0.7,
    "maxTokens": 220
  }
}
```

### Complete Tree AI Settings:
```json
{
  "tree.ai.endpoint": "http://127.0.0.1:5010/v1",
  "tree.ai.apiKey": "DUMMY_API_KEY_FOR_LOCAL",
  "tree.ai.model": "phi-2",
  "tree.ai.temperature": 0.7,
  "tree.ai.maxTokens": 220
}
```

---

## 🎯 Benefits

### Using Proxy (Port 5010):
- ✅ All requests intercepted and logged
- ✅ Centralized API key management
- ✅ Request/response monitoring
- ✅ Error handling and retry logic
- ✅ CORS support

### Using Direct Connection (Port 8001):
- ✅ Lower latency
- ✅ Simpler setup
- ✅ Direct agent access

---

## 📌 Important Notes

1. **API Key:** সব editor এর জন্য `DUMMY_API_KEY_FOR_LOCAL` ব্যবহার করুন
2. **Model Name:** Default model `phi-2` (configurable in `config/agent_config.json`)
3. **Ports:** 
   - Agent: 8001
   - Proxy: 5010
   - Model Server: 8007/8080
4. **Session Management:** `X-Session-ID` header ব্যবহার করুন conversation context maintain করার জন্য
5. **Language:** Agent default language বাংলা, কিন্তু English ও support করে

---

## 🔄 Updates & Maintenance

### Check Server Status:
```powershell
# All servers
netstat -ano | findstr ":8001 :5010 :8007 :8080"
```

### View Logs:
```powershell
# Agent logs
Get-Content logs\zombiecoder_agent.log -Tail 50

# Proxy logs
Get-Content logs\proxy_adapter.log -Tail 50
```

### Restart Servers:
```powershell
# Stop all Python processes
Get-Process python | Where-Object {$_.Path -like "*venv*"} | Stop-Process -Force

# Start agent
.\venv\Scripts\python.exe unified_agent_system.py

# Start proxy
.\venv\Scripts\python.exe proxy_cursor_enhanced.py
```

---

## ✅ Verification Checklist

- [ ] Agent server running on port 8001
- [ ] Proxy server running on port 5010
- [ ] Model server running on port 8007/8080
- [ ] Editor settings configured correctly
- [ ] API key set to `DUMMY_API_KEY_FOR_LOCAL`
- [ ] Model name set to `phi-2`
- [ ] Test chat working in editor
- [ ] Bengali responses working (if applicable)

---

**Documentation Created By:** Auto (Cursor AI Agent)  
**Date:** 2025-11-14  
**Version:** 2.0.0  
**Signature:** AI Assistant - Cursor AI Integration

---

*এই guide অনুসরণ করে আপনি Tree AI, Cursor AI, এবং Qoder editor সবগুলোর সাথে ZombieCoder Agent ব্যবহার করতে পারবেন।*

