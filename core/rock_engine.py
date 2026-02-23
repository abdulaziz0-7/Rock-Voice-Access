import sounddevice as sd
from scipy.io.wavfile import write
from transformers import pipeline
import warnings
import os
from action_dispatcher import execute_command 


warnings.filterwarnings("ignore")

def boot_rock_asr():
    print("--- 🧠 ROCK AI: INITIALIZING SYSTEM ---")
    # Loads the offline speech-to-text model
    transcriber = pipeline("automatic-speech-recognition", model="openai/whisper-tiny.en")
    print("✅ Brain Loaded! Rock is online.\n")
    return transcriber

def listen_and_transcribe(transcriber):
    fs = 16000
    duration = 4 
    temp_file = "temp_audio.wav"
    
    print(f"\n{'='*40}")
    print("🎙️ LISTENING... (Speak now for 4 seconds)")
    print(f"{'='*40}")
    
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(temp_file, fs, recording)
    
    print("⚙️ Transcribing...")
    result = transcriber(temp_file)
    text = result['text'].strip().lower()
    
    print(f"\n🗣️ Rock heard: '{text}'")
    
    if os.path.exists(temp_file):
        os.remove(temp_file)
        
    return text

if __name__ == "__main__":
    rock_brain = boot_rock_asr()
    
    while True:
        try:
            input("\nPress [ENTER] to speak to Rock (or Ctrl+C to quit)...")
            transcription = listen_and_transcribe(rock_brain)
            
           
            execute_command(transcription)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down Rock AI...")
            break

