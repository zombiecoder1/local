#!/usr/bin/env pwsh

Write-Host ""
Write-Host "========================================" 
Write-Host "STARTING ALL ZOMBIECODER SERVICES"
Write-Host "========================================"
Write-Host ""

$ProjectRoot = Get-Location
$LogDir = Join-Path $ProjectRoot "logs"
$VenvPath = Join-Path $ProjectRoot "zombiecoder_env\Scripts\python.exe"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

Write-Host "[INFO] Project Root: $ProjectRoot"
Write-Host "[INFO] Python: $VenvPath"
Write-Host ""

# Function to start a background service
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$Command,
        [string]$WorkingDir,
        [string]$LogFile
    )
    
    Write-Host "[STARTING] $ServiceName..."
    
    $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessInfo.FileName = "powershell.exe"
    $ProcessInfo.Arguments = "-NoProfile -Command `"cd '$WorkingDir'; $Command`""
    $ProcessInfo.RedirectStandardOutput = $true
    $ProcessInfo.RedirectStandardError = $true
    $ProcessInfo.UseShellExecute = $false
    $ProcessInfo.CreateNoWindow = $true
    
    $Process = [System.Diagnostics.Process]::Start($ProcessInfo)
    
    # Capture output to log
    $ProcessInfo.RedirectStandardOutput | Out-Null
    
    Start-Sleep -Milliseconds 500
    
    if ($Process.HasExited) {
        Write-Host "[ERROR] $ServiceName failed to start"
        return $null
    }
    else {
        Write-Host "[OK] $ServiceName started (PID: $($Process.Id))"
        return $Process
    }
}

# Function to check port
function Test-Port {
    param([int]$Port)
    $netstat = netstat -ano -p tcp 2>$null | Select-String ":$Port" | Select-String "LISTENING"
    return $null -ne $netstat
}

# Start Agent Server first
$AgentCmd = "& '`$env:PYTHONPATH' '$ProjectRoot\unified_agent_system.py'"
$AgentProcess = Start-Service -ServiceName "Agent Server (Port 8001)" -Command $AgentCmd -WorkingDir $ProjectRoot -LogFile (Join-Path $LogDir "agent.log")

Start-Sleep -Seconds 2

# Check if ports are available
Write-Host ""
Write-Host "========================================" 
Write-Host "PORT STATUS CHECK"
Write-Host "========================================" 
Write-Host ""

$ports = @{
    8155 = "Model Server"
    8001 = "Agent Server"
    5010 = "Proxy Server"
}

foreach ($port in $ports.Keys) {
    $name = $ports[$port]
    if (Test-Port -Port $port) {
        Write-Host "[LISTENING] Port $port ($name)"
    }
    else {
        Write-Host "[WAITING] Port $port ($name)"
    }
}

Write-Host ""
Write-Host "========================================" 
Write-Host "ALL SERVICES INITIALIZED"
Write-Host "========================================" 
Write-Host ""

Write-Host "Agent Service Details:"
Write-Host "  - URL: http://127.0.0.1:8001"
Write-Host "  - Endpoint: /v1/chat/completions"
Write-Host ""

Write-Host "To test the agent, open another terminal and run:"
Write-Host "  curl -X POST http://127.0.0.1:8001/v1/chat/completions -H 'Content-Type: application/json' -d '{\"messages\": [{\"role\": \"user\", \"content\": \"hello\"}]}'"
Write-Host ""

Write-Host "Press Ctrl+C to stop all services"
Write-Host ""

# Keep the script running
while ($true) {
    Start-Sleep -Seconds 10
    
    if ($AgentProcess -and $AgentProcess.HasExited) {
        Write-Host "[WARNING] Agent process has exited"
        break
    }
}
