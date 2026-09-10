@echo off
rem Launcher for booth.py: uses the .venv made by setup.bat, else the system Python.
setlocal
set "DIR=%~dp0"
if exist "%DIR%.venv\Scripts\python.exe" goto venv
where py >nul 2>nul
if not errorlevel 1 goto launcher
python "%DIR%booth.py" %*
exit /b %errorlevel%

:venv
"%DIR%.venv\Scripts\python.exe" "%DIR%booth.py" %*
exit /b %errorlevel%

:launcher
py -3 "%DIR%booth.py" %*
exit /b %errorlevel%
