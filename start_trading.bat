@echo off
echo ========================================
echo   QUANTP1 v3.1 Trading System
echo ========================================
cd /d "%~dp0"
python --version
echo.
echo Starting trading system...
echo.
python src/main.py
echo.
echo System stopped
pause
