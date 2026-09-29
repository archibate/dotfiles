# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a single-file Terminal User Interface (TUI) for managing Clash proxy configurations. The Python script (`clash_select.py`) provides an interactive curses-based interface to select and switch between proxy servers/groups via the Clash controller API.

## Commands

### Running the Application
```bash
python3 clash_select.py
```
With custom controller and secret:
```bash
python3 clash_select.py --controller http://localhost:9090 --secret mypassword
```

### Installing Dependencies
The external dependencies are `requests` and `PyYAML` (the latter is needed only when loading local configuration):
```bash
uv run --with requests --with pyyaml clash_select.py
```
Python 3.7+ is required for dataclasses support.

## Architecture

The application consists of a single file with the following key components:

- `ControllerConfig` dataclass: Stores controller URL and secret for authentication
- API interaction functions: `fetch_proxies()`, `select_proxy()`, `selector_groups()`, `proxy_options()`, `current_selection()`
- UI function: `draw_ui()` implements the curses interface with keyboard navigation
- Main function: Parses command-line arguments and launches the TUI

### Data Flow
1. Fetch proxy configuration from Clash controller API (`/proxies`)
2. Extract "Selector" type proxy groups
3. Display groups and their available proxies in TUI
4. Handle user input to switch proxies via API (`/proxies/{group}` PUT)

## Configuration

With neither connection option supplied, read the controller and secret together from `config.yaml` beside the script. Wildcard bind addresses are connected to through loopback.

Explicit `--controller` or `--secret` bypasses file loading. The explicit-mode defaults are `http://127.0.0.1:9090` and an empty secret. A custom controller never implicitly receives local credentials. Credentials are not displayed in the TUI.

## UI Controls

- **Up/Down arrows**: Navigate proxy options within a group
- **Left/Right arrows** or **[ / ] keys**: Switch between proxy groups
- **Enter**: Select the currently highlighted proxy
- **R**: Refresh the proxy list from the controller
- **Q**: Quit the application

The UI displays:
- Current proxy group and its currently selected proxy
- List of available proxies with `→` indicating the cursor position and `*` indicating the currently active proxy
- Status messages in Chinese (e.g., "按上下键选择，Enter 切换，r 刷新，q 退出")

## Notes

- UI text is in Chinese (simplified)
- Error handling is minimal; network failures may crash the application
- HTTPS uses Requests default certificate verification
- Malformed local configuration is reported without dumping its contents
- Run configuration regressions with `python -m unittest discover -s . -p "test_*.py"` from this directory
