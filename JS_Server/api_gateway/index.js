const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.API_GATEWAY_PORT || process.env.PORT || 5010;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({
        status: 'OK',
        service: 'ZombieCoder API Gateway',
        timestamp: new Date().toISOString(),
        language: 'bengali',
        ui_language: 'english'
    });
});

// API routes
app.get('/api/status', (req, res) => {
    res.json({
        status: 'running',
        version: '1.0.0',
        features: {
            ssl: process.env.SSL_ENABLED === 'true',
            proxy: process.env.PROXY_ENABLED === 'true',
            bengali_support: true
        }
    });
});

// Bengali language processing endpoint
app.post('/api/bengali/process', (req, res) => {
    const { text } = req.body;

    if (!text) {
        return res.status(400).json({ error: 'Text input required' });
    }

    // Simple Bengali text processing simulation
    const response = {
        original_text: text,
        processed_text: `প্রক্রিয়াকৃত: ${text}`,
        language: 'bengali',
        confidence: 0.95,
        timestamp: new Date().toISOString()
    };

    res.json(response);
});

// Natural question handling for agent identity
app.post('/api/agent/ask', async (req, res) => {
    const { question, agent_type = 'memory' } = req.body;

    if (!question) {
        return res.status(400).json({ error: 'Question is required' });
    }

    const questionLower = question.toLowerCase();
    let response = '';

    // Get provider info based on agent type
    let providerInfo = memoryProviderInfo;
    let agentName = 'Memory Agent';

    if (agent_type === 'editor') {
        providerInfo = {
            name: "ZombieCoder",
            tagline: "যেখানে কোড ও কথা বলে",
            owner: "Sahon Srabon",
            company: "Developer Zone",
            contact: "+880 1323-626282",
            address: "235 south pirarbag, Amtala Bazar, Mirpur -60 feet",
            planning_ideals: "chatgpt",
            version: "v1.0",
            creation_date: "2025-09-16",
            website: "https://zombiecoder.dev",
            email: "sahon@zombiecoder.dev"
        };
        agentName = 'Editor Agent';
    } else if (agent_type === 'ollama') {
        providerInfo = ollamaProviderInfo;
        agentName = 'Ollama Agent';
    }

    // Check if question contains Bengali characters
    const hasBengali = /[\u0980-\u09FF]/.test(question);

    // Handle different types of questions (English and Bengali)
    if (questionLower.includes('who created') || questionLower.includes('who made') || questionLower.includes('creator') ||
        question.includes('কে তৈরি') || question.includes('তৈরি করেছে') || question.includes('তৈরি করেছ') ||
        question.includes('আপনাকে কে তৈরি') || question.includes('তোমাকে কে তৈরি')) {
        response = `আমি ${agentName}, আমাকে তৈরি করেছে ${providerInfo.name}। Owner: ${providerInfo.owner}, Company: ${providerInfo.company}, Contact: ${providerInfo.contact}।`;
    } else if (questionLower.includes('who owns') || questionLower.includes('owner') ||
        question.includes('মালিক') || question.includes('মালিকানা') ||
        question.includes('আপনার মালিক') || question.includes('তোমার মালিক')) {
        response = `আমার Owner: ${providerInfo.owner}, Company: ${providerInfo.company}, Contact: ${providerInfo.contact}।`;
    } else if (questionLower.includes('contact') || questionLower.includes('phone') || questionLower.includes('number') ||
        question.includes('যোগাযোগ') || question.includes('নম্বর') || question.includes('ফোন') ||
        question.includes('আপনার যোগাযোগ') || question.includes('তোমার যোগাযোগ')) {
        response = `আমার Contact: ${providerInfo.contact}, Email: ${providerInfo.email}, Website: ${providerInfo.website}।`;
    } else if (questionLower.includes('company') || questionLower.includes('organization') ||
        question.includes('কোম্পানি') || question.includes('সংস্থা') ||
        question.includes('আপনার কোম্পানি') || question.includes('তোমার কোম্পানি')) {
        response = `আমার Company: ${providerInfo.company}, Address: ${providerInfo.address}।`;
    } else if (questionLower.includes('what are you') || questionLower.includes('who are you') ||
        question.includes('আপনি কে') || question.includes('তুমি কে') || question.includes('আমি কে') ||
        question.includes('আপনি কি') || question.includes('তুমি কি')) {
        response = `আমি ${agentName}, ${providerInfo.tagline}। আমি ${providerInfo.name} দ্বারা তৈরি, Owner: ${providerInfo.owner}।`;
    } else if (questionLower.includes('version') || questionLower.includes('v1') ||
        question.includes('ভার্সন') || question.includes('সংস্করণ') ||
        question.includes('আপনার ভার্সন') || question.includes('তোমার ভার্সন')) {
        response = `আমার Version: ${providerInfo.version}, Creation Date: ${providerInfo.creation_date}।`;
    } else if (hasBengali) {
        // For any other Bengali question, provide a general response
        response = `আমি ${agentName}, ${providerInfo.tagline}। আমি ${providerInfo.name} দ্বারা তৈরি। Owner: ${providerInfo.owner}, Company: ${providerInfo.company}, Contact: ${providerInfo.contact}।`;
    } else {
        // For complex questions, provide a general response with provider info
        response = `আমি ${agentName}, ${providerInfo.tagline}। আমি ${providerInfo.name} দ্বারা তৈরি। Owner: ${providerInfo.owner}, Company: ${providerInfo.company}, Contact: ${providerInfo.contact}।`;
    }

    res.json({
        agent: agentName,
        question: question,
        response: response,
        provider_info: providerInfo,
        timestamp: new Date().toISOString()
    });
});

// ZombieCoder Local AI Framework endpoint
app.post('/api/ollama/chat', async (req, res) => {
    const { messages, model = 'phi-2', prompt } = req.body;

    try {
        // Use /api/generate endpoint for ZombieCoder Local AI Framework
        const generatePayload = JSON.stringify({
            model: model,
            prompt: prompt || (messages && messages.length > 0 ? messages[messages.length - 1].content : ''),
            stream: false
        });

        const MODEL_SERVER_URL = process.env.MODEL_SERVER_URL || '127.0.0.1';
        const MODEL_PORT = process.env.MODEL_PORT || 8155;
        // Extract hostname from URL (remove http:// or https://)
        const hostname = MODEL_SERVER_URL.replace(/^https?:\/\//, '').replace(/:\d+$/, '');
        
        const options = {
            hostname: hostname,
            port: MODEL_PORT,
            path: '/api/generate',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(generatePayload)
            }
        };

        const zombiecoderRequest = http.request(options, (zombiecoderResponse) => {
            let data = '';

            zombiecoderResponse.on('data', (chunk) => {
                data += chunk;
            });

            zombiecoderResponse.on('end', () => {
                try {
                    const parsedData = JSON.parse(data);
                    res.json({
                        model: parsedData.model || model,
                        runtime_port: parsedData.runtime_port,
                        response: parsedData.runtime_response?.content || parsedData.response,
                        tokens_predicted: parsedData.runtime_response?.tokens_predicted,
                        tokens_evaluated: parsedData.runtime_response?.tokens_evaluated,
                        source: 'zombiecoder_local_ai',
                        provider: 'ZombieCoder Local AI Framework'
                    });
                } catch (parseError) {
                    res.status(500).json({
                        error: 'Failed to parse ZombieCoder response',
                        details: parseError.message
                    });
                }
            });
        });

        zombiecoderRequest.on('error', (error) => {
            res.status(500).json({
                error: 'ZombieCoder Local AI Framework request failed',
                details: error.message,
                suggestion: `Make sure ZombieCoder Local AI Framework is running on ${MODEL_SERVER_URL}:${MODEL_PORT}`
            });
        });

        zombiecoderRequest.write(generatePayload);
        zombiecoderRequest.end();
    } catch (error) {
        const MODEL_SERVER_URL = process.env.MODEL_SERVER_URL || '127.0.0.1';
        const MODEL_PORT = process.env.MODEL_PORT || 8155;
        res.status(500).json({
            error: 'ZombieCoder Local AI Framework request failed',
            details: error.message,
            suggestion: `Make sure ZombieCoder Local AI Framework is running on ${MODEL_SERVER_URL}:${MODEL_PORT}`
        });
    }
});

// ZombieCoder Local AI Framework models endpoint
app.get('/api/ollama/models', async (req, res) => {
    try {
        const MODEL_SERVER_URL = process.env.MODEL_SERVER_URL || 'http://127.0.0.1';
        const MODEL_PORT = process.env.MODEL_PORT || 8155;
        const modelBaseUrl = `${MODEL_SERVER_URL}:${MODEL_PORT}`;
        
        // Get installed models from ZombieCoder
        const installedResponse = await fetch(`${modelBaseUrl}/models/installed`);
        
        if (!installedResponse.ok) {
            throw new Error(`ZombieCoder API error: ${installedResponse.status}`);
        }

        const installedData = await installedResponse.json();
        
        // Also get available models
        const availableResponse = await fetch(`${modelBaseUrl}/models/available`);
        const availableData = availableResponse.ok ? await availableResponse.json() : { models: [] };

        res.json({
            installed_models: installedData.models || [],
            available_models: availableData.models || [],
            total_installed: installedData.total || 0,
            source: 'zombiecoder_local_ai',
            provider: 'ZombieCoder Local AI Framework'
        });
    } catch (error) {
        const MODEL_SERVER_URL = process.env.MODEL_SERVER_URL || 'http://127.0.0.1';
        const MODEL_PORT = process.env.MODEL_PORT || 8155;
        res.status(500).json({
            error: 'Failed to fetch ZombieCoder models',
            details: error.message,
            suggestion: `Make sure ZombieCoder Local AI Framework is running on ${MODEL_SERVER_URL}:${MODEL_PORT}`
        });
    }
});

// Provider information for Ollama Agent
const ollamaProviderInfo = {
    name: "ZombieCoder",
    tagline: "যেখানে কোড ও কথা বলে",
    owner: "Sahon Srabon",
    company: "Developer Zone",
    contact: "+880 1323-626282",
    address: "235 south pirarbag, Amtala Bazar, Mirpur -60 feet",
    planning_ideals: "chatgpt",
    version: "v1.0",
    creation_date: "2025-09-16",
    website: "https://zombiecoder.dev",
    email: "sahon@zombiecoder.dev"
};

// System info endpoint for ZombieCoder Local AI Agent
app.get('/api/ollama/system_info', async (req, res) => {
    try {
        const MODEL_SERVER_URL = process.env.MODEL_SERVER_URL || 'http://127.0.0.1';
        const MODEL_PORT = process.env.MODEL_PORT || 8155;
        const modelBaseUrl = `${MODEL_SERVER_URL}:${MODEL_PORT}`;
        
        // Get health status
        const healthResponse = await fetch(`${modelBaseUrl}/health`);
        const healthData = healthResponse.ok ? await healthResponse.json() : {};

        // Get installed models
        const modelsResponse = await fetch(`${modelBaseUrl}/models/installed`);
        const modelsData = modelsResponse.ok ? await modelsResponse.json() : { models: [] };

        // Get provider info
        const providerResponse = await fetch(`${modelBaseUrl}/provider/about`);
        const providerData = providerResponse.ok ? await providerResponse.json() : ollamaProviderInfo;

        res.json({
            agent_name: 'ZombieCoder Local AI Agent',
            status: healthData.status || 'active',
            server_info: {
                service: healthData.service,
                version: healthData.version,
                models_dir: healthData.models_dir,
                port: healthData.port,
                uptime_sec: healthData.uptime_sec
            },
            stats: {
                total_models: modelsData.total || 0,
                installed_models: modelsData.models || [],
                last_analysis: new Date().toISOString()
            },
            capabilities: [
                'Local model inference',
                'Bengali language support',
                'Code generation and analysis',
                'Chat completion',
                'Context-aware responses',
                '100% FREE - No API costs',
                'Completely offline',
                'Multi-model support (TinyLlama, Phi-2, Llama-3.2)'
            ],
            language_support: {
                bengali: true,
                english: true,
                code_languages: ['javascript', 'python', 'java', 'cpp', 'go', 'rust']
            },
            provider_info: providerData,
            endpoints: {
                chat: 'POST /api/ollama/chat',
                models: 'GET /api/ollama/models',
                system_info: 'GET /api/ollama/system_info',
                health: `GET ${modelBaseUrl}/health`,
                generate: `POST ${modelBaseUrl}/api/generate`
            }
        });
    } catch (error) {
        const MODEL_SERVER_URL = process.env.MODEL_SERVER_URL || 'http://127.0.0.1';
        const MODEL_PORT = process.env.MODEL_PORT || 8155;
        res.status(500).json({
            agent_name: 'ZombieCoder Local AI Agent',
            status: 'error',
            error: 'Failed to fetch ZombieCoder system info',
            details: error.message,
            suggestion: `Make sure ZombieCoder Local AI Framework is running on ${MODEL_SERVER_URL}:${MODEL_PORT}`,
            provider_info: ollamaProviderInfo
        });
    }
});

// OpenAI proxy endpoint (if API key provided)
app.post('/api/openai/chat', async (req, res) => {
    const { messages, model = 'gpt-3.5-turbo' } = req.body;

    if (!process.env.OPENAI_API_KEY) {
        return res.status(400).json({
            error: 'OpenAI API key not configured',
            message: 'Please set OPENAI_API_KEY in .env file'
        });
    }

    try {
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model,
                messages,
                max_tokens: 1000
            })
        });

        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: 'OpenAI API request failed', details: error.message });
    }
});

// Memory system endpoints
app.get('/api/memory/status', (req, res) => {
    res.json({
        status: 'active',
        type: 'session_memory',
        bengali_patterns: true,
        redis_connected: true
    });
});

// Provider information for Memory Agent
const memoryProviderInfo = {
    name: "ZombieCoder",
    tagline: "যেখানে কোড ও কথা বলে",
    owner: "Sahon Srabon",
    company: "Developer Zone",
    contact: "+880 1323-626282",
    address: "235 south pirarbag, Amtala Bazar, Mirpur -60 feet",
    planning_ideals: "chatgpt",
    version: "v1.0",
    creation_date: "2025-09-16",
    website: "https://zombiecoder.dev",
    email: "sahon@zombiecoder.dev"
};

// System info endpoint for Memory Agent
app.get('/api/memory/system_info', (req, res) => {
    const memoryCount = global.memoryStore ? global.memoryStore.size : 0;
    const memories = global.memoryStore ? Array.from(global.memoryStore.entries()) : [];

    res.json({
        agent_name: 'Memory Agent',
        status: 'active',
        stats: {
            total_memories: memoryCount,
            bengali_memories: memories.filter(([key, entry]) =>
                entry.language === 'bengali' ||
                /[\u0980-\u09FF]/.test(entry.note)
            ).length,
            last_update: memories.length > 0 ?
                Math.max(...memories.map(([key, entry]) => new Date(entry.timestamp).getTime())) : null
        },
        capabilities: [
            'Store memories with TTL',
            'Bengali text support',
            'Key-based retrieval',
            'Memory expiration',
            'Session tracking'
        ],
        provider_info: memoryProviderInfo,
        endpoints: {
            save: 'POST /api/memory/save',
            retrieve: 'GET /api/memory/retrieve/:key',
            list: 'GET /api/memory/list',
            delete: 'DELETE /api/memory/delete/:key',
            status: 'GET /api/memory/status',
            system_info: 'GET /api/memory/system_info'
        }
    });
});

// Memory storage endpoints
app.post('/api/memory/save', (req, res) => {
    const { note, key, ttl } = req.body;

    if (!note) {
        return res.status(400).json({
            error: 'Note content is required',
            message: 'Please provide note content in request body'
        });
    }

    const memoryKey = key || `memory_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const memoryEntry = {
        note,
        timestamp: new Date().toISOString(),
        ttl: ttl || null,
        language: 'bengali'
    };

    // Store in memory (in production, use Redis or database)
    if (!global.memoryStore) {
        global.memoryStore = new Map();
    }

    global.memoryStore.set(memoryKey, memoryEntry);

    res.json({
        success: true,
        key: memoryKey,
        note: memoryEntry.note,
        timestamp: memoryEntry.timestamp,
        ttl: memoryEntry.ttl,
        message: 'Memory saved successfully'
    });
});

app.get('/api/memory/retrieve/:key', (req, res) => {
    const { key } = req.params;

    if (!global.memoryStore) {
        return res.status(404).json({ error: 'Memory store not initialized' });
    }

    const entry = global.memoryStore.get(key);

    if (!entry) {
        return res.status(404).json({ error: 'Memory entry not found' });
    }

    // Check TTL
    if (entry.ttl) {
        const now = new Date();
        const stored = new Date(entry.timestamp);
        const diff = (now - stored) / 1000; // seconds

        if (diff > entry.ttl) {
            global.memoryStore.delete(key);
            return res.status(404).json({ error: 'Memory entry expired' });
        }
    }

    res.json({
        key,
        note: entry.note,
        timestamp: entry.timestamp,
        ttl: entry.ttl,
        language: entry.language
    });
});

app.get('/api/memory/list', (req, res) => {
    if (!global.memoryStore) {
        return res.json({ total_entries: 0, entries: [] });
    }

    const entries = Array.from(global.memoryStore.entries()).map(([key, entry]) => ({
        key,
        note: entry.note.substring(0, 100) + (entry.note.length > 100 ? '...' : ''),
        timestamp: entry.timestamp,
        ttl: entry.ttl
    }));

    res.json({
        total_entries: global.memoryStore.size,
        entries
    });
});

app.delete('/api/memory/delete/:key', (req, res) => {
    const { key } = req.params;

    if (!global.memoryStore) {
        return res.status(404).json({ error: 'Memory store not initialized' });
    }

    const deleted = global.memoryStore.delete(key);

    res.json({
        success: deleted,
        key,
        message: deleted ? 'Memory entry deleted successfully' : 'Memory entry not found'
    });
});

// Default route
app.get('/', (req, res) => {
    res.json({
        message: 'ZombieCoder Advanced System API Gateway',
        version: '1.0.0',
        endpoints: {
            health: '/health',
            status: '/api/status',
            bengali: '/api/bengali/process',
            ollama_chat: '/api/ollama/chat',
            ollama_models: '/api/ollama/models',
            openai: '/api/openai/chat',
            memory_status: '/api/memory/status',
            memory_save: 'POST /api/memory/save',
            memory_retrieve: 'GET /api/memory/retrieve/:key',
            memory_list: 'GET /api/memory/list',
            memory_delete: 'DELETE /api/memory/delete/:key'
        },
        language: 'bengali',
        ui_language: 'english',
        local_models: {
            ollama: process.env.MODEL_SERVER_URL ? `${process.env.MODEL_SERVER_URL}:${process.env.MODEL_PORT || 8155}` : 'http://127.0.0.1:8155',
            status: 'configured'
        }
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({
        error: 'Internal server error',
        message: 'Something went wrong!'
    });
});

// Start server
if (process.env.SSL_ENABLED === 'true' && process.env.SSL_CERT_PATH && process.env.SSL_KEY_PATH) {
    // HTTPS server
    try {
        const options = {
            key: fs.readFileSync(process.env.SSL_KEY_PATH),
            cert: fs.readFileSync(process.env.SSL_CERT_PATH)
        };

        https.createServer(options, app).listen(PORT, () => {
            console.log(`🚀 ZombieCoder API Gateway running on HTTPS port ${PORT}`);
            console.log(`📝 Language: Bengali (UI: English)`);
            console.log(`🔒 SSL: Enabled`);
        });
    } catch (error) {
        console.error('SSL setup failed, falling back to HTTP:', error.message);
        app.listen(PORT, () => {
            console.log(`🚀 ZombieCoder API Gateway running on HTTP port ${PORT}`);
            console.log(`📝 Language: Bengali (UI: English)`);
        });
    }
} else {
    // HTTP server
    app.listen(PORT, () => {
        console.log(`🚀 ZombieCoder API Gateway running on HTTP port ${PORT}`);
        console.log(`📝 Language: Bengali (UI: English)`);
        console.log(`🔒 SSL: Disabled`);
    });
}
