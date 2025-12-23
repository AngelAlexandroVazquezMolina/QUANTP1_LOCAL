@echo off
REM QUANTP1 v3.1 - Emergency Stop
echo ========================================
echo   EMERGENCY STOP - Killing Python
echo ========================================

taskkill /F /IM python.exe /T

echo.
echo All Python processes terminated
pause
