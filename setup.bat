@echo off

echo ========================================
echo N2F Project Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Check if virtual environment exists
if exist "env\Scripts\python.exe" (
    echo Virtual environment already exists!
    echo Do you want to recreate it? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q env
        goto :create_venv
    ) else (
        echo Using existing virtual environment.
        goto :install_requirements
    )
) else (
    echo Virtual environment not found, creating new one...
    goto :create_venv
)

:create_venv
echo Creating virtual environment...
python -m venv env
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)
echo Virtual environment created successfully!
echo.

:install_requirements
echo Installing requirements...
echo.

REM Upgrade pip
echo Upgrading pip...
env\Scripts\python.exe -m pip install --upgrade pip

REM Install requirements
echo Installing project requirements...
env\Scripts\pip.exe install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
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
