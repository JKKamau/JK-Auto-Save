[JK_auto_save.py](https://github.com/user-attachments/files/34683173/JK_auto_save.py)
import ctypes
import sys
import platform
import time
import pyautogui
from pynput import keyboard
from plyer import notification

# 1. Cross-Platform Window Detection Imports (Run Once at Top)
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
else:
    NSWorkspace = None


# 2. Helper Functions Defined Globally
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

def get_user_interval():
    """Prompt the user to inpit the auto-save frequency in minutes"""
    while True:
        try:
            minutes_input = input("Enter auto-save interval in minutes (e.g., 4 or 0.5): ")
            interval_minutes = float(minutes_input)
            if interval_minutes > 0:
                return interval_minutes * 60
            print("Please enter a number greater than 0.")
        except ValueError:
            print("Invalid input, Please enter a valid number.")

#prompt for interval before starting global state & loops
INTERVAL_SECONDS = get_user_interval()

# 3. Global State & Key Monitoring
running = True
active_keys = set()


def on_press(key):
    active_keys.add(key)


def on_release(key):
    active_keys.discard(key)


def quit_app():
    global running
    print("\nShutting down JK Auto-Save...")
    running = False

    notification.notify(
        title="JK Auto-Saver is off",
        message="JK Auto-Saver is stopped",
        timeout=2
    )

    # Stop all active listeners before exiting
    hotkey_listener.stop()
    key_listener.stop()

    sys.exit(0)


# 4. Setup Hotkeys and Listeners
EXIT_KEY = "<f1>"
HOTKEY_MODIFIER = get_save_modifier()


hotkey_listener = keyboard.GlobalHotKeys({
    EXIT_KEY: quit_app
})
hotkey_listener.start()

key_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
key_listener.start()

#initial start notification
notification.notify(
    title="JK Auto-Saver",
    message=f"Running every {INTERVAL_SECONDS / 60:.1f} min(s)",
    timeout=2
)

print(f"\nJK Auto-save active on {os_name} (Saving every {INTERVAL_SECONDS / 60:.1f} minute(s)).")
print(f"Press '{EXIT_KEY}' to stop.\n")

# 5. Single Main Execution Loop
try:
    while running:
        time.sleep(INTERVAL_SECONDS)

        if not running:
            break

        if not is_application_active():
            print(f"[{time.strftime('%H:%M:%S')}] Skipped: No active application focused.")
            continue

        # Wait if user is actively typing
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
    quit_app()
