#!/usr/bin/env python3
"""
repeat_clicker.py - 鼠标连点器

用法:
    python repeat_clicker.py --interval 100 --count 50 --button left
"""

import argparse
import time
import sys
from pynput.mouse import Button, Controller

def parse_arguments():
    parser = argparse.ArgumentParser(description="鼠标连点器")
    parser.add_argument("--interval", type=int, default=100,
                        help="点击间隔（毫秒），默认100")
    parser.add_argument("--count", type=int, default=50,
                        help="点击次数，默认50")
    parser.add_argument("--button", choices=["left", "right"], default="left",
                        help="鼠标按钮：left 或 right，默认left")
    return parser.parse_args()

def main():
    args = parse_arguments()

    # 参数转换
    interval_sec = args.interval / 1000.0
    button = Button.left if args.button == "left" else Button.right
    count = args.count

    print(f"开始连点：次数={count}，间隔={interval_sec}秒，按钮={args.button}")
    print("按 Ctrl+C 可提前终止")

    mouse = Controller()
    try:
        for i in range(count):
            mouse.click(button, 1)
            # 不是最后一次点击时才等待，避免多余等待
            if i < count - 1 and interval_sec > 0:
                time.sleep(interval_sec)
        print("连点完成！")
    except KeyboardInterrupt:
        print("\n用户中断，连点已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
