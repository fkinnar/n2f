#!/bin/bash
# ========================================
# N2F Project Setup Script
# ========================================
# This shell script sets up the N2F project environment
# Creates virtual environment and installs requirements

echo "========================================"
echo "N2F Project Setup"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "========================================"
    echo "ERROR: Python 3 is not installed or not in PATH!"
    echo "========================================"
    echo "Please install Python 3.8+ from https://python.org"
    echo "or use your system package manager."
    echo
    exit 1
fi

echo "Python found:"
python3 --version
echo

# Check if virtual environment already exists
if [ -d "env/bin/python" ]; then
    echo "========================================"
    echo "Virtual environment already exists!"
    echo "========================================"
    echo "Do you want to recreate it? (y/n)"
    read -r choice
    if [[ $choice =~ ^[Yy]$ ]]; then
        echo "Removing existing virtual environment..."
        rm -rf env
    else
        echo "Skipping virtual environment creation."
        goto_install_requirements=true
    fi
fi

# Create virtual environment if not skipping
if [ "$goto_install_requirements" != "true" ]; then
    echo "========================================"
    echo "Creating virtual environment..."
    echo "========================================"
    python3 -m venv env
    if [ $? -ne 0 ]; then
        echo "========================================"
        echo "ERROR: Failed to create virtual environment!"
        echo "========================================"
        echo "Please check your Python installation."
        echo
        exit 1
    fi
    echo "Virtual environment created successfully!"
    echo
fi

# Install requirements
echo "========================================"
echo "Installing requirements..."
echo "========================================"

# Activate virtual environment
source env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Ask for environment type
echo
echo "Which environment do you want to install?"
echo "  1) Development (includes testing/linting tools) - Default"
echo "  2) Production  (application only)"
read -r -t 15 -p "Enter your choice [1]: " env_choice

case $env_choice in
    2)
        echo
        echo "Installing PRODUCTION requirements..."
        REQ_FILE="requirements.txt"
        ;;
    *)
        echo
        echo "Installing DEVELOPMENT requirements..."
        REQ_FILE="requirements-dev.txt"
        ;;
esac

echo "This may take a few minutes..."
echo

# Install requirements from the selected file
pip install -r "$REQ_FILE"

if [ $? -ne 0 ]; then
    echo "========================================"
    echo "ERROR: Failed to install requirements!"
    echo "========================================"
    echo "Please check your internet connection and try again."
    echo
    exit 1
fi

echo
echo "========================================"
echo "Setup completed successfully!"
echo "========================================"
echo
echo "You can now run the synchronization with:"
echo "  ./sync_n2f.sh"
echo
echo "Or run tests with:"
echo "  python tests/run_tests.py"
echo
echo "Press Enter to continue..."
read
