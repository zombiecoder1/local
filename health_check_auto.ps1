# Auto Health Check Script
# This script verifies that all services are running correctly

Write-Host "=== Auto Health Check ===" -ForegroundColor Green

# Check if ports 5010 and 8001 are listening
Write-Host "Checking if required ports are listening..." -ForegroundColor Yellow

$port5010 = Get-NetTCPConnection -LocalPort 5010 -ErrorAction SilentlyContinue
$port8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue

if ($port5010) {
    Write-Host "✓ Port 5010 (Proxy) is listening" -ForegroundColor Green
} else {
    Write-Host "✗ Port 5010 (Proxy) is NOT listening" -ForegroundColor Red
}

if ($port8001) {
    Write-Host "✓ Port 8001 (Agent) is listening" -ForegroundColor Green
} else {
    Write-Host "✗ Port 8001 (Agent) is NOT listening" -ForegroundColor Red
}

# Check health endpoints
Write-Host "Checking health endpoints..." -ForegroundColor Yellow

try {
    $proxyHealth = Invoke-WebRequest -Uri "http://127.0.0.1:5010/health" -ErrorAction Stop
    if ($proxyHealth.StatusCode -eq 200) {
        Write-Host "✓ Proxy health check passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Proxy health check failed with status: $($proxyHealth.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Proxy health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $agentHealth = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -ErrorAction Stop
    if ($agentHealth.StatusCode -eq 200) {
        Write-Host "✓ Agent health check passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Agent health check failed with status: $($agentHealth.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Agent health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check model endpoints
Write-Host "Checking model endpoints..." -ForegroundColor Yellow

try {
    $models = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/models" -ErrorAction Stop
    if ($models.StatusCode -eq 200) {
        Write-Host "✓ /v1/models endpoint is active" -ForegroundColor Green
    } else {
        Write-Host "✗ /v1/models endpoint failed with status: $($models.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ /v1/models endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $chat = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/chat/completions" -Method POST -Body "{}" -ErrorAction Stop
    if ($chat.StatusCode -eq 200) {
        Write-Host "✓ /v1/chat/completions endpoint is active" -ForegroundColor Green
    } else {
        Write-Host "✗ /v1/chat/completions endpoint failed with status: $($chat.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ /v1/chat/completions endpoint check failed (expected if no body): $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "Health check complete!" -ForegroundColor Green