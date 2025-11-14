# Health check script
Write-Host "Checking health endpoints..." -ForegroundColor Yellow

# Check proxy health
try {
    $proxyHealth = Invoke-RestMethod -Uri "http://127.0.0.1:5010/health" -Method GET
    Write-Host "Proxy Health: OK" -ForegroundColor Green
    Write-Host "Proxy Response: $($proxyHealth | ConvertTo-Json -Depth 10)"
} catch {
    Write-Host "Proxy Health: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host ""

# Check agent health
try {
    $agentHealth = Invoke-RestMethod -Uri "http://127.0.0.1:8001/health" -Method GET
    Write-Host "Agent Health: OK" -ForegroundColor Green
    Write-Host "Agent Response: $($agentHealth | ConvertTo-Json -Depth 10)"
} catch {
    Write-Host "Agent Health: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}

Write-Host ""

# Check models endpoint via proxy
try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:5010/v1/models" -Method GET
    Write-Host "Models Endpoint: OK" -ForegroundColor Green
    Write-Host "Models Response: $($models | ConvertTo-Json -Depth 10)"
} catch {
    Write-Host "Models Endpoint: FAILED" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)"
}