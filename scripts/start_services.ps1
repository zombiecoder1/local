#!/usr/bin/env pwsh
# ZombieCoder Services Startup Script
# Usage: .\scripts\start_services.ps1 [-All] [-Gateway] [-Agent] [-Editor] [-Memory] [-Multiprocessing]

param(
    [switch]$All,
    [switch]$Gateway,
    [switch]$Agent,
    [switch]$Editor,
    [switch]$Memory,
    [switch]$Multiprocessing
)

$ErrorActionPreference = "Stop"
$basePath = "C:\Users\sahon\local"

Write-Host "`n=== ZombieCoder Services Startup ===" -ForegroundColor Cyan
Write-Host "Base Path: $basePath`n" -ForegroundColor Gray

# Function to start service in new window
function Start-ServiceInWindow {
    param(
        [string]$ServiceName,
        [string]$WorkingDirectory,
        [string]$Command,
        [string]$Arguments = ""
    )
    
    Write-Host "Starting $ServiceName..." -ForegroundColor Yellow
    
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = "pwsh"
    $processInfo.Arguments = "-NoExit -Command `"cd '$WorkingDirectory'; $Command $Arguments`""
    $processInfo.UseShellExecute = $true
    $processInfo.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Normal
    
    $process = [System.Diagnostics.Process]::Start($processInfo)
    
    if ($process) {
        Write-Host "✅ $ServiceName started (PID: $($process.Id))" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        Write-Host "❌ Failed to start $ServiceName" -ForegroundColor Red
    }
}

# Start API Gateway
if ($All -or $Gateway) {
    $gatewayPath = Join-Path $basePath "JS_Server\api_gateway"
    
    if (-not (Test-Path $gatewayPath)) {
        Write-Host "❌ API Gateway path not found: $gatewayPath" -ForegroundColor Red
    } else {
        Set-Location $gatewayPath
        
        # Create .env if not exists
        if (-not (Test-Path ".env")) {
            Write-Host "Creating .env file for API Gateway..." -ForegroundColor Yellow
            @"
PORT=5010
API_GATEWAY_PORT=5010
NODE_ENV=production
TARGET_AGENT=http://127.0.0.1:8001
AGENT_URL=http://127.0.0.1:8001
SSL_ENABLED=false
PROXY_ENABLED=true
CORS_ORIGINS=http://localhost:3000,http://localhost:8001,vscode://
LOG_LEVEL=info
"@ | Out-File -FilePath ".env" -Encoding UTF8
        }
        
        # Install dependencies if needed
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing API Gateway dependencies..." -ForegroundColor Yellow
            npm ci
        }
        
        Start-ServiceInWindow -ServiceName "API Gateway" -WorkingDirectory $gatewayPath -Command "node index.js"
    }
}

# Start Python Agent
if ($All -or $Agent) {
    $agentPath = $basePath
    
    if (-not (Test-Path (Join-Path $agentPath "venv\Scripts\python.exe"))) {
        Write-Host "❌ Python virtual environment not found" -ForegroundColor Red
    } else {
        Set-Location $agentPath
        
        # Activate venv and start agent
        $venvPython = Join-Path $agentPath "venv\Scripts\python.exe"
        Start-ServiceInWindow -ServiceName "Python Agent" -WorkingDirectory $agentPath -Command $venvPython -Arguments "unified_agent_system.py"
    }
}

# Start Editor Agent
if ($All -or $Editor) {
    $editorPath = Join-Path $basePath "JS_Server\editor_agent"
    
    if (-not (Test-Path $editorPath)) {
        Write-Host "⚠️ Editor Agent path not found: $editorPath" -ForegroundColor Yellow
    } else {
        Set-Location $editorPath
        
        # Create .env if not exists
        if (-not (Test-Path ".env")) {
            @"
PORT=49110
EDITOR_AGENT_PORT=49110
NODE_ENV=production
LOG_LEVEL=info
"@ | Out-File -FilePath ".env" -Encoding UTF8
        }
        
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing Editor Agent dependencies..." -ForegroundColor Yellow
            npm ci
        }
        
        Start-ServiceInWindow -ServiceName "Editor Agent" -WorkingDirectory $editorPath -Command "node index.js"
    }
}

# Start Memory Service
if ($All -or $Memory) {
    $memoryPath = Join-Path $basePath "JS_Server\memory_service"
    
    if (-not (Test-Path $memoryPath)) {
        Write-Host "⚠️ Memory Service path not found: $memoryPath" -ForegroundColor Yellow
    } else {
        Set-Location $memoryPath
        
        # Create .env if not exists
        if (-not (Test-Path ".env")) {
            @"
PORT=49120
MEMORY_SERVICE_PORT=49120
NODE_ENV=production
LOG_LEVEL=info
"@ | Out-File -FilePath ".env" -Encoding UTF8
        }
        
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing Memory Service dependencies..." -ForegroundColor Yellow
            npm ci
        }
        
        Start-ServiceInWindow -ServiceName "Memory Service" -WorkingDirectory $memoryPath -Command "node index.js"
    }
}

# Start Multiprocessing Service
if ($All -or $Multiprocessing) {
    $multiprocessingPath = Join-Path $basePath "JS_Server\multiprocessing_service"
    
    if (-not (Test-Path $multiprocessingPath)) {
        Write-Host "⚠️ Multiprocessing Service path not found: $multiprocessingPath" -ForegroundColor Yellow
    } else {
        Set-Location $multiprocessingPath
        
        # Create .env if not exists
        if (-not (Test-Path ".env")) {
            @"
PORT=50150
MULTIPROCESSING_SERVICE_PORT=50150
NODE_ENV=production
LOG_LEVEL=info
"@ | Out-File -FilePath ".env" -Encoding UTF8
        }
        
        if (-not (Test-Path "node_modules")) {
            Write-Host "Installing Multiprocessing Service dependencies..." -ForegroundColor Yellow
            npm ci
        }
        
        Start-ServiceInWindow -ServiceName "Multiprocessing Service" -WorkingDirectory $multiprocessingPath -Command "node index.js"
    }
}

# Default: Start all if no flags specified
if (-not ($All -or $Gateway -or $Agent -or $Editor -or $Memory -or $Multiprocessing)) {
    Write-Host "No service specified. Starting all services..." -ForegroundColor Yellow
    & $MyInvocation.MyCommand.Path -All
    exit
}

Write-Host "`n=== Services Started ===" -ForegroundColor Green
Write-Host "Waiting 5 seconds for services to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Quick health check
Write-Host "`n=== Quick Health Check ===" -ForegroundColor Cyan
try {
    $gatewayHealth = Invoke-WebRequest -Uri "http://127.0.0.1:5010/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($gatewayHealth.StatusCode -eq 200) {
        Write-Host "✅ API Gateway: Healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ API Gateway: Not responding yet (may need more time)" -ForegroundColor Yellow
}

try {
    $agentHealth = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($agentHealth.StatusCode -eq 200) {
        Write-Host "✅ Python Agent: Healthy" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Python Agent: Not responding yet (may need more time)" -ForegroundColor Yellow
}

Write-Host "`n=== Done ===" -ForegroundColor Green
Write-Host "All services started in separate windows." -ForegroundColor Gray
Write-Host "Check each window for service status." -ForegroundColor Gray

