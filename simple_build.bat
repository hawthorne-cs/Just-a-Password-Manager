@echo off
echo Building Password Manager executable...
echo.

echo Make sure PyInstaller is installed with:
echo pip install --user pyinstaller
echo.

echo Creating executable...
python -m PyInstaller --clean --name="Password Manager" --windowed --icon=key.ico --add-data="key.ico;." --add-data="lock.png;." --noconsole main.py

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