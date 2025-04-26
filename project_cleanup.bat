@echo off
echo Cleaning up project structure...

REM Create directory structure if it doesn't exist
if not exist src mkdir src
if not exist docs mkdir docs
if not exist scripts mkdir scripts

REM Move source code to src directory
echo Moving source files to src directory...
move /y main.py src\ 2>nul
move /y database.py src\ 2>nul
move /y password_generator.py src\ 2>nul
move /y utils.py src\ 2>nul

REM Move documentation to docs directory
echo Moving documentation to docs directory...
move /y README.md docs\ 2>nul
move /y IMPLEMENTATION_GUIDE.md docs\ 2>nul
copy /y docs\README.md README.md 2>nul

REM Move scripts to scripts directory
echo Moving build and utility scripts to scripts directory...
move /y build.bat scripts\ 2>nul
move /y build_app.py scripts\ 2>nul
move /y create_shortcut.bat scripts\ 2>nul
move /y run.bat scripts\ 2>nul
move /y run.sh scripts\ 2>nul

REM Create a new simplified run.bat in root directory
echo Creating new simplified run.bat...
echo @echo off > run.bat
echo echo Starting Password Manager... >> run.bat
echo. >> run.bat
echo python src\main.py >> run.bat
echo. >> run.bat
echo if %%errorlevel%% neq 0 ( >> run.bat
echo   echo Error: Failed to start application. >> run.bat
echo   echo Please make sure Python and all dependencies are installed. >> run.bat
echo   echo. >> run.bat
echo   echo Installing dependencies... >> run.bat
echo   python -m pip install -r requirements.txt >> run.bat
echo   echo. >> run.bat
echo   echo Trying to start application again... >> run.bat
echo   python src\main.py >> run.bat
echo ) >> run.bat
echo. >> run.bat
echo pause >> run.bat

REM Create a new simplified build.bat in root directory
echo Creating new simplified build.bat...
echo @echo off > build.bat
echo echo Starting build process... >> build.bat
echo. >> build.bat
echo scripts\build.bat >> build.bat

REM Clean up temporary files
echo Cleaning up temporary files...
del /q simple_build.bat 2>nul
del /q robust_build.bat 2>nul
del /q build_with_python.bat 2>nul
del /q Password_Manager.spec 2>nul

REM Update imports in main.py
echo Updating imports in source files...
powershell -Command "(Get-Content src\main.py) -replace 'from database import Database', 'from src.database import Database' -replace 'from password_generator import PasswordGenerator', 'from src.password_generator import PasswordGenerator' -replace 'from utils import', 'from src.utils import' | Set-Content src\main.py"

echo.
echo Project cleanup complete!
echo.
echo New structure:
echo - src\     : Source code files
echo - docs\    : Documentation
echo - scripts\ : Build and utility scripts
echo.
echo Use run.bat to start the application
echo Use build.bat to build the executable
echo.
pause 