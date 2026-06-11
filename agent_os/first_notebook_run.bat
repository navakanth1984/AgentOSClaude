@echo off
title NotebookLM First Run
color 0B
echo.
echo  ================================================
echo   NotebookLM Agent - First Run / Login
echo  ================================================
echo.
echo  This will open a Chrome window pointing to NotebookLM.
echo  If you're already logged into Google in Chrome, it
echo  will log in automatically. Otherwise, log in manually.
echo.
echo  The session is saved after login - you won't need
echo  to log in again for future runs.
echo.
pause

cd /d %~dp0
python notebooklm_agent.py list

echo.
echo  Done. Check above for your notebook list.
pause
