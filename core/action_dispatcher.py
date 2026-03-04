import os             # Allows Python to interact with the Windows OS (opening apps, shutting down)
import string         # Used to quickly access a list of punctuation marks for text cleaning
import difflib        # The library used for "Fuzzy Matching" (finding closely related strings)
import pyautogui      # Automates keyboard and mouse presses for dictation and scrolling
import time           # Used for naming screenshot files based on the current timestamp
import screen_brightness_control as sbc # Specialized library to control monitor hardware
import re             # Regular Expressions (Regex) used to extract numbers from spoken text
import pyttsx3        # Offline Text-to-Speech engine so Rock can talk without internet
import threading      # Allows Rock to speak without freezing the rest of the application
import webbrowser     # Used to open URLs in the user's default browser

def speak(text):
    """
    Makes Rock speak the text safely using a background thread.
    If we didn't use threading, the entire application would freeze and stop 
    listening until Rock finished talking.
    """
    print(f"🔊 Rock says: {text}")
    
    def _speak_task():
        import pythoncom
        # Windows Component Object Model (COM) requires initialization when 
        # accessing hardware (like speakers) from a secondary background thread.
        pythoncom.CoInitialize() 
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 170) # Speed of the voice
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id) # 0 for male, 1 for female
            engine.say(text)
            engine.runAndWait()
        finally:
            # Safely release the Windows hardware lock to prevent memory leaks
            pythoncom.CoUninitialize()

    # Launch the speech task in a 'daemon' thread that runs independently
    t = threading.Thread(target=_speak_task, daemon=True)
    t.start()
    t.join() # Wait for the speech to finish before returning to the main listener

# --- DYNAMIC SEARCH URLS ---
# A scalable dictionary mapping websites to their specific search URLs.
# The {} acts as a placeholder where the user's spoken query will be injected.
SEARCH_ENGINES = {
    "youtube": "https://www.youtube.com/results?search_query={}",
    "amazon": "https://www.amazon.in/s?k={}",
    "wikipedia": "https://en.wikipedia.org/wiki/{}",
    "github": "https://github.com/search?q={}",
    "google": "https://www.google.com/search?q={}" 
}

# --- THE O(1) ACTION DISPATCHER ---
# Using a Dictionary (Hash Map) instead of a massive chain of if/elif statements.
# This provides O(1) time complexity, meaning finding a command takes the exact same 
# amount of time whether you have 10 commands or 10,000 commands.
# We use 'lambda' to delay the execution of the code until the user actually asks for it.
COMMANDS = {
    # === 🌐 BROWSER & APPS ===
    "open google chrome": lambda: (os.system("start chrome"), speak("Opening Google Chrome...")),
    "open chrome": lambda: (os.system("start chrome"), speak("Opening Google Chrome...")),
    "launch google chrome": lambda: (os.system("start chrome"), speak("Launching Google Chrome...")),
    "launch chrome": lambda: (os.system("start chrome"), speak("Launching Google Chrome...")),
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
    "open notepad": lambda: (os.system("start notepad"), speak("Opening Notepad...")),
    "launch notepad": lambda: (os.system("start notepad"), speak("Opening Notepad...")),
    "open vs code": lambda: (os.system("code"), speak("Opening Visual Studio Code...")),
    "launch vs code": lambda: (os.system("code"), speak("Opening Visual Studio Code...")),
    "open visual studio code": lambda: (os.system("code"), speak("Opening Visual Studio Code...")),

    # === 🛑 CLOSE COMMANDS ===
    # 'taskkill /im [process_name] /f' forcefully closes the background process
    "close google chrome": lambda: (os.system("taskkill /im chrome.exe /f"), speak("Closing Chrome...")),
    "close chrome": lambda: (os.system("taskkill /im chrome.exe /f"), speak("Closing Chrome...")),
    "exit google chrome": lambda: (os.system("taskkill /im chrome.exe /f"), speak("Closing Chrome...")),
    "exit chrome": lambda: (os.system("taskkill /im chrome.exe /f"), speak("Closing Chrome...")),
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
    "close notepad": lambda: (os.system("taskkill /im notepad.exe /f"), speak("Closing Notepad...")),
    "exit notepad": lambda: (os.system("taskkill /im notepad.exe /f"), speak("Closing Notepad...")),
    "close vs code": lambda: (os.system("taskkill /im Code.exe /f"), speak("Closing Visual Studio Code...")),
    "exit vs code": lambda: (os.system("taskkill /im Code.exe /f"), speak("Closing Visual Studio Code...")),

    # === 💻 SYSTEM COMMANDS ===
    "lock pc": lambda: (os.system("rundll32.exe user32.dll,LockWorkStation"), speak("Locking PC...")),
    "shutdown pc": lambda: (os.system("shutdown /s /t 5"), speak("SHUTTING DOWN PC in 5 seconds! Say 'cancel shutdown' to abort!")),
    "turn off computer": lambda: (os.system("shutdown /s /t 5"), speak("SHUTTING DOWN PC in 5 seconds! Say 'cancel shutdown' to abort!")),
    "cancel shutdown": lambda: (os.system("shutdown /a"), speak("Shutdown Aborted!")),
    "restart pc": lambda: (os.system("shutdown /r /t 5"), speak("Restarting PC...")),
    
    "show desktop": lambda: (pyautogui.hotkey('win', 'd'), speak("Minimizing all windows...")),
    "minimize window": lambda: (pyautogui.hotkey('win', 'd'), speak("Minimizing all windows...")),
    # Saves screenshot dynamically based on the current Unix timestamp
    "take screenshot": lambda: (pyautogui.screenshot(rf"C:\aziz\screenshots\{int(time.time())}.png"), speak("Saving to external folder...")),
    
    "volume up": lambda: (pyautogui.press(['volumeup', 'volumeup', 'volumeup', 'volumeup', 'volumeup']), speak("Increasing Volume...")),
    "volume down": lambda: (pyautogui.press(['volumedown', 'volumedown', 'volumedown', 'volumedown', 'volumedown']), speak("Decreasing Volume...")),
    "mute audio": lambda: (pyautogui.press('volumemute'), speak("Toggling Mute...")),
    "play media": lambda: (pyautogui.press('playpause'), speak("Play/Pause Media...")),
    "pause media": lambda: (pyautogui.press('playpause'), speak("Play/Pause Media...")),
    "next track": lambda: (pyautogui.press('nexttrack'), speak("Skipping to next song...")),
    "increase brightness": lambda: (sbc.set_brightness('+25'), speak("Increasing Brightness...")),
    "decrease brightness": lambda: (sbc.set_brightness('-25'), speak("Decreasing Brightness...")),
    "empty recycle bin": lambda: (os.system('powershell.exe -NoProfile -Command "Clear-RecycleBin -Force"'), speak("Emptying Trash...")),

    # === ⌨️ NAVIGATION & TYPING ===
    "enter": lambda: (pyautogui.press('enter'), print("⌨️ Action: Pressed Enter")),
    "press enter": lambda: (pyautogui.press('enter'), print("⌨️ Action: Pressed Enter")),
    "backspace": lambda: (pyautogui.press('backspace'), print("⌨️ Action: Pressed Backspace")),
    "delete word": lambda: (pyautogui.hotkey('ctrl', 'backspace'), print("⌨️ Action: Deleted Word")),
    "scroll up": lambda: (pyautogui.scroll(800), print("🖱️ Action: Scrolled Up")),
    "scroll down": lambda: (pyautogui.scroll(-800), print("🖱️ Action: Scrolled Down")),
}

# --- 6. SILENT FALLBACK ---
def handle_unknown_command(spoken_text):
    """
    If the spoken text is neither a command nor a typing request, Rock simply ignores it.
    This prevents the AI from acting erratically during normal background conversations.
    """
    print(f"💤 Ignored: '{spoken_text}' (Not a command. Say 'type' to dictate)")


def execute_command(transcription):
    """
    The main routing logic. It takes raw text from Google, cleans it, checks for 
    dynamic variables (like numbers or URLs), and routes it to the correct action.
    """
    # 1. Normalization: Lowercase the text, strip punctuation, and fix common mishearings
    clean_text = transcription.lower().translate(str.maketrans('', '', string.punctuation)).strip()
    clean_text = clean_text.replace(" for me", "").replace("please ", "").replace("zero", "0")
    
    # --- 📝 THE EXPLICIT TYPING INTERCEPTOR ---
    # If the user specifically says the word "type", we intercept it here.
    if clean_text.startswith("type "):
        # We slice the string to remove the word "type " and keep the exact payload 
        lower_original = transcription.lower()
        start_index = lower_original.find("type ") + 5
        payload = transcription[start_index:].strip()
        
        print(f"⌨️ Dictating: '{payload}'...")
        pyautogui.write(payload + " ", interval=0.01) # interval simulates natural typing speed
        return
    
    # --- DYNAMIC INTERCEPTORS (Commands with variables) ---
    # Brightness Interceptor: Uses Regex to find any integers spoken in the command
    elif "brightness to" in clean_text:
        numbers = re.findall(r'\d+', clean_text) 
        if numbers:
            # Clamps the value between 0 and 100 to prevent errors
            target = max(0, min(100, int(numbers[0]))) 
            sbc.set_brightness(target)
            speak(f"Setting Brightness to {target}%...")
            return
            
    # --- 4. DYNAMIC SEARCHING ---
    elif clean_text.startswith("search "):
        request = clean_text.replace("search ", "", 1).strip()
        
        # WhatsApp Web doesn't accept query parameters, so we handle it as a special case
        if "whatsapp" in request:
            speak("Opening WhatsApp Web...")
            webbrowser.open("https://web.whatsapp.com/")
            return

        # Set default values
        engine = "google"
        query = request
        
        # Check if the user mentioned a specific platform (e.g., "search youtube for...")
        for key in SEARCH_ENGINES.keys():
            if request.startswith(f"{key} for "):
                engine = key
                query = request.replace(f"{key} for ", "", 1).strip()
                break
        
        # Remove the word "for" if the user just said "search for..."
        if query.startswith("for "):
            query = query.replace("for ", "", 1).strip()

        # Format the final URL and open the browser
        if query:
            speak(f"Searching {engine.capitalize()} for {query}...")
            # Replace spaces with plus signs (+) as required by standard URL formatting
            formatted_url = SEARCH_ENGINES[engine].format(query.replace(" ", "+"))
            webbrowser.open(formatted_url)
        else:
            speak("What do you want me to search for?")
        return
        
    # --- STATIC COMMAND MATCHING ---
    # difflib.get_close_matches implements a "Levenshtein Distance" algorithm.
    # It calculates the similarity between what the user said and our official commands.
    # cutoff=0.80 means it requires an 80% match. This handles slight mispronunciations 
    # or minor transcription errors from Google seamlessly.
    matches = difflib.get_close_matches(clean_text, COMMANDS.keys(), n=1, cutoff=0.80)
    
    # If a match is found, take the first one. If not, default to "unknown".
    best_match = (matches + ["unknown"])[0]
    
    # Execute the command found in the dictionary, or trigger the silent fallback.
    action = COMMANDS.get(best_match, lambda: handle_unknown_command(transcription))
    action()