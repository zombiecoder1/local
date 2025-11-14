# 🎯 সম্পূর্ণ সেটআপ - Cursor AI + ZombieCoder Agent + Proxy

## কী করেছি

আপনার `proxy_adapter.py` এর সাথে সম্পূর্ণ Cursor AI ইন্টিগ্রেশন সেটআপ করেছি। এখন Cursor AI এর সব ইন্টারনাল কল আপনার লোকাল ZombieCoder এজেন্টে যাবে।

---

## 🚀 দ্রুত শুরু করুন

### ৩ ধাপ:

#### ১. এজেন্ট সার্ভার চালু করুন
```powershell
# First Terminal
./full_auto_install.ps1
```
✅ ফলাফল: `http://127.0.0.1:8001` চলছে

#### २. প্রক্সি সার্ভার চালু করুন
```powershell
# Second Terminal
.\scripts\start_proxy.ps1
```
✅ ফলাফল: `http://127.0.0.1:5010` চলছে

#### ३. Cursor AI কনফিগার করুন
Cursor Settings (`Cmd+,`) এ যোগ করুন:
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

এখন Cursor এ চ্যাট করুন এবং সব কল প্রক্সির মাধ্যমে যাবে! ✨

---

## 📁 নতুন ফাইলগুলি

| ফাইল | উদ্দেশ্য |
|------|---------|
| `config/proxy_config.json` | প্রক্সি কনফিগারেশন |
| `scripts/start_proxy.ps1` | প্রক্সি শুরু করার PowerShell স্ক্রিপ্ট |
| `scripts/start_proxy.py` | প্রক্সি শুরু করার Python স্ক্রিপ্ট |
| `scripts/test_proxy.py` | প্রক্সি টেস্ট স্ক্রিপ্ট |
| `docs/PROXY_ADAPTER_GUIDE.md` | বিস্তারিত ডকুমেন্টেশন |
| `CURSOR_SETUP_QUICKSTART.md` | Cursor AI দ্রুত শুরু গাইড |
| `CURSOR_CONFIG_UPDATED.json` | Cursor কনফিগারেশন রেফারেন্স |

---

## 🏗️ আর্কিটেকচার

```
Cursor AI
   ↓ (request to port 5010)
Proxy Server (port 5010)
   ↓ (intercepts + logs + retries)
ZombieCoder Agent (port 8001)
   ↓ (calls model API)
Model Server (port 8155)
   ↓ (inference)
deepseek-coder-1.3b
```

**প্রক্সি কী করে:**
1. ✅ সব Cursor কলকে ইন্টারসেপ্ট করে
2. ✅ API key ভ্যালিডেট করে
3. ✅ সন্দেহজনক headers স্ট্রিপ করে
4. ✅ সব রিকোয়েস্ট লগ করে
5. ✅ স্ট্রিমিং সাপোর্ট করে
6. ✅ ফেইলিউরে রিট্রাই করে (60 বার)
7. ✅ ZombieCoder এজেন্টে ফরওয়ার্ড করে

---

## ⚙️ কনফিগারেশন

### proxy_config.json
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

**কী মানে কী:**
- `api_key`: Authorization টোকেন (সিকিউরিটি)
- `port`: প্রক্সি পোর্ট
- `target_base`: ZombieCoder এজেন্ট ঠিকানা
- `log_file`: লগ ফাইল পাথ

---

## 🧪 পরীক্ষা করুন

### প্রক্সি স্বাস্থ্য চেক
```powershell
curl http://127.0.0.1:5010/health
```

### সরাসরি চ্যাট টেস্ট
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

### Python টেস্ট
```powershell
python scripts/test_proxy.py
```

---

## 📊 ডেটা ফ্লো

### উদাহরণ: Cursor এ একটি প্রশ্ন করুন

```
1. Cursor AI:
   POST http://127.0.0.1:5010/v1/chat/completions
   Headers: Authorization: Bearer DUMMY_API_KEY_FOR_LOCAL
   Body: {messages: [{role: "user", content: "Hello"}]}

2. Proxy Adapter:
   ✓ API key চেক করে
   ✓ Headers ফিল্টার করে
   ✓ এজেন্টে ফরওয়ার্ড করে
   ✓ রেসপন্স লগ করে
   ✓ Cursor এ রিটার্ন করে

3. ZombieCoder Agent:
   POST http://127.0.0.1:8001/v1/chat/completions
   → মডেল সার্ভারে পাঠায় (port 8155)
   → মডেল থেকে রেসপন্স পায়
   → Cursor এ রিটার্ন করে
```

---

## 📝 লগিং

### প্রক্সি লগ দেখুন
```powershell
Get-Content logs/proxy_adapter.log -Tail 20
```

### রিয়েল-টাইম মনিটরিং
```powershell
Get-Content logs/proxy_adapter.log -Wait
```

### এরর খুঁজুন
```powershell
Select-String "ERROR|WARNING" logs/proxy_adapter.log
```

---

## 🔧 ট্রাবলশুট

### সমস্যা: "Connection refused"

**চেক করুন কোন সার্ভার চলছে:**
```powershell
netstat -ano | findstr ":5010"   # প্রক্সি
netstat -ano | findstr ":8001"   # এজেন্ট
netstat -ano | findstr ":8155"   # মডেল
```

### সমস্যা: Cursor চ্যাট কাজ করছে না

1. **Cursor সেটিংস চেক করুন:**
   ```json
   "url": "http://127.0.0.1:5010/v1"
   "apiKey": "DUMMY_API_KEY_FOR_LOCAL"
   ```

2. **প্রক্সি লগ দেখুন:**
   ```powershell
   Get-Content logs/proxy_adapter.log -Tail 50
   ```

3. **প্রক্সি রিস্টার্ট করুন:**
   ```powershell
   .\scripts\start_proxy.ps1 -Force
   ```

### সমস্যা: "Unauthorized"

**আপনার Cursor সেটিংস সঠিক কিনা চেক করুন:**
```json
{
  "cursor.chat.customModel": {
    "url": "http://127.0.0.1:5010/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL"  // এটা সঠিক হতে হবে
  }
}
```

---

## 🎯 কী ঘটছে পর্দার পিছনে

### প্রক্সি ইন্টারসেপশন
```python
# proxy_adapter.py এর মূল লজিক:

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def _is_authorized(self):
        # API key ভ্যালিডেশন
        token = self.headers.get('Authorization', '').split(' ')[1]
        return token == os.environ.get('PROXY_API_KEY')
    
    def _copy_and_strip_headers(self):
        # সন্দেহজনক headers বাদ দেওয়া
        # x-cursor-client-*, x-hellozombie-* ইত্যাদি
    
    def _forward(self, method, path, body):
        # রিট্রাই লজিক সহ ফরওয়ার্ডিং
        # স্ট্রিমিং সাপোর্ট
        # ফেইলোভার হ্যান্ডলিং
```

### স্ট্রিমিং সাপোর্ট
- `stream: true` ডিটেক্ট করে
- Upstream এ streaming অনুরোধ করে
- SSE ফরম্যাটে ফরওয়ার্ড করে
- যদি ফেইল হয় → non-stream fallback

### রিট্রাই লজিক
- প্রাথমিক কানেকশন ফেইল → retry করে
- 60 বার পর্যন্ত চেষ্টা করে
- Exponential backoff (0.5s → 30s max)
- লগে সব attempt রেকর্ড করে

---

## ✨ বৈশিষ্ট্যসমূহ

| বৈশিষ্ট্য | স্ট্যাটাস | বিবরণ |
|----------|---------|-------|
| Request Forwarding | ✅ | GET, POST, HEAD সাপোর্ট |
| API Key Validation | ✅ | Bearer token চেক |
| Header Filtering | ✅ | সন্দেহজনক headers স্ট্রিপ |
| Streaming | ✅ | SSE ফরম্যাটে |
| Retry Logic | ✅ | 60 attempts with backoff |
| CORS Support | ✅ | সব রেসপন্সে |
| Logging | ✅ | Rotating file logs |
| Error Handling | ✅ | Fallback mechanisms |

---

## 📚 আরও পড়ুন

- **দ্রুত শুরু**: `CURSOR_SETUP_QUICKSTART.md`
- **বিস্তারিত**: `docs/PROXY_ADAPTER_GUIDE.md`
- **এডিটর সেটআপ**: `EDITOR_SETUP_GUIDE.md`

---

## 🎉 ফলাফল

**আগে:**
- Cursor AI → OpenAI API বা অন্য সেবা

**এখন:**
- Cursor AI → Proxy (5010) → ZombieCoder Agent (8001) → Model (8155) → deepseek-coder-1.3b

**উপকার:**
- ✅ সবকিছু লোকাল
- ✅ কোন API cost নেই
- ✅ সম্পূর্ণ নিয়ন্ত্রণ
- ✅ সব কল লগ হয়
- ✅ দ্রুত রেসপন্স (5-13 সেকেন্ড)

---

## 🔐 নিরাপত্তা নোট

⚠️ **এটি শুধুমাত্র স্থানীয় ডেভেলপমেন্ট এর জন্য:**

- API key হার্ডকোডেড
- কোন SSL/TLS নেই
- কোন rate limiting নেই
- **পাবলিক ইন্টারনেটে expose করবেন না**

---

## 🚀 পরবর্তী ধাপ

1. ✅ প্রক্সি কনফিগারেশন তৈরি
2. ✅ স্টার্ট স্ক্রিপ্ট তৈরি
3. ✅ ডকুমেন্টেশন তৈরি
4. **TODO**: Cursor সেটিংস আপডেট করুন
5. **TODO**: প্রক্সি শুরু করুন
6. **TODO**: Cursor এ চ্যাট করুন এবং পরীক্ষা করুন

---

**সবকিছু প্রস্তুত! আপনি এখন প্রক্সির মাধ্যমে Cursor AI ব্যবহার করতে পারেন।** 🎊

