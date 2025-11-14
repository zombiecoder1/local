const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
require('dotenv').config();

const app = express();
const PORT = process.env.MEMORY_SERVICE_PORT || process.env.MEMORY_PORT || 49120;

// In-memory storage (in production, use Redis or database)
const memoryStore = new Map();
const conversationHistory = new Map();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({
        status: 'OK',
        service: 'ZombieCoder Memory Service',
        timestamp: new Date().toISOString(),
        memory_entries: memoryStore.size,
        conversations: conversationHistory.size
    });
});

// Memory management endpoints
app.post('/api/memory/store', (req, res) => {
    const { key, value, ttl } = req.body;

    if (!key || value === undefined) {
        return res.status(400).json({ error: 'Key and value are required' });
    }

    const memoryEntry = {
        value,
        timestamp: new Date().toISOString(),
        ttl: ttl || null
    };

    memoryStore.set(key, memoryEntry);

    res.json({
        success: true,
        key,
        stored_at: memoryEntry.timestamp,
        ttl: memoryEntry.ttl
    });
});

app.get('/api/memory/retrieve/:key', (req, res) => {
    const { key } = req.params;
    const entry = memoryStore.get(key);

    if (!entry) {
        return res.status(404).json({ error: 'Memory entry not found' });
    }

    // Check TTL
    if (entry.ttl) {
        const now = new Date();
        const stored = new Date(entry.timestamp);
        const diff = (now - stored) / 1000; // seconds

        if (diff > entry.ttl) {
            memoryStore.delete(key);
            return res.status(404).json({ error: 'Memory entry expired' });
        }
    }

    res.json({
        key,
        value: entry.value,
        timestamp: entry.timestamp,
        ttl: entry.ttl
    });
});

app.delete('/api/memory/delete/:key', (req, res) => {
    const { key } = req.params;
    const deleted = memoryStore.delete(key);

    res.json({
        success: deleted,
        key,
        message: deleted ? 'Memory entry deleted' : 'Memory entry not found'
    });
});

app.get('/api/memory/list', (req, res) => {
    const entries = Array.from(memoryStore.entries()).map(([key, entry]) => ({
        key,
        timestamp: entry.timestamp,
        ttl: entry.ttl
    }));

    res.json({
        total_entries: memoryStore.size,
        entries
    });
});

// Conversation history endpoints
app.post('/api/conversation/store', (req, res) => {
    const { sessionId, messages } = req.body;

    if (!sessionId || !messages) {
        return res.status(400).json({ error: 'Session ID and messages are required' });
    }

    conversationHistory.set(sessionId, {
        messages,
        last_updated: new Date().toISOString()
    });

    res.json({
        success: true,
        sessionId,
        message_count: messages.length,
        last_updated: conversationHistory.get(sessionId).last_updated
    });
});

app.get('/api/conversation/retrieve/:sessionId', (req, res) => {
    const { sessionId } = req.params;
    const conversation = conversationHistory.get(sessionId);

    if (!conversation) {
        return res.status(404).json({ error: 'Conversation not found' });
    }

    res.json({
        sessionId,
        messages: conversation.messages,
        last_updated: conversation.last_updated
    });
});

// Default route
app.get('/', (req, res) => {
    res.json({
        message: 'ZombieCoder Memory Service',
        version: '1.0.0',
        endpoints: {
            health: '/health',
            memory_store: 'POST /api/memory/store',
            memory_retrieve: 'GET /api/memory/retrieve/:key',
            memory_delete: 'DELETE /api/memory/delete/:key',
            memory_list: 'GET /api/memory/list',
            conversation_store: 'POST /api/conversation/store',
            conversation_retrieve: 'GET /api/conversation/retrieve/:sessionId'
        },
        stats: {
            memory_entries: memoryStore.size,
            conversations: conversationHistory.size
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🧠 ZombieCoder Memory Service running on port ${PORT}`);
    console.log(`📊 Memory entries: ${memoryStore.size}`);
    console.log(`💬 Conversations: ${conversationHistory.size}`);
});

// Error handling
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (err) => {
    console.error('Unhandled Rejection:', err);
});
