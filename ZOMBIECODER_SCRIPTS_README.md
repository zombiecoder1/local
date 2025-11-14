# ZombieCoder Local Agent System Scripts

This directory contains PowerShell scripts to manage the complete ZombieCoder local agent system according to the official directive.

## Scripts Overview

### 1. `setup_proxy.ps1`
Sets up the proxy server environment:
- Ensures Proxy Server directory exists at `C:\Users\sahon\local\Proxy Server`
- Initializes git repository if needed
- Installs required Node.js dependencies

### 2. `setup_agent.ps1`
Sets up the Python agent environment:
- Creates Python virtual environment if needed
- Activates virtual environment
- Installs Python requirements

### 3. `start_all.ps1`
Starts all services in the correct order:
1. Commits changes with git
2. Starts Python agent
3. Waits 3 seconds
4. Starts Proxy Server

### 4. `health_check_auto.ps1`
Performs automated health checks:
- Verifies ports 5010 and 8001 are listening
- Checks health endpoints
- Validates model endpoints

### 5. `auto_repair.ps1`
Attempts to repair common issues:
- Checks required directories and files
- Installs missing dependencies
- Verifies virtual environment

### 6. `validate_config.ps1`
Validates editor configuration:
- Checks VS Code/Cursor settings
- Verifies API base URL, model, and API key
- Validates system endpoints

### 7. `zombiecoder_start.ps1`
Unified startup script with comprehensive features:
- Complete implementation of the official directive
- Process checking to avoid duplicates
- Detailed status reporting
- Optional flags to skip git or health checks

## Usage Instructions

### Initial Setup
```powershell
# Run these scripts once to set up the environment
.\setup_proxy.ps1
.\setup_agent.ps1
```

### Starting the System
```powershell
# Start everything with full health check
.\zombiecoder_start.ps1

# Start without git commit
.\zombiecoder_start.ps1 -NoGit

# Start without health check
.\zombiecoder_start.ps1 -NoHealthCheck
```

### Maintenance
```powershell
# Run health check
.\health_check_auto.ps1

# Run auto repair
.\auto_repair.ps1

# Validate configuration
.\validate_config.ps1
```

## System Requirements
- Windows PowerShell 5.1 or later
- Node.js 14+ installed
- Python 3.8+ installed
- Git installed and in PATH

## Directory Structure
```
C:\Users\sahon\local\
├── Proxy Server\
│   ├── proxy_server_enforced.js
│   ├── proxy_server.js
│   └── package.json
├── setup_proxy.ps1
├── setup_agent.ps1
├── start_all.ps1
├── health_check_auto.ps1
├── auto_repair.ps1
├── validate_config.ps1
└── zombiecoder_start.ps1
```

## Ports
- Agent: `http://127.0.0.1:8001`
- Proxy: `http://127.0.0.1:5010`

## Endpoints
- `/health` - Health check for both services
- `/v1/models` - Model listing (proxy shim)
- `/v1/models/microsoft/phi-2` - Specific model details (proxy shim)
- `/v1/chat/completions` - Chat completions (OpenAI-compatible)

## Editor Configuration
Set your editor settings to:
- Base URL: `http://127.0.0.1:5010/v1`
- Model: `microsoft/phi-2`
- API Key: (leave empty)