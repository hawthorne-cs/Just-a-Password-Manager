"""
Build script for Password Manager application
This script installs PyInstaller if needed and builds the application
"""
import os
import sys
import subprocess
import platform

def run_command(command):
    """Run a command and return the result"""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)
    return result

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    pip_command = [sys.executable, "-m", "pip", "install", "--upgrade", "pyinstaller"]
    result = run_command(pip_command)
    
    if result.returncode != 0:
        print("Failed to install PyInstaller. Trying with --user flag...")
        pip_command = [sys.executable, "-m", "pip", "install", "--upgrade", "--user", "pyinstaller"]
        result = run_command(pip_command)
        
    if result.returncode != 0:
        print("ERROR: Failed to install PyInstaller")
        print("Error details:")
        print(result.stderr)
        return False
        
    return True

def build_app():
    """Build the application using PyInstaller"""
    print("\nBuilding Password Manager application...")
    
    # Determine system-specific options
    icon_option = "key.ico"
    separator = ";" if platform.system() == "Windows" else ":"
    
    # Build the PyInstaller command
    pyinstaller_command = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--name=Password Manager",
        "--windowed",
        f"--icon={icon_option}",
        f"--add-data=key.ico{separator}.",
        f"--add-data=lock.png{separator}.",
        "--noconsole",
        "main.py"
    ]
    
    # Run PyInstaller
    result = run_command(pyinstaller_command)
    
    if result.returncode != 0:
        print("ERROR: PyInstaller failed to build the application")
        print("Error details:")
        print(result.stderr)
        return False
        
    # Check if executable was created
    exe_extension = ".exe" if platform.system() == "Windows" else ""
    executable_path = os.path.join("dist", "Password Manager", f"Password Manager{exe_extension}")
    
    if os.path.exists(executable_path):
        print("\nBuild successful!")
        print(f"Executable created at: {executable_path}")
        
        if platform.system() == "Windows":
            print("\nYou can now run create_shortcut.bat to create a desktop shortcut.")
        
        return True
    else:
        print("\nERROR: Executable not found after build")
        return False

def main():
    """Main function"""
    print("===== Password Manager Build Script =====\n")
    
    # Install PyInstaller if needed
    if not install_pyinstaller():
        print("\nFailed to install PyInstaller. Cannot continue.")
        return False
    
    # Build the application
    if not build_app():
        print("\nFailed to build the application.")
        return False
    
    print("\nBuild process completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n===== BUILD FAILED =====")
        print("\nTry the following:")
        print("1. Make sure Python is properly installed")
        print("2. Make sure pip is working (python -m pip --version)")
        print("3. Try installing PyInstaller manually: python -m pip install pyinstaller")
        print("4. Run this script again")
        
    input("\nPress Enter to continue...") 