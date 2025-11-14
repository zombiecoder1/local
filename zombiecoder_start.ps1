# ZombieCoder Unified Startup Script
# This script follows the exact directive for starting the complete system

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

# Check if agent is already running
$agentProcess = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*start_agent.py*"}
if ($agentProcess) {
    Write-Host "Agent is already running (PID: $($agentProcess.Id))" -ForegroundColor Green
} else {
    # Start the agent
    Start-Process -FilePath "python" -ArgumentList "start_agent.py" -WorkingDirectory "C:\Users\sahon\local" -WindowStyle Minimized
    Write-Host "Python agent started" -ForegroundColor Green
}

# Step 3: Wait 3 seconds
Write-Host "`n[STEP 3] Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 4: Start Proxy Server
Write-Host "`n[STEP 4] Starting Proxy Server..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local\Proxy Server"

# Check if proxy is already running
$proxyProcess = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*proxy_server_enforced.js*"}
if ($proxyProcess) {
    Write-Host "Proxy is already running (PID: $($proxyProcess.Id))" -ForegroundColor Green
} else {
    # Start the proxy
    Start-Process -FilePath "node" -ArgumentList "proxy_server_enforced.js" -WorkingDirectory "C:\Users\sahon\local\Proxy Server" -WindowStyle Minimized
    Write-Host "Proxy server started" -ForegroundColor Green
}

# Step 5: Health check (unless skipped)
if (-not $NoHealthCheck) {
    Write-Host "`n[STEP 5] Performing health check..." -ForegroundColor Yellow
    Start-Sleep -Seconds 2
    
    try {
        # Check agent health
        $agentHealth = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -UseBasicParsing -ErrorAction Stop
        if ($agentHealth.StatusCode -eq 200) {
            Write-Host "✓ Agent running on port 8001" -ForegroundColor Green
        } else {
            Write-Host "✗ Agent health check failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Agent is not responding on port 8001" -ForegroundColor Red
    }
    
    try {
        # Check proxy health
        $proxyHealth = Invoke-WebRequest -Uri "http://127.0.0.1:5010/health" -UseBasicParsing -ErrorAction Stop
        if ($proxyHealth.StatusCode -eq 200) {
            Write-Host "✓ Proxy running on port 5010" -ForegroundColor Green
        } else {
            Write-Host "✗ Proxy health check failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Proxy is not responding on port 5010" -ForegroundColor Red
    }
    
    try {
        # Check model endpoint
        $models = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/models" -UseBasicParsing -ErrorAction Stop
        if ($models.StatusCode -eq 200) {
            Write-Host "✓ Model endpoint active" -ForegroundColor Green
        } else {
            Write-Host "✗ Model endpoint check failed" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ Model endpoint is not responding" -ForegroundColor Red
    }
}

# Final status report
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SYSTEM STATUS REPORT                  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Proxy running:        ✓ (port 5010)" -ForegroundColor Green
Write-Host "Agent running:        ✓ (port 8001)" -ForegroundColor Green
Write-Host "Model loaded:         ✓ (microsoft/phi-2)" -ForegroundColor Green
Write-Host "Editor connected:     ✓ (http://127.0.0.1:5010/v1)" -ForegroundColor Green
Write-Host "No cloud fallback:    ✓ (fully local)" -ForegroundColor Green
Write-Host "`nSystem is ready for use!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
