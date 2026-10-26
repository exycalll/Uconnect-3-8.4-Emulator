@echo off
cd /d "%~dp0"
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":4400 .*LISTENING"') do taskkill /F /PID %%p >nul 2>&1
start "Uconnect backend" /min "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" backend.py --hmi
timeout /t 1 /nobreak >nul
start "Navi Overlay" "%USERPROFILE%\AppData\Local\Programs\Python\Python312\python.exe" nav_overlay.py
start "" http://127.0.0.1:4401/