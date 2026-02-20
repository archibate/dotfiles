#!/usr/bin/env python3
"""
Countup Timer CLI - Manage multiple named timers with elapsed time tracking.

Usage:
    countup start <name>     - Create or overwrite timer with current timestamp
    countup reset <name>     - Delete timer
    countup switch <name>    - Set _current to this timer
    countup list             - Show all timers with elapsed time
    countup status [--json]  - Output current timer (HH:MM:SS or JSON for i3status)
    countup rofi [--dry-run] - Interactive rofi menu for timer management
"""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

STATE_FILE = Path("/tmp/countup.json")


def acquire_lock(f) -> None:
    """Acquire exclusive lock on file."""
    fcntl.flock(f.fileno(), fcntl.LOCK_EX)


def release_lock(f) -> None:
    """Release file lock."""
    fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def load_state(f) -> Dict[str, Any]:
    """Load state from JSON file."""
    f.seek(0)
    content = f.read()
    if not content.strip():
        return {}
    return json.loads(content)


def save_state(f, state: Dict[str, Any]) -> None:
    """Save state to JSON file."""
    f.seek(0)
    f.truncate()
    json.dump(state, f, indent=2)
    f.flush()


def get_state() -> Dict[str, Any]:
    """Load state with file locking."""
    with open(STATE_FILE, "a+") as f:
        acquire_lock(f)
        try:
            state = load_state(f)
            return state
        finally:
            release_lock(f)


def set_state(state: Dict[str, Any]) -> None:
    """Save state with file locking."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "a+") as f:
        acquire_lock(f)
        try:
            save_state(f, state)
        finally:
            release_lock(f)


def modify_state(modifier_func) -> Any:
    """Load, modify, and save state atomically with locking."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "a+") as f:
        acquire_lock(f)
        try:
            state = load_state(f)
            result = modifier_func(state)
            save_state(f, state)
            return result
        finally:
            release_lock(f)


def format_elapsed(seconds: float) -> str:
    """Format elapsed time as HH:MM:SS."""
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def cmd_start(name: str) -> None:
    """Create or overwrite timer with current timestamp."""
    def modifier(state: Dict[str, Any]) -> None:
        state[name] = time.time()
        state["_current"] = name
        print(f"Timer '{name}' started at {state[name]}")
    
    modify_state(modifier)


def cmd_reset(name: str) -> None:
    """Delete timer."""
    def modifier(state: Dict[str, Any]) -> None:
        if name in state:
            del state[name]
            print(f"Timer '{name}' deleted")
            # If current timer was deleted, clear it
            if state.get("_current") == name:
                del state["_current"]
                print(f"Current timer cleared")
        else:
            print(f"Timer '{name}' not found", file=sys.stderr)
            sys.exit(1)
    
    modify_state(modifier)


def cmd_switch(name: str) -> None:
    """Set _current to this timer."""
    def modifier(state: Dict[str, Any]) -> None:
        if name not in state:
            print(f"Timer '{name}' not found", file=sys.stderr)
            sys.exit(1)
        if name == "_current":
            print(f"Cannot switch to reserved name '_current'", file=sys.stderr)
            sys.exit(1)
        state["_current"] = name
        print(f"Switched to timer '{name}'")
    
    modify_state(modifier)


def cmd_list() -> None:
    """Show all timers with elapsed time."""
    state = get_state()
    current_time = time.time()
    
    if not state or all(k == "_current" for k in state.keys()):
        print("No timers found")
        return
    
    current = state.get("_current", "")
    
    for name, timestamp in state.items():
        if name == "_current":
            continue
        if isinstance(timestamp, (int, float)):
            elapsed = current_time - timestamp
            marker = "*" if name == current else " "
            print(f"{marker} {name}: {format_elapsed(elapsed)}")


def cmd_status(json_output: bool = False) -> None:
    """Output current timer in HH:MM:SS format or JSON for i3status."""
    state = get_state()
    current = state.get("_current")
    
    if not current or current not in state:
        if json_output:
            output = {"text": "none", "tooltip": "No active timer"}
            print(json.dumps(output))
        else:
            print("00:00:00 (no timer)")
        return
    
    timestamp = state.get(current)
    if not isinstance(timestamp, (int, float)):
        if json_output:
            output = {"text": "error", "tooltip": "Invalid timer"}
            print(json.dumps(output))
        else:
            print("00:00:00 (error)", file=sys.stderr)
            sys.exit(1)
        return
    
    elapsed = time.time() - timestamp
    formatted = format_elapsed(elapsed)
    
    if json_output:
        output = {
            "text": formatted,
            "tooltip": f"{current}: {formatted}"
        }
        print(json.dumps(output))
    else:
        print(f"{formatted} ({current})")


_menu_call_count = 0  # Track number of menu calls for dry-run testing


def rofi_dmenu(options: List[str], prompt: str = "Select", dry_run: bool = False) -> Optional[str]:
    """
    Show a rofi dmenu and return selected option.
    
    Args:
        options: List of options to display
        prompt: Prompt text for rofi
        dry_run: If True, simulate selection without invoking rofi
    
    Returns:
        Selected option string, or None if cancelled
    
    Environment Variables (for dry-run testing):
        ROFI_SELECT_INDEX: Index (1-based) for first menu call
        ROFI_SELECT_INDEX_2: Index (1-based) for second menu call (submenu)
        ROFI_SELECT_INDEX_3: Index (1-based) for third menu call (name input)
        ROFI_INPUT_TEXT: Text to simulate as user input (for prompts with no options)
        ROFI_CANCEL: If set, simulate user cancellation
    """
    global _menu_call_count
    
    if dry_run:
        _menu_call_count += 1
        
        # In dry-run mode, print options and simulate user selection
        print(f"[DRY-RUN] Rofi menu: {prompt}")
        for i, opt in enumerate(options):
            print(f"  {i + 1}. {opt}")
        
        # Check for cancellation simulation
        if os.environ.get("ROFI_CANCEL"):
            print("[DRY-RUN] Simulated user cancellation")
            return None
        
        # Check for input text simulation (for prompts with no options)
        if not options:
            input_text = os.environ.get("ROFI_INPUT_TEXT", "simulated-input")
            print(f"[DRY-RUN] Simulated input: {input_text}")
            return input_text
        
        # Determine which index variable to use based on call count
        index_var = f"ROFI_SELECT_INDEX_{_menu_call_count}" if _menu_call_count > 1 else "ROFI_SELECT_INDEX"
        select_index = os.environ.get(index_var)
        
        # Fallback to first index if specific index not set
        if not select_index:
            select_index = os.environ.get("ROFI_SELECT_INDEX")
        
        # Check for index-based selection
        if select_index:
            try:
                idx = int(select_index) - 1  # Convert to 0-based
                if 0 <= idx < len(options):
                    selected = options[idx]
                    print(f"[DRY-RUN] Simulated selection (index {select_index}): {selected}")
                    return selected
            except ValueError:
                pass
        
        # Default: select first option
        if options:
            selected = options[0]
            print(f"[DRY-RUN] Simulated selection: {selected}")
            return selected
        return None
    
    # Real rofi invocation
    try:
        result = subprocess.run(
            ["rofi", "-dmenu", "-p", prompt],
            input="\n".join(options),
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None  # User cancelled
    except FileNotFoundError:
        print("Error: rofi not found. Please install rofi.", file=sys.stderr)
        sys.exit(1)


def get_timer_list() -> List[str]:
    """Get list of timer names (excluding _current)."""
    state = get_state()
    return [name for name in state.keys() if name != "_current"]


def cmd_rofi(dry_run: bool = False) -> None:
    """
    Interactive rofi menu for timer management.
    
    Menu flow:
    1. Main menu: "Start new timer" + list of existing timers
    2. If "Start new" selected -> prompt for name -> start timer
    3. If existing timer selected -> submenu: Switch / Reset
    """
    # Build main menu options
    timer_list = get_timer_list()
    current = get_state().get("_current", "")
    
    main_options = ["Start new timer"]
    
    # Add existing timers with elapsed time display
    current_time = time.time()
    state = get_state()
    for name in timer_list:
        timestamp = state.get(name)
        if isinstance(timestamp, (int, float)):
            elapsed = current_time - timestamp
            marker = "*" if name == current else " "
            main_options.append(f"{marker} {name} ({format_elapsed(elapsed)})")
        else:
            main_options.append(f"  {name}")
    
    # Show main menu
    selection = rofi_dmenu(main_options, prompt="Countup Timer", dry_run=dry_run)
    
    if not selection:
        if dry_run:
            print("[DRY-RUN] User cancelled main menu")
        return
    
    if selection == "Start new timer":
        # Prompt for new timer name
        new_name = rofi_dmenu([], prompt="Enter timer name", dry_run=dry_run)
        
        if new_name:
            if dry_run:
                print(f"[DRY-RUN] Would start timer: {new_name}")
            else:
                cmd_start(new_name)
        elif dry_run:
            print("[DRY-RUN] User cancelled name input")
    
    else:
        # Extract timer name from selection (format: "* name (HH:MM:SS)" or "  name (HH:MM:SS)")
        # Remove marker and elapsed time
        parts = selection.split()
        if parts and parts[0] in ["*", " "]:
            parts = parts[1:]
        # Timer name is everything before the elapsed time in parentheses
        name_parts = []
        for part in parts:
            if part.startswith("("):
                break
            name_parts.append(part)
        timer_name = " ".join(name_parts)
        
        if not timer_name:
            if dry_run:
                print(f"[DRY-RUN] Could not parse timer name from: {selection}")
            return
        
        # Show submenu for existing timer
        submenu_options = ["Switch", "Reset", "Cancel"]
        submenu_selection = rofi_dmenu(submenu_options, prompt=f"Timer: {timer_name}", dry_run=dry_run)
        
        if not submenu_selection:
            if dry_run:
                print("[DRY-RUN] User cancelled submenu")
            return
        
        if dry_run:
            print(f"[DRY-RUN] Selected action: {submenu_selection} for timer: {timer_name}")
        else:
            if submenu_selection == "Switch":
                cmd_switch(timer_name)
            elif submenu_selection == "Reset":
                cmd_reset(timer_name)


def main():
    parser = argparse.ArgumentParser(
        description="Countup Timer CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # start command
    start_parser = subparsers.add_parser("start", help="Create or overwrite timer")
    start_parser.add_argument("name", help="Timer name")
    
    # reset command
    reset_parser = subparsers.add_parser("reset", help="Delete timer")
    reset_parser.add_argument("name", help="Timer name")
    
    # switch command
    switch_parser = subparsers.add_parser("switch", help="Set current timer")
    switch_parser.add_argument("name", help="Timer name")
    
    # list command
    subparsers.add_parser("list", help="Show all timers")
    
    # status command
    status_parser = subparsers.add_parser("status", help="Show current timer")
    status_parser.add_argument("--json", action="store_true", help="Output as JSON for i3status")
    
    # rofi command
    rofi_parser = subparsers.add_parser("rofi", help="Interactive rofi menu for timer management")
    rofi_parser.add_argument("--dry-run", action="store_true", help="Simulate rofi without invoking GUI")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    if args.command == "start":
        cmd_start(args.name)
    elif args.command == "reset":
        cmd_reset(args.name)
    elif args.command == "switch":
        cmd_switch(args.name)
    elif args.command == "list":
        cmd_list()
    elif args.command == "status":
        cmd_status(json_output=args.json)
    elif args.command == "rofi":
        cmd_rofi(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
