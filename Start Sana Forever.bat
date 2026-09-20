@echo off
title Sana AI v1.1.0 — Voice Assistant
color 0A

echo.
echo  ╔══════════════════════════════════════════╗
echo  ║   Sana AI v1.1.0 — Starting up ...      ║
echo  ║   github.com/saisatwi/MyDataWhisperer   ║
echo  ╚══════════════════════════════════════════╝
echo.

:: Change to the script directory
cd /d "%~dp0"

:: Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo [SANA] Activating virtual environment ...
    call venv\Scripts\activate.bat
) else (
    echo [SANA] No venv found — using system Python
)

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found. Install Python 3.11+ from python.org
    pause
    exit /b 1
)

:: Run Sana
echo [SANA] Launching ...
echo.
python "Sana Forever.py"

echo.
echo [SANA] Session ended.
pause