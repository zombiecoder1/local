Set-Location "C:\Users\sahon\local"
git add .
git commit -m "auto: commit before start - $(Get-Date -Format o)"
# start agent
.\venv\Scripts\Activate.ps1
Start-Process -FilePath "python" -ArgumentList "unified_agent_system.py" -WorkingDirectory "C:\Users\sahon\local"
# wait a bit then start proxy service
Start-Sleep -Seconds 3
Start-Process -FilePath "C:\nssm\nssm.exe" -ArgumentList "start ZombieCoderProxy"