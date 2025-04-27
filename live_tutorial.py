#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Live Tutorial / Walkthrough Assistant (V2 - Threaded & Configurable)

Monitors screen context using Gemini, provides proactive tips from a knowledge base,
and responds to manual tip requests. Uses threading for responsiveness.
"""

import speech_recognition as sr
import pyttsx3
import time
import sys
import platform
import mss
from PIL import Image
import random
import json # For loading config
import threading # For concurrency
import queue # For potential inter-thread communication (optional here)
import os

# Import the updated Gemini analyzer module
try:
    import gemini
except ImportError:
    print("ERROR: Cannot find 'gemini.py'. Ensure it's in the same directory.")
    sys.exit(1)

# --- Default Configuration (can be overridden by config.json) ---
DEFAULT_CONFIG = {
    "WAKE_WORD": "hey gemini",
    "ENERGY_THRESHOLD": 400,
    "PAUSE_THRESHOLD": 0.8,
    "CONTEXT_CHECK_INTERVAL_SECONDS": 30,
    "MIN_TIP_INTERVAL_SECONDS": 120,
    "CONTEXT_PROMPT": """Analyze this screenshot. Identify the main application window visible (e.g., 'Adobe Photoshop', 'Visual Studio Code', 'Google Chrome', 'Finder'). Also, identify the primary task or UI panel the user seems to be interacting with (e.g., 'Layers Panel', 'Debugger Console', 'Editing Document', 'File Browser'). Return the result as 'APP_NAME - CONTEXT_DESCRIPTION'. If unsure, return 'Unknown - Unknown'.""",
    "KNOWLEDGE_BASE_PATH": "knowledge_base.json", # Path to KB file
    "EXIT_COMMAND": "exit assistant"
}

# --- Knowledge Base Example (will be loaded from JSON) ---
DEFAULT_KNOWLEDGE_BASE = {
    "visual_studio_code-editing_document": [
        "Tip: Use Ctrl+Shift+P (Cmd+Shift+P on Mac) to open the Command Palette.",
        "Tip: Multi-cursor editing: Hold Alt (Option on Mac) and click to add cursors.",
    ],
    "unknown-unknown": [
        "I'm not sure what application or context this is.",
    ]
}

class TutorialAssistant:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.knowledge_base = self._load_knowledge_base(self.config["KNOWLEDGE_BASE_PATH"])

        self.tts_engine = self._init_tts()
        self.recognizer, self.microphone = self._init_sr()

        # State variables
        self.current_context = "unknown-unknown"
        self.last_context = "unknown-unknown"
        self.last_proactive_tip_time = 0
        self.context_tip_indices = {ctx: 0 for ctx in self.knowledge_base}
        self.running = True # Flag to control threads

        # Threading locks for shared state access
        self.context_lock = threading.Lock()
        self.tip_time_lock = threading.Lock()
        self.running_lock = threading.Lock()

        # Configure Gemini early
        if not gemini.configure_gemini():
            self.speak("CRITICAL ERROR: Failed to configure Gemini API. Exiting.")
            sys.exit(1)

    def _load_config(self, path):
        """Loads configuration from JSON file, falling back to defaults."""
        try:
            with open(path, 'r') as f:
                user_config = json.load(f)
            # Merge user config with defaults (user config overrides)
            config = {**DEFAULT_CONFIG, **user_config}
            print(f"INFO: Loaded configuration from {path}")
            return config
        except FileNotFoundError:
            print(f"WARN: Config file '{path}' not found. Using default settings.")
            return DEFAULT_CONFIG
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in config file '{path}'. Using default settings.")
            return DEFAULT_CONFIG
        except Exception as e:
            print(f"ERROR: Failed to load config '{path}': {e}. Using default settings.")
            return DEFAULT_CONFIG

    def _load_knowledge_base(self, path):
        """Loads knowledge base from JSON file."""
        try:
            with open(path, 'r') as f:
                kb = json.load(f)
            print(f"INFO: Loaded knowledge base from {path}")
            # Initialize tip indices for loaded contexts
            self.context_tip_indices = {ctx: 0 for ctx in kb}
            return kb
        except FileNotFoundError:
            print(f"WARN: Knowledge base file '{path}' not found. Using empty KB.")
            # Add default unknown context if KB is empty/missing
            return {"unknown-unknown": ["No tips available for unknown contexts."]}
        except json.JSONDecodeError:
            print(f"ERROR: Invalid JSON in knowledge base file '{path}'. Using empty KB.")
            return {"unknown-unknown": ["No tips available for unknown contexts."]}
        except Exception as e:
            print(f"ERROR: Failed to load knowledge base '{path}': {e}. Using empty KB.")
            return {"unknown-unknown": ["No tips available for unknown contexts."]}


    def _init_tts(self):
        """Initializes the Text-to-Speech engine."""
        try:
            engine = pyttsx3.init()
            # Optional: Configure voice properties here if needed
            # engine.setProperty('rate', 160)
            print("INFO: TTS engine initialized.")
            return engine
        except Exception as e:
            print(f"WARN: Failed to initialize TTS engine: {e}. Speech output disabled.")
            return None

    def _init_sr(self):
        """Initializes Speech Recognition components."""
        try:
            r = sr.Recognizer()
            m = sr.Microphone()
            r.energy_threshold = self.config["ENERGY_THRESHOLD"]
            r.pause_threshold = self.config["PAUSE_THRESHOLD"]
            # Calibrate microphone once
            with m as source:
                print("INFO: Calibrating microphone...")
                # r.adjust_for_ambient_noise(source, duration=1)
                print(f"INFO: Mic calibrated. Energy threshold: {r.energy_threshold:.2f}")
            return r, m
        except Exception as e:
            print(f"ERROR: Failed to initialize Speech Recognition: {e}")
            self.speak("ERROR: Could not initialize microphone or speech recognition.")
            sys.exit(1)

    def speak(self, text):
        """Thread-safe speaking method (basic)."""
        # Note: pyttsx3 might have issues if called rapidly from multiple threads.
        # A dedicated TTS queue thread might be needed for complex scenarios.
        print(f"Speaking: {text}")
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except RuntimeError as e:
                 print(f"ERROR: TTS runtime error (possibly busy): {e}")
            except Exception as e:
                 print(f"ERROR: TTS failed: {e}")
        else:
            print("       (TTS engine not available)")

    def listen_for_audio(self, prompt="Listening..."):
        """Listens for audio and returns transcribed text."""
        if not self.is_running(): return None # Check if assistant should still be running
        print(prompt)
        try:
            with self.microphone as source:
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                except sr.WaitTimeoutError: return None # No speech detected
            print("Processing audio...")
            text = self.recognizer.recognize_google(audio)
            print(f"Heard: {text}")
            return text.lower()
        except sr.UnknownValueError: print("DEBUG: Could not understand audio."); return None
        except sr.RequestError as e: print(f"ERROR: SR RequestError; {e}"); self.speak("Speech service connection issue."); return None
        except Exception as e: print(f"ERROR: Listening/SR failed: {e}"); return None

    def capture_screen(self):
        """Captures the primary screen."""
        try:
            with mss.mss() as sct:
                if len(sct.monitors) < 2: print("ERROR: No primary monitor."); return None
                monitor = sct.monitors[1]
                sct_img = sct.grab(monitor)
                img_pil = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                return img_pil
        except Exception as e: print(f"ERROR: Screen capture failed: {e}"); return None

    def identify_context(self):
        """Identifies screen context using Gemini."""
        print("Identifying screen context...")
        screen_image = self.capture_screen()
        if not screen_image: return "unknown-unknown"

        context_desc = gemini.analyze_image_with_gemini(screen_image, prompt=self.config["CONTEXT_PROMPT"])

        if not context_desc or "error" in context_desc.lower():
            print(f"WARN: Context analysis failed: {context_desc}")
            return "unknown-unknown"

        # --- Basic Context Normalization ---
        context_desc_lower = context_desc.lower()
        normalized_context = "unknown-unknown"
        # Try to find a direct match first (case-insensitive keys)
        kb_keys_lower = {k.lower(): k for k in self.knowledge_base}
        for kb_key_lower, original_key in kb_keys_lower.items():
             # A simple check if the Gemini description *contains* a key phrase
             # This is still basic and might misinterpret.
             # Example: If KB key is "vscode-debugger", check if Gemini output contains "visual studio code" and "debugger"
             parts = kb_key_lower.split('-')
             if len(parts) == 2:
                 app_name = parts[0].replace('_', ' ')
                 context_detail = parts[1].replace('_', ' ')
                 if app_name in context_desc_lower and context_detail in context_desc_lower:
                     normalized_context = original_key
                     break # Take the first match
             elif kb_key_lower in context_desc_lower: # Simpler check if key is just one part
                 normalized_context = original_key
                 break

        # Fallback if no specific match, check for app names
        if normalized_context == "unknown-unknown":
             if "visual studio code" in context_desc_lower: normalized_context = "visual_studio_code-editing_document" # Example fallback
             elif "photoshop" in context_desc_lower: normalized_context = "adobe_photoshop-layers_panel" # Example fallback
             elif "chrome" in context_desc_lower: normalized_context = "google_chrome-general_browsing" # Example fallback

        print(f"Identified context (raw): '{context_desc}' -> Normalized: '{normalized_context}'")
        return normalized_context

    def get_tip(self, context):
        """Gets the next tip for the context."""
        if context in self.knowledge_base:
            tips = self.knowledge_base[context]
            if not tips: return None
            with self.context_lock: # Lock to safely access/update shared index
                current_index = self.context_tip_indices.get(context, 0)
                tip = tips[current_index % len(tips)]
                self.context_tip_indices[context] = (current_index + 1)
            return tip
        return None

    def is_running(self):
        """Checks if the assistant should continue running."""
        with self.running_lock:
            return self.running

    def stop(self):
        """Signals the assistant threads to stop."""
        with self.running_lock:
            if self.running:
                print("INFO: Stop signal received.")
                self.running = False

    def _proactive_context_checker(self):
        """Thread target: Periodically checks context and offers tips."""
        global current_context, last_context, last_proactive_tip_time # Access instance vars directly

        while self.is_running():
            now = time.time()
            time_since_last_check = now - getattr(self, 'last_context_check_time', 0)

            if time_since_last_check > self.config["CONTEXT_CHECK_INTERVAL_SECONDS"]:
                self.last_context_check_time = now
                identified_ctx = self.identify_context()

                with self.context_lock: # Lock for reading/writing context and tip time
                    self.current_context = identified_ctx
                    context_changed = (self.current_context != self.last_context)
                    time_since_last_tip = (now - self.last_proactive_tip_time)

                    should_give_tip = self.current_context != "unknown-unknown" and \
                                      (context_changed or time_since_last_tip > self.config["MIN_TIP_INTERVAL_SECONDS"])

                    if should_give_tip:
                        tip = self.get_tip(self.current_context) # get_tip handles its own locking for indices
                        if tip:
                            print(f"Proactively offering tip for context: {self.current_context}")
                            self.speak(tip) # Speak the tip
                            self.last_proactive_tip_time = now # Update last tip time
                        else:
                            print(f"No tips found for context: {self.current_context}")

                    self.last_context = self.current_context # Update last context

            # Sleep briefly to prevent busy-waiting
            time.sleep(1)
        print("INFO: Proactive checker thread finished.")


    def _listen_for_commands(self):
        """Thread target: Listens for wake word and commands."""
        global current_context, last_proactive_tip_time # Access instance vars directly

        while self.is_running():
            command = self.listen_for_audio(f"Listening for '{self.config['WAKE_WORD']}' or '{self.config['EXIT_COMMAND']}'...")

            if not self.is_running(): break # Exit if stop signal received during listen

            if command and self.config["WAKE_WORD"] in command:
                self.speak("Yes?")
                action = self.listen_for_audio("How can I help? (e.g., 'any tips?')")

                if not self.is_running(): break

                if action and ("tip" in action or "advice" in action or "help" in action):
                    with self.context_lock: # Read current context safely
                        ctx_for_tip = self.current_context
                    speak(f"Okay, looking for tips related to {ctx_for_tip.replace('_', ' ')}...")
                    tip = self.get_tip(ctx_for_tip)
                    if tip:
                        self.speak(tip)
                        with self.tip_time_lock: # Lock for writing last tip time
                             self.last_proactive_tip_time = time.time() # Reset proactive timer
                    else:
                        self.speak(f"Sorry, I don't have specific tips for {ctx_for_tip.replace('_', ' ')} right now.")
                elif action:
                    self.speak("Sorry, I didn't understand that command. Ask for 'any tips'.")

            elif command and self.config["EXIT_COMMAND"] in command:
                 self.speak("Goodbye!")
                 self.stop() # Signal other threads to stop
                 break # Exit this thread

            # Small delay if nothing relevant heard
            time.sleep(0.1)
        print("INFO: Command listener thread finished.")


    def run(self):
        """Starts the assistant threads and waits for them to complete."""
        self.speak("Live tutorial assistant activated.")
        self.last_context_check_time = time.time() # Initialize check timer

        # Create threads
        listener_thread = threading.Thread(target=self._listen_for_commands, daemon=True)
        checker_thread = threading.Thread(target=self._proactive_context_checker, daemon=True)

        # Start threads
        listener_thread.start()
        checker_thread.start()

        # Keep the main thread alive while the others run
        # Or implement a more graceful shutdown mechanism
        try:
            while self.is_running():
                # Check if threads are alive, maybe handle unexpected exits
                if not listener_thread.is_alive() or not checker_thread.is_alive():
                     if self.is_running(): # If they died unexpectedly
                          print("ERROR: A worker thread has stopped unexpectedly. Stopping assistant.")
                          self.stop()
                time.sleep(1) # Keep main thread from busy-waiting
        except KeyboardInterrupt:
            print("\nINFO: KeyboardInterrupt received. Stopping assistant.")
            self.stop()

        # Wait for threads to finish (optional, depends on shutdown strategy)
        print("INFO: Waiting for threads to finish...")
        listener_thread.join(timeout=2)
        checker_thread.join(timeout=2)
        print("INFO: Assistant stopped.")


if __name__ == "__main__":
    assistant = TutorialAssistant(config_path="config.json")
    assistant.run()
