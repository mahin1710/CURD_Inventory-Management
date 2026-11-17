@echo off
title CURD Inventory - GitHub 10-Min Auto-Push
cd /d "%~dp0"

echo ===================================================
echo   CURD Inventory - GitHub 10-Min Auto-Push
echo   Repository: https://github.com/mahin1710/CURD_Inventory-Management
echo ===================================================
echo.
echo Starting 10-minute auto-push background monitor...
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "auto_push.ps1"
