# Config Validator Script
# This script validates the editor configuration according to the ZombieCoder directive

Write-Host "=== Config Validator ===" -ForegroundColor Green

# Validate editor configuration
Write-Host "Validating editor configuration..." -ForegroundColor Yellow

# Check if config directory exists
$configDir = "C:\Users\sahon\local\config"
if (!(Test-Path $configDir)) {
    Write-Host "Config directory not found" -ForegroundColor Red
    Write-Host "Creating config directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $configDir | Out-Null
}

# Check for common editor config files
$editorConfigs = @(
    "C:\Users\sahon\AppData\Roaming\Code\User\settings.json",  # VS Code
    "C:\Users\sahon\AppData\Roaming\Cursor\User\settings.json"  # Cursor
)

$configValid = $false
foreach ($configPath in $editorConfigs) {
    if (Test-Path $configPath) {
        Write-Host "Found editor config: $configPath" -ForegroundColor Green
        try {
            $config = Get-Content $configPath | ConvertFrom-Json
            if ($config."openai.apiKey" -eq "" -or $config."openai.apiKey" -eq $null) {
                Write-Host "✓ API Key is correctly set to empty" -ForegroundColor Green
            } else {
                Write-Host "⚠ API Key should be empty for local mode" -ForegroundColor Yellow
            }
            
            if ($config."openai.apiBaseUrl" -eq "http://127.0.0.1:5010/v1") {
                Write-Host "✓ Base URL is correctly set to http://127.0.0.1:5010/v1" -ForegroundColor Green
                $configValid = $true
            } else {
                Write-Host "✗ Base URL is not set correctly. Expected: http://127.0.0.1:5010/v1" -ForegroundColor Red
            }
            
            if ($config."openai.defaultModel" -eq "microsoft/phi-2") {
                Write-Host "✓ Model is correctly set to microsoft/phi-2" -ForegroundColor Green
            } else {
                Write-Host "⚠ Model should be set to microsoft/phi-2" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "Error reading config file: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

if (-not $configValid) {
    Write-Host "Editor configuration needs to be updated:" -ForegroundColor Yellow
    Write-Host "  Base URL should be: http://127.0.0.1:5010/v1" -ForegroundColor Cyan
    Write-Host "  Model should be: microsoft/phi-2" -ForegroundColor Cyan
    Write-Host "  API Key should be empty" -ForegroundColor Cyan
}

# Validate system endpoints
Write-Host "Validating system endpoints..." -ForegroundColor Yellow

# Check if proxy server has the required endpoints
$proxyServerFile = "C:\Users\sahon\local\Proxy Server\proxy_server_enforced.js"
if (Test-Path $proxyServerFile) {
    $content = Get-Content $proxyServerFile -Raw
    if ($content -like "*'/v1/models'*") {
        Write-Host "✓ /v1/models endpoint found in proxy server" -ForegroundColor Green
    } else {
        Write-Host "✗ /v1/models endpoint missing in proxy server" -ForegroundColor Red
    }
    
    if ($content -like "*'/v1/chat/completions'*") {
        Write-Host "✓ /v1/chat/completions endpoint found in proxy server" -ForegroundColor Green
    } else {
        Write-Host "✗ /v1/chat/completions endpoint missing in proxy server" -ForegroundColor Red
    }
} else {
    Write-Host "Proxy server file not found: $proxyServerFile" -ForegroundColor Red
}

Write-Host "Config validation complete!" -ForegroundColor Green