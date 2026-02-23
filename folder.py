import os

def scaffold_rock_project():
    # 1. Define the directory tree
    folders = [
        "dataset/open_cmd",
        "dataset/close_cmd",
        "dataset/system_cmd",
        "dataset/neutral",
        "models",
        "core",
        "ui"
    ]
    
    print("--- 🏗️ Building Rock AI Workspace ---")
    
    # 2. Create folders safely using exist_ok
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✔️ Created folder: {folder}")
        
    # 3. Create empty placeholder files
    files = [
        "core/train_model.py",
        "core/rock_engine.py",
        "core/action_dispatcher.py",
        "ui/index.html",
        "ui/style.css",
        "ui/ui_main.py",
        "collect_data.py",
        "requirements.txt"
    ]
    
    for file in files:
        if not os.path.exists(file):
            # Creates an empty file
            with open(file, 'w') as f:
                f.write("# Rock AI Component\n")
            print(f"📄 Created file: {file}")
        else:
            print(f"⚠️ Skipped (already exists): {file}")
            
    print("\n✅ Project structure is ready! Let the coding begin.")

if __name__ == "__main__":
    scaffold_rock_project()