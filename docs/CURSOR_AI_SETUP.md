# 🎯 Cursor AI Integration with Hello Zombie

## 📋 Overview
এই গাইড আপনাকে দেখাবে কিভাবে Cursor AI এর input box থেকে সরাসরি আপনার লোকাল Hello Zombie agent ব্যবহার করতে পারবেন।

## 🛠️ Setup Instructions

### 1. **Hello Zombie Server চালু করুন**
```bash
# Main Server চালু করুন
python main_server.py

# Server running on: http://localhost:12346
```

### 2. **Cursor AI Settings Configuration**

#### **Step 1: Cursor AI খুলুন**
- Cursor AI application খুলুন
- `Ctrl + ,` (Windows) বা `Cmd + ,` (Mac) চাপুন settings খুলতে

#### **Step 2: Model Provider Settings**
- Settings এ গিয়ে **"Model Provider"** খুঁজুন
- **"Custom"** select করুন

#### **Step 3: API Configuration**
```
Provider: Custom
Base URL: http://localhost:12346/v1
API Key: hello-zombie-local (যেকোনো dummy key)
Model: gemma:2b (বা আপনার পছন্দের model)
```

### 3. **Available Models**
আপনার Hello Zombie server এ এই models available:
- `gemma:2b` - Google's Gemma 2B model
- `deepseek-coder:1.3b` - DeepSeek Coder model

## 🧪 Testing Integration

### **Test 1: Models Endpoint**
```bash
curl http://localhost:12346/v1/models
```

### **Test 2: Chat Completions**
```bash
curl -X POST http://localhost:12346/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma:2b",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

## 🎯 How It Works

### **Cursor AI → Hello Zombie Flow:**
1. **Cursor AI** input box এ আপনি prompt লিখেন
2. **Cursor AI** আপনার custom endpoint এ request পাঠায়
3. **Hello Zombie Server** request receive করে
4. **Ollama** এ prompt forward করে
5. **Response** Cursor AI এ ফিরে আসে
6. **Memory** automatically save হয়

### **API Endpoints:**
- `POST /v1/chat/completions` - OpenAI compatible chat
- `GET /v1/models` - Available models list
- `GET /health` - Server health check

## 🔧 Troubleshooting

### **Problem 1: Connection Failed**
```
Solution: Check if Hello Zombie server is running
Test: http://localhost:12346/health
```

### **Problem 2: Model Not Found**
```
Solution: Check available models
Test: http://localhost:12346/v1/models
```

### **Problem 3: CORS Error**
```
Solution: Server already configured with CORS
Check: main_server.py line 76-82
```

## 📊 Monitoring

### **Real-time Monitoring:**
- Dashboard: `http://localhost:12346/index.html`
- Health: `http://localhost:12346/health`
- Logs: Check `main_server.log`

### **Memory Tracking:**
- All conversations automatically saved
- Location: `data/memory/hello_zombie_memory.sqlite`
- View: Dashboard → Memory & Monitoring section

## 🚀 Advanced Features

### **Custom Model Selection:**
```json
{
  "model": "deepseek-coder:1.3b",
  "messages": [
    {"role": "user", "content": "Write a Python function"}
  ]
}
```

### **Context Preservation:**
```json
{
  "model": "gemma:2b",
  "messages": [
    {"role": "system", "content": "You are a coding assistant"},
    {"role": "user", "content": "Help me with Python"}
  ]
}
```

## ✅ Success Indicators

### **Working Integration:**
- ✅ Cursor AI input box এ prompt লিখলে response আসে
- ✅ Response quality ভালো (Ollama model quality অনুযায়ী)
- ✅ Memory automatically save হয়
- ✅ Dashboard এ conversation history দেখা যায়

### **Performance:**
- **Response Time:** ~2-5 seconds (model dependent)
- **Memory Usage:** Local SQLite database
- **Uptime:** 24/7 (server running থাকলে)

## 🎉 Ready to Use!

এখন আপনি Cursor AI এর input box থেকে সরাসরি আপনার লোকাল Hello Zombie agent ব্যবহার করতে পারবেন। সব conversation automatically save হবে এবং dashboard এ monitor করতে পারবেন।

---

**Happy Coding with Hello Zombie! 🧟‍♂️💻**
