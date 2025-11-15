# ZombieCoder Dashboard Usage Guide

## 🚀 Quick Start

1. Ensure all ZombieCoder services are running:
   - Proxy Server (Port: 5051)
   - API Gateway (Port: 5050)
   - Python Agent (Port: 8001)
   - Ollama Model Server (Port: 8007)

2. Start the dashboard:
   ```
   cd dashboard
   npm start
   ```

3. Open your browser and go to: http://localhost:3000

## 📊 Dashboard Features

### Real-time Service Monitoring
The dashboard provides real-time status updates for all ZombieCoder services with 5-second refresh intervals.

### Visual Status Indicators
- 🟢 Green dot: Service is running correctly
- 🔴 Red dot: Service is down or unreachable

### Detailed Service Information
Each service card displays:
- Service name and port
- Current status
- Detailed response JSON
- Last update timestamp

### Agent Live Reply Simulation
The bottom section simulates live agent replies to demonstrate WebSocket functionality.

## 🛠️ Technical Details

### Backend Architecture
- Node.js server with Express.js
- WebSocket support using Socket.IO
- REST API endpoints for service status
- Periodic service health checks

### Frontend Features
- Responsive HTML/CSS design
- Real-time updates via WebSocket
- JSON response visualization
- Service status indicators

### Services Monitored
1. **Proxy Server** (`http://localhost:5051`)
   - Endpoint: `/v1/models`
   - Purpose: Editor compatibility layer

2. **API Gateway** (`http://localhost:5050`)
   - Endpoint: `/health`
   - Purpose: Central request routing

3. **Python Agent** (`http://localhost:8001`)
   - Endpoint: `/v1/agent/info`
   - Purpose: AI processing and logic

4. **Ollama Model Server** (`http://localhost:8007`)
   - Endpoint: `/api/tags`
   - Purpose: Local AI model hosting

## 🐍 Service Check Script

A Python script is included to verify all services are running:

```bash
python check_services.py
```

This script will:
- Check each service endpoint
- Display status with visual indicators
- Save detailed results to `service_status.json`

## 📁 Directory Structure

```
dashboard/
├── server.js              # Main server application
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── README.md              # Setup instructions
├── USAGE.md               # This file
├── start_dashboard.bat    # Windows startup script
├── check_services.py      # Service verification script
├── service_status.json    # Generated service status report
└── public/
    └── index.html         # Dashboard frontend
```

## ⚙️ Customization

### Changing Update Interval
Modify the interval in `server.js`:
```javascript
// Currently set to 5000ms (5 seconds)
const interval = setInterval(async () => {
  const status = await checkAllServices();
  socket.emit('statusUpdate', status);
}, 5000);
```

### Adding New Services
Add new services to the `SERVICES` object in `server.js`:
```javascript
const services = {
  // ... existing services
  newService: { port: 9000, url: 'http://127.0.0.1:9000/health' }
};
```

## 📞 WebSocket API

### Events

**Server to Client:**
- `statusUpdate` - Sends updated service status information

**Client to Server:**
- None (dashboard is read-only)

### Data Structure
```json
{
  "proxy": {
    "port": 5051,
    "status": "OK",
    "response": { ... },
    "timestamp": "2025-..."
  },
  // ... other services
}
```

## 🐛 Troubleshooting

### Dashboard Not Loading
1. Check if the dashboard server is running
2. Verify no port conflicts on port 3000
3. Ensure all required services are running

### Service Shows Error
1. Run `python check_services.py` to diagnose issues
2. Check if the specific service is running
3. Verify service ports match configuration

### WebSocket Connection Issues
1. Check browser console for errors
2. Verify dashboard server is accessible
3. Ensure no firewall blocking WebSocket connections

## 🔧 Development

### Adding New Features
1. Modify `public/index.html` for frontend changes
2. Update `server.js` for backend functionality
3. Restart the server to apply changes

### Auto-restart Development Server
```bash
npm run dev
```

This uses nodemon to automatically restart the server when files change.