#!/usr/bin/env python3
import subprocess
import re
import sys
import time

def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv

    result = subprocess.run(["adb", "tcpip", "5555"])
    if result.returncode != 0:
        print("Error: Failed to enable TCP mode", file=sys.stderr)
        sys.exit(1)

    time.sleep(1)

    for _ in range(5):
        result = subprocess.run(["adb", "shell", "ip", "a"], capture_output=True, text=True)
        if result.returncode == 0:
            break
        time.sleep(1)
    else:
        print("Error: Failed to get network info after retries", file=sys.stderr)
        sys.exit(1)

    match = re.search(r'wlan0:.*?inet\s+(\d+\.\d+\.\d+\.\d+)', result.stdout, re.DOTALL)
    if not match:
        print("Error: Could not find wlan0 IP", file=sys.stderr)
        sys.exit(1)

    ip = match.group(1)

    if dry_run:
        print(f"adb connect {ip}")
    else:
        subprocess.run(["adb", "connect", ip])

if __name__ == "__main__":
    main()
