import os
import string
import difflib
import pyautogui
import time
import screen_brightness_control as sbc
import re
import pyttsx3
import threading

# ❌ REMOVE the global engine = pyttsx3.init() from here!

def speak(text):
    """Makes Rock speak the text safely without crashing the background thread."""
    print(f"🔊 Rock says: {text}")
    
    def _speak_task():
        import pythoncom
        # 🔓 1. Unlock Windows COM for this specific mini-thread
        pythoncom.CoInitialize() 
        try:
            # 2. Initialize the engine locally so it doesn't cross threads
            engine = pyttsx3.init()
            engine.setProperty('rate', 170)
            
            # (Optional) Set to male or female voice
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id) 
            
            # 3. Speak
            engine.say(text)
            engine.runAndWait()
        finally:
            # 🔒 4. Clean up and lock COM so memory doesn't leak
            pythoncom.CoUninitialize()

    # Launch the protected speech in a disposable thread
    t = threading.Thread(target=_speak_task, daemon=True)
    t.start()
    
    # CRITICAL: Wait for Rock to finish speaking so his mic doesn't hear his own voice!
    t.join()

# --- THE O(1) ACTION DISPATCHER (MASTER EDITION) ---
COMMANDS = {
    # === 🟢 OPEN COMMANDS ===
    # Notice how os.system fires FIRST, and speak() fires SECOND.
    "open google chrome": lambda: (os.system("start chrome"), speak("Opening Google Chrome...")),
    "launch google chrome": lambda: (os.system("start chrome"), speak("Launching Google Chrome...")),
    "open brave": lambda: (os.system("start brave"), speak("Opening Brave...")),
    "launch brave": lambda: (os.system("start brave"), speak("Opening Brave...")),
    "open settings": lambda: (os.system("start ms-settings:"), speak("Opening Settings...")),
    "launch settings": lambda: (os.system("start ms-settings:"), speak("Opening Settings...")),
    "open file explorer": lambda: (os.system("explorer"), speak("Opening File Explorer...")),
    "launch file explorer": lambda: (os.system("explorer"), speak("Opening File Explorer...")),
    "open task manager": lambda: (os.system("start taskmgr"), speak("Opening Task Manager...")),
    "launch task manager": lambda: (os.system("start taskmgr"), speak("Opening Task Manager...")),
    "open microsoft edge": lambda: (os.system("start msedge"), speak("Opening Edge...")),
    "launch microsoft edge": lambda: (os.system("start msedge"), speak("Opening Edge...")),
    "open copilot": lambda: (os.system("start msedge https://copilot.microsoft.com"), speak("Opening Copilot...")),
    "launch copilot": lambda: (os.system("start msedge https://copilot.microsoft.com"), speak("Opening Copilot...")),
    "open word": lambda: (os.system("start winword"), speak("Opening Word...")),
    "launch word": lambda: (os.system("start winword"), speak("Opening Word...")),
    "open excel": lambda: (os.system("start excel"), speak("Opening Excel...")),
    "launch excel": lambda: (os.system("start excel"), speak("Opening Excel...")),
    "open powerpoint": lambda: (os.system("start powerpnt"), speak("Opening PowerPoint...")),
    "launch powerpoint": lambda: (os.system("start powerpnt"), speak("Opening PowerPoint...")),
    "open calculator": lambda: (os.system("calc"), speak("Opening Calculator...")),
    "launch calculator": lambda: (os.system("calc"), speak("Opening Calculator...")),
    "open camera": lambda: (os.system("start microsoft.windows.camera:"), speak("Opening Camera...")),
    "launch camera": lambda: (os.system("start microsoft.windows.camera:"), speak("Opening Camera...")),
    "open clock": lambda: (os.system("start ms-clock:"), speak("Opening Clock...")),
    "launch clock": lambda: (os.system("start ms-clock:"), speak("Opening Clock...")),
    "open whatsapp": lambda: (os.system("start whatsapp:"), speak("Opening WhatsApp...")),
    "launch whatsapp": lambda: (os.system("start whatsapp:"), speak("Opening WhatsApp...")),
    "open microsoft store": lambda: (os.system("start ms-windows-store:"), speak("Opening Microsoft Store...")),
    "launch microsoft store": lambda: (os.system("start ms-windows-store:"), speak("Opening Microsoft Store...")),

    # === 🛑 CLOSE COMMANDS ===
    "close google chrome": lambda: (os.system("taskkill /im chrome.exe /f"), speak("Closing Chrome...")),
    "exit google chrome": lambda: (os.system("taskkill /im chrome.exe /f"), speak("Closing Chrome...")),
    "close brave": lambda: (os.system("taskkill /im brave.exe /f"), speak("Closing Brave...")),
    "exit brave": lambda: (os.system("taskkill /im brave.exe /f"), speak("Closing Brave...")),
    "close settings": lambda: (os.system("taskkill /im SystemSettings.exe /f"), speak("Closing Settings...")),
    "exit settings": lambda: (os.system("taskkill /im SystemSettings.exe /f"), speak("Closing Settings...")),
    "close file explorer": lambda: (os.system('powershell -command "(New-Object -comObject Shell.Application).Windows() | foreach-object {$_.quit()}"'), speak("Closing File Explorer...")),
    "exit file explorer": lambda: (os.system('powershell -command "(New-Object -comObject Shell.Application).Windows() | foreach-object {$_.quit()}"'), speak("Closing File Explorer...")),
    "close task manager": lambda: (os.system("taskkill /im Taskmgr.exe /f"), speak("Closing Task Manager...")),
    "exit task manager": lambda: (os.system("taskkill /im Taskmgr.exe /f"), speak("Closing Task Manager...")),
    "close microsoft edge": lambda: (os.system("taskkill /im msedge.exe /f"), speak("Closing Edge...")),
    "exit microsoft edge": lambda: (os.system("taskkill /im msedge.exe /f"), speak("Closing Edge...")),
    "close copilot": lambda: (os.system("taskkill /im msedge.exe /f"), speak("Closing Copilot...")),
    "exit copilot": lambda: (os.system("taskkill /im msedge.exe /f"), speak("Closing Copilot...")),
    "close word": lambda: (os.system("taskkill /im winword.exe /f"), speak("Closing Word...")),
    "exit word": lambda: (os.system("taskkill /im winword.exe /f"), speak("Closing Word...")),
    "close excel": lambda: (os.system("taskkill /im excel.exe /f"), speak("Closing Excel...")),
    "exit excel": lambda: (os.system("taskkill /im excel.exe /f"), speak("Closing Excel...")),
    "close powerpoint": lambda: (os.system("taskkill /im powerpnt.exe /f"), speak("Closing PowerPoint...")),
    "exit powerpoint": lambda: (os.system("taskkill /im powerpnt.exe /f"), speak("Closing PowerPoint...")),
    "close calculator": lambda: (os.system("taskkill /im CalculatorApp.exe /f"), speak("Closing Calculator...")),
    "exit calculator": lambda: (os.system("taskkill /im CalculatorApp.exe /f"), speak("Closing Calculator...")),
    "close camera": lambda: (os.system("taskkill /im WindowsCamera.exe /f"), speak("Closing Camera...")),
    "exit camera": lambda: (os.system("taskkill /im WindowsCamera.exe /f"), speak("Closing Camera...")),
    "close clock": lambda: (os.system("taskkill /im Time.exe /f"), speak("Closing Clock...")),
    "exit clock": lambda: (os.system("taskkill /im Time.exe /f"), speak("Closing Clock...")),
    "close whatsapp": lambda: (os.system('powershell -command "Get-Process *whatsapp* -ErrorAction SilentlyContinue | Stop-Process -Force"'), speak("Closing WhatsApp...")),
    "exit whatsapp": lambda: (os.system('powershell -command "Get-Process *whatsapp* -ErrorAction SilentlyContinue | Stop-Process -Force"'), speak("Closing WhatsApp...")),
    "close microsoft store": lambda: (os.system("taskkill /im WinStore.App.exe /f"), speak("Closing Microsoft Store...")),
    "exit microsoft store": lambda: (os.system("taskkill /im WinStore.App.exe /f"), speak("Closing Microsoft Store...")),

    # === 💻 SYSTEM COMMANDS ===
    "lock pc": lambda: (os.system("rundll32.exe user32.dll,LockWorkStation"), speak("Locking PC...")),
    # Power Controls
    "shutdown pc": lambda: (os.system("shutdown /s /t 5"), speak("SHUTTING DOWN PC in 5 seconds! Say 'cancel shutdown' to abort!")),
    "turn off computer": lambda: (os.system("shutdown /s /t 5"), speak("SHUTTING DOWN PC in 5 seconds! Say 'cancel shutdown' to abort!")),
    "cancel shutdown": lambda: (os.system("shutdown /a"), speak("Shutdown Aborted!")),
    "restart pc": lambda: (os.system("shutdown /r /t 5"), speak("Restarting PC...")),
    
    # Desktop Navigation
    "show desktop": lambda: (pyautogui.hotkey('win', 'd'), speak("Minimizing all windows...")),
    "minimize window": lambda: (pyautogui.hotkey('win', 'd'), speak("Minimizing all windows...")),
    "take screenshot": lambda: (pyautogui.screenshot(rf"C:\aziz\screenshots\{int(time.time())}.png"), speak("Saving to external folder...")),
    
    # Hardware/Media Controls
    "volume up": lambda: (pyautogui.press(['volumeup', 'volumeup', 'volumeup', 'volumeup', 'volumeup']), speak("Increasing Volume...")),
    "volume down": lambda: (pyautogui.press(['volumedown', 'volumedown', 'volumedown', 'volumedown', 'volumedown']), speak("Decreasing Volume...")),
    "mute audio": lambda: (pyautogui.press('volumemute'), speak("Toggling Mute...")),
    "play media": lambda: (pyautogui.press('playpause'), speak("Play/Pause Media...")),
    "pause media": lambda: (pyautogui.press('playpause'), speak("Play/Pause Media...")),
    "next track": lambda: (pyautogui.press('nexttrack'), speak("Skipping to next song...")),
    "increase brightness ": lambda: (sbc.set_brightness('+25'), speak("Increasing Brightness...")),
    "decrease brightness": lambda: (sbc.set_brightness('-25'), speak("Decreasing Brightness...")),
    
    # Advanced OS Control
    "empty recycle bin": lambda: (os.system('powershell.exe -NoProfile -Command "Clear-RecycleBin -Force"'), speak("Emptying Trash..."))
}

def execute_command(transcription):
    # 1. Normalize the text
    clean_text = transcription.lower().translate(str.maketrans('', '', string.punctuation)).strip()
    clean_text = clean_text.replace(" for me", "").replace("please ", "").replace("zero", "0")
    
    typing_trigger = "enter "
    # 1. Brightness Interceptor
    if "brightness to" in clean_text:
        numbers = re.findall(r'\d+', clean_text) 
        if numbers:
            target = max(0, min(100, int(numbers[0]))) 
            sbc.set_brightness(target)
            speak(f"Setting Brightness to {target}%...")
            return

    elif clean_text.startswith(typing_trigger):
        lower_original = transcription.lower()
        start_index = lower_original.find(typing_trigger) + len(typing_trigger)
        
        payload = transcription[start_index:].strip()
        
        if payload.endswith('.'):
            payload = payload[:-1]
            
        print(f"⌨️ Action: Typing '{payload}'...")
        pyautogui.write(payload, interval=0.02)
        speak("Typing complete.")
        return    
            
    
    
    # 2. Mathematical Fuzzy Matching (Levenshtein Distance)
    matches = difflib.get_close_matches(clean_text, COMMANDS.keys(), n=1, cutoff=0.75)
    best_match = (matches + ["unknown"])[0]
    
    # 3. O(1) Execution with Fallback Print
    action = COMMANDS.get(best_match, lambda: print(f"💤 (No valid command match for: '{clean_text}')"))
    action()