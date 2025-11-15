@echo off
title ZombieCoder - All Services
echo ========================================
echo   ZombieCoder AI System - Start All Services
echo ========================================
echo.

echo This script will start all ZombieCoder services in separate windows.
echo Please ensure you have all dependencies installed before proceeding.
echo.
echo Services to be started:
echo  - API Gateway (Port 5050)
echo  - Proxy Server (Port 5051)
echo  - Python Agent (Port 8001)
echo  - Dashboard (Port 3000)
echo  - Ollama Model Server (Port 8007) - Manual Start Required
echo.

echo Press any key to continue...
pause >nul
cls

echo ========================================
echo Starting ZombieCoder Services...
echo ========================================
echo.

echo 1. Starting API Gateway (Port 5050)...
cd /d "C:\Users\sahon\local\JS_Server\api_gateway"
start "API Gateway" cmd /k "npm start"
timeout /t 3 /nobreak >nul

echo 2. Starting Proxy Server (Port 5051)...
cd /d "C:\Users\sahon\local\Proxy Server"
start "Proxy Server" cmd /k "node proxy_server_enforced.js"
timeout /t 2 /nobreak >nul

echo 3. Starting Python Agent (Port 8001)...
cd /d "C:\Users\sahon\local"
start "Python Agent" cmd /k "python start_agent.py"
timeout /t 5 /nobreak >nul

echo 4. Starting Dashboard (Port 3000)...
cd /d "C:\Users\sahon\local\dashboard"
start "Dashboard" cmd /k "node server.js"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Services Started Successfully!
echo ========================================
echo.
echo Please note:
echo - Ollama Model Server (Port 8007) must be started manually
echo - Run 'ollama serve' in a separate terminal
echo.
echo Services are now running in separate windows:
echo - API Gateway: http://localhost:5050
echo - Proxy Server: http://localhost:5051
echo - Python Agent: http://localhost:8001
echo - Dashboard: http://localhost:3000
echo.
echo To stop services, close each window individually.
echo.
echo Press any key to exit...
pause >nul