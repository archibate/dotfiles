#!/usr/bin/env bash
# Refresh both clash proxy subscriptions (right click on the waybar module).
set -uo pipefail

CONFIG="$HOME/.config/clash/config.yaml"
secret=$(grep -m1 '^secret: ' "$CONFIG" 2>/dev/null | cut -d' ' -f2-)

notify() {
    command -v notify-send >/dev/null && notify-send -a clash -t 4000 "Clash 订阅" "$1"
}

failed=""
for p in airport airport2; do
    if ! curl -s -m 60 -o /dev/null -X PUT -H "Authorization: Bearer $secret" \
        "http://127.0.0.1:9090/providers/proxies/$p"; then
        failed="$failed $p"
    fi
done

if [ -n "$failed" ]; then
    notify "刷新失败:$failed"
    exit 1
fi
notify "两个订阅已刷新"
