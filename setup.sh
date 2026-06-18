#!/bin/bash
# Create a Python virtual environment and install dependencies

echo "Creating virtual environment 'venv'..."
python -m venv venv

echo "Activating virtual environment..."
# Check if we are on Windows (which uses Scripts/) vs Linux/macOS (which uses bin/)
if [ -d "venv/Scripts" ]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing requirements..."
pip install -r requirements.txt

echo "Setup completed successfully!"
