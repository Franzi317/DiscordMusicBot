#!/bin/bash

echo "Starting Discord Music Bot..."
echo ""
echo "Make sure you have:"
echo "1. Created a .env file with your DISCORD_TOKEN"
echo "2. Installed all requirements (pip install -r requirements.txt)"
echo "3. Installed FFmpeg"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one with your DISCORD_TOKEN."
    echo "Press Enter to continue anyway..."
    read
fi

echo "Starting bot with $PYTHON_CMD..."
$PYTHON_CMD main.py

echo ""
echo "Bot has stopped."
