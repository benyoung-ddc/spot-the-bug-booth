@echo off
rem One-time setup for Windows: double-click setup.bat, or run it from a terminal.
rem
rem The puzzles need only the Python standard library, so there is nothing to
rem pip install. This finds (or installs) Python 3.8+, pins it in .venv,
rem prepares the candidate workspace, runs the self-test, and prints the
rem command to run each puzzle on its own.
setlocal
cd /d "%~dp0"

rem Reuse .venv only if it runs here (one copied from another machine won't).
if not exist ".venv\Scripts\python.exe" goto find_python
".venv\Scripts\python.exe" -c "pass" >nul 2>nul
if not errorlevel 1 goto ready

:find_python
set "PY="
where py >nul 2>nul
if errorlevel 1 goto try_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul
if errorlevel 1 goto try_python
set "PY=py -3"
goto make_venv

:try_python
rem "python" may be the Microsoft Store stub, which fails this check. That's fine.
where python >nul 2>nul
if errorlevel 1 goto no_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >nul 2>nul
if errorlevel 1 goto no_python
set "PY=python"
goto make_venv

:no_python
echo No Python 3.8+ found on this machine.
where winget >nul 2>nul
if errorlevel 1 goto manual_install
set /p "REPLY=Install Python 3.12 with winget now? [y/N] "
if /i not "%REPLY%"=="y" goto manual_install
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
echo.
echo Python installed. Close this window, open a new one, and run setup.bat again.
pause
exit /b 0

:manual_install
echo Install Python 3.8+ from https://www.python.org/downloads/
echo (tick "Add python.exe to PATH"), then run setup.bat again.
pause
exit /b 1

:make_venv
if exist .venv rmdir /s /q .venv
%PY% -m venv --without-pip .venv
if errorlevel 1 (
    echo Could not create .venv
    pause
    exit /b 1
)

:ready
call booth.bat reset
call booth.bat verify
if errorlevel 1 (
    echo Self-test failed. See the messages above.
    pause
    exit /b 1
)

echo.
echo Setup complete.
echo.
echo Run any puzzle on its own as a plain Python script (from this folder):
for %%f in (puzzles\E*.py puzzles\M*.py puzzles\H*.py) do echo   .venv\Scripts\python %%f
echo   Tip: run .venv\Scripts\activate once, then just: python puzzles\^<file^>.py
echo   A candidate's edited copy runs the same way: .venv\Scripts\python workspace\^<file^>.py
echo.
echo Or use the booth tool:
echo   booth            list puzzles and commands
echo   booth show easy  put a random easy puzzle on screen
echo   booth key        staff answer key
pause
