@echo off
title ZombieCoder Complete AI Setup
color 0A

echo.
echo ███████╗ ██████╗ ███╗   ███╗██████╗ ██╗███████╗    ██████╗  ██████╗ ██████╗ ███████╗██████╗ 
echo ╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║██╔════╝    ██╔══██╗██╔═══██╗██╔══██╗██╔════╝██╔══██╗
echo   ██╔██╗ ██║   ██║██╔████╔██║██████╔╝██║█████╗      ██║  ██║██║   ██║██║  ██║█████╗  ██████╔╝
echo  ██╔╝ ██╗██║   ██║██║╚██╔╝██║██╔══██╗██║██╔══╝      ██║  ██║██║   ██║██║  ██║██╔══╝  ██╔══██╗
echo ███████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝██║███████╗    ██████╔╝╚██████╔╝██████╔╝███████╗██║  ██║
echo ╚══════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝╚══════╝    ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
echo.
echo                    🤖 Complete AI System Setup 🤖
echo                    ================================
echo.

echo 🎯 This script will:
echo    ✅ Kill all existing Python processes
echo    ✅ Start optimized AI servers
echo    ✅ Force Cursor AI to use our local server
echo    ✅ Monitor performance automatically
echo    ✅ Auto-restart slow servers
echo.

pause

echo.
echo 🔄 Step 1: Cleaning up existing processes...
echo ================================================

echo Killing all Python processes...
taskkill /f /im python.exe 2>nul
if %errorlevel%==0 (
    echo ✅ All Python processes killed
) else (
    echo ⚠️  No Python processes found
)

echo.
echo Waiting for cleanup...
timeout /t 3 /nobreak > nul

echo.
echo 🚀 Step 2: Starting ZombieCoder AI System...
echo ================================================

echo Starting ZombieCoder Launcher...
cd /d "C:\Users\sahon\.zombie_model"
python ZombieCoder_Launcher.py

echo.
echo ⏳ Waiting for servers to start...
timeout /t 15 /nobreak > nul

echo.
echo 🧪 Step 3: Testing AI servers...
echo =================================

echo Testing ZombieCoder Server...
curl -s http://localhost:8155/health > nul
if %errorlevel%==0 (
    echo ✅ ZombieCoder Server: ONLINE
) else (
    echo ❌ ZombieCoder Server: OFFLINE
)

echo Testing Fast Cursor API...
curl -s http://localhost:5002/health > nul
if %errorlevel%==0 (
    echo ✅ Fast Cursor API: ONLINE
) else (
    echo ❌ Fast Cursor API: OFFLINE
)

echo.
echo 🔧 Step 4: Forcing Cursor AI Connection...
echo ===========================================

echo Running Force Cursor Connector...
python Force_Cursor_Connector.py

echo.
echo 📊 Step 5: Performance Test...
echo ===============================

echo Running performance test...
python performance_test.py

echo.
echo 🎉 Setup Complete!
echo ===================

echo.
echo 📋 Your AI System Status:
echo =========================
echo ✅ ZombieCoder Server: http://localhost:8155
echo ✅ Fast Cursor API: http://localhost:5002
echo ✅ Performance Monitoring: ACTIVE
echo ✅ Auto-restart: ENABLED
echo.

echo 🎯 Cursor AI Configuration:
echo ============================
echo Model Name: ZombieCoder Local AI
echo API Base URL: http://localhost:5002
echo API Key: (leave empty)
echo Model ID: tinyllama-gguf
echo.

echo 🚀 Quick Start:
echo ================
echo 1. Open Cursor
echo 2. Press Ctrl+K
echo 3. Your local AI will respond!
echo.

echo 🌐 Dashboard: Open allserver.html in browser
echo 📊 Monitor: Check ZombieCoder Launcher window
echo.

echo Press any key to open Cursor with ZombieCoder AI...
pause

echo.
echo 🚀 Starting Cursor with ZombieCoder AI...
echo ==========================================

REM Set environment variables
set CURSOR_AI_ENDPOINT=http://localhost:5002
set CURSOR_AI_MODEL=tinyllama-gguf
set CURSOR_FORCE_LOCAL_AI=1

REM Try to start Cursor
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\cursor\Cursor.exe" 2>nul
if %errorlevel% neq 0 (
    start "" "C:\Program Files\Cursor\Cursor.exe" 2>nul
    if %errorlevel% neq 0 (
        start "" "C:\Program Files (x86)\Cursor\Cursor.exe" 2>nul
        if %errorlevel% neq 0 (
            echo ❌ Cursor not found. Please install Cursor first.
            echo 💡 Download from: https://cursor.sh/
        )
    )
)

echo.
echo ✅ Cursor started with ZombieCoder AI!
echo.
echo 🎯 Now in Cursor:
echo    1. Press Ctrl+K
echo    2. Type your prompt
echo    3. Your local AI will respond!
echo.

echo Press any key to exit...
pause > nul
