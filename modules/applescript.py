import subprocess
import speech_recognition as sr
import threading
import time

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

    def listen_for_wake_word(self, wake_word, recognizer, microphone, callback):
        """Continuously listens for the wake word and calls the callback function when detected."""
        while True:
            print("Say the wake word...")
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            try:
                speech_text = recognizer.recognize_google(audio).lower()
                if wake_word in speech_text:
                    print("Wake word detected!")
                    callback()
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError:
                print("Sorry, my speech service is down.")

            time.sleep(1)  # Pause for a short moment before listening again

    def start_listening(self, wake_word, callback):
        """Starts the background thread to listen for the wake word."""
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        listen_thread = threading.Thread(target=self.listen_for_wake_word, args=(wake_word, recognizer, microphone, callback))
        listen_thread.daemon = True
        listen_thread.start()
        print("Listening for wake word...")

    @staticmethod
    def run_main_py():
        """Runs the main.py script in the same folder."""
        try:
            subprocess.run(['python3', 'main.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running main.py: {e}")

# Example usage
def on_wake_word_detected():
    print("Wake word callback executed")
    AppleScriptModule.run_main_py()

if __name__ == "__main__":
    asm = AppleScriptModule()
    asm.start_listening("hey jarvis", on_wake_word_detected)
    # Keep the main thread alive
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down JARVIS.")
