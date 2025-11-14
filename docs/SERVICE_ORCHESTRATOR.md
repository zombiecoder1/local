# 🎭 Service Orchestrator Guide

## সব সার্ভার একসাথে চালান

### কী করে এই স্ক্রিপ্ট?

`start_all_services.ps1` স্ক্রিপ্ট:

1. **তিনটি সার্ভার শুরু করে:**
   - Model Server (port 8155)
   - Agent Server (port 8001)
   - Proxy Adapter (port 5010)

2. **রিয়েল-টাইম মনিটরিং:**
   - আসা সব requests দেখায়
   - GET/POST দেখায়
   - Status code দেখায় (200, 500, etc)

3. **রিসোর্স মনিটরিং:**
   - RAM/Memory ট্র্যাক করে
   - প্রতি সেবার জন্য আলাদা
   - প্রতি ১০ সেকেন্ডে আপডেট হয়

4. **লগিং:**
   - সব requests এবং responses লগ করে
   - ফাইলে সেভ করে (`logs/` ফোল্ডারে)

---

## 🚀 ব্যবহার করুন

### সবচেয়ে সহজ উপায়:

```powershell
.\scripts\start_all_services.ps1
```

এটুকু! তিনটি সার্ভারই শুরু হবে এবং মনিটরিং দেখা যাবে।

### বিকল্প:

```powershell
# টেস্টিং ছাড়াই শুরু করুন
.\scripts\start_all_services.ps1 -NoTest

# Verbose মোড (বিস্তারিত আউটপুট)
.\scripts\start_all_services.ps1 -Verbose
```

---

## 📊 মনিটরিং আউটপুট বোঝা

### উদাহরণ আউটপুট:

```
🟵 [MODEL] (POST) 127.0.0.1 POST /api/generate -> 200
🟢 [AGENT] (POST) 127.0.0.1 POST /chat -> 200
🟡 [PROXY] (POST) 127.0.0.1 POST /v1/chat/completions -> 200

📈 Resource Usage:
   Model Server (PID 12345): 256.50 MB
   Agent Server (PID 12346): 189.75 MB
   Proxy Adapter (PID 12347): 45.25 MB
```

### রঙের অর্থ:

- **🔵 BLUE [MODEL]** - Model Server এ অনুরোধ
- **🟢 GREEN [AGENT]** - Agent Server এ অনুরোধ
- **🟡 YELLOW [PROXY]** - Proxy Adapter এ অনুরোধ

### Method এবং Status:

- **(GET)** - GET request পাঠানো হয়েছে
- **(POST)** - POST request পাঠানো হয়েছে
- **-> 200** - সফল রেসপন্স
- **-> 500** - সার্ভার এরর
- **-> 401** - Unauthorized

---

## 🧪 লাইভ টেস্টিং করার সময়

যখন স্ক্রিপ্ট চলছে, অন্য টার্মিনালে:

### Model Server টেস্ট করুন:

```powershell
curl -X POST http://127.0.0.1:8155/api/generate `
  -H "Content-Type: application/json" `
  -d '{
    "model": "deepseek-coder-1.3b",
    "prompt": "Hello",
    "stream": false
  }'
```

লাইভ মনিটরিং এ দেখবেন:
```
🔵 [MODEL] (POST) 127.0.0.1 POST /api/generate -> 200
```

### Agent Server টেস্ট করুন:

```powershell
curl -X POST http://127.0.0.1:8001/chat `
  -H "Content-Type: application/json" `
  -d '{"message": "test"}'
```

লাইভ মনিটরিং এ দেখবেন:
```
🟢 [AGENT] (POST) 127.0.0.1 POST /chat -> 200
```

### Proxy Server টেস্ট করুন:

```powershell
curl -X POST http://127.0.0.1:5010/v1/chat/completions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer DUMMY_API_KEY_FOR_LOCAL" `
  -d '{
    "model": "deepseek-coder-1.3b",
    "messages": [{"role": "user", "content": "test"}],
    "stream": false
  }'
```

লাইভ মনিটরিং এ দেখবেন:
```
🟡 [PROXY] (POST) 127.0.0.1 POST /v1/chat/completions -> 200
```

---

## 📈 রিসোর্স মনিটরিং

প্রতি ১০ সেকেন্ডে স্ক্রিপ্ট দেখায়:

```
📈 Resource Usage:
   Model Server (PID 12345): 256.50 MB
   Agent Server (PID 12346): 189.75 MB
   Proxy Adapter (PID 12347): 45.25 MB
```

### কী দেখতে চান:

- **Model Server**: ৫০০ MB পর্যন্ত (স্বাভাবিক)
- **Agent Server**: ২০০-৩০০ MB (স্বাভাবিক)
- **Proxy Adapter**: ৫০ MB এর কম (প্রায়ই)

যদি একটি হঠাৎ বেড়ে যায়, সেটা মেমরি লিক হতে পারে।

---

## 🔍 লগ ফাইলগুলি

স্ক্রিপ্ট তিনটি লগ ফাইল তৈরি করে:

```
logs/
├── model_server.log          (Model Server লগ)
├── zombiecoder_agent.log     (Agent Server লগ)
└── proxy_adapter.log         (Proxy Adapter লগ)
```

### লগ দেখুন (বেকগ্রাউন্ডে):

```powershell
# নতুন entries শুধু দেখুন
Get-Content logs/model_server.log -Tail 10

Get-Content logs/zombiecoder_agent.log -Tail 10

Get-Content logs/proxy_adapter.log -Tail 10
```

### রিয়েল-টাইম ট্র্যাক করুন (ফলো mode):

```powershell
# Model Server লাইভ দেখুন
Get-Content logs/model_server.log -Wait

# Agent Server লাইভ দেখুন
Get-Content logs/zombiecoder_agent.log -Wait

# Proxy Adapter লাইভ দেখুন
Get-Content logs/proxy_adapter.log -Wait
```

---

## 🎯 সাধারণ ওয়ার্কফ্লো

### সেটআপ ১: Development

```powershell
# Terminal 1: সব সার্ভার শুরু করুন
.\scripts\start_all_services.ps1

# Terminal 2: আপনার code এডিট করুন, টেস্ট করুন
# মনিটরিং Terminal 1 এ রিয়েল-টাইম দেখা যাবে
```

### সেটআপ २: ডেবাগিং

```powershell
# Terminal 1: সব সার্ভার শুরু করুন (Verbose)
.\scripts\start_all_services.ps1 -Verbose

# Terminal 2: লগ দেখুন
Get-Content logs/proxy_adapter.log -Wait

# Terminal 3: টেস্ট রিকোয়েস্ট পাঠান
curl -X POST http://127.0.0.1:5010/v1/chat/completions ...
```

### সেটআপ ३: Production টেস্টিং

```powershell
# Terminal 1: সব সার্ভার শুরু করুন
.\scripts\start_all_services.ps1

# Terminal 2: একাধিক requests পাঠান
for ($i=1; $i -le 10; $i++) {
    curl -X POST http://127.0.0.1:5010/v1/chat/completions ...
}

# Monitor memory growth এবং response times Terminal 1 এ
```

---

## 🛑 সার্ভার বন্ধ করুন

### বেশিরভাগ সময়:

```powershell
Ctrl+C
```

স্ক্রিপ্ট স্বয়ংক্রিয়ভাবে:
- তিনটি সার্ভার বন্ধ করবে
- Temp ফাইল পরিষ্কার করবে
- Status দেখাবে

### যদি Ctrl+C কাজ না করে:

```powershell
# পৃথকভাবে প্রসেস বন্ধ করুন
taskkill /F /PID 12345  # Model Server
taskkill /F /PID 12346  # Agent Server
taskkill /F /PID 12347  # Proxy Adapter
```

---

## ⚙️ কাস্টমাইজ করুন

### Model Server Path পরিবর্তন করুন:

স্ক্রিপ্টে, লাইন ৫৮-এ পরিবর্তন করুন:
```powershell
if ($Name -eq "Model Server") {
    Set-Location "C:\your\custom\path"  # এখানে
```

### পোর্ট পরিবর্তন করুন:

স্ক্রিপ্টে, লাইন ২৫-२७ পরিবর্তন করুন:
```powershell
$ModelServerPort = 9155    # পরিবর্তন করুন
$AgentPort = 9001          # পরিবর্তন করুন
$ProxyPort = 9010          # পরিবর্তন করুন
```

### মনিটরিং ইন্টারভাল পরিবর্তন করুন:

স্ক্রিপ্টে, লাইন २५२-এ:
```powershell
if ($Counter % 10 -eq 0) {  # ১০ সেকেন্ড
    # পরিবর্তন করুন: ১০ = २० সেকেন্ড, ৫ = 2.৫ সেকেন্ড
```

---

## 🆘 সমস্যা সমাধান

### সমস্যা: "স্ক্রিপ্ট কাজ করছে না"

```powershell
# PowerShell execution policy চেক করুন
Get-ExecutionPolicy

# যদি "Restricted" হয়:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### সমস্যা: "একটি সার্ভার শুরু হয়নি"

লগ দেখুন:
```powershell
Get-Content logs/model_server.log -Tail 20
Get-Content logs/zombiecoder_agent.log -Tail 20
Get-Content logs/proxy_adapter.log -Tail 20
```

### সমস্যা: "কোন requests দেখা যাচ্ছে না"

১. নিশ্চিত করুন সার্ভারগুলি চলছে
२. টেস্ট করুন: `curl http://127.0.0.1:8001/health`
३. লগ ফাইল চেক করুন

---

## 📚 আরও পড়ুন

- **PROXY_ADAPTER_GUIDE.md** - প্রক্সি বিস্তারিত
- **COMPLETE_SETUP_CHECKLIST.md** - সম্পূর্ণ চেকলিস্ট
- **TROUBLESHOOTING.md** - সমস্যা সমাধান

---

**এখন সার্ভার শুরু করুন এবং মনিটরিং দেখুন!**

```powershell
.\scripts\start_all_services.ps1
```

✨ Happy Monitoring! ✨
