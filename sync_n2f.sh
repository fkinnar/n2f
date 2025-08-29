#!/bin/bash
# ========================================
# N2F Synchronization Script
# ========================================
# This shell script runs the N2F synchronization script
# with proper log redirection and error handling

echo "Starting N2F synchronization..."
echo

# Set environment variables for encoding
export PYTHONIOENCODING=utf-8

# Check if virtual environment exists
if [ ! -f "env/bin/python" ]; then
    echo "========================================"
    echo "ERROR: Virtual environment not found!"
    echo "========================================"
    echo "Please run setup.sh first to create the environment:"
    echo "./setup.sh"
    echo
    exit 1
fi

# Check if requirements are installed
echo "Checking if requirements are installed..."
env/bin/python -c "import pandas, requests, yaml, sqlalchemy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "========================================"
    echo "Installing requirements..."
    echo "======================================="
    echo "This may take a few minutes..."
    echo
    env/bin/pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "========================================"
        echo "ERROR: Failed to install requirements!"
        echo "========================================"
        echo "Please check your internet connection and try again."
        echo
        exit 1
    fi
    echo
    echo "Requirements installed successfully!"
    echo
else
    echo "Requirements are already installed."
    echo
fi

# Create logs directory if it doesn't exist
if [ ! -d "python/logs" ]; then
    mkdir -p python/logs
fi

# Generate timestamp for log files
timestamp=$(date +"%y%m%d_%H%M%S")

# Run the synchronization script with log redirection using virtual environment Python
echo "Running synchronization script..."
echo "Using Python from virtual environment..."
env/bin/python python/sync-agresso-n2f.py "$@" > "python/logs/sync_${timestamp}.log" 2>&1

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "Synchronization completed successfully!"
    echo "========================================"
    echo "Log file: python/logs/sync_${timestamp}.log"
    echo
    echo "Press Enter to open the log file..."
    read
    if command -v xdg-open &> /dev/null; then
        xdg-open "python/logs/sync_${timestamp}.log"
    elif command -v open &> /dev/null; then
        open "python/logs/sync_${timestamp}.log"
    else
        echo "Log file: python/logs/sync_${timestamp}.log"
    fi
else
    echo
    echo "========================================"
    echo "Synchronization failed with error code: $?"
    echo "========================================"
    echo "Log file: python/logs/sync_${timestamp}.log"
    echo
    echo "Press Enter to open the log file..."
    read
    if command -v xdg-open &> /dev/null; then
        xdg-open "python/logs/sync_${timestamp}.log"
    elif command -v open &> /dev/null; then
        open "python/logs/sync_${timestamp}.log"
    else
        echo "Log file: python/logs/sync_${timestamp}.log"
    fi
fi

echo
echo "Shell script completed."
