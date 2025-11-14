# Setup Agent Script
# This script sets up the Python agent according to the ZombieCoder directive

Write-Host "=== Setting up Python Agent ===" -ForegroundColor Green

# Check if virtual environment exists, if not create it
$venvPath = "C:\Users\sahon\local\venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Install requirements if requirements.txt exists
$reqPath = "C:\Users\sahon\local\requirements.txt"
if (Test-Path $reqPath) {
    Write-Host "Installing Python requirements..." -ForegroundColor Yellow
    pip install -r $reqPath
}

Write-Host "Python Agent setup complete!" -ForegroundColor Green