#!/usr/bin/env bash
# Waybar module: end-to-end latency of the Clash proxy path (gstatic 204).
# Left click restarts clash (clash-restart.sh), right click refreshes subscriptions.
set -uo pipefail

CFG_DIR="$HOME/.config/clash"
CONFIG="$CFG_DIR/config.yaml"
PROXY="http://127.0.0.1:7890"
TEST_URL="https://www.gstatic.com/generate_204"
ICON=$(printf '\uf0ac')
GRACE=15 # seconds after a (re)start during which failures mean "warming up"

secret=$(grep -m1 '^secret: ' "$CONFIG" 2>/dev/null | cut -d' ' -f2-)

api() { # api METHOD PATH
    curl -s -m 5 -X "$1" -H "Authorization: Bearer $secret" \
        -H 'Content-Type: application/json' "http://127.0.0.1:9090$2"
}

emit() { # emit TEXT CLASS TOOLTIP
    printf '{"text":"%s","class":"%s","tooltip":"%s"}\n' "$1" "$2" "$3"
}

read -r code secs < <(curl -s -o /dev/null -m 6 -x "$PROXY" \
    -w '%{http_code} %{time_total}' "$TEST_URL" 2>/dev/null)

node=$(api GET '/proxies/Proxy%20Auto' 2>/dev/null | jq -r '.now // empty' 2>/dev/null)
[ -z "${node:-}" ] && node="?"

# Latest url-test delay of the picked node (the number Proxy Auto compares),
# taken from the provider health check; 0 means dead or not yet tested.
read -r delay tested < <(api GET /providers/proxies 2>/dev/null | jq -r --arg n "$node" \
    '[.providers[].proxies[] | select(.name == $n) | .history[-1] // empty][0] // {}
     | "\(.delay // 0) \(.time // "" | .[11:19])"' 2>/dev/null)
delay=${delay:-0}
tested=${tested:-?}

ms=$(awk -v t="${secs:-0}" 'BEGIN{printf "%d", t*1000}')

# Age of the running clash instance, so a just-restarted daemon that fails the
# probe is reported as "starting" instead of a misleading red "down".
start_us=$(systemctl --user show -p ActiveEnterTimestampMonotonic --value clash 2>/dev/null)
if [ -n "${start_us:-}" ] && [ "${start_us:-0}" != "0" ]; then
    up_s=$(cut -d' ' -f1 /proc/uptime)
    age=$(( ${up_s%.*} - start_us / 1000000 ))
    [ "$age" -lt 0 ] && age=0
else
    age=999999
fi

if [ "${code:-000}" != "204" ]; then
    if [ "$age" -lt "$GRACE" ]; then
        emit "$ICON 启动中" "starting" "Clash ${age}s 前刚启动，等待就绪…\n出口: $node"
    else
        emit "$ICON down" "critical" "Clash 不可用（HTTP ${code:-000}）\n出口: $node\n左键重启 clash"
    fi
else
    tip="url-test 延迟 ${delay}ms（${tested} 测）\n端到端 gstatic 204 ${ms}ms\n出口: $node\n左键重启 · 右键刷新订阅"
    if [ "$delay" -eq 0 ]; then
        emit "$ICON ? $node" "warning" "$tip"
    elif [ "$delay" -lt 500 ]; then
        emit "$ICON ${delay}ms $node" "ok" "$tip"
    elif [ "$delay" -lt 1200 ]; then
        emit "$ICON ${delay}ms $node" "warning" "$tip"
    else
        emit "$ICON ${delay}ms $node" "critical" "$tip"
    fi
fi
