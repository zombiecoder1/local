# ZombieCoder System Startup Script

Write-Host "Starting ZombieCoder Local Agent System" -ForegroundColor Cyan

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local"
git add .
git commit -m "auto: update before start" 2>&1 > $null

# Start Python agent
Write-Host "Starting Python agent..." -ForegroundColor Yellow
Start-Process -FilePath "python" -ArgumentList "start_agent.py" -WorkingDirectory "C:\Users\sahon\local"

# Wait 3 seconds
Write-Host "Waiting 3 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start Proxy Server
Write-Host "Starting Proxy Server..." -ForegroundColor Yellow
Set-Location "C:\Users\sahon\local\Proxy Server"
Start-Process -FilePath "node" -ArgumentList "proxy_server_enforced.js" -WorkingDirectory "C:\Users\sahon\local\Proxy Server"

Write-Host "System startup complete!" -ForegroundColor Green
Write-Host "Proxy: http://127.0.0.1:5010" -ForegroundColor Cyan
Write-Host "Agent: http://127.0.0.1:8001" -ForegroundColor Cyan