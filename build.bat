@echo off
echo ===== Password Manager Build Script =====
echo.

REM Try to build using Python script (most reliable method)
if exist build_app.py (
    echo Building with Python script method...
    python build_app.py
    if %errorlevel% equ 0 (
        goto :success
    ) else (
        echo Python script method failed, trying direct PyInstaller...
    )
) else (
    echo build_app.py not found, trying direct PyInstaller...
)

REM Try direct PyInstaller method
python -m pip install --upgrade --user pyinstaller
python -m PyInstaller --clean --name="Password Manager" --windowed --icon=key.ico --add-data="key.ico;." --add-data="lock.png;." --noconsole main.py

REM Check if build was successful
if exist "dist\Password Manager\Password Manager.exe" (
    goto :success
) else (
    goto :fail
)

:success
echo.
echo Build completed successfully!
echo Executable created at: dist\Password Manager\Password Manager.exe
echo.
echo You can now run create_shortcut.bat to create a desktop shortcut.
goto :end

:fail
echo.
echo ===== BUILD FAILED =====
echo.
echo Please check the error messages above.
echo.
echo Try running as Administrator or check that Python is correctly installed.

:end
pause 