# ZombieCoder Family Agent 🧟‍♂️

A multi-service AI agent system with local model inference, proxy integration, and dual-layer memory management.

## System Architecture

```
┌─────────────────────────────────────────────┐
│         ZombieCoder Family Agent            │
├─────────────────────────────────────────────┤
│                                             │
│  Cursor AI / Editors / API Clients          │
│  │                                          │
│  └─→ Proxy (Port 5010)                      │
│       │ (Header filtering, logging)         │
│       │                                     │
│       └─→ Agent API (Port 8001)             │
│            │ (Message processing)           │
│            │                                │
│            ├─→ Local Model Server           │
│            │   (Port 8155/Ollama)           │
│            │   Model: deepseek-coder-1.3b  │
│            │                                │
│            ├─→ Memory System                │
│            │   ├─ JSON (fast access)        │
│            │   └─ SQLite (persistence)      │
│            │                                │
│            └─→ LangChain Pipeline           │
│                (Fallback system)            │
│                                             │
└─────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.12+
- Ollama with deepseek-coder-1.3b model loaded
- Git (for version control)

### Setup

1. **Clone/Download the project**
```bash
cd c:\Users\sahon\Desktop\ZombieCoder-Family-Agent
```

2. **Create virtual environment**
```bash
python -m venv zombiecoder_env
zombiecoder_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Check .env file
cat .env
```

Expected `.env` content:
```
AGENT_PORT=8001
OLLAMA_URL=http://127.0.0.1:8007
```

### Running Services

**Option 1: Start Agent Only**
```bash
python unified_agent_system.py
```
- Available at: `http://127.0.0.1:8001`
- Requires Model Server running separately

**Option 2: Start Full System**
```powershell
.\scripts\start_all_services.ps1
```
- Starts: Model Server (8155), Agent (8001), Proxy (5010)

**Option 3: Start Proxy with Agent**
```bash
# Terminal 1: Start Agent
python unified_agent_system.py

# Terminal 2: Start Proxy
python proxy_simple.py
```

## API Endpoints

### Agent Server (Port 8001)

**Chat Completion (OpenAI Compatible)**
```bash
POST /v1/chat/completions
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Hello, agent!"}
  ],
  "model": "deepseek-coder-1.3b",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

**Health Check**
```bash
GET /health
```

**Memory Statistics**
```bash
GET /memory_stats
```

### Proxy Server (Port 5010)

Intercepts and forwards requests to Agent Server on port 8001.

```bash
curl -X POST http://127.0.0.1:5010/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "test"}]}'
```

## Configuration Files

### `.env`
Environment variables for the system.

### `config/enhanced_zombiecoder_config.yaml`
Agent configuration:
- Model: deepseek-coder-1.3b
- Temperature: 0.7
- Max tokens: 2048
- Memory retention: 1000 conversations

### `config/proxy_config.json`
Proxy server configuration:
- Listen port: 5010
- Target: http://127.0.0.1:8001
- API key validation
- Header filtering

## Project Structure

```
c:\Users\sahon\Desktop\ZombieCoder-Family-Agent\
├── unified_agent_system.py        # Main agent server
├── proxy_simple.py                # Simplified proxy server
├── proxy_adapter.py               # Advanced proxy adapter
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables
├── .gitignore                     # Git ignore rules
├── config/
│   ├── enhanced_zombiecoder_config.yaml
│   ├── proxy_config.json
│   └── main_server_integration.py
├── scripts/
│   ├── start_all_services.ps1     # Service orchestrator
│   ├── start_proxy.ps1            # Proxy launcher
│   ├── start_proxy.py             # Proxy startup
│   ├── health_check.py            # System health check
│   └── verify_setup.ps1           # Setup verification
├── docs/                          # Documentation
│   ├── START_HERE_BANGLA.md
│   ├── EDITOR_SETUP_GUIDE.md
│   ├── COMPLETE_SETUP_CHECKLIST.md
│   ├── PROXY_SETUP_README.txt
│   ├── SERVICE_ORCHESTRATOR.md
│   └── ... (more guides)
├── memory/                        # JSON memory storage
├── data/
│   └── memory/                    # SQLite memory database
├── logs/                          # Service logs
└── zombiecoder_env/               # Python virtual environment
```

## Documentation

Complete documentation available in `docs/` folder:

- **Bangla Quick Start**: `docs/START_HERE_BANGLA.md`
- **Editor Setup**: `docs/EDITOR_SETUP_GUIDE.md`
- **Proxy Setup**: `docs/PROXY_SETUP_README.txt`
- **Complete Checklist**: `docs/COMPLETE_SETUP_CHECKLIST.md`
- **Service Orchestrator**: `docs/SERVICE_ORCHESTRATOR.md`
- **Quick Reference**: `docs/QUICK_REFERENCE.txt`

## Features

✅ **Multi-Service Architecture**
- Modular design with separate services
- Proxy for request interception
- Scalable configuration

✅ **Local Model Inference**
- Ollama integration
- Deepseek Coder 1.3B model
- Fallback to LangChain pipeline

✅ **Advanced Memory System**
- JSON for fast access
- SQLite for persistence
- Automatic cleanup (30-day retention)

✅ **OpenAI Compatible API**
- Standard `/v1/chat/completions` endpoint
- Compatible with Cursor AI, Continue.dev
- Drop-in replacement for OpenAI API

✅ **Comprehensive Logging**
- Service-specific logs
- Real-time monitoring
- Detailed error tracking

✅ **Multi-Language Support**
- Bangla + English
- Full Unicode support
- Windows-optimized

## Testing

### Health Check
```bash
curl http://127.0.0.1:8001/health
```

### Simple Message
```bash
curl -X POST http://127.0.0.1:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hello"}]}'
```

### Memory Statistics
```bash
curl http://127.0.0.1:8001/memory_stats
```

## Troubleshooting

### Port Already in Use
```bash
netstat -ano -p tcp | findstr ":8001"
taskkill /PID <PID> /F
```

### Agent Not Starting
1. Check Python: `python --version`
2. Check venv: `zombiecoder_env\Scripts\activate`
3. Check logs: `logs/agent.log`

### Model Server Not Responding
1. Verify Ollama running
2. Check model loaded: `curl http://127.0.0.1:8155/api/health`
3. Agent falls back to LangChain automatically

### Proxy Connection Issues
1. Verify Agent running: `curl http://127.0.0.1:8001/health`
2. Check proxy target: `cat config/proxy_config.json`
3. Review logs: `logs/proxy_adapter.log`

## Performance

**Typical Latency:**
- Health check: <100ms
- Simple message: 5-15 seconds
- Complex query: 15-30 seconds

**Resource Usage:**
- Agent Server: 150-250MB RAM
- Model Server: 200-300MB RAM
- Proxy Server: 30-50MB RAM

## Development

### Adding New Features
1. Update `unified_agent_system.py` for agent logic
2. Add endpoints to Flask app
3. Update documentation in `docs/`
4. Commit changes to git

### Debugging
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

Please ensure:
- Code follows PEP 8
- Documentation is updated
- All tests pass
- Git commits are descriptive

## License

This project is part of the ZombieCoder Family Agent ecosystem.

## Support

For issues or questions:
1. Check `docs/` for documentation
2. Review troubleshooting guide
3. Check logs for error details
4. Consult status reports in `docs/`

---

**Status**: ✅ Ready for Production
**Last Updated**: November 11, 2025
**Version**: 1.0.0
