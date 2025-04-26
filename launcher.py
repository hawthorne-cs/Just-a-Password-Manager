"""
Password Manager Launcher
- Creates desktop shortcut
- Launches the application
"""
import os
import sys
import subprocess
import platform
import importlib.util

def is_module_installed(module_name):
    """Check if a Python module is installed"""
    return importlib.util.find_spec(module_name) is not None

def create_desktop_shortcut():
    """Create a desktop shortcut to the application"""
    try:
        print("Creating desktop shortcut...")
        
        # Get executable path or Python script path
        current_dir = os.path.abspath(os.path.dirname(__file__))
        
        # Check if we're running from the executable or from source
        if getattr(sys, 'frozen', False):
            # Running from executable
            target_path = sys.executable
            icon_path = os.path.join(current_dir, "key.ico")
        else:
            # Running from source
            if os.path.exists(os.path.join(current_dir, "src", "main.py")):
                target_path = f'"{sys.executable}" "{os.path.join(current_dir, "src", "main.py")}"'
            else:
                target_path = f'"{sys.executable}" "{os.path.join(current_dir, "main.py")}"'
            
            icon_path = os.path.join(current_dir, "key.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(current_dir, "src", "key.ico")
        
        if platform.system() == "Windows":
            # Windows shortcut creation
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "Password Manager.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target_path
            shortcut.IconLocation = icon_path
            shortcut.WorkingDirectory = current_dir
            shortcut.save()
            
            print(f"Desktop shortcut created at: {path}")
            return True
        else:
            # Linux/Mac shortcut creation (basic .desktop file)
            home = os.path.expanduser("~")
            desktop = os.path.join(home, "Desktop")
            
            if os.path.exists(desktop):
                desktop_file = os.path.join(desktop, "PasswordManager.desktop")
                
                with open(desktop_file, 'w') as f:
                    f.write("[Desktop Entry]\n")
                    f.write("Type=Application\n")
                    f.write("Name=Password Manager\n")
                    f.write(f"Exec={target_path}\n")
                    f.write(f"Icon={icon_path}\n")
                    f.write("Terminal=false\n")
                
                # Make it executable
                os.chmod(desktop_file, 0o755)
                
                print(f"Desktop shortcut created at: {desktop_file}")
                return True
            else:
                print("Desktop directory not found.")
                return False
    
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        if platform.system() == "Windows":
            print("\nTo create a shortcut manually:")
            print("1. Right-click on Desktop")
            print("2. Select New > Shortcut")
            print(f"3. Enter: {target_path}")
            print("4. Name it 'Password Manager'")
        return False

def launch_app():
    """Launch the password manager application"""
    try:
        print("Launching Password Manager...")
        
        # Check if we're running from the executable
        if getattr(sys, 'frozen', False):
            # Already running from executable
            return
            
        # Running from source, determine path
        current_dir = os.path.abspath(os.path.dirname(__file__))
        
        if os.path.exists(os.path.join(current_dir, "src", "main.py")):
            main_script = os.path.join(current_dir, "src", "main.py")
        else:
            main_script = os.path.join(current_dir, "main.py")
            
        # Import and run
        sys.path.insert(0, os.path.dirname(main_script))
        try:
            if os.path.exists(os.path.join(current_dir, "src")):
                from src.main import main
            else:
                from main import main
            main()
        except ImportError:
            # If import fails, try subprocess
            subprocess.run([sys.executable, main_script])
            
    except Exception as e:
        print(f"Error launching application: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

def main():
    """Main entry point"""
    # Check command line arguments
    create_shortcut = "--create-shortcut" in sys.argv
    
    if create_shortcut:
        print("=== Password Manager Shortcut Creator ===")
        
        # Check for required modules on Windows
        if platform.system() == "Windows":
            for module in ["winshell", "win32com"]:
                if not is_module_installed(module):
                    print(f"Installing required module: {module}")
                    subprocess.run([sys.executable, "-m", "pip", "install", module])
        
        # Create shortcut
        create_desktop_shortcut()
    else:
        # Launch the application
        launch_app()

if __name__ == "__main__":
    main() 