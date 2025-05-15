import os
import subprocess
import logging
import winreg
from typing import Optional, Tuple, Dict, List
from pathlib import Path

class AppLauncher:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.common_apps = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "word": "winword.exe",
            "excel": "excel.exe",
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
            "explorer": "explorer.exe",
            "taskmgr": "taskmgr.exe",
            "control": "control.exe",
            "regedit": "regedit.exe",
            "mspaint": "mspaint.exe",
            "calc": "calc.exe",
            "notepad++": r"C:\Program Files\Notepad++\notepad++.exe",
            "vscode": r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
            "spotify": r"C:\Users\{}\AppData\Roaming\Spotify\Spotify.exe".format(os.getenv('USERNAME')),
            "discord": r"C:\Users\{}\AppData\Local\Discord\app-*\Discord.exe".format(os.getenv('USERNAME'))
        }
        self._cache_app_paths()
        
    def _cache_app_paths(self):
        """Cache common application paths from registry and common locations."""
        try:
            # Add applications from registry
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths") as key:
                i = 0
                while True:
                    try:
                        app_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, app_name) as app_key:
                            try:
                                path = winreg.QueryValue(app_key, None)
                                if path and os.path.exists(path):
                                    self.common_apps[app_name.lower().replace('.exe', '')] = path
                            except WindowsError:
                                pass
                        i += 1
                    except WindowsError:
                        break
        except Exception as e:
            self.logger.error(f"Error caching app paths: {str(e)}")

    def _find_app_in_path(self, app_name: str) -> Optional[str]:
        """Find application in system PATH."""
        try:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_path = os.path.join(path, f"{app_name}.exe")
                if os.path.exists(exe_path):
                    return exe_path
        except Exception as e:
            self.logger.error(f"Error searching PATH: {str(e)}")
        return None

    def _find_app_in_program_files(self, app_name: str) -> Optional[str]:
        """Search for application in Program Files directories."""
        program_files_paths = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs"),
            os.path.join(os.environ.get("APPDATA", ""), "Programs")
        ]
        
        for base_path in program_files_paths:
            if not os.path.exists(base_path):
                continue
                
            for root, _, files in os.walk(base_path):
                for file in files:
                    if file.lower().startswith(app_name.lower()) and file.endswith('.exe'):
                        return os.path.join(root, file)
        return None

    def launch_application(self, app_name: str) -> Tuple[bool, str]:
        """
        Attempts to launch a desktop application.
        
        Args:
            app_name (str): Name of the application to launch
            
        Returns:
            Tuple[bool, str]: (Success status, Message)
        """
        try:
            app_name = app_name.lower().strip()
            
            # Check if it's a common application
            if app_name in self.common_apps:
                app_path = self.common_apps[app_name]
                if '*' in app_path:  # Handle wildcard paths
                    import glob
                    matches = glob.glob(app_path)
                    if matches:
                        app_path = matches[0]
                if os.path.exists(app_path):
                    subprocess.Popen(app_path)
                    return True, f"Successfully launched {app_name}"
            
            # Try to find in PATH
            path_app = self._find_app_in_path(app_name)
            if path_app:
                subprocess.Popen(path_app)
                return True, f"Successfully launched {app_name}"
            
            # Try to find in Program Files
            program_files_app = self._find_app_in_program_files(app_name)
            if program_files_app:
                subprocess.Popen(program_files_app)
                return True, f"Successfully launched {app_name}"
            
            return False, f"Could not find application: {app_name}"
            
        except Exception as e:
            self.logger.error(f"Error launching application {app_name}: {str(e)}")
            return False, f"Error launching {app_name}: {str(e)}"
    
    def get_installed_apps(self) -> List[str]:
        """
        Returns a list of installed applications.
        
        Returns:
            List[str]: List of application names
        """
        return list(self.common_apps.keys())

# Create a singleton instance
app_launcher = AppLauncher() 