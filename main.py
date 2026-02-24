import customtkinter as ctk
import os
import threading
import time
import speech_recognition as sr
import warnings
import random

# --- Import your action dispatcher ---
try:
    from core.action_dispatcher import execute_command
except ImportError:
    print("⚠️ WARNING: Could not import 'execute_command'.")
    def execute_command(text): print(f"Action triggered: {text}")

# --- Configuration ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
warnings.filterwarnings("ignore")

# Global Flags
is_running = True

# --- 🌊 CUSTOM AUDIO WAVE ANIMATION ---
class AnimatedWave(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, bg="#000000", highlightthickness=0, **kwargs)
        self.lines = []
        self.num_lines = 8
        self.width_val = kwargs.get('width', 100)
        self.height_val = kwargs.get('height', 30)
        self.is_animating = False

        # Draw initial flat lines
        spacing = self.width_val / self.num_lines
        for i in range(self.num_lines):
            x = i * spacing + (spacing / 2)
            line = self.create_line(x, self.height_val/2, x, self.height_val/2, fill="#00e5ff", width=2, capstyle="round")
            self.lines.append(line)

    def start(self):
        self.is_animating = True
        self.animate()

    def stop(self):
        self.is_animating = False
        spacing = self.width_val / self.num_lines
        for i, line in enumerate(self.lines):
            x = i * spacing + (spacing / 2)
            self.coords(line, x, self.height_val/2, x, self.height_val/2)
            self.itemconfig(line, fill="#e53e3e")

    def animate(self):
        if not self.is_animating:
            return
            
        spacing = self.width_val / self.num_lines
        for i, line in enumerate(self.lines):
            x = i * spacing + (spacing / 2)
            
            distance_from_center = abs((self.num_lines / 2) - i)
            max_h = (self.height_val / 2) - (distance_from_center * 0.8)
            max_h = max(2, max_h) 
            
            h = random.uniform(2, max_h)
            
            self.coords(line, x, self.height_val/2 - h, x, self.height_val/2 + h)
            self.itemconfig(line, fill="#00e5ff")

        self.after(80, self.animate)

# --- THE MAIN UI CLASS ---
class SpiderUIPill(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Window Setup ---
        self.title("Spider AI")
        pill_width = 460  
        pill_height = 64
        screen_width = self.winfo_screenwidth()
        x_pos = (screen_width // 2) - (pill_width // 2)
        y_pos = 40
        self.geometry(f"{pill_width}x{pill_height}+{int(x_pos)}+{y_pos}")
        
        self.overrideredirect(True) 
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-alpha", 0.95)
        
        transparent_color = '#000001'
        self.config(background=transparent_color)
        self.wm_attributes('-transparentcolor', transparent_color)

        self.is_muted = False

        # --- 2. The Main Container ---
        self.container = ctk.CTkFrame(
            self, corner_radius=0, fg_color="#000000", 
            border_width=1, border_color="#7f8ea9"
        )
        self.container.pack(fill="both", expand=True, padx=0, pady=0)

        # --- 3. UI Elements ---
        self.btn_frame = ctk.CTkFrame(self.container, fg_color="transparent", width=48, height=48)
        self.btn_frame.pack_propagate(False) 
        self.btn_frame.pack(side="left", padx=(12, 10), pady=8)

        self.mute_btn = ctk.CTkButton(
            self.btn_frame, text="🎙", width=48, height=48, corner_radius=24,
            fg_color="transparent", border_width=2, border_color="#00e5ff", 
            text_color="#00e5ff", font=("Arial", 22), hover_color="#2d3748",
            command=self.toggle_mute
        )
        self.mute_btn.pack(expand=True, fill="both")

        self.status_label = ctk.CTkLabel(
            self.container, text="🎙️ Listening...",
            font=("Segoe UI Display", 16, "bold"), text_color="#00e5ff"
        )
        self.status_label.pack(side="left", padx=(0, 15))

        self.audio_wave = AnimatedWave(self.container, width=100, height=30)
        self.audio_wave.pack(side="left", padx=10)
        self.audio_wave.start()

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

        # --- 4. Draggable Logic ---
        self.container.bind("<ButtonPress-1>", self.start_move)
        self.container.bind("<ButtonRelease-1>", self.stop_move)
        self.container.bind("<B1-Motion>", self.on_move)
        self.x_drag_start = None
        self.y_drag_start = None

        # --- 5. Boot AI ---
        self.after(100, self.start_ai_thread)

    # --- UI Interactions ---
    def toggle_mute(self):
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_btn.configure(border_color="#e53e3e", text_color="#e53e3e")
            self.status_label.configure(text="⏸️ Paused", text_color="#e53e3e")
            self.audio_wave.stop()
        else:
            self.mute_btn.configure(border_color="#00e5ff", text_color="#00e5ff")
            self.status_label.configure(text="🎙️ Listening...", text_color="#00e5ff")
            self.audio_wave.start()

    def minimize_app(self):
        self.iconify()

    def close_app(self):
        global is_running
        is_running = False 
        self.destroy()
        os._exit(0)

    # --- Window Dragging ---
    def start_move(self, event):
        self.x_drag_start = event.x
        self.y_drag_start = event.y

    def stop_move(self, event):
        self.x_drag_start = None
        self.y_drag_start = None

    def on_move(self, event):
        deltax = event.x - self.x_drag_start
        deltay = event.y - self.y_drag_start
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    # --- AI Backend Thread ---
    def update_status(self, text, color="#00e5ff"):
        if not self.is_muted:
            self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def start_ai_thread(self):
        thread = threading.Thread(target=self.ai_listener_loop, daemon=True)
        thread.start()

    def ai_listener_loop(self):
        global is_running
        self.update_status("⚙️ Connecting to Cloud...", "#f6ad55") 
        
        recognizer = sr.Recognizer()
        recognizer.pause_threshold = 1.0  
        recognizer.non_speaking_duration = 0.5 
        
        # --- THE GHOST NOISE FIX ---
        # Turn off auto-sensitivity so it doesn't adapt to the hum of your PC fan
        recognizer.dynamic_energy_threshold = False 
        
        microphone = sr.Microphone()
        
        with microphone as source:
            self.update_status("🎧 Calibrating Mic...", "#f6ad55")
            recognizer.adjust_for_ambient_noise(source, duration=2)
            
            # Force a strict minimum volume limit. 
            # Normal speech is usually around 400-600. Background static is usually 50-100.
            if recognizer.energy_threshold < 500:
                recognizer.energy_threshold = 500
            else:
                # If you are in a really loud room, bump it up even higher
                recognizer.energy_threshold += 200 
        
        self.update_status("🎙️ Online & Ready...", "#00e5ff")

        while is_running:
            if self.is_muted:
                time.sleep(1)
                continue

            self.update_status("🎙️ Listening...", "#00e5ff")

            try:
                with microphone as source:
                    # --- LONGER LISTENING WINDOW ---
                    # timeout=4: Waits up to 4 seconds for you to start speaking
                    # phrase_time_limit=10: Allows you to speak for up to 10 seconds straight
                    audio = recognizer.listen(source, timeout=4, phrase_time_limit=10)
                
                self.update_status("⚡ Processing...", "#f6ad55") 
                
                raw_text = recognizer.recognize_google(audio).lower()
                clean_text = raw_text.replace(",", "").replace(".", "").replace("!", "").replace("?", "").strip()

                if clean_text:
                    self.update_status(f"🚀 Executing...", "#4ade80") 
                    print(f"✅ Heard: '{clean_text}' -> Sending to dispatcher")
                    execute_command(clean_text)

            # --- 🐛 DEBUGGING BLOCKS ---
            except sr.WaitTimeoutError:
                print("⏳ Debug: Timeout (Waited 4 seconds, didn't hear you start speaking)") 
            except sr.UnknownValueError:
                print("🤔 Debug: Heard noise, but couldn't understand the words") 
            except sr.RequestError as e:
                print(f"Network Error: {e}")
                self.update_status("⚠️ No Internet!", "#e53e3e")
                time.sleep(2)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    app = SpiderUIPill()
    ctk.deactivate_automatic_dpi_awareness() 
    app.mainloop()