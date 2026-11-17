@echo off
title Stop CURD Inventory Auto-Push
echo Stopping any running CURD_Inventory auto_push background processes...

powershell.exe -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*CURD_Inventory*auto_push*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host 'Stopped process ID:' $_.ProcessId }"

echo Done.
pause
