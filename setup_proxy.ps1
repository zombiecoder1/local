# Setup Proxy Server Script
# This script sets up the proxy server according to the ZombieCoder directive

Write-Host "=== Setting up Proxy Server ===" -ForegroundColor Green

# Check if Proxy Server directory exists
$proxyDir = "C:\Users\sahon\local\Proxy Server"
if (!(Test-Path $proxyDir)) {
    Write-Host "Creating Proxy Server directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $proxyDir | Out-Null
}

Set-Location $proxyDir

# Check if git repository exists, if not initialize it
if (!(Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init | Out-Null
    git checkout -b master | Out-Null
}

# Check if dependencies are installed
if (!(Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
}

Write-Host "Proxy Server setup complete!" -ForegroundColor Green