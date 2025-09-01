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

echo Installing project requirements...
env\Scripts\pip.exe install -r requirements.txt
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
