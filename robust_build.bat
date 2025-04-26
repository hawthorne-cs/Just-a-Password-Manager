@echo off
echo ===== Password Manager Build Script =====
echo.

REM Check Python installation
echo Checking Python installation...
python --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python and ensure it's added to your PATH
    goto :fail
)

REM Find pip path and ensure pip is installed
echo Finding pip...
python -m pip --version 2>nul
if %errorlevel% neq 0 (
    echo ERROR: pip not found
    echo Please ensure pip is installed with your Python installation
    goto :fail
)

REM Install or update PyInstaller
echo Installing/updating PyInstaller...
python -m pip install --upgrade --user pyinstaller
if %errorlevel% neq 0 (
    echo WARNING: Failed to install PyInstaller with --user flag
    echo Trying without --user flag...
    python -m pip install --upgrade pyinstaller
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install PyInstaller
        goto :fail
    )
)

REM Check if PyInstaller is now in PATH
echo Checking PyInstaller installation...
pyinstaller --version 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller command not in PATH, using python -m pyinstaller instead
    set PYINSTALLER_CMD=python -m PyInstaller
) else (
    set PYINSTALLER_CMD=pyinstaller
)

REM Print the PyInstaller version for diagnostic purposes
echo Using PyInstaller:
%PYINSTALLER_CMD% --version

REM Build the application
echo.
echo Building Password Manager executable...
%PYINSTALLER_CMD% --clean --name="Password Manager" --windowed --icon=key.ico --add-data="key.ico;." --add-data="lock.png;." --noconsole main.py

REM Check if build was successful
if exist "dist\Password Manager\Password Manager.exe" (
    echo.
    echo Build successful! Executable created at:
    echo dist\Password Manager\Password Manager.exe
    echo.
    echo You can now run create_shortcut.bat to create a desktop shortcut.
) else (
    echo.
    echo Build failed. Please check the errors above.
    goto :fail
)

echo.
echo Build completed successfully!
goto :end

:fail
echo.
echo ===== BUILD FAILED =====
echo.
echo Try the following:
echo 1. Open a command prompt as Administrator
echo 2. Run: pip install pyinstaller
echo 3. Close and reopen your command prompt
echo 4. Try running this script again
echo.
echo If that doesn't work, you can try installing manually:
echo pip install --user pyinstaller
echo.
echo Or check if your Python installation is in PATH by running:
echo where python

:end
pause 