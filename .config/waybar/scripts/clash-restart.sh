#!/usr/bin/env bash
# Left click on the waybar clash module: restart clash, wait until the proxy
# path is actually healthy again, then force waybar to re-probe (SIGRTMIN+9).
# Without the wait waybar re-runs the ping script while clash is still warming
# up, painting a misleading "down" that lingers until the next 10s tick.
set -uo pipefail

CFG_DIR="$HOME/.config/clash"
CONFIG="$CFG_DIR/config.yaml"
PROXY="http://127.0.0.1:7890"
TEST_URL="https://www.gstatic.com/generate_204"
WAIT=25

notify() {
    command -v notify-send >/dev/null && notify-send -a clash -t 4000 "Clash" "$1"
}

refresh_waybar() {
    pkill -RTMIN+9 -x waybar 2>/dev/null
}

if ! systemctl --user restart clash; then
    notify "重启失败（systemctl 返回非零）"
    refresh_waybar
    exit 1
fi

ready=0
SECONDS=0
while [ "$SECONDS" -lt "$WAIT" ]; do
    code=$(curl -s -o /dev/null -m 2 -x "$PROXY" -w '%{http_code}' "$TEST_URL" 2>/dev/null)
    if [ "${code:-000}" = "204" ]; then
        ready=1
        break
    fi
    sleep 0.3
done

refresh_waybar
[ "$ready" = 1 ] || notify "重启后 ${WAIT}s 内代理未恢复"
