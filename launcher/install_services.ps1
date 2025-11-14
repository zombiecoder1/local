<#
Install SimpleCursor shim and Proxy as Windows services using sc.exe.
This script will:
- Read the workspace venv python path
- Create two services: SimpleCursorShim and SimpleCursorProxy
- Set them to start=auto and start them
- Print service status and perform a quick authorized proxy test

Run as Administrator for best results (service creation may require elevation).
#>

$ErrorActionPreference = 'Stop'
Write-Output "[install-services] Installing services..."

$workspace = (Resolve-Path "$PSScriptRoot\..\").Path
$venvPython = Join-Path $workspace '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Output "[install-services] Warning: venv python not found at $venvPython. Falling back to system python."
    $venvPython = 'python'
}

$shimScript = Join-Path $workspace 'servers\simple_cursor_server.py'
$proxyScript = Join-Path $workspace 'servers\proxy_adapter.py'

function New-ZombieService($name, $exe, $scriptPath) {
    $bin = "`"$exe`" `"$scriptPath`""
    Write-Output "[install-services] sc.exe create $name binPath= $bin start= auto"
    sc.exe create $name binPath= $bin start= auto | Out-Null
    sc.exe description $name "ZombieCoder service: $name" | Out-Null
}

try {
    if (-not (Test-Path $shimScript)) { throw "Shim script not found: $shimScript" }
    if (-not (Test-Path $proxyScript)) { throw "Proxy script not found: $proxyScript" }

    New-ZombieService -name 'SimpleCursorShim' -exe $venvPython -scriptPath $shimScript
    New-ZombieService -name 'SimpleCursorProxy' -exe $venvPython -scriptPath $proxyScript

    Write-Output "[install-services] Starting services..."
    sc.exe start SimpleCursorShim | Out-Null
    sc.exe start SimpleCursorProxy | Out-Null

    Start-Sleep -Seconds 3

    Write-Output "[install-services] Service status:"
    sc.exe query SimpleCursorShim
    sc.exe query SimpleCursorProxy

    # Quick proxy auth test
    $cfg = Join-Path $workspace 'config\proxy_config.json'
    if (Test-Path $cfg) {
        $api = (Get-Content -Raw $cfg | ConvertFrom-Json).api_key
        Write-Output "[install-services] Using API key from $cfg"
        $hdr = @{ Authorization = "Bearer $api"; "Content-Type" = 'application/json' }
        $body = @{ model='tinyllama-gguf'; messages = @(@{ role='user'; content='Service install test: say hi' }); max_tokens=40 } | ConvertTo-Json
        try {
            $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:5010/v1/chat/completions' -Method Post -Headers $hdr -Body $body -TimeoutSec 20 -ErrorAction Stop
            Write-Output "[install-services] Proxy test succeeded: HTTP $($resp.StatusCode.Value__)"
            Write-Output $resp.Content
        } catch {
            Write-Output "[install-services] Proxy test failed: $($_.Exception.Message)"
        }
    } else {
        Write-Output "[install-services] proxy_config.json not found at $cfg"
    }

    Write-Output "[install-services] Done. Use 'sc.exe query <name>' to check services, or Start-Service/Stop-Service cmdlets."
}
catch {
    Write-Output "[install-services] ERROR: $($_.Exception.Message)"
}
