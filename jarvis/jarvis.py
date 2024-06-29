import os
import time
import threading
import logging
from transformers import pipeline, Conversation

from modules.talk import TalkModule
from modules.system_commands.commands import ScriptModule
from modules.chatbot import ChatBotModule
from modules.cv import detect_and_recognize_face  # Import the face recognition function

class JARVIS:
    def __init__(self):
        self.talk_module = TalkModule()
        self.script_module = ScriptModule()
        self.chatbot_module = ChatBotModule(model_type="diablo")
        self.wake_word = "hey jarvis"
        self.running = True

        logging.basicConfig(
            filename='jarvis.log',
            level=logging.DEBUG,
            format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def recognize_speech(self):
        """Listen for a command and return the recognized text."""
        try:
            file_name = "command.wav"
            self.talk_module.record_audio(file_name, duration=5)
            command = self.talk_module.audio_to_text(file_name)
            return command
        except Exception as e:
            logging.error(f"Error in recognize_speech: {e}")
            return ""

    def speak(self, text):
        """Speak the given text."""
        try:
            self.talk_module.speak(text)
        except Exception as e:
            logging.error(f"Error in speak: {e}")

    def listen_for_wake_word(self):
        """Continuously listen for the wake word and trigger the main loop when detected."""
        while self.running:
            try:
                command = self.recognize_speech()
                if self.wake_word in command.lower():
                    if detect_and_recognize_face():
                        self.speak("Good morning Mr. Kevin. How can I help you?")
                        self.main_loop()
                    else:
                        self.speak("Face not recognized.")
            except Exception as e:
                logging.error(f"Error in listen_for_wake_word: {e}")

    def execute_command(self, command):
        """Try to execute a system command, return True if successful."""
        try:
            command_function = self.script_module.get_command(command)
            command_function()
            return True
        except Exception as e:
            logging.error(f"Command not recognized or failed to execute: {e}")
            return False

    def get_response(self, prompt):
        """Get a response from the chatbot module."""
        try:
            return self.chatbot_module.get_response(prompt)
        except Exception as e:
            logging.error(f"Error in get_response: {e}")
            return "I'm sorry, I couldn't process that request."

    def main_loop(self):
        """Listen for commands and handle them appropriately."""
        while self.running:
            try:
                command = self.recognize_speech()
                if command:
                    if self.execute_command(command):
                        self.speak("Command executed successfully.")
                    else:
                        response_text = self.get_response(command)
                        print(f"Chatbot Response: {response_text}")
                        self.speak(response_text)
                        if "shut down" in response_text.lower():
                            logging.info("Shutting down JARVIS.")
                            self.speak("Goodbye.")
                            self.running = False
                            break
                else:
                    self.speak("I didn't catch that. Please try again.")
            except Exception as e:
                logging.error(f"Error in main_loop: {e}")

    def start_visual_indicator(self):
        """Start a visual indicator to show the service is running."""
        def visual_indicator():
            while self.running:
                for c in '|/-\\':
                    sys.stdout.write(f'\rJARVIS is running... {c}')
                    sys.stdout.flush()
                    time.sleep(0.1)
            sys.stdout.write('\rJARVIS has stopped.     \n')
            sys.stdout.flush()

        indicator_thread = threading.Thread(target=visual_indicator)
        indicator_thread.daemon = True
        indicator_thread.start()

    def start(self):
        """Start the JARVIS system."""
        self.start_visual_indicator()
        wake_word_thread = threading.Thread(target=self.listen_for_wake_word)
        wake_word_thread.daemon = True
        wake_word_thread.start()

        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("Shutting down JARVIS.")
            self.speak("Shutting down.")
            self.running = False

if __name__ == "__main__":
    import sys
    jarvis = JARVIS()
    jarvis.start()
