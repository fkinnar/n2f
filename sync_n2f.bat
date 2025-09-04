@echo off
REM ========================================
REM N2F Synchronization Script
REM ========================================
REM This batch file runs the N2F synchronization script.
REM Logging is handled by the Python application itself.

echo Starting N2F synchronization...
echo.

REM Set environment variables for encoding
set PYTHONIOENCODING=utf-8

REM Check if virtual environment exists
if not exist "env\Scripts\python.exe" (
    echo ========================================
    echo ERROR: Virtual environment not found!
    echo ========================================
    echo Please create a virtual environment first:
    echo python -m venv env
    echo.
    echo Then activate it and install requirements:
    echo env\Scripts\activate
    echo pip install -e .[dev]
    echo.
    pause
    exit /b 1
)

REM Run the synchronization script using virtual environment Python
echo Running synchronization script...
echo Using Python from virtual environment...
env\Scripts\python.exe src\sync_agresso_n2f.py %*

REM Check if the script ran successfully
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Synchronization completed successfully!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Synchronization failed with error code: %ERRORLEVEL%
    echo ========================================
)

echo.
echo Batch file completed.
pause
