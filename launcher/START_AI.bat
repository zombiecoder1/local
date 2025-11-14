@echo off
title ZombieCoder AI System - Smart Launcher
color 0A

echo.
echo ========================================
echo    🚀 ZOMBIECODER AI SYSTEM
echo ========================================
echo    🎯 Smart Launcher
echo    🛑 Kills ALL existing processes
echo    🔄 Runs only ONE instance
echo    📊 Background + Frontend
echo ========================================
echo.

echo 🛑 Step 1: Killing ALL existing processes...
taskkill /f /im python.exe 2>nul
taskkill /f /im cmd.exe 2>nul
timeout /t 2 /nobreak > nul

echo.
echo 🚀 Step 2: Starting Smart Launcher...
cd /d "C:\Users\sahon\.zombie_model"
python Smart_Launcher.py

echo.
echo ✅ System started!
echo 📊 Check status in the launcher window
echo.
pause
