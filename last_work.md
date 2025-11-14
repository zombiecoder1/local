# ZombieCoder Family Agent - আজকের কাজের ডকুমেন্টেশন

**তারিখ:** ১৪ নভেম্বর, ২০২৫ (2025-11-14)  
**সময়:** ১০:২৪ AM (Bangladesh Time)  
**এজেন্ট:** Auto (Cursor AI Agent)  
**Signature:** AI Assistant - Cursor AI Integration

---

## 📋 কাজের সারসংক্ষেপ

আজকের সেশনে আমরা ZombieCoder Family Agent System এর জন্য নিম্নলিখিত কাজগুলো সম্পন্ন করেছি:

### ১. Model Configuration & Default Settings
- **Default Model:** `phi-2` (microsoft/phi-2) হিসেবে set করা হয়েছে
- **Model Server:** Port auto-detection implement করা হয়েছে (8007, 8155, 11434)
- **Runtime Port Detection:** Model-specific port (8080) auto-detect করার logic যোগ করা হয়েছে

### ২. Agent Identity & Memory Management
- **Agent Identity Memory:** Agent identity এখন `agent_memory["agent_identity"]` তে persist হচ্ছে
- **Session Metadata:** Conversation context এ `agent_meta` save হচ্ছে (model, temperature, max_tokens সহ)
- **Memory Systems:** JSON + SQLite dual-layer memory system working

### ৩. Bengali Language Support
- **Strict Bengali Prompt:** 6টি কঠোর নিয়ম সহ prompt template তৈরি করা হয়েছে
- **100% Bengali Response:** "CRITICAL: 100% বাংলায় উত্তর" instruction যোগ করা হয়েছে
- **Bengali Response Wrapper:** English response কে automatically Bengali context এ wrap করার logic
- **Bengali Ratio Check:** Response এ minimum 30% Bengali character requirement

### ৪. Trust Verification & Security
- **Identity Indicators:** File path (`C:\\model`) rejection remove করা হয়েছে
- **Trust Verification:** Agent name ("ZombieCoder", "সাহন ভাই") allow করা হয়েছে
- **Response Filtering:** Technical details, company names, contact numbers filter করা হচ্ছে

### ৫. Performance & Reliability
- **Timeout Increase:** Model server timeout 60s থেকে 120s করা হয়েছে
- **Error Handling:** Specific exception handling (Timeout, ConnectionError) improve করা হয়েছে
- **Response Parsing:** Multiple response schema support (runtime_response, response, content)

### ৬. Git Repository & Version Control
- **Repository Initialization:** Git repository initialize করা হয়েছে
- **Initial Commit:** 131 files, 39504 insertions commit করা হয়েছে
- **Subsequent Commits:** 3টি commit করা হয়েছে (model config, Bengali support, fixes)

---

## 🔧 Technical Changes

### Files Modified:
1. **`unified_agent_system.py`**
   - Default model: `phi-2`
   - Port auto-detection logic
   - Bengali prompt template (strict rules)
   - Agent identity memory storage
   - Session metadata persistence
   - Trust verification updates
   - Timeout increase (120s)
   - Bengali response wrapper

2. **`config/agent_config.json`**
   - Default model: `phi-2`
   - Port configuration

### Key Functions Updated:
- `call_model_server()`: Port auto-detect, Bengali prompt, timeout increase
- `process_message()`: Agent identity memory save
- `verify_truth()`: Identity indicators update
- `save_agent_memory()`: Agent identity persistence

---

## 📊 বর্তমান অবস্থা (Current Status)

### Server Status:
- ✅ **Agent Server:** Running on port 8001 (PID: 12012)
- ✅ **Model Server:** Running on port 8007 (PID: 5804)
- ✅ **Model Runtime:** phi-2 running on port 8080 (multiple instances)

### System Health:
- ✅ **Memory Systems:** JSON + SQLite initialized
- ✅ **LangChain Integration:** Active (microsoft/phi-2)
- ✅ **Ollama Detection:** Auto-detected at http://127.0.0.1:8007
- ✅ **CORS:** Configured for localhost:3000, localhost:8001, vscode://

### Features Working:
- ✅ **Chat Completions API:** `/v1/chat/completions` endpoint active
- ✅ **Session Management:** X-Session-ID header support
- ✅ **Agent Identity Memory:** Persisting correctly
- ✅ **Session Metadata:** Saving in conversation context
- ✅ **Bengali Prompt:** Strict instructions active
- ✅ **Trust Verification:** Working (with updated rules)

### Known Issues:
- ⚠️ **Bengali Response Quality:** Model sometimes responds in English (prompt engineering ongoing)
- ⚠️ **Model Loading Time:** phi-2 model loading takes time (timeout increased to 120s)
- ⚠️ **Response Ratio:** Bengali character ratio sometimes low (wrapper logic added)

---

## 🔄 Git Commits

### Commit History:

#### Commit 1: Initial Setup
```
Commit ID: 681703d
Message: Update: phi-2 default model, port auto-detect (8007), agent identity memory storage, session metadata, response quality improvements, Bengali prompt instructions
Files: 131 files changed, 39504 insertions(+)
Date: 2025-11-14
```

#### Commit 2: Bengali Prompt Improvements
```
Commit ID: ba7838e
Message: Fix: Remove C:\\model from identity indicators, improve Bengali prompt strictness, increase timeout to 120s, add Bengali response wrapper for English responses
Files: 1 file changed, 8 insertions(+), 5 deletions(-)
Date: 2025-11-14
```

#### Commit 3: Final Fixes
```
Commit ID: efb86e3 (HEAD -> master)
Message: Fix: Remove C:\\model from identity indicators, increase all timeouts to 120s, improve Bengali response wrapper
Files: 1 file changed, 11 insertions(+), 6 deletions(-)
Date: 2025-11-14 10:24:52 +0600
Author: Shawon <shawon@example.com>
```

### Latest Commit Details:
- **Commit Hash:** `efb86e3ae2b0092e575ac3982d9fa8cb30e78c5f`
- **Branch:** `master`
- **Status:** HEAD (latest)

---

## 📦 Dependencies

### Core Dependencies:
```
flask==2.3.3
requests>=2.31.0,<3.0.0
pyyaml==6.0.1
python-dotenv==1.0.0
```

### LangChain & NLP:
```
banglanltk==0.0.4
langchain>=0.3.10,<0.4.0
langchain-core>=0.3.63,<0.4.0
langchain-community>=0.3.10,<0.4.0
langchain-huggingface>=0.1.2,<0.2.0
transformers>=4.57.1,<5.0.0
sentencepiece==0.2.1
sentence-transformers>=5.1.2,<6.0.0
torch==2.9.0
scikit-learn>=1.7.2,<2.0.0
scipy>=1.16.3,<2.0.0
numpy>=1.26.4,<3.0.0
```

### System Monitoring:
```
psutil>=5.9.8,<6.0.0
```

---

## 🚀 Fresh Installation Guide

### Step 1: Extract ZIP File
```powershell
# যে কোন ড্রাইভে extract করুন (যেমন: D:\ZombieCoder)
Expand-Archive -Path ZombieCoder-Family-Agent-2025-11-14.zip -DestinationPath D:\ZombieCoder
cd D:\ZombieCoder
```

### Step 2: Python Virtual Environment
```powershell
# Python 3.12+ প্রয়োজন
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies
```powershell
# Core dependencies
pip install flask==2.3.3 requests pyyaml python-dotenv --no-cache-dir

# LangChain dependencies
pip install langchain langchain-core langchain-community langchain-huggingface --no-cache-dir

# NLP dependencies
pip install transformers sentencepiece sentence-transformers banglanltk --no-cache-dir

# ML dependencies
pip install torch scikit-learn scipy numpy --no-cache-dir

# System monitoring
pip install psutil --no-cache-dir

# অথবা একসাথে
pip install -r requirements.txt --no-cache-dir
```

### Step 4: Model Server Setup
```powershell
# Ollama server চালু থাকতে হবে
# Port 8007 এ model server running থাকতে হবে
# phi-2 model loaded থাকতে হবে
```

### Step 5: Start Agent Server
```powershell
.\venv\Scripts\python.exe unified_agent_system.py
```

### Step 6: Verify Installation
```powershell
# Health check
Invoke-WebRequest -Uri http://127.0.0.1:8001/health -UseBasicParsing

# Test chat
$headers = @{'X-Session-ID'='test-session'}; $body = @{model='phi-2';messages=@(@{role='user';content='হ্যালো'});max_tokens=50} | ConvertTo-Json -Depth 10; Invoke-WebRequest -Uri http://127.0.0.1:8001/v1/chat/completions -Method POST -Body $body -ContentType 'application/json' -Headers $headers -UseBasicParsing
```

---

## 📝 Configuration Files

### Agent Configuration (`config/agent_config.json`):
- **Agent Port:** 8001
- **Default Model:** phi-2
- **Max Tokens:** 220
- **Temperature:** 0.7
- **CORS Origins:** localhost:3000, localhost:8001, vscode://

### Model Server:
- **Primary Port:** 8007
- **Fallback Ports:** 8155, 11434
- **Runtime Port:** 8080 (auto-detected for phi-2)

---

## 🎯 API Endpoints

### Chat Completions:
```
POST http://127.0.0.1:8001/v1/chat/completions
Headers: X-Session-ID: <session-id>
Body: {
  "model": "phi-2",
  "messages": [{"role": "user", "content": "হ্যালো"}],
  "max_tokens": 220
}
```

### Health Check:
```
GET http://127.0.0.1:8001/health
```

### Agent Info:
```
GET http://127.0.0.1:8001/v1/agent/info
```

### Ollama Completion:
```
POST http://127.0.0.1:8001/api/ollama/completion
```

---

## 🔍 Testing & Verification

### Test Commands:
```powershell
# 1. Server Status
netstat -ano | findstr ":8001 :8007 :8080"

# 2. Health Check
Invoke-WebRequest -Uri http://127.0.0.1:8001/health -UseBasicParsing

# 3. Chat Test
$headers = @{'X-Session-ID'='test-001'}; $body = @{model='phi-2';messages=@(@{role='user';content='হ্যালো, কেমন আছেন?'});max_tokens=80} | ConvertTo-Json -Depth 10; $response = Invoke-WebRequest -Uri http://127.0.0.1:8001/v1/chat/completions -Method POST -Body $body -ContentType 'application/json' -Headers $headers -UseBasicParsing; ($response.Content | ConvertFrom-Json).choices[0].message.content

# 4. Memory Verification
python -c "import json; f=open('memory/hello_zombie_memory.json','r',encoding='utf-8'); d=json.load(f); f.close(); print('Agent Memory:', 'agent_identity' in d.get('agent_memory',{}))"
```

---

## 📌 Important Notes

1. **Model Server:** Ollama server (port 8007) চালু থাকতে হবে
2. **Model Loading:** phi-2 model প্রথমবার load হতে সময় লাগতে পারে
3. **Bengali Response:** Model এখনো perfect Bengali response দিতে পারে না, prompt engineering ongoing
4. **Port Conflicts:** Port 8001, 8007, 8080 available থাকতে হবে
5. **Memory:** `memory/` directory automatically create হবে
6. **Logs:** `logs/` directory এ log files save হবে

---

## 🐛 Troubleshooting

### Issue: Model server timeout
- **Solution:** Timeout already increased to 120s, check model server status

### Issue: Bengali response not working
- **Solution:** Prompt strictness improved, Bengali wrapper added, ongoing optimization

### Issue: Port conflicts
- **Solution:** Check ports 8001, 8007, 8080 availability, kill conflicting processes

### Issue: Dependencies missing
- **Solution:** Run `pip install -r requirements.txt --no-cache-dir`

### Issue: Memory errors
- **Solution:** Check `memory/` directory permissions, ensure disk space available

---

## 📞 Support & Contact

- **Agent Name:** ZombieCoder Agent (সাহন ভাই)
- **Version:** 2.0.0
- **Provider:** ZombieCoder Family Agent System
- **Language:** Bengali (বাংলা)
- **Owner:** Sahon Srabon

---

## ✅ Completion Checklist

- [x] Default model phi-2 set করা হয়েছে
- [x] Port auto-detection implement করা হয়েছে
- [x] Agent identity memory storage working
- [x] Session metadata persistence working
- [x] Bengali prompt strictness improved
- [x] Trust verification updated
- [x] Timeout increased to 120s
- [x] Bengali response wrapper added
- [x] Git repository initialized
- [x] All changes committed
- [x] Documentation created
- [x] ZIP file ready for distribution

---

**Documentation Created By:** Auto (Cursor AI Agent)  
**Date:** 2025-11-14  
**Time:** 10:24 AM (Bangladesh Time)  
**Signature:** AI Assistant - Cursor AI Integration  
**Commit ID:** efb86e3ae2b0092e575ac3982d9fa8cb30e78c5f

---

*এই ডকুমেন্টেশনটি সম্পূর্ণ এবং fresh installation এর জন্য ready। যে কোন ড্রাইভে extract করে dependencies install করে run করা যাবে।*

