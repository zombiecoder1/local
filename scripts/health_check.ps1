#!/usr/bin/env pwsh
# ZombieCoder Health Check Script
# Usage: .\scripts\health_check.ps1 [-Detailed] [-Fix]

param(
    [switch]$Detailed,
    [switch]$Fix
)

$ErrorActionPreference = "Continue"

Write-Host "`n=== ZombieCoder Health Check ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Gray

$services = @(
    @{ Name = "API Gateway"; Port = 5010; URL = "http://127.0.0.1:5010/health"; Required = $true },
    @{ Name = "Python Agent"; Port = 8001; URL = "http://127.0.0.1:8001/health"; Required = $true },
    @{ Name = "Editor Agent"; Port = 49110; URL = "http://127.0.0.1:49110/health"; Required = $false },
    @{ Name = "Memory Service"; Port = 49120; URL = "http://127.0.0.1:49120/health"; Required = $false },
    @{ Name = "Multiprocessing Service"; Port = 50150; URL = "http://127.0.0.1:50150/health"; Required = $false }
)

$results = @()

foreach ($service in $services) {
    Write-Host "Checking $($service.Name)..." -ForegroundColor Yellow
    
    # Check if port is listening
    $portCheck = netstat -ano | Select-String ":$($service.Port)\s" | Select-Object -First 1
    
    if ($portCheck) {
        Write-Host "  ✅ Port $($service.Port): Listening" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Port $($service.Port): Not listening" -ForegroundColor Red
        $results += @{
            Service = $service.Name
            Status = "Port not listening"
            Healthy = $false
        }
        continue
    }
    
    # Check health endpoint
    try {
        $response = Invoke-WebRequest -Uri $service.URL -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "  ✅ Health Endpoint: OK ($($response.StatusCode))" -ForegroundColor Green
            
            if ($Detailed) {
                $content = $response.Content | ConvertFrom-Json
                Write-Host "  📋 Response:" -ForegroundColor Gray
                $content | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
            }
            
            $results += @{
                Service = $service.Name
                Status = "Healthy"
                Healthy = $true
            }
        } else {
            Write-Host "  ⚠️ Health Endpoint: Unexpected status ($($response.StatusCode))" -ForegroundColor Yellow
            $results += @{
                Service = $service.Name
                Status = "Unhealthy (Status: $($response.StatusCode))"
                Healthy = $false
            }
        }
    } catch {
        Write-Host "  ❌ Health Endpoint: Failed - $($_.Exception.Message)" -ForegroundColor Red
        $results += @{
            Service = $service.Name
            Status = "Failed: $($_.Exception.Message)"
            Healthy = $false
        }
    }
    
    Write-Host ""
}

# Test /v1/models endpoint
Write-Host "=== Testing /v1/models Endpoint ===" -ForegroundColor Cyan
try {
    $modelsResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/models" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($modelsResponse.StatusCode -eq 200) {
        Write-Host "✅ /v1/models: OK" -ForegroundColor Green
        $models = $modelsResponse.Content | ConvertFrom-Json
        if ($Detailed) {
            Write-Host "📋 Models:" -ForegroundColor Gray
            $models | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor Gray
        } else {
            $modelCount = if ($models.data) { $models.data.Count } else { 0 }
            Write-Host "  Found $modelCount model(s)" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ /v1/models: Failed - $($_.Exception.Message)" -ForegroundColor Red
}

# Test /v1/chat/completions endpoint
Write-Host "`n=== Testing /v1/chat/completions Endpoint ===" -ForegroundColor Cyan
$testRequest = @{
    model = "microsoft/phi-2"
    messages = @(
        @{
            role = "user"
            content = "Test"
        }
    )
    max_tokens = 10
} | ConvertTo-Json -Depth 10

try {
    $headers = @{
        'Content-Type' = 'application/json'
        'Authorization' = 'Bearer DUMMY_API_KEY_FOR_LOCAL'
    }
    
    $chatResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/chat/completions" -Method POST -Body $testRequest -Headers $headers -UseBasicParsing -TimeoutSec 30 -ErrorAction Stop
    
    if ($chatResponse.StatusCode -eq 200) {
        Write-Host "✅ /v1/chat/completions: OK" -ForegroundColor Green
        if ($Detailed) {
            $chatResult = $chatResponse.Content | ConvertFrom-Json
            Write-Host "📋 Response:" -ForegroundColor Gray
            $chatResult | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ /v1/chat/completions: Failed - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "  Response: $responseBody" -ForegroundColor Gray
    }
}

# Summary
Write-Host "`n=== Health Check Summary ===" -ForegroundColor Cyan
$healthyCount = ($results | Where-Object { $_.Healthy -eq $true }).Count
$unhealthyCount = ($results | Where-Object { $_.Healthy -eq $false }).Count
$requiredUnhealthy = ($results | Where-Object { $_.Healthy -eq $false -and ($services | Where-Object { $_.Name -eq $_.Service }).Required -eq $true }).Count

Write-Host "✅ Healthy Services: $healthyCount" -ForegroundColor Green
Write-Host "❌ Unhealthy Services: $unhealthyCount" -ForegroundColor $(if ($unhealthyCount -gt 0) { "Red" } else { "Green" })

if ($requiredUnhealthy -gt 0) {
    Write-Host "⚠️ Required Services Unhealthy: $requiredUnhealthy" -ForegroundColor Red
    Write-Host "`nUnhealthy Required Services:" -ForegroundColor Yellow
    $results | Where-Object { $_.Healthy -eq $false -and ($services | Where-Object { $_.Name -eq $_.Service }).Required -eq $true } | ForEach-Object {
        Write-Host "  - $($_.Service): $($_.Status)" -ForegroundColor Red
    }
}

# Auto-fix suggestions
if ($Fix -and $requiredUnhealthy -gt 0) {
    Write-Host "`n=== Auto-Fix Attempts ===" -ForegroundColor Cyan
    
    $unhealthyRequired = $results | Where-Object { $_.Healthy -eq $false -and ($services | Where-Object { $_.Name -eq $_.Service }).Required -eq $true }
    
    foreach ($service in $unhealthyRequired) {
        $serviceConfig = $services | Where-Object { $_.Name -eq $service.Service } | Select-Object -First 1
        
        Write-Host "Attempting to fix $($service.Service)..." -ForegroundColor Yellow
        
        # Check if process is running
        $portProcess = netstat -ano | Select-String ":$($serviceConfig.Port)\s" | ForEach-Object {
            if ($_ -match '\s+(\d+)$') {
                $matches[1]
            }
        } | Select-Object -First 1
        
        if ($portProcess) {
            Write-Host "  Process found on port $($serviceConfig.Port) (PID: $portProcess)" -ForegroundColor Gray
            Write-Host "  Service may be starting up. Please wait and check again." -ForegroundColor Yellow
        } else {
            Write-Host "  No process found. Please start the service manually:" -ForegroundColor Yellow
            Write-Host "    .\scripts\start_services.ps1 -$($service.Service.Replace(' ', ''))" -ForegroundColor Gray
        }
    }
}

Write-Host "`n=== Health Check Complete ===" -ForegroundColor Cyan
Write-Host "Run with -Detailed flag for full response details" -ForegroundColor Gray
Write-Host "Run with -Fix flag to attempt automatic fixes`n" -ForegroundColor Gray

