# ZombieCoder Portable Edition

Complete ZombieCoder project that can run on any computer.

## Installation (Windows)

### Method 1: Automatic Setup (Easiest)
1. Double-click 'SETUP.bat'
2. Wait for Python environment to be created
3. All packages will be installed automatically

### Method 2: Manual Setup (PowerShell)
```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

## Running the System

### Terminal 1: Start Backend Server
```powershell
.\venv\Scripts\Activate.ps1
python unified_agent_system.py
```
Server runs on port 8001

### Terminal 2: Start Proxy (new window)
```powershell
.\venv\Scripts\Activate.ps1
python proxy_simple.py
```
Proxy runs on port 5010

## API Endpoints

- Chat Completions: POST http://localhost:5010/v1/chat/completions
- Ollama API: POST http://localhost:5010/api/ollama/completion
- Health Check: GET http://localhost:5010/health
- Agent Info: GET http://localhost:8001/v1/agent/info

## Folder Structure

```
ZombieCoder-Portable/
├── unified_agent_system.py    # Backend server
├── proxy_simple.py             # Proxy server
├── requirements.txt            # Python packages
├── config/                     # Configuration files
├── scripts/                    # Helper scripts
├── logs/                       # Log files
└── SETUP.bat                   # Automatic setup
```

## Troubleshooting

### Python Not Found
1. Download Python 3.10+ from https://www.python.org
2. Check 'Add Python to PATH' during installation

### Port Already in Use
Edit config/proxy_config.json to change port number

### Dependency Issues
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## Version Information

- Project: ZombieCoder Family Agent
- Edition: Portable
- Required Python: 3.10+
- Created: 2025-11-11 10:10:58

## Support

For issues or suggestions, check the documentation or README files.
