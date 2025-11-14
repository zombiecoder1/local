# 🎯 Cursor AI Setup - বাঙালিতে ধাপে ধাপে

## ⚡ এক্ষুনি শুরু করুন (মাত্র ৩ ধাপ)

---

## ধাপ ১️⃣ : এজেন্ট সার্ভার শুরু করুন

### কীভাবে:
1. **PowerShell খুলুন** (প্রজেক্ট ফোল্ডার এ)
2. **এই লিখুন:**
   ```powershell
   ./full_auto_install.ps1
   ```
3. **Enter প্রেস করুন** এবং অপেক্ষা করুন

### কী দেখতে পাবেন:
```
✅ Python environment configured
✅ Installing dependencies...
✅ Agent running on http://127.0.0.1:8001
🔄 Model server on http://127.0.0.1:8155
```

✅ **এখন এজেন্ট চলছে!**

---

## ধাপ २️⃣ : প্রক্সি সার্ভার শুরু করুন

### কীভাবে:
1. **নতুন PowerShell খুলুন** (আগেরটা বন্ধ করবেন না!)
2. **প্রজেক্ট ফোল্ডার এ যান:**
   ```powershell
   cd C:\Users\sahon\Desktop\ZombieCoder-Family-Agent
   ```
3. **এই লিখুন:**
   ```powershell
   .\scripts\start_proxy.ps1
   ```
4. **Enter প্রেস করুন**

### কী দেখতে পাবেন:
```
🚀 Proxy Server Starting...
📍 Listening on:     http://127.0.0.1:5010
🎯 Forwarding to:    http://127.0.0.1:8001
✅ Proxy Adapter Module Loaded
```

✅ **এখন প্রক্সি চলছে!**

---

## ধাপ ३️⃣ : Cursor AI কনফিগার করুন

### কীভাবে:
1. **Cursor AI খুলুন**
2. **সেটিংস খুলুন:** `Cmd+,` (Mac) বা `Ctrl+,` (Windows)
3. **Settings এর ডান দিক এ যান**
4. **নিচে বাম কোণে `{}` (JSON) আইকন ক্লিক করুন**
5. **এখানে এই জিনিস যোগ করুন:**

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

6. **Save করুন** (Ctrl+S)

✅ **এখন Cursor AI কনফিগার করা হয়েছে!**

---

## 🎉 সবকিছু প্রস্তুত!

এখন **Cursor এ কোন প্রশ্ন করুন:**

1. **Cursor খুলুন**
2. **Chat খুলুন:** `Ctrl+L`
3. **কিছু লিখুন:** "Python এ হ্যালো ওয়ার্ল্ড কেমন লেখে?"
4. **এন্টার প্রেস করুন**

**🚀 জাদু ঘটবে!**

---

## ✔️ কীভাবে জানবেন সবকিছু ঠিক আছে?

### প্রক্সি লগ দেখুন:
```powershell
Get-Content logs/proxy_adapter.log -Tail 5
```

আপনার দেখতে পাবেন এমন কিছু:
```
127.0.0.1 POST /v1/chat/completions -> 200
127.0.0.1 POST /v1/chat/completions -> 200
```

✅ **যদি এটা দেখেন = সবকিছু কাজ করছে!**

---

## 🆘 যদি কাজ না করে?

### সমস্যা ১: "Connection refused"

**সমাধান:**
```powershell
# প্রক্সি চলছে কিনা চেক করুন
netstat -ano | findstr ":5010"

# যদি না চলে:
.\scripts\start_proxy.ps1
```

### সমস্যা २: "Unauthorized" Cursor এ

**সমাধান:**
1. Cursor Settings খুলুন
2. JSON এ এই লাইন খুঁজুন:
   ```json
   "apiKey": "DUMMY_API_KEY_FOR_LOCAL"
   ```
3. এটা **একদম সঠিক** আছে কিনা চেক করুন

### সমস্যা ३: কোন রেসপন্স নেই

**সমাধান:**
```powershell
# এজেন্ট লগ দেখুন
Get-Content logs/zombiecoder_agent.log -Tail 10

# প্রক্সি লগ দেখুন
Get-Content logs/proxy_adapter.log -Tail 10
```

### সমস্যা ४: এজেন্ট শুরু হচ্ছে না

**সমাধান:**
```powershell
# সব পোর্ট চেক করুন
netstat -ano | findstr ":8001"    # এজেন্ট
netstat -ano | findstr ":5010"    # প্রক্সি
netstat -ano | findstr ":8155"    # মডেল

# যদি কোন না চলে শুরু করুন:
./full_auto_install.ps1
```

---

## 📊 আর্কিটেকচার (সহজভাবে)

```
আপনি Cursor এ লিখেন
          ↓
      (প্রক্সি এটা দেখে)
          ↓
      এজেন্ট এ পাঠায়
          ↓
      মডেল কল করে
          ↓
      রেসপন্স দেয়
          ↓
      প্রক্সি রেকর্ড করে
          ↓
      Cursor এ দেখান হয়
```

---

## 🔄 কীভাবে কাজ করে (বিস্তারিত)

### উদাহরণ: আপনি যখন "Hello" লিখেন

```
1️⃣ Cursor AI
   "Hello" লেখেন
          ↓
2️⃣ প্রক্সি (port 5010)
   Request পায় → API key চেক করে → লগ করে
          ↓
3️⃣ ZombieCoder এজেন্ট (port 8001)
   Request পায় → লাংচেইন প্রসেস করে
          ↓
4️⃣ মডেল সার্ভার (port 8155)
   Model কল করে (deepseek-coder-1.3b)
   → Response: "Hello! I'm a ZombieCoder..."
          ↓
5️⃣ এজেন্ট
   Response পায় → verification করে
          ↓
6️⃣ প্রক্সি
   Response পায় → লগ করে
          ↓
7️⃣ Cursor AI
   দেখায়: "Hello! I'm a ZombieCoder..."
```

**সময়:** ৫-১৩ সেকেন্ড (স্বাভাবিক)

---

## 💾 ফাইল গুলো কোথায় আছে?

```
আপনার প্রজেক্ট ফোল্ডার
├── scripts/
│   ├── start_proxy.ps1       ← এটা দিয়ে প্রক্সি শুরু করুন
│   ├── start_proxy.py        ← বা এটা
│   └── test_proxy.py         ← প্রক্সি পরীক্ষা করুন
├── config/
│   └── proxy_config.json     ← প্রক্সি সেটিংস
├── logs/
│   ├── proxy_adapter.log     ← প্রক্সি লগ
│   └── zombiecoder_agent.log ← এজেন্ট লগ
└── docs/
    └── PROXY_ADAPTER_GUIDE.md ← বিস্তারিত ডক
```

---

## 🧪 পরীক্ষা করুন সবকিছু

### সবচেয়ে সহজ পরীক্ষা:

```powershell
# এজেন্ট চলছে?
curl http://127.0.0.1:8001/health

# প্রক্সি চলছে?
curl http://127.0.0.1:5010/health

# মডেল চলছে?
curl http://127.0.0.1:8155/health
```

যদি সবাই `200` দেয় = **সবকিছু ঠিক!** ✅

---

## 🎯 সফলতার চিহ্ন

যখন এই সবকিছু দেখতে পাবেন = **আপনি সফল!**

- ✅ দুটো PowerShell উভয় চলছে (কোন error নেই)
- ✅ Cursor Settings এ JSON আছে
- ✅ Cursor এ কিছু লেখার পর লোডিং শুরু হয়
- ✅ লোডিং শেষে আসে: রেসপন্স (বেংগালি বা ইংরেজি)
- ✅ logs/proxy_adapter.log এ নতুন লাইন দেখা যায়

---

## 🚀 পরবর্তী: অপটিমাইজ করুন (ঐচ্ছিক)

### Continue.dev এও যোগ করুন:

1. VS Code খুলুন
2. Continue এক্সটেনশন খুলুন
3. Settings যান
4. এই যোগ করুন:
```json
{
  "models": [
    {
      "title": "ZombieCoder",
      "provider": "openai",
      "model": "deepseek-coder-1.3b",
      "apiBase": "http://127.0.0.1:5010/v1"
    }
  ]
}
```

---

## 📞 দ্রুত রেফারেন্স

| চিজ | ঠিকানা | কমান্ড |
|-----|--------|--------|
| এজেন্ট | port 8001 | `./full_auto_install.ps1` |
| প্রক্সি | port 5010 | `.\scripts\start_proxy.ps1` |
| মডেল | port 8155 | স্বয়ংক্রিয় চলে |
| এজেন্ট লগ | logs/zombiecoder_agent.log | `Get-Content ...` |
| প্রক্সি লগ | logs/proxy_adapter.log | `Get-Content ...` |

---

## ❓ সবচেয়ে সাধারণ প্রশ্ন

**Q: সবকিছু স্থানীয়ভাবে চলছে?**
A: হ্যাঁ! OpenAI API প্রয়োজন নেই, কোন কস্ট নেই।

**Q: অফলাইনে কাজ করে?**
A: সম্পূর্ণভাবে অফলাইন! (শুধু প্রথম মডেল ডাউনলোড অনলাইনে দরকার)

**Q: বেংগালি সাপোর্ট?**
A: হ্যাঁ! "ভাইয়া, পাইথন কেমন লেখে?" এটা বুঝে।

**Q: ইংরেজি সাপোর্ট?**
A: হ্যাঁ! ইংরেজিতেও কাজ করে।

**Q: গতি কত?**
A: ৫-১৩ সেকেন্ড সাধারণ। আপনার CPU দ্রুত হলে আরও দ্রুত।

---

## 🎊 শুরু করুন এখনই!

```powershell
# টার্মিনাল ১
./full_auto_install.ps1

# টার্মিনাল २
.\scripts\start_proxy.ps1

# তারপর Cursor এ কিছু লিখুন এবং চ্যাট করুন! 🚀
```

---

**✨ Happy Coding with Local AI! ✨**
