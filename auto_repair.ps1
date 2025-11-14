# Auto Repair Script
# This script attempts to repair common issues with the ZombieCoder system

Write-Host "=== Auto Repair System ===" -ForegroundColor Green

# Check if required directories exist
Write-Host "Checking required directories..." -ForegroundColor Yellow

$proxyDir = "C:\Users\sahon\local\Proxy Server"
if (!(Test-Path $proxyDir)) {
    Write-Host "Creating missing Proxy Server directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $proxyDir | Out-Null
}

# Check if required files exist in Proxy Server directory
Write-Host "Checking required proxy server files..." -ForegroundColor Yellow

$requiredFiles = @("proxy_server_enforced.js", "proxy_server.js", "package.json")
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $proxyDir $file
    if (!(Test-Path $filePath)) {
        Write-Host "Missing file: $file" -ForegroundColor Red
        Write-Host "Please ensure all proxy server files are in place" -ForegroundColor Yellow
    } else {
        Write-Host "Found: $file" -ForegroundColor Green
    }
}

# Check if Node.js dependencies are installed
Write-Host "Checking Node.js dependencies..." -ForegroundColor Yellow
Set-Location $proxyDir

if (!(Test-Path "node_modules")) {
    Write-Host "Installing missing Node.js dependencies..." -ForegroundColor Yellow
    npm install --legacy-peer-deps
} else {
    Write-Host "Node.js dependencies found" -ForegroundColor Green
}

# Check if Python virtual environment exists
Write-Host "Checking Python virtual environment..." -ForegroundColor Yellow
$venvPath = "C:\Users\sahon\local\venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating missing Python virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
} else {
    Write-Host "Python virtual environment found" -ForegroundColor Green
}

# Check if requirements.txt dependencies are installed
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$reqPath = "C:\Users\sahon\local\requirements.txt"
if (Test-Path $reqPath) {
    # Activate virtual environment and check some key packages
    & "$venvPath\Scripts\Activate.ps1"
    try {
        $installed = pip list --format=freeze
        if ($installed -like "*requests*") {
            Write-Host "Python dependencies appear to be installed" -ForegroundColor Green
        } else {
            Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
            pip install -r $reqPath
        }
    } catch {
        Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
        pip install -r $reqPath
    }
} else {
    Write-Host "requirements.txt not found, skipping Python dependency check" -ForegroundColor Yellow
}

Write-Host "Auto repair complete!" -ForegroundColor Green