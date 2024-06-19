import platform

from apple_command import AppleScriptModule
from windows_command import PowerShellModule 

class ScriptModule:
    def __init__(self):
        self.os_name = platform.system()
        if self.os_name == "Darwin":
            self.module = AppleScriptModule()
        elif self.os_name == "Windows":
            self.module = PowerShellModule()
        else:
            raise Exception(f"Unsupported operating system: {self.os_name}")

        self.command_mapping = {
            'open application': self.module.open_application,
            'set volume': self.module.set_volume,
            'mute volume': self.module.mute_volume,
            'unmute volume': self.module.unmute_volume,
            'get volume': self.module.get_volume,
            'display dialog': self.module.display_dialog,
            'display notification': self.module.display_notification,
            'create folder': self.module.create_folder,
            'move file': self.module.move_file,
            'delete file': self.module.delete_file,
            'get current time': self.module.get_current_time,
            'get battery status': self.module.get_battery_status,
            'get network info': self.module.get_network_info,
            'open finder window': self.module.open_finder_window,
            'get frontmost finder path': self.module.get_frontmost_finder_path,
            'close all finder windows': self.module.close_all_finder_windows,
        }

    def get_command(self, command):
        """Maps a command to the appropriate method."""
        for key in self.command_mapping.keys():
            if key in command:
                return self.command_mapping[key]
        raise Exception(f"Command '{command}' not recognized.")

    def execute_script(self, script):
        return self.module.execute_script(script)

    def open_application(self, app_name):
        return self.module.open_application(app_name)

    def set_volume(self, volume_level):
        return self.module.set_volume(volume_level)

    def mute_volume(self):
        return self.module.mute_volume()

    def unmute_volume(self):
        return self.module.unmute_volume()

    def get_volume(self):
        return self.module.get_volume()

    def display_dialog(self, message):
        return self.module.display_dialog(message)

    def display_notification(self, message, title):
        return self.module.display_notification(message, title)

    def create_folder(self, folder_name):
        return self.module.create_folder(folder_name)

    def move_file(self, source, destination):
        return self.module.move_file(source, destination)

    def delete_file(self, file_path):
        return self.module.delete_file(file_path)

    def get_current_time(self):
        return self.module.get_current_time()

    def get_battery_status(self):
        return self.module.get_battery_status()

    def get_network_info(self):
        return self.module.get_network_info()

    def open_finder_window(self):
        return self.module.open_finder_window()

    def get_frontmost_finder_path(self):
        return self.module.get_frontmost_finder_path()

    def close_all_finder_windows(self):
        return self.module.close_all_finder_windows()

if __name__ == "__main__":
    base_module = ScriptModule()
    
    # Example commands
    commands = [
        "open application Safari",
        "set volume 50",
        "mute volume",
        "unmute volume",
        "get volume",
        "display dialog Hello, World!",
        "display notification Hello, World! with title Greetings",
        "create folder TestFolder",
        "move file /path/to/source.txt to /path/to/destination/",
        "delete file /path/to/source.txt",
        "get current time",
        "get battery status",
        "open finder window",
        "get frontmost finder path",
        "close all finder windows"
    ]

    for command in commands:
        try:
            # Extract command and argument(s) from the command string
            if " " in command:
                cmd, arg = command.split(" ", 1)
            else:
                cmd, arg = command, ""
            
            command_method = base_module.get_command(command)
            
            if cmd == "open application":
                result = command_method(arg)
            elif cmd == "set volume":
                result = command_method(int(arg))
            elif cmd == "display dialog":
                result = command_method(arg)
            elif cmd == "display notification":
                message, title = arg.split(" with title ")
                result = command_method(message, title)
            elif cmd == "create folder":
                result = command_method(arg)
            elif cmd == "move file":
                source, destination = arg.split(" to ")
                result = command_method(source, destination)
            elif cmd == "delete file":
                result = command_method(arg)
            else:
                result = command_method()
            
            print(f"Command: {command} -> Result: {result}")
        except Exception as e:
            print(f"Error executing command '{command}': {e}")
