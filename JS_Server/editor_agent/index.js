const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
require('dotenv').config();

const app = express();
const PORT = process.env.EDITOR_AGENT_PORT || process.env.EDITOR_PORT || 49110;

// File system tracking
const fileStructure = new Map();
const projectContext = {
    rootPath: process.env.PROJECT_ROOT || process.cwd(),
    lastScan: null,
    fileTypes: {
        code: ['.js', '.jsx', '.ts', '.tsx', '.py', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go', '.rs'],
        config: ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf', '.env'],
        assets: ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.css', '.scss', '.sass'],
        docs: ['.md', '.txt', '.rst', '.doc', '.docx', '.pdf']
    }
};

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({
        status: 'OK',
        service: 'ZombieCoder Editor Agent',
        timestamp: new Date().toISOString(),
        tracked_files: fileStructure.size,
        last_scan: projectContext.lastScan
    });
});

// Scan project structure
app.post('/api/editor/scan', (req, res) => {
    const { rootPath } = req.body;
    const scanPath = rootPath || projectContext.rootPath;

    try {
        const structure = scanDirectory(scanPath);
        fileStructure.clear();

        // Store structure in memory
        structure.forEach((fileInfo, filePath) => {
            fileStructure.set(filePath, fileInfo);
        });

        projectContext.lastScan = new Date().toISOString();
        projectContext.rootPath = scanPath;

        res.json({
            success: true,
            scanned_path: scanPath,
            total_files: fileStructure.size,
            structure: structure,
            timestamp: projectContext.lastScan,
            message: 'Project structure scanned successfully'
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to scan project structure',
            details: error.message
        });
    }
});

// Get file structure
app.get('/api/editor/structure', (req, res) => {
    const { type, path: filterPath } = req.query;

    let filteredStructure = Array.from(fileStructure.entries());

    if (type) {
        filteredStructure = filteredStructure.filter(([filePath, fileInfo]) => {
            return fileInfo.type === type;
        });
    }

    if (filterPath) {
        filteredStructure = filteredStructure.filter(([filePath, fileInfo]) => {
            return filePath.includes(filterPath);
        });
    }

    res.json({
        total_files: fileStructure.size,
        filtered_files: filteredStructure.length,
        structure: Object.fromEntries(filteredStructure),
        last_scan: projectContext.lastScan
    });
});

// Get specific file info
app.get('/api/editor/file/:filePath(*)', (req, res) => {
    const filePath = decodeURIComponent(req.params.filePath);

    if (!fileStructure.has(filePath)) {
        return res.status(404).json({ error: 'File not found in tracked structure' });
    }

    const fileInfo = fileStructure.get(filePath);

    // Read file content if it's a text file
    if (fileInfo.type === 'code' || fileInfo.type === 'config' || fileInfo.type === 'docs') {
        try {
            const content = fs.readFileSync(filePath, 'utf8');
            fileInfo.content = content;
            fileInfo.content_length = content.length;
        } catch (error) {
            fileInfo.content = null;
            fileInfo.content_error = error.message;
        }
    }

    res.json(fileInfo);
});

// Analyze code structure
app.post('/api/editor/analyze', (req, res) => {
    const { filePath, analysisType = 'functions' } = req.body;

    if (!fileStructure.has(filePath)) {
        return res.status(404).json({ error: 'File not found in tracked structure' });
    }

    const fileInfo = fileStructure.get(filePath);

    if (fileInfo.type !== 'code') {
        return res.status(400).json({ error: 'File is not a code file' });
    }

    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const analysis = analyzeCode(content, filePath, analysisType);

        res.json({
            file_path: filePath,
            analysis_type: analysisType,
            analysis: analysis,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to analyze code',
            details: error.message
        });
    }
});

// Generate code suggestions
app.post('/api/editor/suggest', (req, res) => {
    const { filePath, cursorPosition, context } = req.body;

    if (!fileStructure.has(filePath)) {
        return res.status(404).json({ error: 'File not found in tracked structure' });
    }

    const fileInfo = fileStructure.get(filePath);

    if (fileInfo.type !== 'code') {
        return res.status(400).json({ error: 'File is not a code file' });
    }

    try {
        const content = fs.readFileSync(filePath, 'utf8');
        const suggestions = generateCodeSuggestions(content, cursorPosition, context);

        res.json({
            file_path: filePath,
            cursor_position: cursorPosition,
            suggestions: suggestions,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to generate suggestions',
            details: error.message
        });
    }
});

// Update file
app.post('/api/editor/update', (req, res) => {
    const { filePath, content, backup = true } = req.body;

    if (!fileStructure.has(filePath)) {
        return res.status(404).json({ error: 'File not found in tracked structure' });
    }

    try {
        // Create backup if requested
        if (backup) {
            const backupPath = `${filePath}.backup.${Date.now()}`;
            fs.copyFileSync(filePath, backupPath);
        }

        // Update file
        fs.writeFileSync(filePath, content, 'utf8');

        // Update file info
        const fileInfo = fileStructure.get(filePath);
        fileInfo.last_modified = new Date().toISOString();
        fileInfo.content_length = content.length;
        fileInfo.content = content;

        res.json({
            success: true,
            file_path: filePath,
            content_length: content.length,
            last_modified: fileInfo.last_modified,
            message: 'File updated successfully'
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to update file',
            details: error.message
        });
    }
});

// Helper functions
function scanDirectory(dirPath, relativePath = '') {
    const structure = new Map();

    try {
        const items = fs.readdirSync(dirPath);

        for (const item of items) {
            const fullPath = path.join(dirPath, item);
            const relativeItemPath = path.join(relativePath, item);

            const stats = fs.statSync(fullPath);

            if (stats.isDirectory()) {
                // Skip node_modules, .git, etc.
                if (['node_modules', '.git', 'dist', 'build', '.next'].includes(item)) {
                    continue;
                }

                structure.set(relativeItemPath, {
                    type: 'directory',
                    name: item,
                    path: fullPath,
                    relative_path: relativeItemPath,
                    size: 0,
                    last_modified: stats.mtime.toISOString(),
                    children: []
                });

                // Recursively scan subdirectory
                const subStructure = scanDirectory(fullPath, relativeItemPath);
                subStructure.forEach((value, key) => structure.set(key, value));
            } else {
                const fileType = getFileType(item);
                structure.set(relativeItemPath, {
                    type: fileType,
                    name: item,
                    path: fullPath,
                    relative_path: relativeItemPath,
                    size: stats.size,
                    last_modified: stats.mtime.toISOString(),
                    extension: path.extname(item)
                });
            }
        }
    } catch (error) {
        console.error(`Error scanning directory ${dirPath}:`, error.message);
    }

    return structure;
}

function getFileType(filename) {
    const ext = path.extname(filename).toLowerCase();

    for (const [type, extensions] of Object.entries(projectContext.fileTypes)) {
        if (extensions.includes(ext)) {
            return type;
        }
    }

    return 'other';
}

function analyzeCode(content, filePath, analysisType) {
    const analysis = {
        functions: [],
        classes: [],
        imports: [],
        variables: [],
        comments: []
    };

    const lines = content.split('\n');

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // Function detection
        if (line.match(/function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\(|var\s+\w+\s*=\s*\(/)) {
            analysis.functions.push({
                line: i + 1,
                content: line,
                name: extractFunctionName(line)
            });
        }

        // Class detection
        if (line.match(/class\s+\w+/)) {
            analysis.classes.push({
                line: i + 1,
                content: line,
                name: extractClassName(line)
            });
        }

        // Import detection
        if (line.match(/import\s+|require\s*\(/)) {
            analysis.imports.push({
                line: i + 1,
                content: line
            });
        }

        // Comment detection
        if (line.match(/\/\/|\/\*|\*/)) {
            analysis.comments.push({
                line: i + 1,
                content: line
            });
        }
    }

    return analysis;
}

function extractFunctionName(line) {
    const match = line.match(/(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=)/);
    return match ? (match[1] || match[2]) : 'anonymous';
}

function extractClassName(line) {
    const match = line.match(/class\s+(\w+)/);
    return match ? match[1] : 'unknown';
}

function generateCodeSuggestions(content, cursorPosition, context) {
    // Simple code completion suggestions
    const suggestions = [];
    const lines = content.split('\n');
    const currentLine = lines[cursorPosition.line - 1] || '';

    // Common patterns
    if (currentLine.includes('if')) {
        suggestions.push('if (condition) {\n    // code here\n}');
    }

    if (currentLine.includes('function')) {
        suggestions.push('function name() {\n    // code here\n}');
    }

    if (currentLine.includes('const') || currentLine.includes('let')) {
        suggestions.push('const variableName = value;');
    }

    return suggestions;
}

// Provider information for Editor Agent
const editorProviderInfo = {
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

// System info endpoint for Editor Agent
app.get('/api/editor/system_info', (req, res) => {
    const codeFiles = Array.from(fileStructure.values()).filter(f => f.type === 'code');
    const configFiles = Array.from(fileStructure.values()).filter(f => f.type === 'config');
    const assetFiles = Array.from(fileStructure.values()).filter(f => f.type === 'assets');

    res.json({
        agent_name: 'Editor Agent',
        status: 'active',
        stats: {
            total_files: fileStructure.size,
            code_files: codeFiles.length,
            config_files: configFiles.length,
            asset_files: assetFiles.length,
            last_scan: projectContext.lastScan,
            project_root: projectContext.rootPath
        },
        capabilities: [
            'Real-time file scanning',
            'Code analysis and parsing',
            'File context fetching',
            'Inline code suggestions',
            'Memory integration',
            'Model integration',
            'Bengali language support'
        ],
        file_types: projectContext.fileTypes,
        provider_info: editorProviderInfo,
        endpoints: {
            health: 'GET /health',
            scan: 'POST /api/editor/scan',
            structure: 'GET /api/editor/structure',
            file_info: 'GET /api/editor/file/:filePath',
            context: 'GET /api/editor/context',
            analyze: 'POST /api/editor/analyze',
            suggest: 'POST /api/editor/suggest',
            update: 'POST /api/editor/update',
            system_info: 'GET /api/editor/system_info'
        }
    });
});

// Real-time file context fetch endpoint
app.get('/api/editor/context', (req, res) => {
    const { filePath, line = 1, window = 10 } = req.query;

    if (!filePath) {
        return res.status(400).json({ error: 'filePath parameter is required' });
    }

    if (!fileStructure.has(filePath)) {
        return res.status(404).json({ error: 'File not found in tracked structure' });
    }

    const fileInfo = fileStructure.get(filePath);

    if (fileInfo.type !== 'code') {
        return res.status(400).json({ error: 'File is not a code file' });
    }

    try {
        const content = fs.readFileSync(fileInfo.path, 'utf8');
        const lines = content.split('\n');
        const currentLine = parseInt(line);
        const startLine = Math.max(0, currentLine - window - 1);
        const endLine = Math.min(lines.length, currentLine + window);

        const context = {
            file_path: filePath,
            current_line: currentLine,
            total_lines: lines.length,
            context_lines: lines.slice(startLine, endLine),
            context_range: { start: startLine + 1, end: endLine },
            file_type: fileInfo.extension,
            last_modified: fileInfo.last_modified,
            size: fileInfo.size
        };

        res.json(context);
    } catch (error) {
        res.status(500).json({
            error: 'Failed to fetch file context',
            details: error.message
        });
    }
});

// Enhanced inline code suggestions with context awareness
app.post('/api/editor/suggest', async (req, res) => {
    const { filePath, cursorPosition, context, prompt } = req.body;

    if (!filePath || !cursorPosition) {
        return res.status(400).json({ error: 'filePath and cursorPosition are required' });
    }

    // Normalize file path for Windows
    const normalizedPath = filePath.replace(/\//g, '\\');

    // Try multiple path variations
    let fileInfo = fileStructure.get(normalizedPath);
    if (!fileInfo) {
        fileInfo = fileStructure.get(filePath);
    }
    if (!fileInfo) {
        fileInfo = fileStructure.get(filePath.replace(/\\/g, '/'));
    }
    if (!fileInfo) {
        fileInfo = fileStructure.get(filePath.replace(/\//g, '\\'));
    }

    if (!fileInfo) {
        return res.status(404).json({ error: 'File not found in tracked structure' });
    }

    if (fileInfo.type !== 'code') {
        return res.status(400).json({ error: 'File is not a code file' });
    }

    try {
        const content = fs.readFileSync(fileInfo.path, 'utf8');
        const lines = content.split('\n');
        const currentLine = cursorPosition.line - 1;
        const currentColumn = cursorPosition.column || 0;

        // Get context around cursor
        const contextWindow = 5;
        const startLine = Math.max(0, currentLine - contextWindow);
        const endLine = Math.min(lines.length, currentLine + contextWindow + 1);
        const contextLines = lines.slice(startLine, endLine);

        // Basic code completion suggestions
        const basicSuggestions = generateCodeSuggestions(content, cursorPosition, context);

        // If prompt is provided, use model for enhanced suggestions
        let modelSuggestions = [];
        if (prompt) {
            try {
                const API_GATEWAY_URL = process.env.API_GATEWAY_URL || 'http://127.0.0.1';
                const API_GATEWAY_PORT = process.env.API_GATEWAY_PORT || 49100;
                const gatewayUrl = `${API_GATEWAY_URL}:${API_GATEWAY_PORT}`;
                
                const modelResponse = await fetch(`${gatewayUrl}/api/ollama/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        messages: [{
                            role: 'user',
                            content: `File: ${filePath}\nContext:\n${contextLines.join('\n')}\n\nPrompt: ${prompt}\n\nProvide code suggestions for the current cursor position.`
                        }],
                        model: 'deepseek-coder:1.3b'
                    })
                });

                if (modelResponse.ok) {
                    const modelData = await modelResponse.json();
                    modelSuggestions = [modelData.message.content];
                }
            } catch (error) {
                console.error('Model suggestion error:', error.message);
            }
        }

        res.json({
            file_path: filePath,
            cursor_position: cursorPosition,
            context_lines: contextLines,
            basic_suggestions: basicSuggestions,
            model_suggestions: modelSuggestions,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            error: 'Failed to generate suggestions',
            details: error.message
        });
    }
});

// Default route
app.get('/', (req, res) => {
    res.json({
        message: 'ZombieCoder Editor Agent',
        version: '1.0.0',
        endpoints: {
            health: '/health',
            scan: 'POST /api/editor/scan',
            structure: 'GET /api/editor/structure',
            file_info: 'GET /api/editor/file/:filePath',
            context: 'GET /api/editor/context',
            analyze: 'POST /api/editor/analyze',
            suggest: 'POST /api/editor/suggest',
            update: 'POST /api/editor/update',
            system_info: 'GET /api/editor/system_info'
        },
        stats: {
            tracked_files: fileStructure.size,
            last_scan: projectContext.lastScan
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`📁 ZombieCoder Editor Agent running on port ${PORT}`);
    console.log(`📊 Tracked files: ${fileStructure.size}`);
    console.log(`📂 Project root: ${projectContext.rootPath}`);
});

// Error handling
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
});

process.on('unhandledRejection', (err) => {
    console.error('Unhandled Rejection:', err);
});
