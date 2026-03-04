import customtkinter as ctk  # Used for building the modern, dark-themed GUI
import os                    # Used for system-level operations (like exiting the app)
import threading             # Crucial: Allows the AI to listen in the background without freezing the UI
import time                  # Used for adding slight delays to prevent CPU overload
import speech_recognition as sr # The core audio recording and transcription engine
import warnings              # Used to hide unnecessary technical warnings from the console
import random                # Used to generate random heights for the audio wave animation

# --- Import your action dispatcher ---
# We use a try-except block here. If action_dispatcher.py is missing or broken, 
# the UI will still load, but it will just print the command instead of crashing.
try:
    from core.action_dispatcher import execute_command
except ImportError:
    print("⚠️ WARNING: Could not import 'execute_command'.")
    def execute_command(text): print(f"Action triggered: {text}")

# --- Configuration ---
ctk.set_appearance_mode("Dark")        # Forces the app into dark mode
ctk.set_default_color_theme("dark-blue") # Sets the default accent colors
warnings.filterwarnings("ignore")      # Keeps the terminal output clean

# Global Flag to control the background listening thread. 
# When set to False, the background loop will safely shut down.
is_running = True

# --- 🌊 CUSTOM AUDIO WAVE ANIMATION ---
# This class creates a custom canvas widget that draws a fake, animated voice wave.
class AnimatedWave(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        # highlightthickness=0 removes the default white border around the canvas
        super().__init__(master, bg="#000000", highlightthickness=0, **kwargs)
        self.lines = []           # Will store the drawn vertical lines
        self.num_lines = 8        # How many vertical bars make up the wave
        self.width_val = kwargs.get('width', 100)
        self.height_val = kwargs.get('height', 30)
        self.is_animating = False # Toggle to start/stop the animation

        # Draw the initial flat lines (when the app boots up)
        spacing = self.width_val / self.num_lines
        for i in range(self.num_lines):
            x = i * spacing + (spacing / 2)
            # create_line(x1, y1, x2, y2)
            line = self.create_line(x, self.height_val/2, x, self.height_val/2, fill="#00e5ff", width=2, capstyle="round")
            self.lines.append(line)

    def start(self):
        """Turns the animation flag on and triggers the loop."""
        self.is_animating = True
        self.animate()

    def stop(self):
        """Stops the animation, flattens the wave, and turns it red (muted state)."""
        self.is_animating = False
        spacing = self.width_val / self.num_lines
        for i, line in enumerate(self.lines):
            x = i * spacing + (spacing / 2)
            # Reset coords to make it a flat horizontal line
            self.coords(line, x, self.height_val/2, x, self.height_val/2)
            self.itemconfig(line, fill="#e53e3e") # Change color to red

    def animate(self):
        """The core animation loop. Adjusts the height of each line randomly."""
        if not self.is_animating:
            return # Exit the loop if we are muted
            
        spacing = self.width_val / self.num_lines
        for i, line in enumerate(self.lines):
            x = i * spacing + (spacing / 2)
            
            # Math logic: Makes the lines in the middle of the canvas taller, 
            # and the lines on the outer edges shorter, simulating a real audio wave.
            distance_from_center = abs((self.num_lines / 2) - i)
            max_h = (self.height_val / 2) - (distance_from_center * 0.8)
            max_h = max(2, max_h) 
            
            # Pick a random height up to the maximum allowed for this specific line
            h = random.uniform(2, max_h)
            
            # Apply the new coordinates
            self.coords(line, x, self.height_val/2 - h, x, self.height_val/2 + h)
            self.itemconfig(line, fill="#00e5ff") # Ensure color is cyan

        # Call this exact function again in 80 milliseconds (creates the continuous loop)
        self.after(80, self.animate)

# --- THE MAIN UI CLASS ---
class RockUIPill(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Window Setup ---
        self.title("Rock AI")
        pill_width = 460  
        pill_height = 64
        
        # Calculate screen width to place the app perfectly in the top center
        screen_width = self.winfo_screenwidth()
        x_pos = (screen_width // 2) - (pill_width // 2)
        y_pos = 40
        self.geometry(f"{pill_width}x{pill_height}+{int(x_pos)}+{y_pos}")
        
        # UI Hacks to make a "Floating Widget"
        self.overrideredirect(True) # Removes the default Windows title bar (close/minimize buttons)
        self.wm_attributes("-topmost", True) # Forces the app to always stay above other windows
        self.wm_attributes("-alpha", 0.95)   # Makes the window slightly transparent (95% opacity)
        
        # Magic color hack: We pick a specific color, set it as the background, 
        # and tell Windows to make that exact color invisible. 
        # This allows for rounded corners without a square box around it.
        transparent_color = '#000001'
        self.config(background=transparent_color)
        self.wm_attributes('-transparentcolor', transparent_color)

        self.is_muted = False # Microphone state flag

        # --- 2. The Main Container ---
        # Everything goes inside this frame, which provides the visible black background and border
        self.container = ctk.CTkFrame(
            self, corner_radius=0, fg_color="#000000", 
            border_width=1, border_color="#7f8ea9"
        )
        self.container.pack(fill="both", expand=True, padx=0, pady=0)

        # --- 3. UI Elements ---
        
        # A. Mute Button (Left side)
        self.btn_frame = ctk.CTkFrame(self.container, fg_color="transparent", width=48, height=48)
        self.btn_frame.pack_propagate(False) # Prevents the button from stretching the frame
        self.btn_frame.pack(side="left", padx=(12, 10), pady=8)

        self.mute_btn = ctk.CTkButton(
            self.btn_frame, text="🎙", width=48, height=48, corner_radius=24,
            fg_color="transparent", border_width=2, border_color="#00e5ff", 
            text_color="#00e5ff", font=("Arial", 22), hover_color="#2d3748",
            command=self.toggle_mute # Triggers the toggle_mute function when clicked
        )
        self.mute_btn.pack(expand=True, fill="both")

        # B. Status Label (Text showing what the AI is doing)
        self.status_label = ctk.CTkLabel(
            self.container, text="🎙️ Listening...",
            font=("Segoe UI Display", 16, "bold"), text_color="#00e5ff"
        )
        self.status_label.pack(side="left", padx=(0, 15))

        # C. The Animated Audio Wave Instance
        self.audio_wave = AnimatedWave(self.container, width=100, height=30)
        self.audio_wave.pack(side="left", padx=10)
        self.audio_wave.start()

        # D. Right Controls (Minimize & Close buttons)
        self.controls_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.controls_frame.pack(side="right", padx=(0, 12))

        self.min_btn = ctk.CTkButton(
            self.controls_frame, text="—", width=32, height=32, corner_radius=8,
            fg_color="transparent", hover_color="#4a5568", text_color="white",
            font=("Arial", 14, "bold"), command=self.minimize_app
        )
        self.min_btn.pack(side="left", padx=4)

        self.close_btn = ctk.CTkButton(
            self.controls_frame, text="✕", width=32, height=32, corner_radius=8,
            fg_color="transparent", hover_color="#e53e3e", text_color="white",
            font=("Arial", 14, "bold"), command=self.close_app
        )
        self.close_btn.pack(side="left", padx=4)

        # --- 4. Draggable Window Logic ---
        # Because we removed the Windows title bar, we have to code our own way to drag the window.
        # We bind left-click (<ButtonPress-1>) and mouse movement (<B1-Motion>) to custom functions.
        self.container.bind("<ButtonPress-1>", self.start_move)
        self.container.bind("<ButtonRelease-1>", self.stop_move)
        self.container.bind("<B1-Motion>", self.on_move)
        self.bind("<Map>", self.restore_window)
        self.x_drag_start = None
        self.y_drag_start = None

        # --- 5. Boot AI ---
        # Waits 100 milliseconds for the UI to fully load, then launches the AI brain
        self.after(100, self.start_ai_thread)

    # --- UI Interaction Methods ---
    def toggle_mute(self):
        """Switches the UI between active (cyan) and muted (red)."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_btn.configure(border_color="#e53e3e", text_color="#e53e3e")
            self.status_label.configure(text="⏸️ Paused", text_color="#e53e3e")
            self.audio_wave.stop() # Stops the wave animation
        else:
            self.mute_btn.configure(border_color="#00e5ff", text_color="#00e5ff")
            self.status_label.configure(text="🎙️ Listening...", text_color="#00e5ff")
            self.audio_wave.start() # Restarts the wave animation

    def minimize_app(self):
        """Force Windows to recognize the app before sending it to the taskbar."""
        self.is_minimized = True
        self.withdraw()               # 1. Instantly hide the floating pill
        self.overrideredirect(False)  # 2. Tell Windows it is a normal app again
        self.iconify()                # 3. Send it to the taskbar!

    def restore_window(self, event):
        """When clicking the taskbar icon, strip the borders and reveal the pill."""
        if getattr(self, "is_minimized", False) and event.widget is self:
            self.withdraw()               # 1. Hide the ugly Windows borders 
            self.overrideredirect(True)   # 2. Turn back into a borderless pill
            self.is_minimized = False     # 3. Reset our flag
            self.deiconify()              # 4. Reveal the app on screen!

    def close_app(self):
        """Safely shuts down the app and kills the background thread."""
        global is_running
        is_running = False  # Tells the while-loop in the background thread to stop
        self.destroy()      # Destroys the UI window
        os._exit(0)         # Force kills any lingering Python processes

    # --- Window Dragging Methods ---
    def start_move(self, event):
        """Records the exact X and Y coordinates where the user clicked."""
        self.x_drag_start = event.x
        self.y_drag_start = event.y

    def stop_move(self, event):
        """Clears the coordinates when the user lets go of the mouse button."""
        self.x_drag_start = None
        self.y_drag_start = None

    def on_move(self, event):
        """Calculates how far the mouse moved and updates the window's position."""
        deltax = event.x - self.x_drag_start
        deltay = event.y - self.y_drag_start
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}") # Moves the window to the new calculated coordinates

    # --- AI Backend Integration ---
    def update_status(self, text, color="#00e5ff"):
        """
        A safe way to update the UI text from a background thread.
        You cannot directly change UI elements from a separate thread, 
        so we use self.after(0, ...) to tell the main UI thread to do it safely.
        """
        if not self.is_muted:
            self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def start_ai_thread(self):
        """
        Launches the AI listener in a separate 'daemon' thread. 
        If we didn't use threading, the UI would completely freeze while 
        the microphone waits for you to speak.
        """
        thread = threading.Thread(target=self.ai_listener_loop, daemon=True)
        thread.start()

    def ai_listener_loop(self):
        """The core brain of the assistant. Runs constantly in the background."""
        global is_running
        self.update_status("⚙️ Connecting to Cloud...", "#f6ad55") 
        
        recognizer = sr.Recognizer()
        
        # Configure how patient the AI is when listening
        recognizer.pause_threshold = 2.0  # Waits 2 seconds of silence before assuming you finished speaking
        recognizer.non_speaking_duration = 0.5 
        
        # --- THE GHOST NOISE FIX ---
        # Turns off automatic sensitivity. If this was True, the AI would 
        # constantly lower its threshold until it started transcribing laptop fan noise.
        recognizer.dynamic_energy_threshold = False 
        
        microphone = sr.Microphone()
        
        with microphone as source:
            self.update_status("🎧 Calibrating Mic...", "#f6ad55")
            # Listens to the room for 2 seconds to figure out how loud the background hum is
            recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Force a strict minimum volume limit (Audio Gating).
            # Normal speech is around 400-600. Background static is usually 50-100.
            # This ensures Rock only wakes up for loud, intentional speech.
            if recognizer.energy_threshold < 250:
                recognizer.energy_threshold = 250
            else:
                # If the room is already loud, bump the threshold up even higher
                recognizer.energy_threshold += 100 
        
        self.update_status("🎙️ Online & Ready...", "#00e5ff")

        # The infinite loop that keeps the AI alive
        while is_running:
            # If the user clicked the mute button, pause the loop and do nothing
            if self.is_muted:
                time.sleep(1)
                continue

            self.update_status("🎙️ Listening...", "#00e5ff")

            try:
                with microphone as source:
                    # Listen to the microphone.
                    # timeout=10: Waits up to 10 seconds for the user to start speaking.
                    # phrase_time_limit=20: Cuts off the recording if the user talks for 20 seconds straight.
                    audio = recognizer.listen(source, timeout=10, phrase_time_limit=20)
                
                self.update_status("⚡ Processing...", "#f6ad55") 
                
                # Send the recorded audio to Google's Speech-to-Text cloud API
                raw_text = recognizer.recognize_google(audio).lower()
                
                # Clean up the text by removing punctuation that might confuse the command dispatcher
                clean_text = raw_text.replace(",", "").replace(".", "").replace("!", "").replace("?", "").strip()

                if clean_text:
                    self.update_status(f"🚀 Executing...", "#4ade80") 
                    print(f"✅ Heard: '{clean_text}' -> Sending to dispatcher")
                    
                    # Send the text to action_dispatcher.py to figure out what to do with it
                    execute_command(clean_text)

            # --- 🐛 EXCEPTION HANDLING (Error Catching) ---
            except sr.WaitTimeoutError:
                # The user didn't say anything for 10 seconds. Ignore and loop back.
                print("⏳ Debug: Timeout (Waited 10 seconds, didn't hear you start speaking)") 
            except sr.UnknownValueError:
                # The user spoke, but it was too muffled or too quiet for Google to understand.
                print("🤔 Debug: Heard noise, but couldn't understand the words") 
            except sr.RequestError as e:
                # The computer lost internet connection, so it can't reach Google's API.
                print(f"Network Error: {e}")
                self.update_status("⚠️ No Internet!", "#e53e3e")
                time.sleep(2)
            except Exception as e:
                # Catch-all for any other weird errors to prevent the app from crashing entirely.
                print(f"Error: {e}")
                time.sleep(1)

# Application Entry Point
if __name__ == "__main__":
    app = RockUIPill()
    ctk.deactivate_automatic_dpi_awareness() # Fixes blurry text issues on some Windows displays
    app.mainloop() # Starts the CustomTkinter GUI loop