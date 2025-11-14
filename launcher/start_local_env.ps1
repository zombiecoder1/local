<#
One-click launcher to set up the workspace and start local shim + proxy.
This script performs the following, with no interactive prompts:
- Create a Python venv at .venv if missing
- Install dependencies from requirements.txt
- Write a default `config/proxy_config.json` with a generated API key
- Start `servers/simple_cursor_server.py` and `servers/proxy_adapter.py` in background
- Optionally start `start_servers.ps1` if present
- Run quick verification (health, models, quick generate) and write `launcher/startup_report.txt`

Run from any folder by calling (PowerShell):
    pwsh .\launcher\start_local_env.ps1
#>

$ErrorActionPreference = 'Stop'
Write-Output "[launcher] Starting automatic setup..."

# Resolve workspace root (script lives in launcher/)
$workspaceRoot = (Resolve-Path "$PSScriptRoot\..").Path
Write-Output "[launcher] Workspace root: $workspaceRoot"

# Paths
$venvPath = Join-Path $workspaceRoot '.venv'
$pythonExe = Join-Path $venvPath 'Scripts\python.exe'
$requirements = Join-Path $workspaceRoot 'requirements.txt'

# Ensure venv exists (non-interactive)
if (-not (Test-Path $pythonExe)) {
    Write-Output "[launcher] Creating Python virtual environment at $venvPath (if system Python accessible)..."
    & python -m venv $venvPath 2>$null || & py -3 -m venv $venvPath 2>$null
}

if (Test-Path $pythonExe) {
    $pythonCmd = $pythonExe
} else {
    Write-Output "[launcher] .venv python not found; falling back to system 'python' command. Ensure Python 3 is on PATH."
    $pythonCmd = 'python'
}

# Install requirements (non-interactive)
if (Test-Path $requirements) {
    Write-Output "[launcher] Installing Python requirements from $requirements..."
    & $pythonCmd -m pip install --upgrade pip setuptools 2>$null | Out-Null
    & $pythonCmd -m pip install -r $requirements 2>&1 | ForEach-Object { Write-Output "[pip] $_" }
} else {
    Write-Output "[launcher] requirements.txt not found at $requirements. Skipping pip install."
}

# Prepare config directory and write proxy_config.json with generated API key
$configDir = Join-Path $workspaceRoot 'config'
if (-not (Test-Path $configDir)) { New-Item -ItemType Directory -Path $configDir | Out-Null }

$apiKey = [System.Guid]::NewGuid().ToString()
$proxyConfig = @{
    bind_host = '127.0.0.1'
    proxy_port = 5010
    shim_host = '127.0.0.1'
    shim_port = 5001
    require_api_key = $true
    api_key = $apiKey
}

$proxyConfigPath = Join-Path $configDir 'proxy_config.json'
$proxyConfig | ConvertTo-Json -Depth 6 | Out-File -FilePath $proxyConfigPath -Encoding UTF8
Write-Output "[launcher] Wrote default proxy config to $proxyConfigPath"

# Ensure log directory exists
$logDir = Join-Path $workspaceRoot 'log'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

Write-Output "[launcher] Starting Python servers (simple_cursor_server + proxy_adapter)..."

# Start the shim and proxy in background processes. We don't wait for them here.
Start-Process -FilePath $pythonCmd -ArgumentList "`"$workspaceRoot\servers\simple_cursor_server.py`"" -WorkingDirectory $workspaceRoot -WindowStyle Hidden -NoNewWindow:$false
Start-Process -FilePath $pythonCmd -ArgumentList "`"$workspaceRoot\servers\proxy_adapter.py`"" -WorkingDirectory $workspaceRoot -WindowStyle Hidden -NoNewWindow:$false

# If repository includes a start_servers.ps1 helper (to start model runtime), try to start it too
$startServers = Join-Path $workspaceRoot 'start_servers.ps1'
if (Test-Path $startServers) {
    Write-Output "[launcher] Found start_servers.ps1; starting it in background (if it launches runtime)."
    Start-Process -FilePath pwsh -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-File","`"$startServers`"" -WorkingDirectory $workspaceRoot -WindowStyle Hidden -NoNewWindow:$false -ErrorAction SilentlyContinue
}

Write-Output "[launcher] Waiting briefly for services to start..."
Start-Sleep -Seconds 4

# Verification (non-fatal)
$reportPath = Join-Path $workspaceRoot 'launcher\startup_report.txt'
$reportLines = @()

function Append-Report($line) {
    $reportLines += $line
    Write-Output $line
}

try {
    $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8155/health' -TimeoutSec 5
    Append-Report "health: OK - $($health | ConvertTo-Json -Depth 5)"
} catch {
    Append-Report "health: FAILED - $($_.Exception.Message)"
}

try {
    $models = Invoke-RestMethod -Uri 'http://127.0.0.1:8155/models/installed' -TimeoutSec 5
    Append-Report "models: $($models | ConvertTo-Json -Depth 5)"
} catch {
    Append-Report "models: FAILED - $($_.Exception.Message)"
}

try {
    $body = @{ prompt = 'Hello from launcher test'; max_tokens = 32; stream = $false } | ConvertTo-Json
    $gen = Invoke-RestMethod -Uri 'http://127.0.0.1:8155/api/generate' -Method Post -ContentType 'application/json' -Body $body -TimeoutSec 10
    Append-Report "generate: $($gen | ConvertTo-Json -Depth 5)"
} catch {
    Append-Report "generate: FAILED - $($_.Exception.Message)"
}

$reportLines | Out-File -FilePath $reportPath -Encoding UTF8
Write-Output "[launcher] Startup verification written to: $reportPath"
Write-Output "[launcher] Proxy API key saved to $proxyConfigPath"
Write-Output "[launcher] To configure VS Code / Cursor: set Base URL to http://127.0.0.1:5010 and use the API key above."

Write-Output "[launcher] Done. If something failed, open $reportPath to see details."
