# text_to_speech.py
from gtts import gTTS
import os

def speak(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")

if __name__ == "__main__":
    speak("Hello, I am JARVIS.")
