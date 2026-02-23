import customtkinter as ctk
from PIL import Image
import os

# --- Configuration ---
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("black")  

class RockUIPill(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 1. Window Setup ---
        self.title("Rock AI Interface")
        pill_width = 380
        pill_height = 70
        screen_width = self.winfo_screenwidth()
        x_pos = (screen_width // 2) - (pill_width // 2)
        y_pos = 50
        self.geometry(f"{pill_width}x{pill_height}+{int(x_pos)}+{y_pos}")
        
        self.overrideredirect(True) 
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-alpha", 0.90) 
        
        transparent_color = '#000001'
        self.config(background=transparent_color)
        self.wm_attributes('-transparentcolor', transparent_color)

        # --- 2. The Main Rounded Container ---
        self.container_frame = ctk.CTkFrame(
            self, 
            corner_radius=35,
            fg_color="#1c1c1c",
            border_width=1,
            border_color="#2a2a2a"
        )
        self.container_frame.pack(fill="both", expand=True, padx=0, pady=0)

        # --- 3. UI Elements ---
        
        # A. Microphone Icon
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "assets", "mic_blue.png")

        try:
            self.mic_image = ctk.CTkImage(
                light_image=Image.open(image_path),
                dark_image=Image.open(image_path),
                size=(32, 32)
            )
            self.mic_label = ctk.CTkLabel(self.container_frame, text="", image=self.mic_image)
        except FileNotFoundError:
             print(f"⚠️ WARNING: Icon not found at {image_path}. Using text fallback.")
             self.mic_label = ctk.CTkLabel(self.container_frame, text="🎤", font=("Arial", 28))

        self.mic_label.pack(side="left", padx=(20, 15))

        # B. Text Container
        self.text_frame = ctk.CTkFrame(self.container_frame, fg_color="transparent")
        self.text_frame.pack(side="left", fill="y", pady=10)

        # Main Status Text
        main_font = ctk.CTkFont(family="Segoe UI Display", size=16, weight="bold")
        self.status_label = ctk.CTkLabel(
            self.text_frame, 
            text="Rock AI: Listening...",
            font=main_font,
            text_color="white",
            anchor="w"
        )
        self.status_label.pack(fill="x", anchor="w")
        
        # Sub-text Engine Status
        sub_font = ctk.CTkFont(family="Segoe UI", size=11)
        self.engine_label = ctk.CTkLabel(
            self.text_frame, 
            text="Engine: Local Whisper (Offline)",
            font=sub_font,
            text_color="#aaaaaa",
            anchor="w"
        )
        self.engine_label.pack(fill="x", anchor="w")

        # C. Close Button
        self.close_btn = ctk.CTkButton(
            self.container_frame,
            text="✕",
            width=24,
            height=24,
            corner_radius=12,
            fg_color="#333333",
            hover_color="#c42b1c",
            font=("Arial", 12, "bold"),
            command=self.close_app
        )
        self.close_btn.pack(side="right", padx=15)

        # --- 4. Make it Draggable ---
        self.container_frame.bind("<ButtonPress-1>", self.start_move)
        self.container_frame.bind("<ButtonRelease-1>", self.stop_move)
        self.container_frame.bind("<B1-Motion>", self.on_move)
        self.x_drag_start = None
        self.y_drag_start = None

    def start_move(self, event):
        self.x_drag_start = event.x
        self.y_drag_start = event.y

    def stop_move(self, event):
        self.x_drag_start = None
        self.y_drag_start = None

    def on_move(self, event):
        deltax = event.x - self.x_drag_start
        deltay = event.y - self.y_drag_start
        new_x = self.winfo_x() + deltax
        new_y = self.winfo_y() + deltay
        self.geometry(f"+{new_x}+{new_y}")

    def close_app(self):
        self.destroy()

if __name__ == "__main__":
    app = RockUIPill()
    ctk.deactivate_automatic_dpi_awareness() 
    app.mainloop()