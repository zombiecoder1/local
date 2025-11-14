# ZombieCoder Local AI System

This repository contains the local AI system setup for ZombieCoder, including the proxy server and agent configuration.

## Components

1. **Proxy Server** - Handles requests from editors (Cursor/Qoder) and forwards them to the local agent
2. **Agent Server** - Runs the AI models locally
3. **Configuration Files** - Settings for both proxy and agent

## Setup Instructions

1. Ensure Node.js is installed
2. Install dependencies: `npm install` in the Proxy Server directory
3. Start the proxy server: `node proxy_server_enforced.js`
4. Start the agent server according to its documentation

## Configuration

- **Proxy Port**: 5010
- **Agent Port**: 8001
- **Model**: microsoft/phi-2
- **Local Only**: Enabled

## Endpoints

- `/v1/models` - Lists available models
- `/v1/chat/completions` - Chat completions endpoint
- `/health` - Health check endpoint

## Scripts

- `start_all.ps1` - Starts both agent and proxy
- `git_commit_and_start.ps1` - Commits changes and starts services