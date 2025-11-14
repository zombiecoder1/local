# 🎯 Cursor AI - Local Server Integration Guide

## সমস্যা: Cursor AI ক্লাউডকে কল করছে

**উপসর্গ:**
- Cursor AI সেটিংসে "Cloud" দেখা যাচ্ছে
- প্রক্সি পোর্ট 5010 ব্যবহার করছে না
- ক্লাউড API কল হচ্ছে

**কারণ:**
- Cursor AI default কনফিগ ক্লাউড API ব্যবহার করে
- আমাদের প্রক্সি বাইপাস হয়ে যাচ্ছে
- Cursor এর সেটিংসে আমাদের লোকাল সার্ভার নেই

---

## ✅ সমাধান: 3 পদক্ষেপে

### পদক্ষেপ 1: Cursor AI কনফিগ পরিবর্তন করুন

**ফাইল:**
- `Force_Cursor_Connector_ADAPTED.py` (নতুন তৈরি)

**কমান্ড:**
```powershell
python Force_Cursor_Connector_ADAPTED.py
```

**এটি কী করবে:**
1. Cursor AI এর কনফিগ ডিরেক্টরি খুঁজে বের করবে
2. `settings.json` ফাইল খুলবে
3. আমাদের লোকাল সার্ভার যোগ করবে:
   - নাম: "ZombieCoder Local AI"
   - URL: `http://localhost:5010` (আমাদের প্রক্সি)
   - মডেল: `deepseek-coder-1.3b`
4. এটিকে **default model** করবে
5. অফলাইন মোড চালু করবে

**ফলাফল:**
```json
{
  "ai": {
    "defaultModel": "ZombieCoder Local AI",
    "preferredModel": "ZombieCoder Local AI",
    "customModels": [
      {
        "name": "ZombieCoder Local AI",
        "baseURL": "http://localhost:5010",
        "model": "deepseek-coder-1.3b",
        "priority": 1,
        "enabled": true
      }
    ]
  }
}
```

---

### পদক্ষেপ 2: সার্ভার চালু করুন (একটি কমান্ড)

**সবকিছু একসাথে চালানোর জন্য:**
```powershell
START_CURSOR_LOCAL.bat
```

**এটি করবে:**
1. ✅ কিল বিদ্যমান প্রসেস
2. ✅ Agent চালু করবে (পোর্ট 8001)
3. ✅ Proxy চালু করবে (পোর্ট 5010)
4. ✅ সংযোগ পরীক্ষা করবে
5. ✅ Cursor AI কনফিগ করবে
6. ✅ প্রস্তুত!

---

### পদক্ষেপ 3: Cursor AI রিস্টার্ট করুন

**গুরুত্বপূর্ণ:**
1. Cursor AI সম্পূর্ণ বন্ধ করুন (Taskbar থেকে)
2. Cursor AI পুনরায় খুলুন
3. Cursor এখন লোকাল সার্ভার ব্যবহার করবে

---

## 🔄 প্রবাহ: কীভাবে কাজ করে?

```
Cursor AI  
    ↓
    Request to Model
    ↓
http://localhost:5010 (Proxy)
    ↓
Agent (8001)
    ↓
Model Server (8155 - deepseek-coder-1.3b)
    ↓
    Response back to Cursor AI

❌ NO CLOUD CALLS
```

---

## 🚀 অপশনাল: Windows সার্ভিসেস (Auto-Start)

**কেন ব্যবহার করব?**
- কম্পিউটার বুট করলেও সার্ভার স্বয়ংক্রিয়ভাবে চলবে
- ম্যানুয়াল স্টার্ট করতে হবে না
- সর্বদা উপলব্ধ

**ইনস্টল করতে:**
```powershell
# Admin হিসেবে চালান:
.\Install_Services_ADAPTED.ps1
```

**সেবাগুলো:**
1. **ZombieCoder-Agent** (পোর্ট 8001)
   - AI প্রসেসিং
   - স্বয়ংক্রিয় স্টার্ট

2. **ZombieCoder-Proxy** (পোর্ট 5010)
   - Cursor সংযোগ
   - স্বয়ংক্রিয় স্টার্ট

**আনইনস্টল করতে:**
```powershell
.\Install_Services_ADAPTED.ps1 -Uninstall
```

---

## 🔒 নিরাপত্তা যাচাইকরণ

**নিশ্চিত করুন:**

1. ✅ Agent চলছে:
   ```powershell
   curl http://localhost:8001/health
   ```

2. ✅ Proxy চলছে:
   ```powershell
   curl http://localhost:5010/health
   ```

3. ✅ Cursor Log দেখুন:
   ```powershell
   cat CURSOR_CONNECTION_LOG.txt
   ```

---

## 📊 ফলাফল: আগে vs পরে

### আগে (সমস্যা):
```
Cursor AI ──→ Cloud API (OpenAI, Claude, etc.)
                ↓
                ❌ Personal data sent to cloud
                ❌ Slow (network latency)
                ❌ Paid services
```

### পরে (সমাধান):
```
Cursor AI ──→ http://localhost:5010 (Proxy)
                ↓
                unified_agent_system.py (8001)
                ↓
                Local LLM (deepseek-coder-1.3b)
                ↓
                ✅ Completely offline
                ✅ Fast (local)
                ✅ Free
                ✅ Private
```

---

## 🛠️ ট্রাবলশুটিং

### সমস্যা 1: "Could not connect to http://localhost:5010"
**সমাধান:**
- প্রক্সি উইন্ডো খোলা আছে কিনা চেক করুন
- `START_CURSOR_LOCAL.bat` পুনরায় চালান

### সমস্যা 2: Cursor এখনও ক্লাউড ব্যবহার করছে
**সমাধান:**
- Cursor সম্পূর্ণ বন্ধ করুন (Taskbar থেকে)
- কমান্ড প্রম্পট থেকে খুলুন: `cursor`
- সেটিংস দেখুন (Model নাম চেক করুন)

### সমস্যা 3: কনেক্টর স্ক্রিপ্ট কাজ করছে না
**সমাধান:**
- Admin হিসেবে চালান
- `CURSOR_CONNECTION_LOG.txt` দেখুন
- Cursor ইনস্টল আছে কিনা চেক করুন

### সমস্যা 4: "requests" মডিউল নেই
**সমাধান:**
```powershell
pip install requests
```

---

## 📁 তৈরি ফাইলগুলো

| ফাইল | উদ্দেশ্য |
|------|---------|
| `Force_Cursor_Connector_ADAPTED.py` | Cursor সেটিংস পরিবর্তন |
| `START_CURSOR_LOCAL.bat` | সব সার্ভার একসাথে চালু |
| `Install_Services_ADAPTED.ps1` | Windows সার্ভিসেস সেটআপ |
| `LAUNCHER_ANALYSIS.txt` | ডিটেইল বিশ্লেষণ |
| `CURSOR_CONNECTION_LOG.txt` | লগ (স্বয়ংক্রিয় তৈরি) |

---

## ⚡ দ্রুত শুরু (Quick Start)

### সাধারণ ব্যবহার:
```powershell
# 1. এক সাথে সব চালু করুন
START_CURSOR_LOCAL.bat

# 2. Cursor খুলুন (স্বাভাবিকভাবে)
cursor

# 3. এখন Cursor লোকাল AI ব্যবহার করবে ✓
```

### উন্নত সেটআপ (Auto-Start):
```powershell
# 1. Admin উইন্ডো খুলুন
# 2. চালান:
.\Install_Services_ADAPTED.ps1

# 3. কম্পিউটার রিবুট করুন

# 4. এখন থেকে স্বয়ংক্রিয়ভাবে চলবে
```

---

## 🎯 যাচাইকরণ তালিকা

- [ ] Python ইনস্টল আছে
- [ ] `unified_agent_system.py` আছে
- [ ] `proxy_simple.py` আছে
- [ ] `Force_Cursor_Connector_ADAPTED.py` চালিয়েছি
- [ ] `START_CURSOR_LOCAL.bat` কাজ করেছে
- [ ] Agent উইন্ডো খোলা আছে
- [ ] Proxy উইন্ডো খোলা আছে
- [ ] Cursor AI রিস্টার্ট করেছি
- [ ] Cursor এ "ZombieCoder Local AI" মডেল দেখা যাচ্ছে
- [ ] সাফল্য! ✅

---

## 📞 সাহায্য প্রয়োজন?

1. **লগ দেখুন:**
   ```powershell
   cat CURSOR_CONNECTION_LOG.txt
   ```

2. **Agent লগ চেক করুন:**
   - "ZombieCoder Agent" উইন্ডো দেখুন

3. **Proxy লগ চেক করুন:**
   - "ZombieCoder Proxy" উইন্ডো দেখুন

---

## ✨ সাফল্য! এখন আপনার কাছে:

✅ **সম্পূর্ণ অফলাইন Cursor AI**
✅ **লোকাল LLM (deepseek-coder-1.3b)**
✅ **কোন ক্লাউড কল নেই**
✅ **ব্যক্তিগত ডেটা সুরক্ষিত**
✅ **দ্রুত সাড়া**
✅ **বিনামূল্যে**

**উপভোগ করুন! 🚀**
