#!/usr/bin/env pwsh
# ZombieCoder Model Load Fix Script
# Usage: .\scripts\fix_model_load.ps1 [-ModelName] [-CheckOnly]

param(
    [string]$ModelName = "microsoft/phi-2",
    [switch]$CheckOnly
)

$ErrorActionPreference = "Continue"

Write-Host "`n=== ZombieCoder Model Load Fix ===" -ForegroundColor Cyan
Write-Host "Model: $ModelName`n" -ForegroundColor Gray

# Check 1: Model Server Status
Write-Host "=== Step 1: Checking Model Server ===" -ForegroundColor Yellow

$modelServerPorts = @(8007, 8080)
$modelServerFound = $false

foreach ($port in $modelServerPorts) {
    $portCheck = netstat -ano | Select-String ":$port\s" | Select-Object -First 1
    if ($portCheck) {
        Write-Host "✅ Model Server listening on port $port" -ForegroundColor Green
        $modelServerFound = $true
        
        # Check /runtime/status endpoint
        try {
            $statusUrl = "http://127.0.0.1:$port/runtime/status"
            $statusResponse = Invoke-WebRequest -Uri $statusUrl -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($statusResponse.StatusCode -eq 200) {
                Write-Host "  ✅ Model Server status endpoint responding" -ForegroundColor Green
                $status = $statusResponse.Content | ConvertFrom-Json
                Write-Host "  📋 Status:" -ForegroundColor Gray
                $status | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
            }
        } catch {
            Write-Host "  ⚠️ Status endpoint not responding: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        break
    }
}

if (-not $modelServerFound) {
    Write-Host "❌ Model Server not found on ports 8007 or 8080" -ForegroundColor Red
    Write-Host "  Please ensure Ollama or model server is running" -ForegroundColor Yellow
}

# Check 2: Agent Health
Write-Host "`n=== Step 2: Checking Agent Health ===" -ForegroundColor Yellow

try {
    $agentHealth = Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($agentHealth.StatusCode -eq 200) {
        Write-Host "✅ Agent is healthy" -ForegroundColor Green
        $health = $agentHealth.Content | ConvertFrom-Json
        if ($health.model_status) {
            Write-Host "  📋 Model Status:" -ForegroundColor Gray
            $health.model_status | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "❌ Agent not responding: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "  Please start the agent: .\scripts\start_services.ps1 -Agent" -ForegroundColor Yellow
}

# Check 3: Model Availability via /v1/models
Write-Host "`n=== Step 3: Checking Model Availability ===" -ForegroundColor Yellow

try {
    $modelsResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/models" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    if ($modelsResponse.StatusCode -eq 200) {
        $models = $modelsResponse.Content | ConvertFrom-Json
        $modelFound = $false
        
        if ($models.data) {
            foreach ($model in $models.data) {
                if ($model.id -eq $ModelName) {
                    $modelFound = $true
                    Write-Host "✅ Model '$ModelName' found in /v1/models" -ForegroundColor Green
                    Write-Host "  📋 Model Info:" -ForegroundColor Gray
                    $model | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
                    
                    if ($model.ready -eq $true) {
                        Write-Host "  ✅ Model is ready" -ForegroundColor Green
                    } else {
                        Write-Host "  ⚠️ Model is not ready" -ForegroundColor Yellow
                    }
                    break
                }
            }
        }
        
        if (-not $modelFound) {
            Write-Host "❌ Model '$ModelName' not found in /v1/models" -ForegroundColor Red
            Write-Host "  Available models:" -ForegroundColor Yellow
            if ($models.data) {
                foreach ($model in $models.data) {
                    Write-Host "    - $($model.id)" -ForegroundColor Gray
                }
            }
        }
    }
} catch {
    Write-Host "❌ Failed to check /v1/models: $($_.Exception.Message)" -ForegroundColor Red
}

# Check 4: Test Model Load via Chat Completions
Write-Host "`n=== Step 4: Testing Model Load ===" -ForegroundColor Yellow

if (-not $CheckOnly) {
    Write-Host "Sending test request to load model..." -ForegroundColor Gray
    
    $testRequest = @{
        model = $ModelName
        messages = @(
            @{
                role = "user"
                content = "Test model load"
            }
        )
        max_tokens = 10
    } | ConvertTo-Json -Depth 10
    
    try {
        $headers = @{
            'Content-Type' = 'application/json'
            'Authorization' = 'Bearer DUMMY_API_KEY_FOR_LOCAL'
            'X-Session-ID' = 'test-model-load-' + (Get-Date -Format 'yyyyMMddHHmmss')
        }
        
        Write-Host "  Request URL: http://127.0.0.1:5010/v1/chat/completions" -ForegroundColor Gray
        Write-Host "  Model: $ModelName" -ForegroundColor Gray
        Write-Host "  Waiting for response (timeout: 120s)..." -ForegroundColor Gray
        
        $chatResponse = Invoke-WebRequest -Uri "http://127.0.0.1:5010/v1/chat/completions" -Method POST -Body $testRequest -Headers $headers -UseBasicParsing -TimeoutSec 120 -ErrorAction Stop
        
        if ($chatResponse.StatusCode -eq 200) {
            Write-Host "✅ Model load test successful" -ForegroundColor Green
            $chatResult = $chatResponse.Content | ConvertFrom-Json
            if ($chatResult.choices -and $chatResult.choices.Count -gt 0) {
                Write-Host "  📋 Response:" -ForegroundColor Gray
                Write-Host "    $($chatResult.choices[0].message.content)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "❌ Model load test failed: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "  Response: $responseBody" -ForegroundColor Gray
        }
        
        # Check for timeout
        if ($_.Exception.Message -like "*timeout*" -or $_.Exception.Message -like "*timed out*") {
            Write-Host "`n⚠️ Timeout detected. Possible causes:" -ForegroundColor Yellow
            Write-Host "  1. Model is still loading (first request takes longer)" -ForegroundColor Gray
            Write-Host "  2. Model server is slow or overloaded" -ForegroundColor Gray
            Write-Host "  3. Network issues" -ForegroundColor Gray
            Write-Host "`n  Solution: Wait a few minutes and try again, or check model server logs" -ForegroundColor Yellow
        }
        
        # Check for 404
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "`n⚠️ Model not found (404). Possible causes:" -ForegroundColor Yellow
            Write-Host "  1. Model name incorrect: '$ModelName'" -ForegroundColor Gray
            Write-Host "  2. Model not installed in model server" -ForegroundColor Gray
            Write-Host "`n  Solution: Check model name and ensure model is installed" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "Check-only mode: Skipping model load test" -ForegroundColor Gray
}

# Check 5: Agent Logs
Write-Host "`n=== Step 5: Checking Agent Logs ===" -ForegroundColor Yellow

$logPath = "C:\Users\sahon\local\logs\zombiecoder_agent.log"
if (Test-Path $logPath) {
    Write-Host "✅ Log file found: $logPath" -ForegroundColor Green
    
    $recentLogs = Get-Content $logPath -Tail 20 -ErrorAction SilentlyContinue
    if ($recentLogs) {
        Write-Host "  📋 Recent log entries (last 5 lines):" -ForegroundColor Gray
        $recentLogs | Select-Object -Last 5 | ForEach-Object {
            Write-Host "    $_" -ForegroundColor Gray
        }
        
        # Check for model-related errors
        $modelErrors = $recentLogs | Select-String -Pattern "model|Model|MODEL" -CaseSensitive:$false
        if ($modelErrors) {
            Write-Host "`n  ⚠️ Model-related log entries found:" -ForegroundColor Yellow
            $modelErrors | Select-Object -Last 3 | ForEach-Object {
                Write-Host "    $_" -ForegroundColor Gray
            }
        }
    }
} else {
    Write-Host "⚠️ Log file not found: $logPath" -ForegroundColor Yellow
}

# Summary and Recommendations
Write-Host "`n=== Summary & Recommendations ===" -ForegroundColor Cyan

if ($modelServerFound) {
    Write-Host "✅ Model Server: Running" -ForegroundColor Green
} else {
    Write-Host "❌ Model Server: Not running" -ForegroundColor Red
    Write-Host "  Recommendation: Start model server (Ollama or custom server)" -ForegroundColor Yellow
}

Write-Host "`nNext Steps:" -ForegroundColor Yellow
Write-Host "  1. If model server not running, start it first" -ForegroundColor Gray
Write-Host "  2. If model not found, check model name: '$ModelName'" -ForegroundColor Gray
Write-Host "  3. Check agent logs for detailed error messages" -ForegroundColor Gray
Write-Host "  4. Try loading model manually via model server API" -ForegroundColor Gray
Write-Host "  5. Run health check: .\scripts\health_check.ps1 -Detailed" -ForegroundColor Gray

Write-Host "`n=== Model Load Fix Complete ===" -ForegroundColor Cyan

