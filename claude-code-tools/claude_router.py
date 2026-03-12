#!/usr/bin/env python3
"""Usage: claude_router.py [router_name] [claude args...]"""
import json, os, sys
from pathlib import Path

DEFAULT_ROUTER = "default"

def main():
    router_file = Path(os.path.realpath(__file__)).parent / "router.json"
    routers = json.loads(router_file.read_text())

    if len(sys.argv) < 2:
        # Case 3: no args -> default router, run claude
        router_name = DEFAULT_ROUTER
        claude_args = []
    elif len(sys.argv) == 2:
        # Single arg: could be router name or claude arg
        arg = sys.argv[1]
        if arg in routers:
            # Case 2: arg is router name -> use that router, run claude
            router_name = arg
            claude_args = []
        else:
            # Case 4: arg is not a router -> default router, run claude <arg>
            router_name = DEFAULT_ROUTER
            claude_args = [arg]
    else:
        # 2+ args: check if first is a router name
        first_arg = sys.argv[1]
        if first_arg in routers:
            # Case 1: first arg is router -> use that router, run claude <rest>
            router_name = first_arg
            claude_args = sys.argv[2:]
        else:
            # Case 4: first arg not a router -> default router, run claude <all args>
            router_name = DEFAULT_ROUTER
            claude_args = sys.argv[1:]

    env = {**os.environ, **{k: str(v) for k, v in routers[router_name].items()}}
    os.execvpe("claude", ["claude"] + claude_args, env)

if __name__ == "__main__":
    main()
