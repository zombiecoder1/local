# Check ports script
Write-Host "Checking if ports 5010 and 8001 are listening..."

# Check port 5010 (proxy)
$port5010 = netstat -an | findstr ":5010"
if ($port5010) {
    Write-Host "Port 5010 (Proxy): Listening" -ForegroundColor Green
    Write-Host $port5010
} else {
    Write-Host "Port 5010 (Proxy): Not listening" -ForegroundColor Red
}

# Check port 8001 (agent)
$port8001 = netstat -an | findstr ":8001"
if ($port8001) {
    Write-Host "Port 8001 (Agent): Listening" -ForegroundColor Green
    Write-Host $port8001
} else {
    Write-Host "Port 8001 (Agent): Not listening" -ForegroundColor Red
}