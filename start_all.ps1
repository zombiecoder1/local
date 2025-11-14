# start_all.ps1
# 1. Commit, then start agent and proxy service
Set-Location "C:\Users\sahon\local"
git add .; git commit -m "auto start: $(Get-Date -Format o)" -ErrorAction SilentlyContinue

# Activate venv and start agent if not running
$pid = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*unified_agent_system.py*"} 
if (-not $pid) {
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit -Command `".\venv\Scripts\Activate.ps1; python unified_agent_system.py`"" -WorkingDirectory "C:\Users\sahon\local"
    Start-Sleep -Seconds 6
}

# start proxy service via NSSM
C:\nssm\nssm.exe start ZombieCoderProxy

# check health
Start-Sleep -Seconds 5
curl http://127.0.0.1:5010/health
curl http://127.0.0.1:8001/health