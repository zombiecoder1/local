#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start All ZombieCoder Services (Model, Agent, Proxy)
.DESCRIPTION
    Complete orchestrator that:
    - Starts Model Server (port 8155)
    - Starts Agent Server (port 8001)
    - Starts Proxy Adapter (port 5010)
    - Monitors requests in real-time
    - Shows request type (GET/POST)
    - Displays response status
    - Live memory and CPU monitoring
#>

param(
    [switch]$NoTest,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

# Colors
$Success = 'Green'
$Error = 'Red'
$Warning = 'Yellow'
$Info = 'Cyan'
$Highlight = 'Magenta'

# Configuration
$ProjectRoot = Get-Location
$ModelServerPort = 8155
$AgentPort = 8001
$ProxyPort = 5010

Write-Host @"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🚀 ZombieCoder Complete Service Orchestrator              ║
║                                                               ║
║     Starting:                                                 ║
║     • Model Server (port $ModelServerPort)                    ║
║     • Agent Server (port $AgentPort)                          ║
║     • Proxy Adapter (port $ProxyPort)                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor $Info

# Check prerequisites
Write-Host "📋 Checking Prerequisites..." -ForegroundColor $Warning
$PrereqOk = $true

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor $Success
} catch {
    Write-Host "❌ Python not found" -ForegroundColor $Error
    $PrereqOk = $false
}

# Check virtual environment
if (Test-Path "zombiecoder_env/Scripts/Activate.ps1") {
    Write-Host "✅ Virtual environment found" -ForegroundColor $Success
} else {
    Write-Host "❌ Virtual environment not found" -ForegroundColor $Error
    $PrereqOk = $false
}

# Check model_server directory
if (Test-Path "C:\model") {
    Write-Host "✅ Model server directory found" -ForegroundColor $Success
} else {
    Write-Host "⚠️  Model server directory not found at C:\model" -ForegroundColor $Warning
    Write-Host "   Creating placeholder..." -ForegroundColor $Warning
}

if (-not $PrereqOk) {
    Write-Host "`n❌ Some prerequisites missing" -ForegroundColor $Error
    exit 1
}

Write-Host "`n" -ForegroundColor $Info

# Function to start service in background with logging
function Start-Service {
    param(
        [string]$Name,
        [string]$Port,
        [string]$Command,
        [string]$WorkingDirectory = $ProjectRoot,
        [string]$LogFile
    )
    
    Write-Host "🚀 Starting $Name on port $Port..." -ForegroundColor $Highlight
    
    $LogDir = Split-Path $LogFile
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    # Create PowerShell script file
    $ScriptFile = "temp_start_$Name.ps1"
    
    if ($Name -eq "Model Server") {
        @"
Set-Location "C:\model"
& activate_model.ps1 2>>`"$LogFile`"
python -m uvicorn model_server:app --host 0.0.0.0 --port $Port 2>>`"$LogFile`"
"@ | Out-File -FilePath $ScriptFile -Encoding UTF8
    } else {
        @"
Set-Location "$WorkingDirectory"
. ./zombiecoder_env/Scripts/Activate.ps1
$Command 2>>`"$LogFile`"
"@ | Out-File -FilePath $ScriptFile -Encoding UTF8
    }
    
    # Start process
    $Process = Start-Process -FilePath "pwsh.exe" `
        -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File $ScriptFile" `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError $LogFile `
        -PassThru
    
    Start-Sleep -Seconds 2
    
    # Check if process is running
    if (Get-Process -Id $Process.Id -ErrorAction SilentlyContinue) {
        Write-Host "✅ $Name started (PID: $($Process.Id))" -ForegroundColor $Success
        Write-Host "   Log: $LogFile" -ForegroundColor $Info
        return $Process.Id
    } else {
        Write-Host "❌ Failed to start $Name" -ForegroundColor $Error
        if (Test-Path $LogFile) {
            Write-Host "   Error output:" -ForegroundColor $Error
            Get-Content $LogFile -Tail 5 | ForEach-Object { Write-Host "   $_" -ForegroundColor $Error }
        }
        return $null
    }
}

# Start services
$ModelPid = Start-Service `
    -Name "Model Server" `
    -Port $ModelServerPort `
    -Command "python -m uvicorn model_server:app --host 0.0.0.0 --port $ModelServerPort" `
    -WorkingDirectory "C:\model" `
    -LogFile "logs/model_server.log"

Start-Sleep -Seconds 3

$AgentPid = Start-Service `
    -Name "Agent Server" `
    -Port $AgentPort `
    -Command "python unified_agent_system.py" `
    -LogFile "logs/zombiecoder_agent.log"

Start-Sleep -Seconds 3

$ProxyPid = Start-Service `
    -Name "Proxy Adapter" `
    -Port $ProxyPort `
    -Command "python scripts/start_proxy.py" `
    -LogFile "logs/proxy_adapter.log"

# Store PIDs for later cleanup
@{
    ModelServer = $ModelPid
    Agent = $AgentPid
    Proxy = $ProxyPid
} | ConvertTo-Json | Out-File "running_services.json"

Write-Host "`n" -ForegroundColor $Info

# Test connectivity
Write-Host "🧪 Testing Service Connectivity..." -ForegroundColor $Warning
Write-Host "═══════════════════════════════════" -ForegroundColor $Warning

function Test-Service {
    param(
        [string]$Name,
        [int]$Port,
        [string]$Path = "/health"
    )
    
    $Url = "http://127.0.0.1:$Port$Path"
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ $Name: $Url (Status 200)" -ForegroundColor $Success
            return $true
        }
    } catch {
        Write-Host "❌ $Name: $Url (Connection failed)" -ForegroundColor $Error
        return $false
    }
}

$ModelOk = Test-Service -Name "Model Server" -Port $ModelServerPort
$AgentOk = Test-Service -Name "Agent Server" -Port $AgentPort
$ProxyOk = Test-Service -Name "Proxy Adapter" -Port $ProxyPort

Write-Host "`n" -ForegroundColor $Info

# Live monitoring section
Write-Host "📊 Live Request Monitor" -ForegroundColor $Highlight
Write-Host "═══════════════════════════════════" -ForegroundColor $Highlight
Write-Host "Watching logs for incoming requests..." -ForegroundColor $Info
Write-Host "`n" -ForegroundColor $Info

# Function to parse and display logs
function Monitor-Logs {
    $LastLines = @{
        Model = 0
        Agent = 0
        Proxy = 0
    }
    
    Write-Host "🔄 Starting real-time log monitoring..." -ForegroundColor $Info
    Write-Host "`nPress Ctrl+C to stop and cleanup" -ForegroundColor $Warning
    Write-Host "`n" -ForegroundColor $Info
    
    $Monitor = $true
    $Counter = 0
    
    while ($Monitor) {
        try {
            # Check Model Server logs
            if (Test-Path "logs/model_server.log") {
                $Content = Get-Content "logs/model_server.log" -ErrorAction SilentlyContinue
                $LineCount = @($Content).Count
                if ($LineCount -gt $LastLines.Model) {
                    $NewLines = @($Content) | Select-Object -Skip $LastLines.Model
                    foreach ($Line in $NewLines) {
                        if ($Line -match "POST|GET|PUT|DELETE|HEAD|OPTIONS") {
                            $Method = if ($Line -match "POST") { "POST" } elseif ($Line -match "GET") { "GET" } else { "?" }
                            Write-Host "🔵 [MODEL] ($Method) $Line" -ForegroundColor Cyan
                        }
                    }
                    $LastLines.Model = $LineCount
                }
            }
            
            # Check Agent logs
            if (Test-Path "logs/zombiecoder_agent.log") {
                $Content = Get-Content "logs/zombiecoder_agent.log" -ErrorAction SilentlyContinue
                $LineCount = @($Content).Count
                if ($LineCount -gt $LastLines.Agent) {
                    $NewLines = @($Content) | Select-Object -Skip $LastLines.Agent
                    foreach ($Line in $NewLines) {
                        if ($Line -match "POST|GET|chat|request|response") {
                            $Method = if ($Line -match "POST") { "POST" } elseif ($Line -match "GET") { "GET" } else { "?" }
                            Write-Host "🟢 [AGENT] ($Method) $Line" -ForegroundColor Green
                        }
                    }
                    $LastLines.Agent = $LineCount
                }
            }
            
            # Check Proxy logs
            if (Test-Path "logs/proxy_adapter.log") {
                $Content = Get-Content "logs/proxy_adapter.log" -ErrorAction SilentlyContinue
                $LineCount = @($Content).Count
                if ($LineCount -gt $LastLines.Proxy) {
                    $NewLines = @($Content) | Select-Object -Skip $LastLines.Proxy
                    foreach ($Line in $NewLines) {
                        if ($Line -match "POST|GET|PUT|DELETE") {
                            # Extract method and status
                            if ($Line -match "(\w+)\s.*->\s(\d+)") {
                                $Method = $Matches[1]
                                $Status = $Matches[2]
                                $StatusColor = if ($Status -eq "200") { $Success } else { $Warning }
                                Write-Host "🟡 [PROXY] ($Method) $Line" -ForegroundColor Magenta
                            }
                        }
                    }
                    $LastLines.Proxy = $LineCount
                }
            }
            
            # Memory and CPU monitoring (every 10 seconds)
            $Counter++
            if ($Counter % 10 -eq 0) {
                Write-Host "`n📈 Resource Usage:" -ForegroundColor $Info
                
                if ($ModelPid) {
                    try {
                        $Proc = Get-Process -Id $ModelPid -ErrorAction SilentlyContinue
                        if ($Proc) {
                            $Mem = [Math]::Round($Proc.WorkingSet / 1MB, 2)
                            Write-Host "   Model Server (PID $ModelPid): $Mem MB" -ForegroundColor Cyan
                        }
                    } catch { }
                }
                
                if ($AgentPid) {
                    try {
                        $Proc = Get-Process -Id $AgentPid -ErrorAction SilentlyContinue
                        if ($Proc) {
                            $Mem = [Math]::Round($Proc.WorkingSet / 1MB, 2)
                            Write-Host "   Agent Server (PID $AgentPid): $Mem MB" -ForegroundColor Green
                        }
                    } catch { }
                }
                
                if ($ProxyPid) {
                    try {
                        $Proc = Get-Process -Id $ProxyPid -ErrorAction SilentlyContinue
                        if ($Proc) {
                            $Mem = [Math]::Round($Proc.WorkingSet / 1MB, 2)
                            Write-Host "   Proxy Adapter (PID $ProxyPid): $Mem MB" -ForegroundColor Magenta
                        }
                    } catch { }
                }
                
                Write-Host "`n" -ForegroundColor $Info
            }
            
            Start-Sleep -Milliseconds 500
        } catch {
            if ($_.Exception.Message -notmatch "pipeline has been stopped") {
                Write-Host "⚠️  Monitoring error: $_" -ForegroundColor $Warning
            }
            break
        }
    }
}

# Run monitoring
if (-not $NoTest) {
    Monitor-Logs
}

# Cleanup function
function Cleanup {
    Write-Host "`n`n🛑 Shutting down services..." -ForegroundColor $Warning
    
    if ($ModelPid) {
        try {
            Stop-Process -Id $ModelPid -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Model Server stopped" -ForegroundColor $Success
        } catch { }
    }
    
    if ($AgentPid) {
        try {
            Stop-Process -Id $AgentPid -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Agent Server stopped" -ForegroundColor $Success
        } catch { }
    }
    
    if ($ProxyPid) {
        try {
            Stop-Process -Id $ProxyPid -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Proxy Adapter stopped" -ForegroundColor $Success
        } catch { }
    }
    
    # Cleanup temp files
    Get-Item "temp_start_*.ps1" -ErrorAction SilentlyContinue | Remove-Item -Force
    
    Write-Host "`n✨ All services stopped" -ForegroundColor $Success
    exit 0
}

# Register cleanup on exit
$null = Register-EngineEvent -SourceIdentifier PowerShell.Exiting -Action { Cleanup }
trap { Cleanup }
