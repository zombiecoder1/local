const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const path = require('path');
const fetch = require('node-fetch');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

const PORT = 3000;

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'Dashboard Server' });
});

// API endpoint to get service status
app.get('/api/status', async (req, res) => {
  const status = await checkAllServices();
  res.json(status);
});

// Function to check all services
async function checkAllServices() {
  const services = {
    proxy: { port: 5051, url: 'http://127.0.0.1:5051/v1/models', name: 'Proxy Server' },
    gateway: { port: 5050, url: 'http://127.0.0.1:5050/health', name: 'API Gateway' },
    agent: { port: 8001, url: 'http://127.0.0.1:8001/v1/agent/info', name: 'Python Agent' },
    model: { port: 8007, url: 'http://127.0.0.1:8007/api/tags', name: 'Ollama Model Server' }
  };

  const results = {};

  for (const [key, service] of Object.entries(services)) {
    try {
      const response = await fetch(service.url, { 
        method: 'GET',
        timeout: 5000
      });
      
      results[key] = {
        port: service.port,
        status: response.ok ? 'OK' : 'ERROR',
        response: response.ok ? await response.json() : { error: `HTTP ${response.status}` },
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      results[key] = {
        port: service.port,
        status: 'ERROR',
        response: { error: error.message },
        timestamp: new Date().toISOString()
      };
    }
  }

  return results;
}

// WebSocket connection
io.on('connection', (socket) => {
  console.log('Client connected');
  
  // Send initial status
  checkAllServices().then(status => {
    socket.emit('statusUpdate', status);
  });

  // Periodically send updates
  const interval = setInterval(async () => {
    const status = await checkAllServices();
    socket.emit('statusUpdate', status);
  }, 5000);

  socket.on('disconnect', () => {
    console.log('Client disconnected');
    clearInterval(interval);
  });
});

server.listen(PORT, () => {
  console.log(`Dashboard server running on http://localhost:${PORT}`);
});