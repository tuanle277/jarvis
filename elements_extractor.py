#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Conceptual Example: Screen Analysis Script using Gemini API and PyAutoGUI Control
with a Scrollable GUI Text Area.

This script captures the screen, sends it to Gemini for analysis, displays the
description in a scrollable text area, and attempts basic screen control.

WARNINGS:
- HIGH RISK: Enables automated screen control. Use with extreme caution and supervision.
- Permissions REQUIRED: Needs OS permissions for screen capture AND accessibility/input control.
- Privacy Risk: Reads screen content.
- Performance Heavy: API calls and potential image searching add latency.
- Dependencies: Requires 'google-generativeai', 'mss', 'Pillow', 'pyautogui'.
  macOS 'all spaces' feature requires 'pyobjc'.
- API Key Needed: Requires 'GEMINI_API_KEY' environment variable.
- Brittle Control: Default control logic uses placeholder actions - MUST be adapted.

Usage:
1. Install libraries:
   pip install mss Pillow google-generativeai pyautogui pyobjc
2. Set 'GEMINI_API_KEY' environment variable.
3. Grant necessary OS permissions (Screen Recording, Accessibility/Input Monitoring).
4. Save 'gemini_analyzer.py' in the same directory.
5. Run the script: python your_script_name.py
6. Supervise carefully! Move mouse to a corner to trigger PyAutoGUI failsafe if needed.
   Close the window to stop.
"""

import mss
import mss.tools
from PIL import Image
import time
import sys
import platform
import os
import tkinter as tk
from tkinter import ttk # Using ttk for a potentially better looking scrollbar
import tkinter.font as tkFont
import io

# Import the Gemini analyzer module
try:
    import gemini 
except ImportError:
    print("ERROR: Cannot find 'gemini.py'. Ensure it's in the same directory.")
    sys.exit(1)

# Import the GUI automation library
try:
    import pyautogui
except ImportError:
    print("ERROR: Cannot import 'pyautogui'. Install it with: pip install pyautogui")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Failed to import pyautogui: {e}")
    print("       GUI automation might not work on this system/environment.")
    sys.exit(1)


# --- macOS Specific Imports ---
MACOS_PYOBJC_AVAILABLE = False
if platform.system() == 'Darwin':
    try:
        import objc
        from AppKit import NSApplication, NSWindowCollectionBehaviorCanJoinAllSpaces
        from ctypes import c_void_p
        MACOS_PYOBJC_AVAILABLE = True
        print("INFO: PyObjC found. Will attempt 'Show on all spaces' for macOS.")
    except ImportError:
        print("INFO: PyObjC not found. 'Show on all spaces' feature disabled.")
    except Exception as e:
        print(f"ERROR: Failed during PyObjC import or setup: {e}")


# --- Configuration ---
CAPTURE_INTERVAL_SECONDS = 15
POPUP_WIDTH = 500
POPUP_HEIGHT = 400
FONT_SIZE = 10

# PyAutoGUI Configuration
pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = True
print(f"INFO: PyAutoGUI Failsafe enabled. Move mouse to a screen corner to stop.")

# --- Global flag to signal exit ---
continue_running = True

# --- Image Preprocessing Function ---
def preprocess_image_for_display(pil_image):
    return pil_image

# --- Core Capture and Analyze Function ---
def capture_and_analyze_screen():
    global continue_running
    if not continue_running: return None
    try:
        with mss.mss() as sct:
            if len(sct.monitors) < 2: return "Error: No primary monitor found."
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img_pil = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
    except mss.ScreenShotError as ex: return f"Error during capture: {ex}"
    except Exception as e: return f"General Capture Error: {e}"

    description = gemini.analyze_image_with_gemini(img_pil)
    if "Error: Invalid Gemini API Key." in description or "Error: Gemini API not configured." in description:
         continue_running = False
    return description


# --- Function to Update GUI, Perform Actions, and Reschedule ---
def perform_scan_update_and_control(root, text_widget): # Changed text_label to text_widget
    """Gets analysis, updates scrollable text area, performs control actions, and reschedules."""
    global continue_running
    if not continue_running: return

    # Update text widget to show analysis is in progress
    try:
        text_widget.config(state='normal') # Enable editing
        text_widget.delete('1.0', tk.END)  # Clear previous content
        text_widget.insert(tk.END, "[Analyzing screen with Gemini...]")
        text_widget.config(state='disabled') # Disable editing
        root.update_idletasks() # Make sure the update is visible
    except tk.TclError: # Handle cases where the window might be closing
        return

    scan_result = capture_and_analyze_screen()

    if not continue_running: # Check if analysis signaled stop
         try:
             # Update text widget one last time with the error before stopping
             if scan_result:
                 text_widget.config(state='normal')
                 text_widget.delete('1.0', tk.END)
                 text_widget.insert(tk.END, scan_result)
                 text_widget.config(state='disabled')
             root.update_idletasks()
         except tk.TclError: pass
         return

    # Update the text widget with Gemini's description or error
    try:
        text_widget.config(state='normal') # Enable editing
        text_widget.delete('1.0', tk.END)  # Clear previous content
        if scan_result is not None:
            text_widget.insert(tk.END, scan_result)
        else:
            text_widget.insert(tk.END, "[Scan Error or Stopped]")
        text_widget.config(state='disabled') # Disable editing
        root.update_idletasks() # Ensure update is visible before potential action
    except tk.TclError: # Handle cases where the window might be closing
        return


    # --- Experimental Control Logic ---
    # (Code remains the same, logic acts on scan_result text)
    if scan_result and continue_running:
        control_action_taken = False
        try:
            analysis_lower = scan_result.lower()
            if "click the ok button" in analysis_lower:
                 print("INFO: Gemini analysis suggests clicking OK. Attempting placeholder click.")
                 # --- REPLACE THIS ---
                 # Option 1: Fixed Coords
                 # pyautogui.click(200, 250)
                 # Option 2: Image Recognition
                 button_location = pyautogui.locateCenterOnScreen('ok_button.png', confidence=0.8)
                 if button_location:
                     pyautogui.click(button_location)
                     print(f"INFO: Clicked OK button found at {button_location}")
                     control_action_taken = True
                 else:
                     print("WARN: 'OK button' mentioned, but image 'ok_button.png' not found.")
                 # --- END REPLACE ---

        except pyautogui.FailSafeException:
             print("ERROR: PyAutoGUI failsafe triggered. Stopping script.")
             continue_running = False
             try: root.destroy()
             except tk.TclError: pass
        except Exception as e:
             print(f"ERROR: Failed to execute pyautogui action: {e}")

    # --- End Experimental Control Logic ---

    # Reschedule the next scan/action
    if continue_running:
        delay_ms = (CAPTURE_INTERVAL_SECONDS * 1000) + (2000 if control_action_taken else 0)
        root.after(delay_ms, lambda: perform_scan_update_and_control(root, text_widget))


# --- Function to make window visible on all macOS spaces ---
# (Code remains the same)
def set_macos_all_spaces(tk_root):
    if platform.system() == 'Darwin' and MACOS_PYOBJC_AVAILABLE:
        try:
            NSApplication.sharedApplication()
            view_id = tk_root.winfo_id()
            ns_view = objc.objc_object(c_void_p=view_id)
            if ns_view is None: return
            ns_window = ns_view.window()
            if ns_window is None: return
            current_behavior = ns_window.collectionBehavior()
            new_behavior = current_behavior | NSWindowCollectionBehaviorCanJoinAllSpaces
            ns_window.setCollectionBehavior_(new_behavior)
        except Exception as e: print(f"WARN: Failed to set 'all spaces' on macOS: {e}")

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Screen Analysis Script Starting (Gemini + PyAutoGUI + Scrollable GUI) ---")
    print("!!! WARNING: Automated screen control enabled. Supervise carefully! !!!")
    print("!!!          Ensure necessary Accessibility/Input permissions are granted. !!!")

    if not gemini.configure_gemini():
         print("ERROR: Gemini configuration failed. Exiting.")
         sys.exit(1)

    print("Initializing GUI...")
    root = tk.Tk()
    root.title("Screen Viewer (Gemini + Control)")
    root.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}")
    root.wm_attributes("-topmost", 1)

    # --- Create Frame for Content ---
    # Use grid layout manager within the frame for easier scrollbar placement
    content_frame = tk.Frame(root, padx=5, pady=5)
    content_frame.pack(fill=tk.BOTH, expand=True)
    content_frame.grid_rowconfigure(0, weight=1)    # Make text area row expandable
    content_frame.grid_columnconfigure(0, weight=1) # Make text area column expandable

    # --- Create Scrollable Text Area ---
    text_font = tkFont.Font(family="Consolas", size=FONT_SIZE)
    text_widget = tk.Text(
        content_frame,
        wrap=tk.WORD, # Wrap lines at word boundaries
        font=text_font,
        state='disabled', # Start read-only
        borderwidth=0, # Optional: remove border
        highlightthickness=0 # Optional: remove focus highlight
    )
    text_widget.grid(row=0, column=0, sticky="nsew") # Place text widget using grid

    # --- Create Scrollbar ---
    scrollbar = ttk.Scrollbar(
        content_frame,
        orient='vertical',
        command=text_widget.yview # Link scrollbar to text widget's view
    )
    scrollbar.grid(row=0, column=1, sticky="ns") # Place scrollbar next to text widget

    # --- Link Text Widget to Scrollbar ---
    text_widget['yscrollcommand'] = scrollbar.set

    # --- Apply macOS Specific Behavior ---
    root.update_idletasks()
    # set_macos_all_spaces(root) # Attempt macOS feature

    # --- Graceful Exit ---
    def on_closing():
        global continue_running
        print("Window closed by user.")
        continue_running = False
        root.after(100, root.destroy)
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # --- Start the periodic scan ---
    # Pass text_widget instead of text_label to the update function
    print(f"Starting scan loop (interval: {CAPTURE_INTERVAL_SECONDS}s). Close window to stop.")
    root.after(500, lambda: perform_scan_update_and_control(root, text_widget))

    # --- Run the Tkinter event loop ---
    try:
        root.mainloop()
    except Exception as e: print(f"An unexpected error occurred in the main loop: {e}")
    finally: print("--- Script Finished ---")

