#!/usr/bin/env python3
"""
Simulate keyboard input using Xlib XTest extension.
Replaces pynput for faster key simulation.
"""
import sys, os
from Xlib import display, X, XK
from Xlib.ext import xtest

# Global display connection (opened once)
_dpy = None
_keycode_cache = {}
_dry_run = os.environ.get('XTEST_DRY_RUN') == '1'

def get_display():
    """Get or create X display connection."""
    global _dpy
    if _dpy is None:
        _dpy = display.Display()
        # Initialize XTest extension if not already
        if not hasattr(_dpy, 'xtest_get_version'):
            ext_info = _dpy.query_extension('XTEST')
            if ext_info and ext_info.present:
                xtest.init(_dpy, ext_info)
    return _dpy

def keysym_to_keycode(keysym):
    """Convert X keysym to keycode."""
    dpy = get_display()
    return dpy.keysym_to_keycode(keysym)

def get_keycode(name):
    """Get keycode for key name (e.g., 'Insert', 'Control_L', 'c')."""
    if name in _keycode_cache:
        return _keycode_cache[name]
    
    # Map common aliases to XK names
    alias_map = {
        'ctrl': 'Control_L',
        'shift': 'Shift_L',
        'alt': 'Alt_L',
        'cmd': 'Super_L',
        'cmd_l': 'Super_L',
        'insert': 'Insert',
        'delete': 'Delete',
        'enter': 'Return',
        'space': 'space',
        'c': 'c',
        'v': 'v',
        'x': 'x',
        'control_l': 'Control_L',
        'shift_l': 'Shift_L',
        'alt_l': 'Alt_L',
        'super_l': 'Super_L',
        'scroll_lock': 'Scroll_Lock',
        'f12': 'F12',
    }
    xk_name = alias_map.get(name.lower(), name)
    
    # Get keysym
    if len(xk_name) == 1 and xk_name.isalpha():
        # Single letter: use XK_a ... XK_z
        keysym = getattr(XK, f"XK_{xk_name.lower()}", None)
    else:
        keysym = getattr(XK, f"XK_{xk_name}", None)
    
    if keysym is None:
        raise ValueError(f"Unknown key name: {name}")
    
    keycode = keysym_to_keycode(keysym)
    _keycode_cache[name] = keycode
    return keycode

def press_key(keycode, modifiers=0):
    """Send key press event."""
    if _dry_run:
        print(f"[DRY] press keycode={keycode}, modifiers={modifiers}")
        return
    dpy = get_display()
    dpy.xtest_fake_input(X.KeyPress, keycode, modifiers)
    dpy.sync()

def release_key(keycode, modifiers=0):
    """Send key release event."""
    if _dry_run:
        print(f"[DRY] release keycode={keycode}, modifiers={modifiers}")
        return
    dpy = get_display()
    dpy.xtest_fake_input(X.KeyRelease, keycode, modifiers)
    dpy.sync()

def tap_key(keycode, modifiers=0):
    """Press and release a key."""
    press_key(keycode, modifiers)
    release_key(keycode, modifiers)

def simulate_combo(modifiers, main_key):
    """
    Simulate key combination.
    modifiers: list of modifier names (e.g., ['ctrl', 'shift'])
    main_key: main key name (e.g., 'Insert', 'c')
    """
    dpy = get_display()
    # Press modifiers
    mod_keycodes = []
    for mod in modifiers:
        code = get_keycode(mod)
        press_key(code)
        mod_keycodes.append(code)
    
    # Press and release main key
    main_code = get_keycode(main_key)
    press_key(main_code)
    release_key(main_code)
    
    # Release modifiers in reverse order
    for code in reversed(mod_keycodes):
        release_key(code)
    
    dpy.sync()

# Convenience functions for clipboard operations
def copy_keys(use_terminal_keys=False):
    """Simulate copy key combination."""
    if use_terminal_keys:
        simulate_combo(['ctrl', 'shift'], 'c')
    else:
        simulate_combo(['ctrl'], 'Insert')

def cut_keys():
    """Simulate cut key combination."""
    simulate_combo(['shift'], 'Delete')

def paste_keys(use_terminal_keys=False):
    """Simulate paste key combination."""
    if use_terminal_keys:
        simulate_combo(['ctrl', 'shift'], 'v')
    else:
        simulate_combo(['shift'], 'Insert')

def release_cmd_l():
    """Release left command key (Super_L)."""
    super_code = get_keycode('Super_L')
    release_key(super_code)

def press_cmd_l():
    """Press left command key (Super_L)."""
    super_code = get_keycode('Super_L')
    press_key(super_code)

if __name__ == "__main__":
    # Simple test: print keycodes
    dpy = get_display()
    print("Display:", dpy)
    print("Super_L keycode:", get_keycode('Super_L'))
    print("Insert keycode:", get_keycode('Insert'))
    print("Control_L keycode:", get_keycode('ctrl'))
    print("Shift_L keycode:", get_keycode('shift'))
    print("c keycode:", get_keycode('c'))
    print("v keycode:", get_keycode('v'))
