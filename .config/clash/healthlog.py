#!/usr/bin/env python3
"""Append a health snapshot of each proxy provider to health.log
(or $HEALTHLOG_PATH). Meant to run every minute.

- provider: one line per provider per run: alive/total, best delay
- group: the selected node of every url-test/fallback group, written when it
  changes (and on the first run), so switches are visible to the minute
- tests: every test result of every group member against that group's test
  URL since the last run, one line per group. mihomo keeps only the last 10
  results per node, so without this the reason a group stayed on a node is
  gone about 10 minutes after an outage. Format: node@HH:MM:SS=delay, 0 = failed.
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
STATE = LOG.with_suffix(".state.json")
MAX_BYTES = 16 << 20


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


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def sortable(t):
    """mihomo times drop trailing zeros of the fraction; pad it so strings compare in order."""
    frac = t[20:].split("+")[0].split("-")[0].split("Z")[0] if t[19:20] == "." else ""
    return t[:19] + "." + frac.ljust(9, "0")


def snapshot(state):
    base, secret = controller()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    out = []
    providers = get(base, secret, "/providers/proxies")["providers"]
    for name in ("airport", "airport2", "airport3"):
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
    groups = {n: d for n, d in proxies.items() if d.get("type") in ("URLTest", "Fallback")}
    # provider nodes are not listed in /proxies; groups (members of Proxy Auto) are
    nodes = dict(proxies)
    for entry in providers.values():
        for d in entry.get("proxies") or []:
            nodes[d["name"]] = d

    last_now = state.get("now", {})
    for name, detail in groups.items():
        now = detail.get("now")
        if last_now.get(name) != now:
            out.append(f"{stamp}\tgroup={name}\tnow={now}")
    state["now"] = {n: d.get("now") for n, d in groups.items()}

    # a node can sit in several groups with the same test URL; log it once per URL
    seen = state.get("seen", {})
    done = set()
    for name, detail in groups.items():
        url = detail.get("testUrl")
        tests = []
        for member in detail.get("all") or []:
            key = f"{member}\t{url}"
            if key in done:
                continue
            done.add(key)
            history = ((nodes.get(member) or {}).get("extra") or {}).get(url, {}).get("history") or []
            new = [h for h in history if sortable(h["time"]) > seen.get(key, "")]
            if new:
                seen[key] = sortable(new[-1]["time"])
                tests += [f"{member}@{h['time'][11:19]}={h['delay']}" for h in new]
        if tests:
            out.append(f"{stamp}\ttests={name}\t{' '.join(tests)}")
    state["seen"] = seen
    return out


def main():
    state = load_state()
    try:
        lines = snapshot(state)
    except Exception as exc:
        lines = [f"{time.strftime('%Y-%m-%dT%H:%M:%S')}\terror={type(exc).__name__}: {exc}"]
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if LOG.exists() and LOG.stat().st_size > MAX_BYTES:
        LOG.replace(LOG.with_suffix(".log.1"))
    with LOG.open("a") as fh:
        fh.write("\n".join(lines) + "\n")
    STATE.write_text(json.dumps(state, ensure_ascii=False))
    return 0 if not any("error=" in line for line in lines) else 1


if __name__ == "__main__":
    sys.exit(main())
