@echo off
echo Starting Just a Password Manager...
echo.

rem Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b
)

rem Check if virtual environment exists, if not create one
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        pause
        exit /b
    )
)

rem Activate virtual environment and install requirements
echo Activating virtual environment...
call venv\Scripts\activate

echo Updating pip...
python -m pip install --upgrade pip

echo Installing packages individually...
pip install pyperclip
pip install cryptography
pip install pycryptodome
pip install Pillow --only-binary Pillow

echo All packages installed.

rem Run the application
echo Starting application...
python main.py
if %errorlevel% neq 0 (
    echo Application failed to start.
    echo.
    echo If you see "ModuleNotFoundError", try running:
    echo pip install pyperclip cryptography pycryptodome Pillow
    pause
    exit /b
)

rem Deactivate virtual environment
call venv\Scripts\deactivate

pause 