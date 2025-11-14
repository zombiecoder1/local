# 📚 ডকুমেন্টেশন ইন্ডেক্স

## 🚀 শুরু করুন এখানে থেকে

### 1️⃣ **START_HERE_BANGLA.md** ← আপনার প্রথম ফাইল!
   - **বাংলায় সম্পূর্ণ নির্দেশনা**
   - ৩ ধাপে শুরু করুন
   - ছবি নেই কিন্তু খুবই সহজ

### २⃣ **PROXY_SETUP_README.txt** 
   - **সম্পূর্ণ সেটআপ সারমর্ম**
   - সব নতুন ফাইলের তালিকা
   - কমান্ড রেফারেন্স

### ३⃣ **CURSOR_SETUP_QUICKSTART.md**
   - **Cursor AI দ্রুত শুরু**
   - ৩ ধাপের গাইড
   - টেস্টিং কমান্ড

---

## 📖 বিস্তারিত গাইডগুলি

### 📘 **PROXY_SETUP_SUMMARY.md**
   - প্রক্সি কীভাবে কাজ করে
   - আর্কিটেকচার ডায়াগ্রাম
   - ডেটা ফ্লো উদাহরণ
   - সফলতার চিহ্ন

### 📙 **COMPLETE_SETUP_CHECKLIST.md**
   - সম্পূর্ণ চেকলিস্ট
   - নতুন ফাইলের অবস্থান
   - পরীক্ষার কমান্ড
   - ট্রাবলশুটিং

### 📕 **docs/PROXY_ADAPTER_GUIDE.md**
   - **সবচেয়ে বিস্তারিত ডকুমেন্টেশন**
   - প্রক্সি ফিচারগুলি
   - কনফিগারেশন বিকল্প
   - Advanced settings

### 📗 **EDITOR_SETUP_GUIDE.md**
   - Continue.dev সেটআপ
   - VS Code সেটআপ
   - অন্যান্য এডিটর

---

## 🛠️ স্ক্রিপ্ট ফাইলগুলি

### ⚙️ **scripts/start_proxy.ps1**
```powershell
.\scripts\start_proxy.ps1
```
প্রক্সি সার্ভার শুরু করে (PowerShell)

### ⚙️ **scripts/start_proxy.py**
```bash
python scripts/start_proxy.py
```
প্রক্সি সার্ভার শুরু করে (Python)

### ⚙️ **scripts/test_proxy.py**
```bash
python scripts/test_proxy.py
```
প্রক্সি পরীক্ষা করে এবং সংযোগ যাচাই করে

### ⚙️ **scripts/verify_setup.ps1**
```powershell
.\scripts\verify_setup.ps1
```
সম্পূর্ণ সেটআপ যাচাই করে (নতুন!)

---

## 📁 কনফিগারেশন ফাইলগুলি

### ⚙️ **config/proxy_config.json**
```json
{
  "api_key": "DUMMY_API_KEY_FOR_LOCAL",
  "port": 5010,
  "bind_host": "127.0.0.1",
  "target_base": "http://127.0.0.1:8001"
}
```

### ⚙️ **.env**
```
AGENT_PORT=8001
OLLAMA_URL=http://127.0.0.1:8155
```

---

## 🚀 কমান্ড দ্রুত রেফারেন্স

### এজেন্ট শুরু করুন
```powershell
./full_auto_install.ps1
```

### প্রক্সি শুরু করুন
```powershell
.\scripts\start_proxy.ps1
```

### প্রক্সি রিস্টার্ট করুন
```powershell
.\scripts\start_proxy.ps1 -Force
```

### সেটআপ যাচাই করুন
```powershell
.\scripts\verify_setup.ps1
```

### প্রক্সি পরীক্ষা করুন
```bash
python scripts/test_proxy.py
```

### স্বাস্থ্য পরীক্ষা
```powershell
curl http://127.0.0.1:8001/health    # এজেন্ট
curl http://127.0.0.1:5010/health    # প্রক্সি
curl http://127.0.0.1:8155/health    # মডেল
```

### লগ দেখুন
```powershell
Get-Content logs/proxy_adapter.log -Tail 20
Get-Content logs/zombiecoder_agent.log -Tail 20
```

### রিয়েল-টাইম লগ দেখুন
```powershell
Get-Content logs/proxy_adapter.log -Wait
```

---

## 🎯 ব্যবহারকারীর প্রয়োজন অনুযায়ী গাইড

### "আমি শুরু করতে চাই এখনই"
**পড়ুন**: START_HERE_BANGLA.md

### "আমি বিস্তারিত জানতে চাই"
**পড়ুন**: docs/PROXY_ADAPTER_GUIDE.md

### "আমি শুধু সেটআপ করতে চাই এবং যেতে চাই"
**পড়ুন**: CURSOR_SETUP_QUICKSTART.md

### "আমি সবকিছু যাচাই করতে চাই"
**রান করুন**: .\scripts\verify_setup.ps1

### "আমি ট্রাবলশুট করছি"
**পড়ুন**: COMPLETE_SETUP_CHECKLIST.md

### "আমি Cursor AI কনফিগার করছি"
**পড়ুন**: CURSOR_SETUP_QUICKSTART.md

### "আমি Continue.dev কনফিগার করছি"
**পড়ুন**: EDITOR_SETUP_GUIDE.md

---

## 📊 ফাইল ম্যাপ

```
ZombieCoder-Family-Agent/
│
├── 📄 START_HERE_BANGLA.md ⭐ শুরু এখানে
├── 📄 PROXY_SETUP_README.txt
├── 📄 PROXY_SETUP_SUMMARY.md
├── 📄 CURSOR_SETUP_QUICKSTART.md
├── 📄 CURSOR_CONFIG_UPDATED.json
├── 📄 COMPLETE_SETUP_CHECKLIST.md
├── 📄 EDITOR_SETUP_GUIDE.md
├── 📄 DOCUMENTATION_INDEX.md ← আপনি এখানে
│
├── config/
│   └── proxy_config.json ⭐ প্রক্সি কনফিগ
│
├── scripts/
│   ├── start_proxy.ps1 ⭐ প্রক্সি শুরু করুন
│   ├── start_proxy.py
│   ├── test_proxy.py
│   └── verify_setup.ps1 ← নতুন
│
├── docs/
│   └── PROXY_ADAPTER_GUIDE.md ⭐ বিস্তারিত
│
├── logs/
│   ├── proxy_adapter.log
│   └── zombiecoder_agent.log
│
├── proxy_adapter.py ⭐ মূল প্রক্সি
├── unified_agent_system.py
└── .env
```

---

## ⭐ সবচেয়ে গুরুত্বপূর্ণ ফাইলগুলি

| ফাইল | কি করে | কখন দেখবেন |
|------|--------|----------|
| START_HERE_BANGLA.md | সম্পূর্ণ গাইড (বাংলায়) | প্রথম আরম্ভ |
| PROXY_SETUP_README.txt | সারমর্ম | দ্রুত রেফারেন্স |
| proxy_config.json | প্রক্সি সেটিংস | কনফিগ পরিবর্তনের সময় |
| scripts/start_proxy.ps1 | প্রক্সি চালায় | প্রক্সি শুরু করার সময় |
| docs/PROXY_ADAPTER_GUIDE.md | বিস্তারিত | Advanced কনফিগের জন্য |

---

## 🧪 পরীক্ষা করার ধাপ

1. **সেটআপ যাচাই করুন**
   ```powershell
   .\scripts\verify_setup.ps1
   ```

2. **প্রক্সি পরীক্ষা করুন**
   ```powershell
   python scripts/test_proxy.py
   ```

3. **লগ পরীক্ষা করুন**
   ```powershell
   Get-Content logs/proxy_adapter.log -Tail 20
   ```

4. **Cursor এ চ্যাট করুন**
   ```
   Ctrl+L (Chat খুলুন)
   "Python এ Hello লেখো" লিখুন
   ```

---

## 📞 সাহায্য পেতে

### দ্রুত সাহায্য
```powershell
# লগ দেখুন
Get-Content logs/proxy_adapter.log -Wait

# সবকিছু যাচাই করুন
.\scripts\verify_setup.ps1
```

### বিস্তারিত সাহায্য
**পড়ুন**: COMPLETE_SETUP_CHECKLIST.md (Troubleshooting বিভাগ)

### আরও সাহায্য
**পড়ুন**: docs/PROXY_ADAPTER_GUIDE.md (Troubleshooting বিভাগ)

---

## ✨ সফলতার জন্য দ্রুত চেকলিস্ট

- [ ] START_HERE_BANGLA.md পড়েছি
- [ ] `./full_auto_install.ps1` চালিয়েছি
- [ ] `.\scripts\start_proxy.ps1` চালিয়েছি
- [ ] Cursor সেটিংস কনফিগার করেছি
- [ ] `.\scripts\verify_setup.ps1` চালিয়েছি (সব সবুজ)
- [ ] Cursor এ চ্যাট করে পরীক্ষা করেছি
- [ ] লগ দেখেছি এবং কাজ করছে দেখেছি

---

🎉 **প্রস্তুত! এখন শুরু করুন!**

**প্রথম ফাইল পড়ুন**: START_HERE_BANGLA.md
