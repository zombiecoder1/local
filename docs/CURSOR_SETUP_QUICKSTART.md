# 🚀 Cursor AI + ZombieCoder Proxy - Quick Start

## এক্ষুনি শুরু করুন (৩ ধাপ)

### ধাপ ১: এজেন্ট সার্ভার চালু করুন
```powershell
# এক্সপ্লোরার এ খুলুন এবং ডাবল ক্লিক করুন:
# full_auto_install.ps1

# অথবা Terminal এ:
./full_auto_install.ps1
```

✅ **আউটপুট**: Agent চলছে `http://127.0.0.1:8001`

---

### ধাপ २: প্রক্সি সার্ভার চালু করুন
```powershell
# New Terminal তে:
.\scripts\start_proxy.ps1
```

✅ **আউটপুট**: Proxy চলছে `http://127.0.0.1:5010`

---

### ধাপ ३: Cursor AI কনফিগারেশন

**Option A: Settings UI (সহজ)**
1. Cursor খুলুন
2. `Cmd+,` (Settings)
3. JSON mode চুন (নিচে বাম কোণে `{}`)
4. এই যোগ করুন:

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

**Option B: Settings File (সরাসরি)**
ফাইল খুলুন: `%APPDATA%\Roaming\Cursor\settings.json`
কনফিগারেশন যোগ করুন (উপরে দেখুন)

---

## যাচাই করুন সবকিছু কাজ করছে

### টার্মিনালে পরীক্ষা করুন:
```powershell
# প্রক্সি চলছে কিনা
curl http://127.0.0.1:5010/health

# এজেন্ট চলছে কিনা
curl http://127.0.0.1:8001/health

# সরাসরি চ্যাট টেস্ট
curl -X POST http://127.0.0.1:5010/v1/chat/completions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer DUMMY_API_KEY_FOR_LOCAL" `
  -d '{
    "model": "deepseek-coder-1.3b",
    "messages": [{"role": "user", "content": "test"}],
    "stream": false
  }'
```

### Cursor এ পরীক্ষা করুন:
1. Cursor খুলুন
2. `Ctrl+L` (Chat)
3. কোন সাধারণ প্রশ্ন করুন: "এটা কাজ করছে?"
4. প্রতিক্রিয়া আসবে ZombieCoder থেকে

---

## 📝 লগ দেখুন

### প্রক্সি লগ:
```
logs/proxy_adapter.log
```

### এজেন্ট লগ:
```
logs/zombiecoder_agent.log
```

---

## 🔧 ট্রাবলশুট

### সমস্যা: "Connection refused"
**সমাধান:**
```powershell
# চেক করুন কোন সার্ভার চলছে
netstat -ano | findstr ":5010"  # প্রক্সি
netstat -ano | findstr ":8001"  # এজেন্ট
netstat -ano | findstr ":8155"  # মডেল সার্ভার
```

### সমস্যা: Cursor এ চ্যাট কাজ করছে না
**সমাধান:**
1. Cursor সেটিংসে সঠিক URL আছে কিনা চেক করুন
2. প্রক্সি লগ দেখুন: `logs/proxy_adapter.log`
3. প্রক্সি রিস্টার্ট করুন: `.\scripts\start_proxy.ps1 -Force`

### সমস্যা: লগ ফাইল নেই
**সমাধান:**
```powershell
mkdir logs -Force
```

---

## 🎯 আর্কিটেকচার

```
Cursor AI
    ↓
    └─→ Proxy Server (port 5010)
           ↓
           └─→ ZombieCoder Agent (port 8001)
                  ↓
                  └─→ Model Server (port 8155)
                         ↓
                         └─→ deepseek-coder-1.3b
```

**সুবিধা:**
- ✅ সব Cursor calls ইন্টারসেপ্ট হয়
- ✅ লগিং সমর্থন
- ✅ স্ট্রিমিং ফরওয়ার্ডিং
- ✅ Error handling এবং retry

---

## 📞 প্রয়োজনীয় পোর্টগুলি

| সেবা | পোর্ট | অবস্থান |
|------|-------|---------|
| ZombieCoder Agent | 8001 | `http://127.0.0.1:8001` |
| Model Server | 8155 | `http://127.0.0.1:8155` |
| Proxy Adapter | 5010 | `http://127.0.0.1:5010` |

---

## ✨ পরবর্তী পদক্ষেপ

1. ✅ এজেন্ট চালু করুন
2. ✅ প্রক্সি চালু করুন
3. ✅ Cursor কনফিগার করুন
4. ✅ চ্যাট করুন!

**সমস্ত কিছু স্থানীয়ভাবে চলছে — কোন API key প্রয়োজন নেই!**
