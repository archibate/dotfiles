#!/usr/bin/env python3
"""Usage: claude_router.py <router_name> [claude args...]"""
import json, os, sys
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <router> [claude args...]", file=sys.stderr)
        sys.exit(1)

    router_name = sys.argv[1]
    claude_args = sys.argv[2:]

    router_file = Path(os.path.realpath(__file__)).parent / "router.json"
    routers = json.loads(router_file.read_text())

    if router_name not in routers:
        available = ", ".join(routers.keys())
        print(f"Error: router '{router_name}' not found. Available: {available}", file=sys.stderr)
        sys.exit(1)

    env = {**os.environ, **{k: str(v) for k, v in routers[router_name].items()}}
    os.execvpe("claude", ["claude"] + claude_args, env)

if __name__ == "__main__":
    main()
