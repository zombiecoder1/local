# Start All Services Script
# This script starts all services according to the ZombieCoder directive

Write-Host "=== Starting All Services ===" -ForegroundColor Green

# Step 1: Commit changes
Write-Host "Step 1: Committing changes..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local"
git add .
git commit -m "auto: update before start" | Out-Null

# Step 2: Start Python agent
Write-Host "Step 2: Starting Python agent..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "start_agent.py" -WorkingDirectory "C:\Users\sahon\local"

# Step 3: Wait 3 seconds
Write-Host "Step 3: Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Step 4: Start Proxy Server
Write-Host "Step 4: Starting Proxy Server..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local\Proxy Server"
Start-Process -FilePath "node" -ArgumentList "proxy_server_enforced.js" -WorkingDirectory "C:\Users\sahon\local\Proxy Server"

Write-Host "All services started!" -ForegroundColor Green
Write-Host "Proxy running on port 5010" -ForegroundColor Cyan
Write-Host "Agent running on port 8001" -ForegroundColor Cyan