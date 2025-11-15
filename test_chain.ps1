Write-Host "=== ZombieCoder Full Chain Verification ===" -ForegroundColor Cyan

function Test-Port {
    param(
        [int]$Port
    )
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $client.Connect("127.0.0.1", $Port)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

$services = @(
    @{ Name="API Gateway"; Port=5050; Url="http://127.0.0.1:5050/health" },
    @{ Name="Local Proxy"; Port=5051; Url="http://127.0.0.1:5051/v1/models" },
    @{ Name="Python Agent"; Port=8001; Url="http://127.0.0.1:8001/v1/agent/info" },
    @{ Name="Ollama Model Server"; Port=8007; Url="http://127.0.0.1:8007/api/tags" }
)

foreach ($svc in $services) {
    Write-Host "`nChecking $($svc.Name) on port $($svc.Port) ..."
    if (Test-Port -Port $svc.Port) {
        Write-Host "  [OK] Port Open" -ForegroundColor Green
        try {
            $response = Invoke-WebRequest -Uri $svc.Url -UseBasicParsing
            Write-Host "  [RESPONSE] Status: $($response.StatusCode)"
        } catch {
            Write-Host "  [ERROR] Failed to reach endpoint"
        }
    } else {
        Write-Host "  [FAILED] Port Closed or Service Not Running" -ForegroundColor Red
    }
}

Write-Host "`n=== Testing Full Chat Chain ===" -ForegroundColor Cyan
$body = @{
    model = "microsoft/phi-2"
    messages = @(
        @{
            role = "user"
            content = "Hello, are you local server?"
        }
    )
} | ConvertTo-Json

try {
    $chat = Invoke-RestMethod -Uri "http://127.0.0.1:5051/v1/chat/completions" `
                             -ContentType "application/json" `
                             -Method POST `
                             -Body $body
    Write-Host "[SUCCESS] Chat Response Received"
} catch {
    Write-Host "[FAILED] Chat Request FAILED -- Proxy is broken or lying"
}