import ctypes
import sys
import platform
import time
import pyautogui
from pynput import keyboard
from plyer import notification

# Force Windows to register the app ID so notifications show up
"""if sys.platform == "win32":
    myappid = 'JK.AutoSave.App.1.0' # Any unique string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)"""

running = True
if running == True:
    notification.notify(
               title="JK Auto-Saver",
               message= "JK Auto-Saver is running",
               timeout=2
           ) 

    
def quit_app():
    global running
    print("\nShutting down JK Auto-Save...")
    running = False
    notification.notify(
                   title="JK Auto-Saver is off",
                   message= "JK Auto-Saver is stopped",
                   timeout=2
               )
    hotkey_listener.stop()
    
    # Force immediate process shutdown
    sys.exit(0) 
# Exit key
EXIT_KEY = "<f1>"  

hotkey_listener = keyboard.GlobalHotKeys({
    EXIT_KEY: quit_app
})
hotkey_listener.start()

print(f"Auto-Save active. Press '{EXIT_KEY}' to stop.")


# Entry of the main loop checks the 'running' boolean
while running == True:


# Safe cross-platform imports
 os_name = platform.system()

 if os_name == "Windows":
    try:
        import pygetwindow as gw
    except ImportError:
        gw = None
 elif os_name == "Darwin":  # macOS
    try:
        from AppKit import NSWorkspace
    except ImportError:
        NSWorkspace = None
        print("AppKit not available. macOS active window detection disabled.")
 else  :      
        NSWorkspace = None

 def is_application_active():
    """Detects whether a valid user application window is currently focused."""
    try:
        if os_name == "Windows" and gw:
            active_win = gw.getActiveWindow()
            if not active_win or not active_win.title:
                return False
            return active_win.title not in ["", "Desktop", "Program Manager"]
            
        elif os_name == "Darwin" and NSWorkspace:
            active_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            return active_app.localizedName() != "Finder"
            
    except Exception:
        return True

    return True

 def get_save_modifier():
    return "command" if os_name == "Darwin" else "ctrl"

 HOTKEY_MODIFIER = get_save_modifier()
 INTERVAL_SECONDS =  4 * 60

 active_keys = set()

 def on_press(key):
    active_keys.add(key)

 def on_release(key):
    active_keys.discard(key)

 listener = keyboard.Listener(on_press=on_press, on_release=on_release)
 listener.start()

 print(f"JK Auto-Save running on {os_name}")

 try:
       while True:
        time.sleep(INTERVAL_SECONDS)
        
        if not is_application_active():
            print(f"[{time.strftime('%H:%M:%S')}] Skipped: No active application focused.")
            continue

        while len(active_keys) > 0:
            time.sleep(0.5)

        pyautogui.hotkey(HOTKEY_MODIFIER, 's')
        
        notification.notify(
            title="JK Auto-Saver",
            message=f"Work saved using {HOTKEY_MODIFIER.upper()} + S",
            app_name="AutoSave",
            timeout=2
        )
        print(f"[{time.strftime('%H:%M:%S')}] Auto-saved active application ({HOTKEY_MODIFIER}+s).")

 except KeyboardInterrupt:
    listener.stop()