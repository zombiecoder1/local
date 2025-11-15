# ZombieCoder System Dashboard

Real-time monitoring dashboard for the ZombieCoder AI system.

## Features

- Real-time status monitoring of all services
- WebSocket-based live updates
- Visual indicators for service status
- Detailed response information
- Agent live reply simulation

## Services Monitored

1. **Proxy Server** (Port: 5051)
2. **API Gateway** (Port: 5050)
3. **Python Agent** (Port: 8001)
4. **Ollama Model Server** (Port: 8007)

## Installation

```bash
cd dashboard
npm install
```

## Running the Dashboard

```bash
cd dashboard
npm start
```

The dashboard will be available at: http://localhost:3000

## Development

For development with auto-restart:

```bash
cd dashboard
npm run dev
```

## How It Works

1. The dashboard server runs on port 3000
2. It connects to all ZombieCoder services via HTTP requests
3. WebSocket connection provides real-time updates to the frontend
4. The frontend displays service status with visual indicators
5. Agent replies are simulated for demonstration purposes

## Service Endpoints

- Proxy Server: http://localhost:5051/v1/models
- API Gateway: http://localhost:5050/health
- Python Agent: http://localhost:8001/v1/agent/info
- Ollama Model Server: http://localhost:8007/api/tags

## Directory Structure

```
dashboard/
├── server.js          # Backend server with WebSocket
├── package.json       # Dependencies and scripts
├── README.md          # This file
└── public/
    └── index.html     # Dashboard frontend
```