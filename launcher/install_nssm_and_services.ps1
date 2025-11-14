<#
Download NSSM (if missing) and install SimpleCursor shim and proxy as services using NSSM.

This script will:
- Create `launcher\nssm\` and download nssm.exe (64-bit) into it if not present
- Install two services using nssm:
    * SimpleCursorShim -> runs: <venv>\Scripts\python.exe servers\simple_cursor_server.py
    * SimpleCursorProxy -> runs: <venv>\Scripts\python.exe servers\proxy_adapter.py
- Configure NSSM to redirect stdout/stderr to `log\simple_cursor_shim.log` and `log\simple_cursor_proxy.log`
- Start the services and perform an authenticated proxy test

Run as Administrator for service installation.
#>

$ErrorActionPreference = 'Stop'
Write-Output "[nssm-installer] Starting NSSM installer script"

$workspace = (Resolve-Path "$PSScriptRoot\..\").Path
$nssmDir = Join-Path $workspace 'launcher\nssm'
if (-not (Test-Path $nssmDir)) { New-Item -ItemType Directory -Path $nssmDir | Out-Null }

# Prefer official nssm releases on GitHub (may change); try common mirror
$nssmExe = Join-Path $nssmDir 'nssm.exe'
if (-not (Test-Path $nssmExe)) {
    Write-Output "[nssm-installer] Downloading nssm to $nssmExe"
    $urls = @(
        'https://nssm.cc/release/nssm-2.24.zip',
        'https://github.com/kohsuke/nssm/releases/download/2.24/nssm-2.24.zip'
    )
    $zipPath = Join-Path $nssmDir 'nssm.zip'
    $got = $false
    foreach ($u in $urls) {
        try {
            Write-Output "[nssm-installer] Trying $u"
            Invoke-WebRequest -Uri $u -OutFile $zipPath -UseBasicParsing -TimeoutSec 30
            $got = $true; break
        }
        catch { Write-Output "[nssm-installer] Download failed: $($_.Exception.Message)" }
    }

    if (-not $got) { throw "Could not download NSSM; please download manually and place nssm.exe in $nssmDir" }

    Write-Output "[nssm-installer] Extracting nssm.zip"
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipPath, $nssmDir)

    # Search for nssm.exe in extracted folders (win64)
    $found = Get-ChildItem -Path $nssmDir -Recurse -Filter 'nssm.exe' -ErrorAction SilentlyContinue | Where-Object { $_.FullName -match 'win64' } | Select-Object -First 1
    if (-not $found) {
        $found = Get-ChildItem -Path $nssmDir -Recurse -Filter 'nssm.exe' -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if ($found) { Copy-Item -Path $found.FullName -Destination $nssmExe -Force }
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue
}

if (-not (Test-Path $nssmExe)) { throw "nssm.exe not found in $nssmDir" }

Write-Output "[nssm-installer] Using nssm at $nssmExe"

# Compute python exe path
$venvPython = Join-Path $workspace '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) { Write-Output "[nssm-installer] .venv python not found; using system python"; $venvPython = 'python' }

# Service definitions
$services = @(
    @{ Name = 'SimpleCursorShim'; Script = 'servers\simple_cursor_server.py'; Log = 'log\simple_cursor_shim.log' },
    @{ Name = 'SimpleCursorProxy'; Script = 'servers\proxy_adapter.py'; Log = 'log\simple_cursor_proxy.log' }
)

foreach ($s in $services) {
    $svcName = $s.Name
    $scriptPath = Join-Path $workspace $s.Script
    $logPath = Join-Path $workspace $s.Log
    $logDir = [System.IO.Path]::GetDirectoryName($logPath)
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

    Write-Output "[nssm-installer] Installing service $svcName"

    # Remove existing if present
    & $nssmExe remove $svcName confirm | Out-Null

    # Install: Application = python exe, AppParameters = script path
    & $nssmExe install $svcName $venvPython $scriptPath

    # Set working directory to workspace
    & $nssmExe set $svcName AppDirectory $workspace

    # Redirect stdout/stderr to log
    & $nssmExe set $svcName AppStdout $logPath
    & $nssmExe set $svcName AppStderr $logPath

    # Set Restart options
    & $nssmExe set $svcName AppThrottle 1500
    & $nssmExe set $svcName AppRestartDelay 5000

    # Start the service
    & $nssmExe start $svcName
    Start-Sleep -Milliseconds 500
}

Start-Sleep -Seconds 2
Write-Output "[nssm-installer] Checking services status..."
sc.exe query SimpleCursorShim
sc.exe query SimpleCursorProxy

# Quick authenticated proxy test
$cfg = Join-Path $workspace 'config\proxy_config.json'
if (Test-Path $cfg) {
    $api = (Get-Content -Raw $cfg | ConvertFrom-Json).api_key
    $hdr = @{ Authorization = "Bearer $api"; "Content-Type" = 'application/json' }
    $body = @{ model = 'tinyllama-gguf'; messages = @(@{ role = 'user'; content = 'NSSM service verification: hello' }); max_tokens = 60 } | ConvertTo-Json
    try {
        $resp = Invoke-WebRequest -Uri 'http://127.0.0.1:5010/v1/chat/completions' -Method Post -Headers $hdr -Body $body -TimeoutSec 20 -ErrorAction Stop
        Write-Output "[nssm-installer] Proxy test HTTP: $($resp.StatusCode.Value__)"
        Write-Output $resp.Content
    }
    catch {
        Write-Output "[nssm-installer] Proxy test failed: $($_.Exception.Message)"
    }
}
else {
    Write-Output "[nssm-installer] proxy_config.json not found"
}

Write-Output "[nssm-installer] Done"
