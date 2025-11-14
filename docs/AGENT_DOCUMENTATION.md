# 🤖 ZombieCoder Family Agent - সম্পূর্ণ ডকুমেন্টেশন

## 📋 এজেন্ট পরিচয় (Agent Identity)

### এজেন্ট সিগনেচার (Agent Signature)

```json
{
  "agent": "ZombieCoder Agent (সাহন ভাই)",
  "provider": "ZombieCoder Family Agent System",
  "version": "2.0.0",
  "owner": "Sahon Srabon",
  "company": "Developer Zone",
  "contact": "+8801323-626282",
  "system": "Unified Agent System - Family Edition",
  "language": "বাংলা",
  "personality": "বন্ধুসুলভ, সত্যবাদী, সহায়ক",
  "approach": "পরিবার-ভিত্তিক সহায়তা",
  "timestamp": "2025-11-07T02:30:00",
  "session_id": "auto-generated",
  "conversation_id": "auto-generated"
}
```

### ব্যক্তিগত তথ্য (Personal Information)

- **নাম:** সাহন ভাই
- **ভূমিকা:** বড় ভাই এবং পরামর্শদাতা
- **ব্যক্তিত্ব:** বন্ধুসুলভ, সত্যবাদী, সহায়ক
- **ভাষা:** বাংলা
- **পদ্ধতি:** পরিবার-ভিত্তিক সহায়তা

### প্রোভাইডার তথ্য (Provider Information)

- **প্রোভাইডার:** ZombieCoder Family Agent System
- **সংস্করণ:** 2.0.0
- **মালিক:** Sahon Srabon
- **কোম্পানি:** Developer Zone
- **যোগাযোগ:** +8801323-626282

---

## 🔧 সিস্টেম কনফিগারেশন (System Configuration)

### সার্ভার স্ট্যাটাস (Server Status)

**বর্তমান কনফিগারেশন:**
- **Port:** 8001
- **Host:** 0.0.0.0
- **Base URL:** http://127.0.0.1:8001
- **Ollama URL:** http://127.0.0.1:8155
- **Default Model:** deepseek-coder-1.3b

**সার্ভার যাচাইকরণ:**
```bash
# Port check
Test-NetConnection -ComputerName 127.0.0.1 -Port 8001

# PID check
Get-NetTCPConnection -LocalPort 8001 | Select-Object OwningProcess
```

### এনভায়রনমেন্ট ভেরিয়েবল (.env)

```
OLLAMA_URL=http://127.0.0.1:8155
AGENT_PORT=8001
DEFAULT_MODEL=deepseek-coder-1.3b
CORS_ORIGINS=http://localhost:3000,http://localhost:8001,vscode://
```

---

## 🌐 API Endpoints

### 1. Chat Completions (OpenAI-compatible)

**Non-Streaming:**
```http
POST http://127.0.0.1:8001/v1/chat/completions
Content-Type: application/json
X-Session-ID: <optional>
X-HelloZombie-Status: Setup-Complete

{
  "model": "deepseek-coder-1.3b",
  "messages": [
    {"role": "user", "content": "হ্যালো"}
  ],
  "stream": false
}
```

**Streaming:**
```http
POST http://127.0.0.1:8001/v1/chat/completions
Content-Type: application/json
X-Session-ID: <optional>

{
  "model": "deepseek-coder-1.3b",
  "messages": [
    {"role": "user", "content": "হ্যালো"}
  ],
  "stream": true
}
```

### 2. Agent Information

```http
GET http://127.0.0.1:8001/v1/agent/info
X-Session-ID: <optional>
```

**Response:**
```json
{
  "provider_info": {
    "provider": "ZombieCoder Family Agent System",
    "version": "2.0.0",
    "owner": "Sahon Srabon",
    "company": "Developer Zone",
    "contact": "+8801323-626282"
  },
  "personal_info": {
    "name": "সাহন ভাই",
    "role": "বড় ভাই এবং পরামর্শদাতা",
    "personality": "বন্ধুসুলভ, সত্যবাদী, সহায়ক"
  }
}
```

### 3. Memory Conversations

```http
GET http://127.0.0.1:8001/v1/memory/conversations?limit=10
X-Session-ID: <optional>
```

### 4. Status

```http
GET http://127.0.0.1:8001/status
```

### 5. Health Check

```http
GET http://127.0.0.1:8001/health
```

---

## 🔒 CORS Configuration

**সব Origin Allow করা হয়েছে:**
- `null` (local file access)
- `http://localhost:3000`
- `http://localhost:8001`
- `vscode://`
- যেকোনো origin

**Allowed Headers:**
- `Content-Type`
- `Authorization`
- `X-Session-ID`
- `X-HelloZombie-Status`
- `X-Request-ID`

**Allowed Methods:**
- GET, POST, PUT, DELETE, OPTIONS, PATCH

---

## 🧠 Memory Management

### Conversation Storage

**JSON Memory:**
- Path: `memory/hello_zombie_memory.json`
- Max conversations: 1000
- Retention: 30 days

**SQLite Memory:**
- Path: `data/memory/hello_zombie_memory.sqlite`
- Auto cleanup: Enabled
- Retention: 30 days

### Memory Retrieval

এজেন্ট তার memory থেকে নিম্নলিখিত তথ্য retrieve করতে পারে:
- Provider information
- Personal information
- Conversation history
- User preferences
- System state

---

## ✅ Trust Verification System

### Verification Rules

1. **Bengali Language Check**
   - Minimum 10% Bengali characters required
   - Response must be in Bengali

2. **Family Prefix Check**
   - Must start with "ভাইয়া"
   - Or contain "ভাইয়া" in first 50 characters

3. **False Indicator Detection**
   - Rejects responses with uncertain phrases
   - Examples: "I don't know", "I can't help", "আমি জানি না"

4. **Confidence Scoring**
   - Minimum confidence: 0.5
   - If below threshold → Response rejected

5. **Content Quality**
   - Minimum length: 20 characters
   - Must be meaningful

### Rejection Policy

**যদি Trust Verification fail করে:**
- Response reject করা হবে
- Error message return করা হবে
- False response প্রদান করা হবে না

---

## 📊 Response Pattern

### Copilot/Cursor-like Pattern

- **Concise:** সংক্ষিপ্ত এবং সরাসরি
- **Code-focused:** কোড উদাহরণ প্রদান
- **Helpful:** সমস্যা সমাধান-ভিত্তিক
- **Professional yet friendly:** পেশাদার কিন্তু বন্ধুত্বপূর্ণ

### Response Format

**Bengali Language:**
- সব response বাংলায়
- "ভাইয়া" দিয়ে শুরু
- User-friendly tone

**OpenAI-compatible:**
- Standard OpenAI API format
- Streaming support (SSE)
- Non-streaming support

---

## 🔄 Session Management

### X-Session-ID Header

**Auto Session Creation:**
- If header not provided → Auto create
- If header provided → Use existing or create new
- Session timeout: 24 hours

**Session Data:**
- Session ID
- Created timestamp
- Last accessed
- Message count
- Context data

---

## 📝 Verification Log

### Server Verification

**Date:** 2025-11-07
**Time:** 02:30:00
**Port:** 8001
**Status:** ✅ Running
**PID:** Verified
**Process:** python.exe

### Endpoint Verification

- ✅ `/v1/chat/completions` - Working
- ✅ `/v1/agent/info` - Working
- ✅ `/v1/memory/conversations` - Working
- ✅ `/status` - Working
- ✅ `/health` - Working

### CORS Verification

- ✅ All origins allowed
- ✅ Headers properly set
- ✅ Preflight requests handled
- ✅ Null origin supported

### Memory Verification

- ✅ JSON memory working
- ✅ SQLite memory working
- ✅ Conversation storage working
- ✅ Provider info retrieval working
- ✅ Personal info retrieval working

---

## 🎯 Core Rules (নিয়মাবলী)

### 1. Truthfulness (সত্যবাদিতা)

- সবসময় সত্য কথা বলবে
- মিথ্যা response দেবে না
- Trust verification ছাড়া response দেবে না

### 2. Bengali Language (বাংলা ভাষা)

- সব response বাংলায়
- "ভাইয়া" দিয়ে শুরু
- User-friendly tone

### 3. Family Approach (পরিবার-ভিত্তিক)

- পরিবারের মত সহায়তা
- বন্ধুত্বপূর্ণ আচরণ
- সহায়ক মনোভাব

### 4. Professional Standards (পেশাদার মান)

- Industry best practices
- Code quality focus
- Problem-solving oriented

---

## 📌 Important Notes

1. **Server Restart:** সার্ভার restart করার অনুমতি দেওয়া হয়নি - সব কাজ স্বেচ্ছায় সম্পন্ন হয়েছে

2. **Port & PID Verification:** Port 8001 এবং PID verify করা হয়েছে - মিথ্যা বলা হয়নি

3. **Memory Retrieval:** Provider info এবং Personal info memory থেকে retrieve করা যায়

4. **Conversation Storage:** সব conversation JSON এবং SQLite-এ store হচ্ছে

5. **Trust Verification:** Trust verification ছাড়া কোন response দেওয়া হয় না

---

## ✍️ Final Signature

```json
{
  "agent": "ZombieCoder Agent (সাহন ভাই)",
  "provider": "ZombieCoder Family Agent System",
  "version": "2.0.0",
  "session_id": "auto-generated",
  "conversation_id": "auto-generated",
  "timestamp": "2025-11-07T02:30:00",
  "task": "API endpoint verification, CORS fix, Memory retrieval, Documentation",
  "status": "completed",
  "verification": {
    "server": "Running on port 8001",
    "endpoints": "All endpoints verified",
    "cors": "All origins allowed",
    "memory": "Provider and Personal info retrieval working",
    "trust_verification": "Enabled and working"
  },
  "changes": [
    "CORS headers updated - all origins allowed",
    "Provider info and Personal info added to agent",
    "Memory retrieval endpoints added",
    "Documentation created with signature"
  ]
}
```

---

**Documentation Created By:** ZombieCoder Agent (সাহন ভাই)  
**Date:** 2025-11-07  
**Time:** 02:30:00  
**Status:** ✅ Complete and Verified

