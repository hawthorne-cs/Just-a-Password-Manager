@echo off
echo Building Password Manager executable...
echo.

rem Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
    if %errorlevel% neq 0 (
        echo Failed to install PyInstaller.
        pause
        exit /b
    )
)

echo.
echo Creating executable...
pyinstaller --clean --name="Password Manager" --windowed --icon=key.ico --add-data="key.ico;." --add-data="lock.png;." --noconsole main.py

echo.
if exist "dist\Password Manager\Password Manager.exe" (
    echo Build successful! Executable created at:
    echo dist\Password Manager\Password Manager.exe
    echo.
    echo You can now run create_shortcut.bat to create a desktop shortcut.
) else (
    echo Build failed. Check for errors above.
)

pause 