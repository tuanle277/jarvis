import speech_recognition as sr
from gtts import gTTS
import os
import simpleaudio as sa
import time
import threading
from transformers import pipeline, Conversation

# Initialize the conversational pipeline with DialoGPT
chatbot = pipeline('conversational', model='microsoft/DialoGPT-medium')

def recognize_speech():
    """Transcribes speech from the microphone."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for 1 second

        # Uncomment these lines if you have sound files:
        # play_sound("listening.wav")
        print("Listening..., please speak soundly and clearly")
        audio = recognizer.listen(source)

        # Uncomment these lines if you have sound files:
        # play_sound("processing.wav")

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return ""
    except sr.RequestError as e:  # Catch RequestError specifically
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

def get_response(prompt, conversation_history):
    """Generates a response using DialoGPT for conversational responses."""
    conversation = Conversation(prompt)
    conversation_history.append(conversation)
    response = chatbot(conversation_history)

    return response[-1]["content"]

def speak(text):
    """Converts text to speech and plays it."""
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 -q response.mp3")  # Use mpg123 if mpg321 isn't available

def play_sound(file_name):
    """Plays a sound file (WAV or MP3) if it exists."""
    try:
        wave_obj = sa.WaveObject.from_wave_file(file_name)
        play_obj = wave_obj.play()
        play_obj.wait_done()
    except FileNotFoundError:
        print(f"Sound file not found: {file_name}")

def chatbot(prompt, conversation_history=[]):
    while True:
        command = recognize_speech()
        conversation_history = []
        if command:
            response_text = get_response(command, conversation_history)
            print("Reponse is basically something like:", response_text)
            if response_text in set(["shut down", "bye bye"]):
                print("break now")
                exit()

            print(f"DialoGPT Response: {response_text}")
            speak(response_text)
        else:
            speak("I didn't catch that. Please try again.")


def listen_for_wake_word(wake_word, recognizer, microphone, conversation_history=[]):
    while True:
        print("Say the wake word...")
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            speech_text = recognizer.recognize_google(audio).lower()
            if wake_word in speech_text:
                print("Wake word detected!")
                speak("How can I help you?")
                command = recognize_speech()
                if command:
                    response_text = get_response(command, conversation_history)
                    print(f"DialoGPT Response: {response_text}")
                    speak(response_text)
                else:
                    speak("I didn't catch that. Please try again.")
            else:
                print("Wake word not detected. Listening again...")

        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("Sorry, my speech service is down.")

        time.sleep(1)  # Pause for a short moment before listening again

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    conversation_history = []

    wake_word = "hey jarvis"

    # Run the wake word listener in a daemon thread
    wake_word_thread = threading.Thread(target=listen_for_wake_word, args=(wake_word, recognizer, microphone, conversation_history))
    wake_word_thread.daemon = True
    wake_word_thread.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down JARVIS.")

if __name__ == "__main__":
    main()



    # conversation_history = []
    # print(get_response("Hello, How are you", conversation_history))
