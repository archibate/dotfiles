#!/usr/bin/env python3
"""Append a low-volume health snapshot of each proxy provider to health.log
(or $HEALTHLOG_PATH).

One line per provider per run: timestamp, provider, alive/total, best delay.
Also logs the selected node of every url-test/fallback group, so a silently
dead provider (all alive=false) becomes visible without turning on debug logs.
"""

import json
import os
import sys
import time
import urllib.request
from pathlib import Path

HOME = Path(__file__).resolve().parent
CONFIG = HOME / "config.yaml"
LOG = Path(os.environ.get("HEALTHLOG_PATH") or HOME / "health.log")
MAX_BYTES = 1 << 20


def controller():
    secret = ""
    for line in CONFIG.read_text(errors="replace").splitlines():
        if line.startswith("secret: "):
            secret = line.split(": ", 1)[1].strip()
            break
    return "http://127.0.0.1:9090", secret


def get(base, secret, path):
    req = urllib.request.Request(base + path, headers={"Authorization": "Bearer " + secret})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.load(resp)


def snapshot():
    base, secret = controller()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    out = []
    providers = get(base, secret, "/providers/proxies")["providers"]
    for name in ("airport", "airport2"):
        entry = providers.get(name)
        if not entry:
            out.append(f"{stamp}\tprovider={name}\tmissing")
            continue
        nodes = entry.get("proxies") or []
        if not nodes:
            out.append(f"{stamp}\tprovider={name}\tempty")
            continue
        alive = [d for d in nodes if d.get("alive")]
        delays = [h[-1]["delay"] for d in alive if (h := d.get("history") or []) and h[-1]["delay"]]
        best = min(delays) if delays else None
        out.append(
            f"{stamp}\tprovider={name}\talive={len(alive)}/{len(nodes)}\tbest={best or '-'}ms"
        )
    proxies = get(base, secret, "/proxies")["proxies"]
    for name, detail in proxies.items():
        if detail.get("type") in ("URLTest", "Fallback"):
            out.append(f"{stamp}\tgroup={name}\tnow={detail.get('now')}")
    return out


def main():
    try:
        lines = snapshot()
    except Exception as exc:
        lines = [f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\terror={type(exc).__name__}: {exc}"]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if LOG.exists() and LOG.stat().st_size > MAX_BYTES:
        LOG.replace(LOG.with_suffix(".log.1"))
    with LOG.open("a") as fh:
        fh.write("\n".join(lines) + "\n")
    return 0 if not any("error=" in line for line in lines) else 1


if __name__ == "__main__":
    sys.exit(main())
