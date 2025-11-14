#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start ZombieCoder Proxy Adapter for Cursor AI integration
.DESCRIPTION
    This script starts the proxy server on port 5010 that intercepts all Cursor AI calls
    and routes them to the local ZombieCoder Agent on port 8001.
#>

param(
    [switch]$Force,
    [switch]$NoActivate
)

$ErrorActionPreference = "Stop"

# Get project root
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot "zombiecoder_env"
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"

Write-Host @"
╔════════════════════════════════════════════════════════════╗
║   ZombieCoder Proxy Adapter - Startup Script               ║
║   Purpose: Intercept Cursor AI calls → Route to Agent      ║
╚════════════════════════════════════════════════════════════╝
"@ -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "❌ Virtual environment not found at: $VenvPath" -ForegroundColor Red
    Write-Host "Please run full_auto_install.ps1 first" -ForegroundColor Yellow
    exit 1
}

# Activate venv
if (-not $NoActivate) {
    Write-Host "🔄 Activating Python virtual environment..." -ForegroundColor Yellow
    & $ActivateScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}

# Check if proxy is already running
$ProxyPort = 5010
$ExistingProcess = Get-NetTCPConnection -LocalPort $ProxyPort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }

if ($ExistingProcess -and -not $Force) {
    Write-Host "⚠️  Proxy adapter already running on port $ProxyPort" -ForegroundColor Yellow
    Write-Host "Use -Force flag to restart it" -ForegroundColor Yellow
    exit 0
}
elseif ($ExistingProcess -and $Force) {
    Write-Host "🔄 Stopping existing proxy process..." -ForegroundColor Yellow
    $ExistingProcess.OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 1
}

# Start proxy server
$ProxyScript = Join-Path $ProjectRoot "scripts\start_proxy.py"
Write-Host "`n🚀 Starting Proxy Server..." -ForegroundColor Green
Write-Host "📍 Listen Address:   127.0.0.1:$ProxyPort" -ForegroundColor Cyan
Write-Host "🎯 Target:           http://127.0.0.1:8001 (ZombieCoder Agent)" -ForegroundColor Cyan
Write-Host "`n📝 Configuration:" -ForegroundColor Green
Write-Host "   • Cursor AI URL:  http://127.0.0.1:5010/v1" -ForegroundColor Gray
Write-Host "   • API Model:      deepseek-coder-1.3b" -ForegroundColor Gray
Write-Host "   • Log File:       logs/proxy_adapter.log" -ForegroundColor Gray
Write-Host ""

# Run proxy
python $ProxyScript

exit $LASTEXITCODE
