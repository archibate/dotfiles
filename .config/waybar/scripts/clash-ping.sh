#!/usr/bin/env bash
# Waybar module: end-to-end latency of one Clash proxy path.
# Shows the real exit node with its airport, e.g. "204ms 机场2 日本01".
# Usage: clash-ping.sh [GROUP TEST_URL EXPECTED_CODE ICON_CODEPOINT NAME]
#   default follows the Proxy group and tests gstatic (204);
#   the Claude module runs: clash-ping.sh Anthropic https://api.anthropic.com/api/hello 200 f06a9 claude
# One failed probe shows yellow "抖", three in a row (~15s) show red "down".
# Left click re-tests all nodes without restarting (clash-kick.sh), middle click
# restarts clash (clash-restart.sh), right click refreshes subscriptions.
set -uo pipefail

CFG_DIR="$HOME/.config/clash"
CONFIG="$CFG_DIR/config.yaml"
PROXY="http://127.0.0.1:7890"
GROUP="${1:-Proxy}"
TEST_URL="${2:-https://www.gstatic.com/generate_204}"
EXPECT="${3:-204}"
ICON=$(printf "\\U$(printf '%08x' "0x${4:-f0ac}")")
NAME="${5:-clash}"
TEST_HOST=${TEST_URL#https://}; TEST_HOST=${TEST_HOST%%/*}
GRACE=15     # seconds after a (re)start during which failures mean "warming up"
DOWN_AFTER=3 # consecutive failed probes before showing "down"
FAILS_FILE="${XDG_RUNTIME_DIR:-/tmp}/${NAME}-ping.fails"

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

# Follow `now` from $GROUP down to the real node, e.g.
# Proxy → Proxy Auto → 日本 → 日本 机场2 → 🇯🇵 日本 01 - 1倍率.
chain=$(api GET /proxies 2>/dev/null | jq -r '
    .proxies as $p
    | def down($n; $d): if ($p[$n].now // "") != "" and $d < 8 then [$n] + down($p[$n].now; $d + 1) else [$n] end;
    down($g; 0) | join(" → ")' --arg g "$GROUP" 2>/dev/null)
leaf=${chain##* → }
[ -z "${leaf:-}" ] && leaf="?"

# Which airport the node belongs to, its latest test delay, and a short label.
# Labels: "JP丨日本1" → "日本1", "🇯🇵 日本 01 - 1倍率" → "日本01", "🇯🇵 日本 09 家宽" → "日本09家宽".
# The delay comes from the group's own tests against TEST_URL (kept under
# .extra[url]); .history is the provider health check, every 10 minutes.
read -r label delay tested < <(api GET /providers/proxies 2>/dev/null | jq -r --arg n "$leaf" --arg u "$TEST_URL" '
    [.providers | to_entries[] | .key as $prov | .value.proxies[] | select(.name == $n)
     | {prov: $prov, h: (.extra[$u].history[-1] // .history[-1] // {})}][0] // {prov: "", h: {}}
    | (if .prov == "airport" then "机场1" elif .prov == "airport2" then "机场2" elif .prov == "airport3" then "机场3" else "" end) as $air
    | ($n | sub(" *- *[0-9.]+倍率$"; "") | sub("^[A-Z]+丨"; "") | sub("\\|.*$"; "") | gsub("[\\x{1F1E6}-\\x{1F1FF}]"; "") | gsub(" "; "")) as $short
    | "\(if $air == "" then $short else $air + "_" + $short end) \(.h.delay // 0) \(.h.time // "" | .[11:19])"' 2>/dev/null)
label=${label:-$leaf}
label=${label/_/ }
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

clicks="左键重测节点 · 中键重启 clash · 右键刷新订阅"

if [ "${code:-000}" != "$EXPECT" ]; then
    fails=$(( $(cat "$FAILS_FILE" 2>/dev/null || echo 0) + 1 ))
    echo "$fails" > "$FAILS_FILE"
    tip="连续 ${fails} 次测不通（HTTP ${code:-000}）\n${chain}\n${clicks}"
    if [ "$age" -lt "$GRACE" ]; then
        emit "$ICON 启动中" "starting" "Clash ${age}s 前刚启动，等待就绪…\n${chain}"
    elif [ "$fails" -lt "$DOWN_AFTER" ]; then
        emit "$ICON 抖 $label" "warning" "$tip"
    else
        emit "$ICON down $label" "critical" "$tip"
    fi
else
    echo 0 > "$FAILS_FILE"
    tip="url-test 延迟 ${delay}ms（${tested} 测）\n端到端 ${TEST_HOST} ${EXPECT} ${ms}ms\n${chain}\n${clicks}"
    if [ "$delay" -eq 0 ]; then
        emit "$ICON ${ms}ms $label" "warning" "$tip"
    elif [ "$delay" -lt 500 ]; then
        emit "$ICON ${delay}ms $label" "ok" "$tip"
    elif [ "$delay" -lt 1200 ]; then
        emit "$ICON ${delay}ms $label" "warning" "$tip"
    else
        emit "$ICON ${delay}ms $label" "critical" "$tip"
    fi
fi
