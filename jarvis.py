import speech_recognition as sr
from gtts import gTTS
import os
import simpleaudio as sa
import time
import threading
from transformers import pipeline, Conversation

class JARVIS:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.conversation_history = []
        self.chatbot = pipeline('conversational', model='microsoft/DialoGPT-medium')
        self.wake_word = "hey jarvis"

    def recognize_speech(self):
        """Transcribes speech from the microphone."""
        with self.microphone as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Listening... please speak soundly and clearly")
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

    def get_response(self, prompt):
        """Generates a response using DialoGPT for conversational responses."""
        conversation = Conversation(prompt)
        self.conversation_history.append(conversation)
        response = self.chatbot(self.conversation_history)
        return response[-1]["content"]

    def speak(self, text):
        """Converts text to speech and plays it."""
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        os.system("mpg321 -q response.mp3")  # Use mpg123 if mpg321 isn't available

    def play_sound(self, file_name):
        """Plays a sound file (WAV or MP3) if it exists."""
        try:
            wave_obj = sa.WaveObject.from_wave_file(file_name)
            play_obj = wave_obj.play()
            play_obj.wait_done()
        except FileNotFoundError:
            print(f"Sound file not found: {file_name}")

    def chatbot_loop(self):
        while True:
            command = self.recognize_speech()
            if command:
                response_text = self.get_response(command)
                print(f"DialoGPT Response: {response_text}")
                if response_text in {"shut down", "bye bye"}:
                    print("Shutting down JARVIS.")
                    break
                self.speak(response_text)
            else:
                self.speak("I didn't catch that. Please try again.")

    def listen_for_wake_word(self):
        while True:
            print("Say the wake word...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio = self.recognizer.listen(source)

            try:
                speech_text = self.recognizer.recognize_google(audio).lower()
                if self.wake_word in speech_text:
                    print("Wake word detected!")
                    self.speak("How can I help you?")
                    command = self.recognize_speech()
                    if command:
                        response_text = self.get_response(command)
                        print(f"DialoGPT Response: {response_text}")
                        self.speak(response_text)
                    else:
                        self.speak("I didn't catch that. Please try again.")
                else:
                    print("Wake word not detected. Listening again...")
            except sr.UnknownValueError:
                print("Sorry, I could not understand the audio.")
            except sr.RequestError:
                print("Sorry, my speech service is down.")

            time.sleep(1)  # Pause for a short moment before listening again

    def start(self):
        wake_word_thread = threading.Thread(target=self.listen_for_wake_word)
        wake_word_thread.daemon = True
        wake_word_thread.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Shutting down JARVIS.")

if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.start()
