@echo off

echo ========================================
echo N2F Project Setup Script
echo ========================================
echo.

echo Python found:
python --version
echo.

echo Checking virtual environment...
if exist "env\Scripts\python.exe" (
    echo Virtual environment exists! Removing it...
    rmdir /s /q env
    goto create
) else (
    echo Virtual environment not found.
    goto create
)

:create
echo Creating virtual environment...
python -m venv env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

:install
echo Installing requirements...
echo.

echo Upgrading pip...
env\Scripts\python.exe -m pip install --upgrade pip

echo.
echo Which environment do you want to install?
echo   [1] Development (includes tools for testing, linting, etc.)
echo   [2] Production  (only includes packages needed to run the application)
choice /c 12 /n /d 1 /t 15 /m "Enter your choice (default is 1):"

if errorlevel 2 (
    echo Installing PRODUCTION requirements...
    set "REQ_FILE=requirements.txt"
) else (
    echo Installing DEVELOPMENT requirements...
    set "REQ_FILE=requirements-dev.txt"
)

echo.
echo Installing project requirements from %REQ_FILE%...
env\Scripts\pip.exe install -r %REQ_FILE%
if errorlevel 1 (
    echo ERROR: Failed to install requirements!
    pause
    exit /b 1
)

echo.
echo Setup completed successfully!
echo.
echo You can now run: sync_n2f.bat
echo.
pause
