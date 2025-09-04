@echo off
REM ========================================
REM N2F Synchronization Script
REM ========================================
REM This batch file runs the N2F synchronization script
REM with proper log redirection and error handling

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

REM Check if requirements are installed
echo Checking if requirements are installed...
env\Scripts\python.exe -c "import pandas, requests, yaml, sqlalchemy" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ========================================
    echo Installing requirements...
    echo ========================================
    echo This may take a few minutes...
    echo.
env\Scripts\pip.exe install -e .[dev]
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
    echo Requirements installed successfully!
    echo.
) else (
    echo Requirements are already installed.
    echo.
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Generate timestamp for log files
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~2,2%"
set "MM=%dt:~4,2%"
set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%"
set "Min=%dt:~10,2%"
set "Sec=%dt:~12,2%"
set "timestamp=%YYYY%%MM%%DD%_%HH%%Min%%Sec%"

REM Run the synchronization script with log redirection using virtual environment Python
echo Running synchronization script...
echo Using Python from virtual environment...
env\Scripts\python.exe src\sync_agresso_n2f.py %* > "logs\sync_%timestamp%.log" 2>&1

REM Check if the script ran successfully
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Synchronization completed successfully!
    echo ========================================
    echo Log file: logs\sync_%timestamp%.log
    echo.
    echo Press any key to open the log file...
    pause > nul
    start notepad "logs\sync_%timestamp%.log"
) else (
    echo.
    echo ========================================
    echo Synchronization failed with error code: %ERRORLEVEL%
    echo ========================================
    echo Log file: logs\sync_%timestamp%.log
    echo.
    echo Press any key to open the log file...
    pause > nul
    start notepad "logs\sync_%timestamp%.log"
)

echo.
echo Batch file completed.
