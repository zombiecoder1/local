@echo off
echo Starting ZombieCoder Family Agent...
echo ====================================
echo.
echo Make sure you have:
echo 1. Extracted this package to a directory
echo 2. Created a Python virtual environment (recommended)
echo 3. Installed dependencies with: pip install -r requirements.txt
echo 4. Installed PyTorch with: pip install torch --index-url https://download.pytorch.org/whl/cpu
echo.
echo Press any key to continue...
pause >nul
echo.
echo Starting agent server on port 8001...
python start_agent.py
pause