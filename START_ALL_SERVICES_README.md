# ZombieCoder - Start All Services

This directory contains scripts to start all ZombieCoder AI system services at once.

## 📋 Services Included

1. **API Gateway** (Port: 5050)
2. **Proxy Server** (Port: 5051)
3. **Python Agent** (Port: 8001)
4. **Dashboard** (Port: 3000)
5. **Ollama Model Server** (Port: 8007) - Manual start required

## 🚀 Usage

### Option 1: Batch File (Recommended)
```batch
START_ALL_SERVICES.bat
```

Features:
- Starts each service in a separate CMD window
- Visual feedback for each startup step
- Manual window management

## ⚙️ Prerequisites

Before running these scripts, ensure you have:

1. **Node.js** installed
2. **Python 3.10+** installed
3. All dependencies installed:
   ```bash
   # Install Node.js dependencies
   cd JS_Server\api_gateway && npm install
   cd ..\..\Proxy Server && npm install
   cd ..\dashboard && npm install
   
   # Install Python dependencies
   pip install -r requirements.txt
   ```

4. **Ollama** installed and models downloaded:
   ```bash
   ollama pull phi-2
   ollama pull tinyllama
   ```

## 📁 Directory Structure

```
Root/
├── JS_Server/
│   └── api_gateway/          # API Gateway service
├── Proxy Server/             # Proxy server
├── dashboard/                # Dashboard service
├── start_agent.py            # Python agent starter
├── START_ALL_SERVICES.bat    # Batch script to start all services
└── START_ALL_SERVICES_README.md  # This file
```

## 🛠️ Script Details

### Batch Script (`START_ALL_SERVICES.bat`)
- Starts each service in a separate CMD window
- Visual step-by-step startup
- Manual window management
- Simple and straightforward

## 🌐 Access Services

After starting all services:

- **API Gateway**: http://localhost:5050
- **Proxy Server**: http://localhost:5051
- **Python Agent**: http://localhost:8001
- **Dashboard**: http://localhost:3000

## ⚠️ Important Notes

1. **Ollama Server**: The Ollama Model Server (port 8007) must be started manually:
   ```bash
   ollama serve
   ```

2. **Port Conflicts**: If services are already running, the scripts will detect and skip them.

3. **Dependencies**: Ensure all Node.js and Python dependencies are installed before running.

4. **Windows Only**: These scripts are designed for Windows environments.

## 🛑 Stopping Services

### Batch Script
- Close each service window individually
- Or use Task Manager to end processes

## 📞 Troubleshooting

### Services Not Starting
1. Check if ports are already in use
2. Verify all dependencies are installed
3. Check console output for error messages

### Port Conflicts
1. Use `netstat -ano | findstr :<port>` to check port usage
2. Kill conflicting processes with `taskkill /PID <pid> /F`

### Dependency Issues
1. Reinstall Node.js dependencies in each service directory
2. Reinstall Python dependencies with `pip install -r requirements.txt`