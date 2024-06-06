
import subprocess

class AppleScriptModule:
    @staticmethod
    def execute_applescript(script):
        """Executes an AppleScript command."""
        process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise Exception(f"AppleScript error: {stderr.decode('utf-8')}")
        return stdout.decode('utf-8')

    @staticmethod
    def open_application(app_name):
        """Opens an application by name."""
        script = f'tell application "{app_name}" to activate'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def set_volume(volume_level):
        """Sets the system volume to a specified level (0-100)."""
        script = f'set volume output volume {volume_level}'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def mute_volume():
        """Mutes the system volume."""
        script = 'set volume with output muted'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def unmute_volume():
        """Unmutes the system volume."""
        script = 'set volume without output muted'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def get_volume():
        """Gets the current system volume."""
        script = 'output volume of (get volume settings)'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def display_dialog(message):
        """Displays a dialog with a specified message."""
        script = f'display dialog "{message}"'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def display_notification(message, title):
        """Displays a notification with a specified message and title."""
        script = f'display notification "{message}" with title "{title}"'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def create_folder(folder_name):
        """Creates a new folder on the desktop with the specified name."""
        script = f'tell application "Finder" to make new folder at desktop with properties {{name:"{folder_name}"}}'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def move_file(source, destination):
        """Moves a file from source to destination."""
        script = f'tell application "Finder" to move file "{source}" to folder "{destination}"'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def delete_file(file_path):
        """Deletes a file at the specified path."""
        script = f'tell application "Finder" to delete file "{file_path}"'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def get_current_time():
        """Gets the current date and time."""
        script = 'get (current date) as string'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def get_battery_status():
        """Gets the current battery status."""
        script = 'do shell script "pmset -g batt | grep -Eo \\"\\d+%\\""'  # Shell script to get battery status
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def get_network_info():
        """Gets the current network information."""
        script = 'do shell script "ifconfig en0"'  # Shell script to get network information
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def open_finder_window():
        """Opens a new Finder window."""
        script = 'tell application "Finder" to make new Finder window'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def get_frontmost_finder_path():
        """Gets the path of the frontmost Finder window."""
        script = 'tell application "Finder" to get POSIX path of (target of front Finder window as alias)'
        return AppleScriptModule.execute_applescript(script)

    @staticmethod
    def close_all_finder_windows():
        """Closes all Finder windows."""
        script = 'tell application "Finder" to close every window'
        return AppleScriptModule.execute_applescript(script)
