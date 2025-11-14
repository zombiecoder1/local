Write-Host "========================================"
Write-Host "ZOMBIECODER SETUP VERIFICATION"
Write-Host "========================================"
Write-Host ""

Write-Host "[1] Checking Required Files..."
$files = @(
    "unified_agent_system.py",
    "scripts/start_all_services.ps1",
    "config/enhanced_zombiecoder_config.yaml",
    ".env"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "    [OK] $file"
    }
    else {
        Write-Host "    [MISSING] $file"
    }
}
Write-Host ""

Write-Host "[2] Checking Python Environment..."
$venvPath = "zombiecoder_env\Scripts\python.exe"
if (Test-Path $venvPath) {
    Write-Host "    [OK] Virtual Environment Found"
    $version = & $venvPath --version 2>&1
    Write-Host "    [INFO] Python Version: $version"
}
else {
    Write-Host "    [ERROR] Virtual Environment Not Found"
}
Write-Host ""

Write-Host "[3] Checking Port Availability..."
$ports = @{8155 = "Model Server"; 8001 = "Agent Server"; 5010 = "Proxy Server" }

foreach ($port in $ports.Keys) {
    $name = $ports[$port]
    $netstat = netstat -ano -p tcp 2>$null | Select-String ":$port" | Select-String "LISTENING"
    
    if ($netstat) {
        Write-Host "    [USED] Port $port ($name)"
    }
    else {
        Write-Host "    [FREE] Port $port ($name)"
    }
}
Write-Host ""

Write-Host "========================================"
Write-Host "SETUP VERIFICATION COMPLETE"
Write-Host "========================================"
Write-Host ""

if (Test-Path ".env") {
    Write-Host "Configuration from .env:"
    Get-Content ".env" | Select-String -Pattern "AGENT_PORT|OLLAMA_URL"
}
Write-Host ""
