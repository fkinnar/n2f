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

REM Create logs directory if it doesn't exist
if not exist "python\logs" mkdir python\logs

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
env\Scripts\python.exe python\sync-agresso-n2f.py %* > "python\logs\sync_%timestamp%.log" 2>&1

REM Check if the script ran successfully
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Synchronization completed successfully!
    echo ========================================
    echo Log file: python\logs\sync_%timestamp%.log
    echo.
    echo Press any key to open the log file...
    pause > nul
    start notepad "python\logs\sync_%timestamp%.log"
) else (
    echo.
    echo ========================================
    echo Synchronization failed with error code: %ERRORLEVEL%
    echo ========================================
    echo Log file: python\logs\sync_%timestamp%.log
    echo.
    echo Press any key to open the log file...
    pause > nul
    start notepad "python\logs\sync_%timestamp%.log"
)

echo.
echo Batch file completed.
