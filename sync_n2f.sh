#!/bin/bash
# ========================================
# N2F Synchronization Script
# ========================================
# This shell script runs the N2F synchronization script.
# Logging is handled by the Python application itself.

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

# Run the synchronization script using virtual environment Python
echo "Running synchronization script..."
echo "Using Python from virtual environment..."
env/bin/python src/sync_agresso_n2f.py "$@"

# Check if the script ran successfully
if [ $? -eq 0 ]; then
    echo
    echo "========================================"
    echo "Synchronization completed successfully!"
    echo "========================================"
else
    echo
    echo "========================================"
    echo "Synchronization failed with error code: $?"
    echo "========================================"
fi

echo
echo "Shell script completed."
