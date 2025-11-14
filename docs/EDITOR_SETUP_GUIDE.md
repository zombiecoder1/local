# Continue.dev এবং Cursor AI সেটআপ গাইড

## 🎯 লোকাল ZombieCoder Agent কনফিগারেশন

আপনার এডিটররা এখন লোকাল এজেন্ট ব্যবহার করবে দুই উপায়ে:

### ✅ অপশন ১: সরাসরি এজেন্ট (দ্রুত)
- **API URL**: `http://127.0.0.1:8001/v1`
- **মডেল**: `deepseek-coder-1.3b`

### ✅ অপশন ২: প্রক্সি সার্ভার (সব কল ইন্টারসেপ্ট)
- **API URL**: `http://127.0.0.1:5010/v1` ← **Cursor AI জন্য সুপারিশকৃত**
- **মডেল**: `deepseek-coder-1.3b`
- **সুবিধা**: সব internal calls রুট হয় ZombieCoder এ

### 🔐 API Key (উভয়ের জন্য)
- **API Key**: `DUMMY_API_KEY_FOR_LOCAL` (লোকাল, সিকিউরিটি নেই)

---

## 🔄 প্রক্সি সার্ভার সেটআপ (Cursor AI জন্য)

Cursor AI এর সব internal calls ইন্টারসেপ্ট করতে প্রক্সি ব্যবহার করুন।

### ১. প্রক্সি শুরু করুন

**PowerShell এ:**
```powershell
# প্রথম বার
.\scripts\start_proxy.ps1

# আবার শুরু করতে
.\scripts\start_proxy.ps1 -Force
```

**Python এ:**
```bash
python scripts/start_proxy.py
```

### २. কনফিগার করুন

Proxy সার্ভার:
- 📍 সুনছে: `http://127.0.0.1:5010`
- 🎯 রুট করছে: `http://127.0.0.1:8001` (ZombieCoder Agent)
- 📝 লগ: `logs/proxy_adapter.log`

### ३. Cursor AI সেটিংস

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

**উপকারিতা:**
- ✅ সব Cursor calls ইন্টারসেপ্ট হয়
- ✅ লগিং সমর্থন
- ✅ Streaming ফরওয়ার্ডিং
- ✅ Error handling

---

## Continue.dev সেটআপ (VS Code Extension)

### ১. ফাইল তৈরি করুন:
```bash
# ওয়ার্কস্পেস লেভেল কনফিগারেশন
.continue/config.json
```

### ২. ব্যবহার করুন:
```
Cmd/Ctrl + Shift + L  # Continue চ্যাট খুলুন
সাহন ভাই সাথে চ্যাট করুন!
```

---

## Cursor AI সেটআপ

### ১. Cursor সেটিংস খুলুন:
```
Cmd/Ctrl + , (Settings)
```

### ২. JSON এডিটর খুলুন:
```
Search: "Cursor Settings" → সার্চ করুন
```

### ३. যোগ করুন:
```json
{
  "cursor.customModel": {
    "title": "ZombieCoder Agent (সাহন ভাই)",
    "url": "http://127.0.0.1:8001/v1",
    "apiKey": "DUMMY_API_KEY_FOR_LOCAL",
    "model": "deepseek-coder-1.3b"
  }
}
```

### ३. ব্যবহার করুন:
```
Cmd/Ctrl + K    # Cursor চ্যাট খুলুন
@ZombieCoder    # আপনার এজেন্ট সিলেক্ট করুন
```

---

## VS Code সেটআপ (Continue.dev সহ)

### ১. Workspace Settings খুলুন:
```
Cmd/Ctrl + Shift + P
> Preferences: Open Workspace Settings (JSON)
```

### २. কপি করুন:
সেটিংস এই ফাইল থেকে: `.vscode-settings.json`

### ३. পেস্ট করুন Workspace settings এ

---

## ✅ পরীক্ষা করুন

```bash
# এজেন্ট এন্ডপয়েন্ট পরীক্ষা
curl -X GET http://127.0.0.1:8001/health
# Output: {"status": "healthy", ...}

# চ্যাট পরীক্ষা
curl -X POST http://127.0.0.1:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "ভাইয়া, Python এ কেমন লেখে?"}'
```

---

## 🚀 প্রি-রিকোয়েজিট

নিশ্চিত করুন:
1. ✅ এজেন্ট সার্ভার চলছে (`http://127.0.0.1:8001`)
2. ✅ মডেল সার্ভার চলছে (`http://127.0.0.1:8155`)
3. ✅ `.env` সঠিকভাবে কনফিগার করা (`AGENT_PORT=8001`)

---

## 🔧 ট্রাবলশুটিং

**সমস্যা**: "Connection refused"
**সমাধান**: এজেন্ট সার্ভার চলছে কিনা চেক করুন:
```bash
netstat -ano | findstr ":8001"
```

**সমস্যা**: Continue.dev এক্সটেনশন ডিজেবল্ড
**সমাধান**:
1. Extensions এ যান
2. Continue খুঁজুন
3. "Enable" ক্লিক করুন

---

## 📝 ফাইল লোকেশন

- **Workspace Config**: `.continue/config.json`
- **VS Code Config**: `C:\Users\sahon\AppData\Roaming\Code\User\settings.json`
- **Cursor Config**: `C:\Users\sahon\AppData\Roaming\Cursor\settings.json`
- **Continue Config**: `C:\Users\sahon\AppData\Roaming\Continue\config.json`

---

## 🎨 কাস্টমাইজেশন

আপনি পরিবর্তন করতে পারেন:
- `systemPrompt` - এজেন্টের ব্যক্তিত্ব
- `model` - কোন মডেল ব্যবহার করবে
- `apiBase` - API এন্ডপয়েন্ট

---

✨ **আপনার লোকাল AI এজেন্ট সব জায়গায় প্রস্তুত!**

.vscode-settings.json → VS Code Settings (Ctrl+,) এ পেস্ট করুন
