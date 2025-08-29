@echo off
REM ========================================
REM N2F Project Setup Script
REM ========================================
REM This batch file sets up the N2F project environment
REM Creates virtual environment and installs requirements

echo ========================================
echo N2F Project Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo ERROR: Python is not installed or not in PATH!
    echo ========================================
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Python found: 
python --version
echo.

REM Check if virtual environment already exists
if exist "env\Scripts\python.exe" (
    echo ========================================
    echo Virtual environment already exists!
    echo ========================================
    echo Do you want to recreate it? (y/n)
    set /p choice=
    if /i "%choice%"=="y" (
        echo Removing existing virtual environment...
        rmdir /s /q env
    ) else (
        echo Skipping virtual environment creation.
        goto :install_requirements
    )
)

REM Create virtual environment
echo ========================================
echo Creating virtual environment...
echo ========================================
python -m venv env
if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo ERROR: Failed to create virtual environment!
    echo ========================================
    echo Please check your Python installation.
    echo.
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

:install_requirements

REM Install requirements
echo ========================================
echo Installing requirements...
echo ========================================
echo This may take a few minutes...
echo.

env\Scripts\pip.exe install --upgrade pip
env\Scripts\pip.exe install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo ERROR: Failed to install requirements!
    echo ========================================
    echo Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo You can now run the synchronization with:
echo   sync_n2f.bat
echo.
echo Or run tests with:
echo   python tests\run_tests.py
echo.
pause
