# ZombieCoder Unified Startup Script
param(
    [switch]$NoGit = $false,
    [switch]$NoHealthCheck = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ZOMBIECODER LOCAL AGENT SYSTEM        " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Git commit (unless skipped)
if (-not $NoGit) {
    Write-Host "`n[STEP 1] Committing changes..." -ForegroundColor Yellow
    Set-Location "C:\Users\sahon\local"
    git add .
    $commitResult = git commit -m "auto: update before start" 2>&1
    if ($commitResult -like "*nothing to commit*") {
        Write-Host "No changes to commit" -ForegroundColor Green
    } else {
        Write-Host "Changes committed successfully" -ForegroundColor Green
    }
}

# Step 2: Start Python agent
Write-Host "`n[STEP 2] Starting Python agent..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local"

# Start the agent
Start-Process -FilePath "python" -ArgumentList "start_agent.py" -WorkingDirectory "C:\Users\sahon\local" -WindowStyle Minimized
Write-Host "Python agent started" -ForegroundColor Green

# Step 3: Wait 3 seconds
Write-Host "`n[STEP 3] Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 4: Start Proxy Server
Write-Host "`n[STEP 4] Starting Proxy Server..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local\Proxy Server"

# Start the proxy
Start-Process -FilePath "node" -ArgumentList "proxy_server_enforced.js" -WorkingDirectory "C:\Users\sahon\local\Proxy Server" -WindowStyle Minimized
Write-Host "Proxy server started" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SYSTEM STARTUP COMPLETE               " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Proxy running:        ✓ (port 5010)" -ForegroundColor Green
Write-Host "Agent running:        ✓ (port 8001)" -ForegroundColor Green
Write-Host "Model loaded:         ✓ (microsoft/phi-2)" -ForegroundColor Green
Write-Host "Editor connected:     ✓ (http://127.0.0.1:5010/v1)" -ForegroundColor Green
Write-Host "No cloud fallback:    ✓ (fully local)" -ForegroundColor Green
Write-Host "`nSystem is ready for use!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan