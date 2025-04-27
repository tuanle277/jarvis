#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Voice Controlled Screen Analyzer using Gemini

Listens for a wake word ("Hey Gemini"), then processes commands like
"read the screen" by capturing the screen, sending it to Gemini for analysis,
and speaking the result using Text-to-Speech.

WARNINGS:
- Requires microphone access and potentially internet for speech recognition.
- Speech recognition accuracy varies.
- Wake word detection is basic and inefficient compared to dedicated engines.
- Ensure necessary OS permissions for microphone access.
- Ensure GEMINI_API_KEY environment variable is set.

Usage:
1. Install libraries: pip install SpeechRecognition PyAudio pyttsx3 google-generativeai mss Pillow
   (May require system packages like portaudio - see script comments)
2. Set GEMINI_API_KEY environment variable.
3. Save 'gemini_analyzer.py' in the same directory.
4. Run the script: python your_voice_script_name.py
5. Say "Hey Gemini", wait for the "Yes?" prompt, then say "read the screen".
"""

import speech_recognition as sr
import pyttsx3
import time
import sys
import platform
import mss
from PIL import Image

# Import the Gemini analyzer module
try:
    import gemini
except ImportError:
    print("ERROR: Cannot find 'gemini.py'. Ensure it's in the same directory.")
    sys.exit(1)

# --- Configuration ---
WAKE_WORD = "hey gemini"
# Adjust microphone energy threshold based on your environment noise level
# Higher value means it needs louder sound to start listening.
ENERGY_THRESHOLD = 400 # Default is 300, adjust if needed
# Seconds of non-speaking audio before considering speech complete
PAUSE_THRESHOLD = 0.8

# --- Initialize Text-to-Speech ---
try:
    tts_engine = pyttsx3.init()
    # Optional: Adjust voice properties
    # voices = tts_engine.getProperty('voices')
    # tts_engine.setProperty('voice', voices[1].id) # Example: changing voice
    # tts_engine.setProperty('rate', 150) # Speed percent (can go over 100)
except Exception as e:
    print(f"ERROR: Failed to initialize TTS engine: {e}")
    print("       Text-to-speech will not work.")
    tts_engine = None

def speak(text):
    """Converts text to speech."""
    print(f"Speaking: {text}")
    if tts_engine:
        try:
            tts_engine.say(text)
            tts_engine.runAndWait()
        except Exception as e:
            print(f"ERROR: TTS failed: {e}")
    else:
        print("       (TTS engine not available)")

# --- Initialize Speech Recognition ---
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Adjust recognizer settings
recognizer.energy_threshold = ENERGY_THRESHOLD
recognizer.pause_threshold = PAUSE_THRESHOLD
# recognizer.dynamic_energy_threshold = True # Can sometimes help adapt

def listen_for_audio(prompt="Listening..."):
    """Listens for audio via microphone and returns the transcribed text."""
    print(prompt)
    with microphone as source:
        # recognizer.adjust_for_ambient_noise(source, duration=0.5) # Adjust based on ambient noise - can help
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10) # Added timeouts
        except sr.WaitTimeoutError:
            print("DEBUG: No speech detected within timeout.")
            return None
        except Exception as e:
            print(f"ERROR: Failed during audio listening: {e}")
            return None

    try:
        print("Processing audio...")
        # Using Google Speech Recognition (requires internet)
        text = recognizer.recognize_google(audio)
        print(f"Heard: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("DEBUG: Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"ERROR: Could not request results from Google Speech Recognition service; {e}")
        speak("Sorry, I'm having trouble connecting to the speech service.")
        return None
    except Exception as e:
        print(f"ERROR: Speech recognition failed: {e}")
        return None

# --- Core Capture and Analyze Function (Simplified - No GUI) ---
def capture_and_analyze_screen_for_voice():
    """Captures screen, sends to Gemini for analysis, returns description."""
    print("Capturing screen...")
    try:
        with mss.mss() as sct:
            # Ensure there's at least one monitor besides the aggregate 'all' monitor
            if len(sct.monitors) < 2:
                return "Error: No primary monitor found."
            # Use the first physical monitor (index 1)
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            # Convert to PIL Image for the analyzer module
            img_pil = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            print("Screen captured.")
    except mss.ScreenShotError as ex:
        print(f"ERROR during screen capture: {ex}")
        return f"Error during capture: {ex}"
    except Exception as e:
        print(f"ERROR during screen capture setup: {e}")
        return f"General Capture Error: {e}"

    print("Analyzing screen with Gemini...")
    # The gemini_analyzer module handles API calls and errors internally
    description = gemini.analyze_image_with_gemini(img_pil)
    print("Analysis complete.")
    return description

# --- Main Loop ---
def run_voice_assistant():
    """Main loop to listen for wake word and commands."""
    speak("Voice assistant activated.")

    # Configure Gemini API early
    if not gemini.configure_gemini():
         speak("Error configuring the analysis service. Exiting.")
         sys.exit(1)

    # Calibrate microphone on startup
    with microphone as source:
        print("Calibrating microphone energy threshold...")
        # recognizer.adjust_for_ambient_noise(source, duration=1)
        print(f"Mic calibrated. Energy threshold: {recognizer.energy_threshold:.2f}")


    while True:
        print("-" * 20)
        # Inefficient wake word listening:
        command = listen_for_audio(f"Listening for wake word ('{WAKE_WORD}')...")

        if command and WAKE_WORD in command:
            speak("Yes?")
            action = listen_for_audio("Listening for command...")

            if action and "read the screen" in action:
                speak("Okay, reading the screen. This might take a moment.")
                description = capture_and_analyze_screen_for_voice()

                if description and "error" not in description.lower():
                    speak("Here's what I see:")
                    # Speak potentially long descriptions carefully
                    # Consider splitting long text if TTS struggles
                    speak(description)
                elif description: # Speak the error message if analysis failed
                    speak(description)
                else: # Handle unexpected None case
                    speak("Sorry, I encountered an issue analyzing the screen.")

            elif action and ("what is" in action or "tell me about" in action):
                speak(f"Okay, looking at the screen to answer: {action}")
                description = capture_and_analyze_screen_for_voice()
                
                if description and "error" not in description.lower():
                    # Send the original question along with the screen capture to Gemini
                    img_pil = None
                    with mss.mss() as sct:
                        monitor = sct.monitors[1]
                        sct_img = sct.grab(monitor)
                        img_pil = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    
                    # Customize prompt for question answering
                    answer = gemini.analyze_image_with_gemini(
                        img_pil,
                        f"Please answer this question about the screen: {action}"
                    )
                    speak(answer)
                elif description:
                    speak(description)  # Speak error if analysis failed
                else:
                    speak("Sorry, I encountered an issue analyzing the screen.")

            elif action: # Heard something, but didn't understand
                speak("Sorry, I didn't understand that command.")

            # If no command heard after wake word
            elif action is None:
                 speak("I didn't hear a command.")

        # Optional: Add a command to exit gracefully
        elif command and "exit assistant" in command:
             speak("Goodbye!")
             break

        # Add a small delay to prevent overly tight looping if listening fails quickly
        time.sleep(0.1)


if __name__ == "__main__":
    run_voice_assistant()
