import speech_recognition as sr
import threading
import webview
import tkinter as tk
import os
import time

# --- 🔇 MUTE PYWEBVIEW ACCESSIBILITY SPAM ---
import logging
logging.getLogger('pywebview').setLevel(logging.CRITICAL)

from core.action_dispatcher import execute_command

# --- 🎯 THE IPC BRIDGE ---
class UIBridge:
    def __init__(self):
        self.window = None
        self.is_paused = False

    def toggle_mic(self):
        self.is_paused = not self.is_paused
        print(f"🔄 Action: Microphone Paused = {self.is_paused}")
        return self.is_paused

    def close_app(self):
        print("🛑 Action: Closing Rock Voice Access...")
        os._exit(0) 

    def minimize_app(self):
        print("🔽 Action: Minimizing UI...")
        self.window.minimize()

def audio_listener_thread(window, api_bridge):
    print("--- 🧠 ROCK AI: BOOTING NEURAL NET ---")
    
    # ---------------------------------------------------------
    # 🐢 LAZY IMPORT: Load the heavy AI inside the background thread!
    # ---------------------------------------------------------
    from transformers import pipeline
    import warnings
    warnings.filterwarnings("ignore")
    
    # Load the Whisper offline model (Downloads ~150MB the very first time)
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en")
    print("✅ Brain Loaded! Rock is completely offline and untethered.")
    # ---------------------------------------------------------

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        print("⚙️ Adjusting for background noise... Please be quiet.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        recognizer.energy_threshold += 50 
        print("✅ Rock Engine Active. Speak your commands directly!")

    temp_file = "temp_audio.wav"

    while True:
        if api_bridge.is_paused:
            time.sleep(1)
            continue 

        try:
            with microphone as source:
                # We listen dynamically for up to 5 seconds
                audio = recognizer.listen(source, phrase_time_limit=5) 
                
            # Visual feedback: Flash the UI to show we are processing
            window.evaluate_js('setListening()') 
            
            # --- 🧠 THE OFFLINE AI HANDOFF ---
            # 1. Save the audio to a temporary local file
            with open(temp_file, "wb") as f:
                f.write(audio.get_wav_data())
            
            # 2. Feed the file to the local Whisper AI brain
            result = transcriber(temp_file)
            text = result['text'].strip().lower()
            
            # 3. Clean up the temp file instantly
            if os.path.exists(temp_file):
                os.remove(temp_file)
            # ---------------------------------
            
            if text: 
                print(f"🗣️ Rock heard: '{text}'")
                execute_command(text)
                window.evaluate_js('setSleeping()')

        except sr.UnknownValueError:
            pass 
        except Exception as e:
            print(f"⚠️ Error: {e}")
            window.evaluate_js('setSleeping()')

# --- 🖥️ MAIN BOOT SEQUENCE ---
if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, 'ui', 'index.html')

    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    root.destroy() 
    
    window_width = 350
    window_height = 45 
    x_position = (screen_width // 2) - (window_width // 2)

    api_bridge = UIBridge()

    window = webview.create_window(
        'Rock UI', 
        url=html_path, 
        width=window_width, 
        height=window_height, 
        x=x_position, 
        y=15, 
        frameless=True, 
        on_top=True, 
        transparent=True, 
        js_api=api_bridge,
        background_color="#000000",
        easy_drag=True,             
        text_select=False           
    )
    
    api_bridge.window = window

    def boot_audio_engine():
        audio_thread = threading.Thread(target=audio_listener_thread, args=(window, api_bridge), daemon=True)
        audio_thread.start()

    webview.start(boot_audio_engine, gui="edgechromium")