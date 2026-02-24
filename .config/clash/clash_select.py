#!/usr/bin/env python3

import argparse
import curses
import json
from dataclasses import dataclass
from typing import Dict, List

import requests


@dataclass
class ControllerConfig:
    base_url: str
    secret: str

    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.secret}"}


def fetch_proxies(config: ControllerConfig) -> Dict:
    resp = requests.get(f"{config.base_url}/proxies", headers=config.headers(), timeout=5)
    resp.raise_for_status()
    return resp.json()


def select_proxy(config: ControllerConfig, group_name: str, proxy_name: str) -> None:
    payload = {"name": proxy_name}
    resp = requests.put(
        f"{config.base_url}/proxies/{group_name}",
        headers={**config.headers(), "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=5,
    )
    resp.raise_for_status()


def selector_groups(proxies_payload: Dict) -> List[str]:
    proxies = proxies_payload["proxies"]
    names: List[str] = []
    for name, detail in proxies.items():
        if detail.get("type") == "Selector":
            names.append(name)
    return names


def proxy_options(proxies_payload: Dict, group_name: str) -> List[str]:
    proxies = proxies_payload["proxies"]
    detail = proxies[group_name]
    return detail["all"]


def current_selection(proxies_payload: Dict, group_name: str) -> str:
    proxies = proxies_payload["proxies"]
    detail = proxies[group_name]
    return detail["now"]


def draw_ui(stdscr: curses.window, config: ControllerConfig) -> None:
    curses.curs_set(0)
    stdscr.nodelay(False)
    stdscr.keypad(True)

    data = fetch_proxies(config)
    groups = selector_groups(data)
    group_idx = 0 if groups else -1
    option_idx = 0
    window_start = 0
    status_message = "按上下键选择，Enter 切换，r 刷新，q 退出"

    while True:
        stdscr.clear()
        max_y, max_x = stdscr.getmaxyx()
        visible_rows = max(1, max_y - 6)
        stdscr.addnstr(0, 0, f"Clash 控制: {config.base_url} (secret: {config.secret})", max_x - 1)
        stdscr.addnstr(1, 0, status_message, max_x - 1)
        stdscr.hline(2, 0, "-", max_x)

        if group_idx == -1:
            stdscr.addnstr(4, 0, "未找到可选的 Selector 组，检查 Clash 配置。", max_x - 1)
            stdscr.refresh()
        else:
            current_group = groups[group_idx]
            options = proxy_options(data, current_group)
            now = current_selection(data, current_group)
            if window_start > max(0, len(options) - visible_rows):
                window_start = max(0, len(options) - visible_rows)
            window_end = min(window_start + visible_rows, len(options))
            stdscr.addnstr(3, 0, f"当前组: {current_group}，已选: {now}", max_x - 1)
            for idx in range(window_start, window_end):
                row = 5 + (idx - window_start)
                if row >= max_y:
                    break
                name = options[idx]
                marker = "→" if idx == option_idx else " "
                prefix = "*" if name == now else " "
                stdscr.addnstr(row, 0, f"{marker}{prefix} {name}", max_x - 1)
            if window_end < len(options) and 5 + (window_end - window_start) < max_y:
                stdscr.addnstr(5 + (window_end - window_start), 0, "...(更多)", max_x - 1)
            stdscr.refresh()

        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break
        if group_idx == -1:
            continue

        if key == curses.KEY_UP:
            options_len = len(proxy_options(data, groups[group_idx]))
            option_idx = (option_idx - 1) % options_len
            if option_idx < window_start:
                window_start = option_idx
        elif key == curses.KEY_DOWN:
            options_len = len(proxy_options(data, groups[group_idx]))
            option_idx = (option_idx + 1) % options_len
            if option_idx >= window_start + visible_rows:
                window_start = option_idx - visible_rows + 1
        elif key in (curses.KEY_RIGHT, ord("]")):
            group_idx = (group_idx + 1) % len(groups)
            option_idx = 0
            window_start = 0
        elif key in (curses.KEY_LEFT, ord("[")):
            group_idx = (group_idx - 1) % len(groups)
            option_idx = 0
            window_start = 0
        elif key in (ord("r"), ord("R")):
            data = fetch_proxies(config)
            groups = selector_groups(data)
            if not groups:
                group_idx = -1
            else:
                group_idx = min(group_idx, len(groups) - 1)
                option_idx = 0
                window_start = 0
            status_message = "已刷新"
        elif key in (curses.KEY_ENTER, 10, 13):
            current_group = groups[group_idx]
            options = proxy_options(data, current_group)
            chosen = options[option_idx]
            select_proxy(config, current_group, chosen)
            data = fetch_proxies(config)
            status_message = f"{current_group} 切换至 {chosen} 成功"
        else:
            status_message = "按上下键选择，Enter 切换，左右键切组，r 刷新，q 退出"


def main() -> None:
    parser = argparse.ArgumentParser(description="Clash 简易 TUI")
    parser.add_argument("--controller", default="http://127.0.0.1:9090", help="Clash 控制器地址")
    parser.add_argument("--secret", default="myssr", help="Clash 外部控制密码")
    args = parser.parse_args()

    config = ControllerConfig(base_url=args.controller, secret=args.secret)
    curses.wrapper(draw_ui, config)


if __name__ == "__main__":
    main()

