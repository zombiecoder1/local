#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Verify Proxy + Agent + Model Server setup
.DESCRIPTION
    Checks if all services are running and properly configured
#>

param(
    [switch]$Verbose,
    [switch]$FixIssues
)

$ErrorActionPreference = "Continue"
$script:Issues = @()
$script:Successes = @()

function Write-Success($msg) {
    Write-Host "✅ $msg" -ForegroundColor Green
    $script:Successes += $msg
}

function Write-Issue($msg) {
    Write-Host "❌ $msg" -ForegroundColor Red
    $script:Issues += $msg
}

function Write-Warning($msg) {
    Write-Host "⚠️  $msg" -ForegroundColor Yellow
}

function Write-Info($msg) {
    Write-Host "ℹ️  $msg" -ForegroundColor Cyan
}

# Header
Write-Host @"

╔════════════════════════════════════════════════════════════╗
║                                                            ║
║      ZombieCoder Proxy Setup Verification                 ║
║      Complete Status Check                                ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# 1. Check ports
Write-Host "1️⃣  Checking Service Ports..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

# Agent Port
$AgentPort = 8001
if (Get-NetTCPConnection -LocalPort $AgentPort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }) {
    Write-Success "Agent Server running on port $AgentPort"
} else {
    Write-Issue "Agent Server NOT running on port $AgentPort"
    Write-Info "   Start: ./full_auto_install.ps1"
}

# Proxy Port
$ProxyPort = 5010
if (Get-NetTCPConnection -LocalPort $ProxyPort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }) {
    Write-Success "Proxy Server running on port $ProxyPort"
} else {
    Write-Issue "Proxy Server NOT running on port $ProxyPort"
    Write-Info "   Start: .\scripts\start_proxy.ps1"
}

# Model Port
$ModelPort = 8155
if (Get-NetTCPConnection -LocalPort $ModelPort -ErrorAction SilentlyContinue | Where-Object { $_.State -eq "Listen" }) {
    Write-Success "Model Server running on port $ModelPort"
} else {
    Write-Issue "Model Server NOT running on port $ModelPort"
}

# 2. Check Configuration Files
Write-Host "`n2️⃣  Checking Configuration Files..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

$ProxyConfig = "config/proxy_config.json"
if (Test-Path $ProxyConfig) {
    Write-Success "Proxy config found: $ProxyConfig"
    if ($Verbose) {
        $config = Get-Content $ProxyConfig | ConvertFrom-Json
        Write-Info "   API Key: $($config.api_key)"
        Write-Info "   Port: $($config.port)"
        Write-Info "   Target: $($config.target_base)"
    }
} else {
    Write-Issue "Proxy config NOT found: $ProxyConfig"
}

$EnvFile = ".env"
if (Test-Path $EnvFile) {
    Write-Success "Environment file found: $EnvFile"
} else {
    Write-Issue "Environment file NOT found: $EnvFile"
}

# 3. Check Log Files
Write-Host "`n3️⃣  Checking Log Files..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

$ProxyLog = "logs/proxy_adapter.log"
if (Test-Path $ProxyLog) {
    Write-Success "Proxy log found: $ProxyLog"
    $logSize = (Get-Item $ProxyLog).Length / 1MB
    Write-Info "   Size: $([Math]::Round($logSize, 2)) MB"
    if ($Verbose) {
        Write-Info "   Recent entries:"
        Get-Content $ProxyLog -Tail 3 | ForEach-Object { Write-Info "   $_" }
    }
} else {
    Write-Warning "Proxy log NOT found (will be created on first request)"
}

$AgentLog = "logs/zombiecoder_agent.log"
if (Test-Path $AgentLog) {
    Write-Success "Agent log found: $AgentLog"
    $logSize = (Get-Item $AgentLog).Length / 1MB
    Write-Info "   Size: $([Math]::Round($logSize, 2)) MB"
} else {
    Write-Warning "Agent log NOT found (will be created on first request)"
}

# 4. Test Connectivity
Write-Host "`n4️⃣  Testing Connectivity..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

function Test-Service($name, $url) {
    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Success "$name: $url (Status 200)"
            return $true
        } else {
            Write-Warning "$name: $url (Status $($response.StatusCode))"
            return $false
        }
    } catch {
        Write-Issue "$name: $url (Error: $($_.Exception.Message))"
        return $false
    }
}

$AgentHealthOk = Test-Service "Agent Health" "http://127.0.0.1:8001/health"
$ProxyHealthOk = Test-Service "Proxy Health" "http://127.0.0.1:5010/health"
$ModelHealthOk = Test-Service "Model Health" "http://127.0.0.1:8155/health"

# 5. Test Chat Endpoint
Write-Host "`n5️⃣  Testing Chat Endpoint..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

if ($ProxyHealthOk) {
    try {
        $payload = @{
            model = "deepseek-coder-1.3b"
            messages = @(@{
                role = "user"
                content = "test"
            })
            stream = $false
            max_tokens = 50
        } | ConvertTo-Json

        $response = Invoke-WebRequest `
            -Uri "http://127.0.0.1:5010/v1/chat/completions" `
            -Method POST `
            -Headers @{ "Authorization" = "Bearer DUMMY_API_KEY_FOR_LOCAL" } `
            -ContentType "application/json" `
            -Body $payload `
            -TimeoutSec 30 `
            -ErrorAction Stop

        if ($response.StatusCode -eq 200) {
            Write-Success "Chat endpoint working (Status 200)"
            $data = $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($data) {
                Write-Info "   Response received successfully"
            }
        } else {
            Write-Warning "Chat endpoint returned: $($response.StatusCode)"
        }
    } catch {
        Write-Issue "Chat endpoint error: $($_.Exception.Message)"
    }
} else {
    Write-Warning "Skipping chat test (Proxy not healthy)"
}

# 6. Check Scripts
Write-Host "`n6️⃣  Checking Scripts..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

$scripts = @(
    "scripts/start_proxy.ps1",
    "scripts/start_proxy.py",
    "scripts/test_proxy.py"
)

$scripts | ForEach-Object {
    if (Test-Path $_) {
        Write-Success "Script found: $_"
    } else {
        Write-Issue "Script NOT found: $_"
    }
}

# 7. Check Documentation
Write-Host "`n7️⃣  Checking Documentation..." -ForegroundColor Yellow
Write-Host "────────────────────────────────" -ForegroundColor DarkGray

$docs = @(
    "PROXY_SETUP_README.txt",
    "CURSOR_SETUP_QUICKSTART.md",
    "START_HERE_BANGLA.md",
    "docs/PROXY_ADAPTER_GUIDE.md"
)

$docs | ForEach-Object {
    if (Test-Path $_) {
        Write-Success "Documentation: $_"
    } else {
        Write-Issue "Documentation missing: $_"
    }
}

# 8. Summary
Write-Host "`n8️⃣  Summary" -ForegroundColor Yellow
Write-Host "════════════════════════════════════" -ForegroundColor DarkGray

$TotalChecks = $script:Successes.Count + $script:Issues.Count
$SuccessRate = if ($TotalChecks -gt 0) { [Math]::Round(($script:Successes.Count / $TotalChecks) * 100) } else { 0 }

Write-Host "Total Checks: $TotalChecks"
Write-Host "Passed: $($script:Successes.Count)" -ForegroundColor Green
Write-Host "Failed: $($script:Issues.Count)" -ForegroundColor Red
Write-Host "Success Rate: $SuccessRate%"

if ($SuccessRate -eq 100) {
    Write-Host "`n✨ EVERYTHING IS WORKING! ✨" -ForegroundColor Green
} elseif ($SuccessRate -ge 75) {
    Write-Host "`n⚠️  MOSTLY WORKING - Check issues above" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ NEEDS ATTENTION - Multiple issues detected" -ForegroundColor Red
}

# 9. Recommendations
Write-Host "`n9️⃣  Next Steps" -ForegroundColor Yellow
Write-Host "════════════════════════════════════" -ForegroundColor DarkGray

if (-not $AgentHealthOk) {
    Write-Host "• Start Agent: ./full_auto_install.ps1"
}

if (-not $ProxyHealthOk) {
    Write-Host "• Start Proxy: .\scripts\start_proxy.ps1"
}

if ($script:Issues.Count -gt 0) {
    Write-Host "• Review documentation: PROXY_SETUP_README.txt"
    Write-Host "• Check logs: Get-Content logs/proxy_adapter.log -Tail 20"
}

Write-Host "• Read Bangla guide: START_HERE_BANGLA.md"
Write-Host "• Test proxy: python scripts/test_proxy.py"

Write-Host "`n════════════════════════════════════`n"
