#!/usr/bin/env python3
import sys

TERMINAL_CLASSES = [
    "Xfce4-terminal",
    "kitty",
    "org.wezfurlong.wezterm",
    "Alacritty",
]

_xlib_display = None

def get_xlib_display():
    """Get cached Xlib display connection."""
    global _xlib_display
    if _xlib_display is None:
        try:
            from Xlib import display
            _xlib_display = display.Display()
        except Exception:
            pass
    return _xlib_display

def get_window_class():
    """Get WM_CLASS of focused window using Xlib, fallback to xdotool."""
    # Try Xlib first (faster, no subprocess)
    dpy = get_xlib_display()
    if dpy:
        try:
            from Xlib import X
            window = dpy.get_input_focus().focus
            # Get WM_CLASS property
            wm_class = window.get_wm_class()
            if wm_class:
                # WM_CLASS returns (instance, class)
                return wm_class[1]  # class part
        except Exception:
            pass
    
    # Fallback to xdotool
    try:
        import subprocess
        result = subprocess.run(
            ["xdotool", "getwindowfocus", "getwindowclassname"],
            capture_output=True,
            text=True,
            timeout=0.1
        )
        return result.stdout.strip()
    except Exception:
        return None

def is_terminal_window():
    """Check if currently focused window is a terminal."""
    window_class = get_window_class()
    return window_class in TERMINAL_CLASSES if window_class else False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: clipboard_operation.py [copy|cut|paste]")
        sys.exit(1)

    operation = sys.argv[1].lower()
    # Use Xlib XTest for key simulation (faster than pynput)
    import xlib_keyboard as xkbd
    use_terminal_keys = is_terminal_window()

    if operation == "copy":
        xkbd.release_cmd_l()
        if use_terminal_keys:
            xkbd.copy_keys(use_terminal_keys=True)
        else:
            xkbd.copy_keys(use_terminal_keys=False)
    elif operation == "cut":
        xkbd.release_cmd_l()
        xkbd.cut_keys()
    elif operation == "paste":
        xkbd.release_cmd_l()
        if use_terminal_keys:
            xkbd.paste_keys(use_terminal_keys=True)
        else:
            xkbd.paste_keys(use_terminal_keys=False)
    else:
        print("Unknown operation:", operation)
        sys.exit(1)

    # operation = sys.argv[1].lower()
    # # Lazy import to reduce startup time
    # from pynput.keyboard import Key, Controller
    # keyboard = Controller()
    # use_terminal_keys = is_terminal_window()
    #
    # if operation == "copy":
    #     keyboard.release(Key.cmd_l)
    #     if use_terminal_keys:
    #         with keyboard.pressed(Key.ctrl, Key.shift):
    #             keyboard.tap('c')
    #     else:
    #         with keyboard.pressed(Key.ctrl):
    #             keyboard.tap(Key.insert)
    #     keyboard.pressed(Key.cmd_l)
    # elif operation == "cut":
    #     keyboard.release(Key.cmd_l)
    #     with keyboard.pressed(Key.shift):
    #         keyboard.tap(Key.delete)
    #     keyboard.pressed(Key.cmd_l)
    # elif operation == "paste":
    #     keyboard.release(Key.cmd_l)
    #     if use_terminal_keys:
    #         with keyboard.pressed(Key.ctrl, Key.shift):
    #             keyboard.tap('v')
    #     else:
    #         with keyboard.pressed(Key.shift):
    #             keyboard.tap(Key.insert)
    #     keyboard.pressed(Key.cmd_l)
    # else:
    #     print("Unknown operation:", operation)
    #     sys.exit(1)
