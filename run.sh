#!/bin/bash

echo "Starting Just a Password Manager..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed. Please install Python 3 to use this application."
    echo "For more information, visit https://www.python.org/downloads/"
    exit 1
fi

# Check if virtual environment exists, if not create one
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment and install requirements
echo "Installing required packages..."
source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

# Run the application
echo "Starting application..."
python3 main.py

# Deactivate virtual environment
deactivate 