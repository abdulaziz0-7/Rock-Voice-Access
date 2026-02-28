# Rock-Voice-Access
# (Desktop Voice Assistant)

rock AI is a continuous-listening, multi-threaded Windows voice assistant and universal dictation tool. Built entirely in Python, it features a sleek, borderless "floating pill" interface that runs quietly in the background, allowing users to control their operating system, automate hardware, and dictate text completely hands-free.

## ✨ Key Features

* **Continuous Background Listening:** Uses a custom multi-threaded architecture to listen for commands without freezing the graphical user interface.

* **Dynamic Audio Gating:** Implements environmental noise calibration to filter out "ghost noises" (like laptop fans or AC units) so it only processes actual human speech.

* **Universal Dictation:** By saying the keyword *"type"*, rock acts as a ghost-keyboard, typing out your spoken words into any active application or document using `pyautogui`.

* **Fuzzy Command Matching:** Utilizes `difflib` (Levenshtein distance) to accurately trigger commands even if the speech-to-text transcription is slightly inaccurate.

* **Floating UI:** A modern, draggable, and transparent dark-mode interface built with `CustomTkinter`, featuring a custom-drawn animated audio wave that reacts to microphone states.

* **Hardware & System Control:** Adjust screen brightness, manage volume, take screenshots, empty the recycle bin, or shut down the PC using OS-level commands.


## 🛠️ Technology Stack

* **Language:** Python 3.x
* **GUI Framework:** CustomTkinter
* **Speech-to-Text:** SpeechRecognition (Google Web Speech API)
* **Text-to-Speech:** pyttsx3 (Offline Windows TTS Engine)
* **Automation:** PyAutoGUI (Keyboard/Mouse simulation)
* **Hardware Control:** screen-brightness-control

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/abdulaziz0-7/Rock-Voice-Access.git](https://github.com/abdulaziz0-7/Rock-Voice-Access.git)
   cd rock-ai
