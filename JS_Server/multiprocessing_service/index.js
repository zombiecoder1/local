const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const { spawn, fork } = require('child_process');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.MULTIPROCESSING_SERVICE_PORT || process.env.MULTIPROCESSING_PORT || 50150;

// Process management
const activeProcesses = new Map();
const processQueue = [];

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({
        status: 'OK',
        service: 'ZombieCoder Multiprocessing Service',
        timestamp: new Date().toISOString(),
        active_processes: activeProcesses.size,
        queued_processes: processQueue.length
    });
});

// Process management endpoints
app.post('/api/process/spawn', (req, res) => {
    const { command, args = [], options = {}, processId } = req.body;

    if (!command) {
        return res.status(400).json({ error: 'Command is required' });
    }

    const id = processId || `process_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    try {
        const childProcess = spawn(command, args, {
            stdio: ['pipe', 'pipe', 'pipe'],
            ...options
        });

        const processInfo = {
            id,
            command,
            args,
            pid: childProcess.pid,
            startTime: new Date().toISOString(),
            status: 'running'
        };

        activeProcesses.set(id, {
            process: childProcess,
            info: processInfo
        });

        // Handle process events
        childProcess.on('exit', (code, signal) => {
            const proc = activeProcesses.get(id);
            if (proc) {
                proc.info.status = 'completed';
                proc.info.exitCode = code;
                proc.info.signal = signal;
                proc.info.endTime = new Date().toISOString();
            }
        });

        childProcess.on('error', (error) => {
            const proc = activeProcesses.get(id);
            if (proc) {
                proc.info.status = 'error';
                proc.info.error = error.message;
                proc.info.endTime = new Date().toISOString();
            }
        });

        res.json({
            success: true,
            processId: id,
            pid: childProcess.pid,
            status: 'spawned'
        });

    } catch (error) {
        res.status(500).json({
            error: 'Failed to spawn process',
            message: error.message
        });
    }
});

app.post('/api/process/fork', (req, res) => {
    const { scriptPath, args = [], processId } = req.body;

    if (!scriptPath) {
        return res.status(400).json({ error: 'Script path is required' });
    }

    const id = processId || `fork_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    try {
        const childProcess = fork(scriptPath, args);

        const processInfo = {
            id,
            scriptPath,
            args,
            pid: childProcess.pid,
            startTime: new Date().toISOString(),
            status: 'running'
        };

        activeProcesses.set(id, {
            process: childProcess,
            info: processInfo
        });

        // Handle process events
        childProcess.on('exit', (code, signal) => {
            const proc = activeProcesses.get(id);
            if (proc) {
                proc.info.status = 'completed';
                proc.info.exitCode = code;
                proc.info.signal = signal;
                proc.info.endTime = new Date().toISOString();
            }
        });

        childProcess.on('error', (error) => {
            const proc = activeProcesses.get(id);
            if (proc) {
                proc.info.status = 'error';
                proc.info.error = error.message;
                proc.info.endTime = new Date().toISOString();
            }
        });

        res.json({
            success: true,
            processId: id,
            pid: childProcess.pid,
            status: 'forked'
        });

    } catch (error) {
        res.status(500).json({
            error: 'Failed to fork process',
            message: error.message
        });
    }
});

app.get('/api/process/status/:processId', (req, res) => {
    const { processId } = req.params;
    const proc = activeProcesses.get(processId);

    if (!proc) {
        return res.status(404).json({ error: 'Process not found' });
    }

    res.json(proc.info);
});

app.post('/api/process/terminate/:processId', (req, res) => {
    const { processId } = req.params;
    const proc = activeProcesses.get(processId);

    if (!proc) {
        return res.status(404).json({ error: 'Process not found' });
    }

    try {
        proc.process.kill();
        proc.info.status = 'terminated';
        proc.info.endTime = new Date().toISOString();

        res.json({
            success: true,
            processId,
            status: 'terminated'
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to terminate process',
            message: error.message
        });
    }
});

app.get('/api/process/list', (req, res) => {
    const processes = Array.from(activeProcesses.values()).map(proc => proc.info);

    res.json({
        total_processes: activeProcesses.size,
        processes
    });
});

// Queue management
app.post('/api/queue/add', (req, res) => {
    const { task, priority = 0 } = req.body;

    if (!task) {
        return res.status(400).json({ error: 'Task is required' });
    }

    const queueItem = {
        id: `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        task,
        priority,
        addedAt: new Date().toISOString(),
        status: 'queued'
    };

    processQueue.push(queueItem);
    processQueue.sort((a, b) => b.priority - a.priority);

    res.json({
        success: true,
        taskId: queueItem.id,
        position: processQueue.findIndex(item => item.id === queueItem.id) + 1,
        totalInQueue: processQueue.length
    });
});

app.get('/api/queue/status', (req, res) => {
    res.json({
        total_tasks: processQueue.length,
        tasks: processQueue.map(item => ({
            id: item.id,
            priority: item.priority,
            addedAt: item.addedAt,
            status: item.status
        }))
    });
});

// Default route
app.get('/', (req, res) => {
    res.json({
        message: 'ZombieCoder Multiprocessing Service',
        version: '1.0.0',
        endpoints: {
            health: '/health',
            spawn_process: 'POST /api/process/spawn',
            fork_process: 'POST /api/process/fork',
            process_status: 'GET /api/process/status/:processId',
            terminate_process: 'POST /api/process/terminate/:processId',
            list_processes: 'GET /api/process/list',
            add_to_queue: 'POST /api/queue/add',
            queue_status: 'GET /api/queue/status'
        },
        stats: {
            active_processes: activeProcesses.size,
            queued_tasks: processQueue.length
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`⚡ ZombieCoder Multiprocessing Service running on port ${PORT}`);
    console.log(`🔄 Active processes: ${activeProcesses.size}`);
    console.log(`📋 Queued tasks: ${processQueue.length}`);
});

// Error handling
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (err) => {
    console.error('Unhandled Rejection:', err);
});
