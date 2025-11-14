@echo off
REM ZombieCoder Portable Setup Script
echo.
echo ==================================
echo ZombieCoder Portable Installation
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install requirements
echo Installing dependencies...
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

REM Success message
echo.
echo ==================================
echo Installation Complete!
echo ==================================
echo.
echo To run the system:
echo 1. Start backend: python unified_agent_system.py
echo 2. Start proxy: python proxy_simple.py
echo.
pause
