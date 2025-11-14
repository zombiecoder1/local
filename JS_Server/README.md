# ZombieCoder JS Server - Portable Edition

## 🚀 Quick Start

### 1. Extract ZIP
```bash
# Extract JS_Server_Portable.zip to any location
unzip JS_Server_Portable.zip
cd JS Server
```

### 2. Setup Environment
```bash
# Copy .env template
cp ../ENV_CONFIG.md .env

# Edit .env file with your configuration
notepad .env
```

### 3. Install Dependencies
```bash
# Install for each service
cd api_gateway && npm install
cd ../editor_agent && npm install
cd ../memory_service && npm install
cd ../multiprocessing_service && npm install
```

### 4. Start Services
```bash
# Start API Gateway
cd api_gateway && node index.js

# Start Editor Agent
cd ../editor_agent && node index.js

# Start Memory Service
cd ../memory_service && node index.js

# Start Multiprocessing Service
cd ../multiprocessing_service && node index.js
```

## 📦 Services

### API Gateway (Port 49100)
- Main entry point for all requests
- Routes to agents and services
- Environment: `API_GATEWAY_PORT=49100`

### Editor Agent (Port 49110)
- File scanning and code analysis
- Editor suggestions
- Environment: `EDITOR_AGENT_PORT=49110`

### Memory Service (Port 49120)
- Memory management
- Conversation history
- Environment: `MEMORY_SERVICE_PORT=49120`

### Multiprocessing Service (Port 50150)
- Process management
- Task queue
- Environment: `MULTIPROCESSING_SERVICE_PORT=50150`

## 🔧 Configuration

### Environment Variables
```env
MODEL_SERVER_URL=http://127.0.0.1
MODEL_PORT=8155
API_GATEWAY_PORT=49100
EDITOR_AGENT_PORT=49110
MEMORY_SERVICE_PORT=49120
MULTIPROCESSING_SERVICE_PORT=50150
```

### Port Configuration
- All ports from `port.md` safe port list
- Configurable via `.env` file
- Windows and Linux compatible

## 🧪 Testing

### Health Checks
```bash
# API Gateway
curl http://localhost:49100/health

# Editor Agent
curl http://localhost:49110/health

# Memory Service
curl http://localhost:49120/health

# Multiprocessing Service
curl http://localhost:50150/health
```

## 📚 Documentation

- See `../Server setup.html` for complete documentation
- See `../model_server.html` for Model Server API
- See `../port.md` for port mapping

## ✅ Checklist

- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Model Server running
- [ ] Services started
- [ ] Health checks passing

