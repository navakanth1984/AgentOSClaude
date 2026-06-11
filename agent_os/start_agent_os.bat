@echo off
title Agent OS Launcher
color 0A
echo.
echo  ==========================================
echo   Agent OS - Starting up...
echo  ==========================================
echo.

:: ── 1. Start the Python API server in a new window ─────────────
echo  [1/2] Starting Agent OS server on localhost:8765...
start "Agent OS Server" cmd /k "cd /d %~dp0 && python server.py"

:: Give the server 2 seconds to bind to port
timeout /t 2 /nobreak > nul

:: ── 2. Verify server is up ──────────────────────────────────────
curl -s http://localhost:8765/health > nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Server is live at http://localhost:8765
    echo  Opening 3D Neural Map Dashboard...
    start http://localhost:8765/neural
) else (
    echo  [!] Server did not respond - check the server window
)

:: ── 3. Launch Flutter dashboard ────────────────────────────────
echo  [2/2] Launching Flutter dashboard...
set FLUTTER=C:\Users\navka\navakanth001\flutter_sdk\bin\flutter.bat

if exist "%FLUTTER%" (
    start "Flutter Dashboard" cmd /k "cd /d %~dp0\..\learning_dashboard_app && "%FLUTTER%" run -d windows"
) else (
    echo  [!] Flutter not found at %FLUTTER%
    echo      Open the app manually from learning_dashboard_app/
)

echo.
echo  ==========================================
echo   Agent OS is running!
echo   - API: http://localhost:8765
echo   - CLI: python agent_os.py  (in this folder)
echo  ==========================================
echo.
pause
