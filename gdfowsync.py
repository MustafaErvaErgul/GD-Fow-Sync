import os
import sys
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil
import configparser

# ========== CONFIGURATION HANDLING ==========
def load_config():
    """Load and validate configuration from .ini file"""
    config = configparser.ConfigParser()
    # Use sys.executable if running as an .exe; otherwise use __file__
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    ini_file_path = os.path.join(base_dir, 'gdfowsync.ini')
    
    print(f"Loading configuration from: {ini_file_path}")
    
    if not os.path.exists(ini_file_path):
        raise FileNotFoundError(f"Configuration file not found: {ini_file_path}")

    config.read(ini_file_path)
    
    if 'PATH' not in config.sections():
        raise ValueError("Missing [PATH] section in configuration file")
    
    required_keys = ['GD_SAVE_PATH', 'GD_EXE_PATH', 'GD_FOWSYNC_PATH']
    for key in required_keys:
        if not config.has_option('PATH', key):
            raise ValueError(f"Missing required key in [PATH] section: {key}")
    
    # Process paths
    save_path = config.get('PATH', 'GD_SAVE_PATH').strip('"')
    save_path = os.path.expanduser(save_path)
    
    # Validate paths
    if not os.path.exists(save_path):
        raise FileNotFoundError(f"Save path does not exist: {save_path}")
    
    return {
        'SAVE_PATH': save_path,
        'GD_EXE_PATH': config.get('PATH', 'GD_EXE_PATH').strip('"'),
        'FOWSYNC_PATH': config.get('PATH', 'GD_FOWSYNC_PATH').strip('"')
    }

# Load configuration at startup
try:
    config_dict = load_config()
    SAVE_PATH = config_dict['SAVE_PATH']
    GD_EXE_PATH = config_dict['GD_EXE_PATH']
    FOWSYNC_PATH = config_dict['FOWSYNC_PATH']
except Exception as e:
    print(f"Configuration error: {e}")
    input("Press Enter to exit...")
    exit(1)

# ========== CORE FUNCTIONALITY ==========
last_synced_file = None

def find_largest_fow():
    """Finds the largest .fow file across all character folders."""
    largest_file = None
    largest_size = 0
    for root, _, files in os.walk(SAVE_PATH):
        for file in files:
            if file.endswith(".fow"):
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    if size > largest_size:
                        largest_file = file_path
                        largest_size = size
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
    return largest_file

def get_character_folders():
    """Returns validated character folder paths."""
    main_folder = os.path.join(SAVE_PATH, "main")
    if os.path.isdir(main_folder):
        return [os.path.join(main_folder, d) for d in os.listdir(main_folder) 
                if os.path.isdir(os.path.join(main_folder, d))]
    return [os.path.join(SAVE_PATH, d) for d in os.listdir(SAVE_PATH) 
            if os.path.isdir(os.path.join(SAVE_PATH, d))]

def sync_character_folder(char_folder, largest_fow):
    """Syncs FOW files with validation and error handling."""
    if not largest_fow or not os.path.exists(largest_fow):
        print("Invalid source .fow file")
        return

    levels_folder = os.path.join(char_folder, "levels_world001.map")
    os.makedirs(levels_folder, exist_ok=True)
    
    for difficulty in ["Normal", "Elite", "Ultimate"]:
        difficulty_folder = os.path.join(levels_folder, difficulty)
        os.makedirs(difficulty_folder, exist_ok=True)
        
        target_path = os.path.join(difficulty_folder, "map.fow")
        if should_sync_file(largest_fow, target_path):
            try:
                shutil.copy2(largest_fow, target_path)
                print(f"Synced: {os.path.basename(target_path)}")
            except Exception as e:
                print(f"Sync failed for {target_path}: {e}")

def should_sync_file(source, target):
    # """Check if files differ and need syncing"""
    # if not os.path.exists(target):
    #     return True
    # try:
    #     return os.path.getsize(source) != os.path.getsize(target)
    # except Exception as e:
    #     print(f"Comparison failed: {e}")
    #     return False
    return True

def sync_all(largest_fow):
    """Syncs FOW file to all character folders"""
    if not largest_fow:
        print("No valid .fow file found to sync")
        return
    for char_folder in get_character_folders():
        sync_character_folder(char_folder, largest_fow)

# ========== FILE WATCHERS ==========
class GDCWatcher(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("player.gdc"):
            print("\nPlayer data modified - triggering sync...")
            sync_all(find_largest_fow())

class NewCharacterHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            new_folder = os.path.abspath(event.src_path)
            parent = os.path.dirname(new_folder)
            if parent in [os.path.abspath(SAVE_PATH), 
                          os.path.abspath(os.path.join(SAVE_PATH, "main"))]:
                print(f"\nNew character detected: {os.path.basename(new_folder)}")
                time.sleep(1)  # Allow folder initialization
                sync_all(find_largest_fow())

# ========== RUNTIME MANAGEMENT ==========
def is_grim_dawn_running():
    return any("Grim Dawn.exe" in p.info.get('name', '') 
             for p in psutil.process_iter(['name']))

def monitor_loop():
    observer = Observer()
    observer.schedule(GDCWatcher(), SAVE_PATH, recursive=True)
    observer.schedule(NewCharacterHandler(), SAVE_PATH, recursive=True)
    observer.start()

    print(f"FOW Sync Active\nMonitoring: {SAVE_PATH}")
    print("Press Ctrl+C to exit...")

    try:
        while is_grim_dawn_running():
            time.sleep(60)
            sync_all(find_largest_fow())
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print("\nPerforming final sync...")
        sync_all(find_largest_fow())

if __name__ == "__main__":
    monitor_loop()
    print("Sync complete. Exiting.")
