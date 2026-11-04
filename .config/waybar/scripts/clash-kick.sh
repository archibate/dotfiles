#!/usr/bin/env bash
# Left click on the waybar clash module: re-test every node right now and let
# the groups re-pick, then drop old connections so apps reconnect through the
# new picks. Unlike a restart there is no warm-up window where groups fall back
# to DIRECT and hit poisoned DNS (discord.com → 103.200.30.143 etc.).
set -uo pipefail

CONFIG="$HOME/.config/clash/config.yaml"
secret=$(grep -m1 '^secret: ' "$CONFIG" 2>/dev/null | cut -d' ' -f2-)

api() { # api METHOD PATH [curl args...]
    local m=$1 p=$2; shift 2
    curl -s -X "$m" -H "Authorization: Bearer $secret" "$@" "http://127.0.0.1:9090$p"
}
urlenc() { jq -rn --arg s "$1" '$s | @uri'; }

notify() {
    command -v notify-send >/dev/null && notify-send -a clash -t 4000 "Clash" "$1"
}

refresh_waybar() {
    pkill -RTMIN+9 -x waybar 2>/dev/null
}

notify "正在重测节点…"

# 1. Re-test the auto groups (this tests every member node): groups whose
#    members are all nodes first, then
#    the groups built on top of them, so the upper layers see fresh results.
groups=$(api GET /proxies -m 5 | jq -r '
    .proxies as $p
    | [$p | to_entries[] | select(.value.type == "URLTest" or .value.type == "Fallback")]
    | (map(select(all(.value.all[]; ($p[.].all // null) == null))) | map(.key) | join("\n")),
      "--",
      (map(select(any(.value.all[]; ($p[.].all // null) != null))) | map(.key) | join("\n"))')
while IFS= read -r g; do
    if [ "$g" = "--" ]; then
        wait
        continue
    fi
    [ -z "$g" ] && continue
    url=$(api GET "/proxies/$(urlenc "$g")" -m 5 | jq -r '.testUrl // "https://www.gstatic.com/generate_204"')
    api GET "/group/$(urlenc "$g")/delay?url=$(urlenc "$url")&timeout=5000" -m 8 -o /dev/null &
done <<< "$groups"
wait

# 2. Drop old connections so they reconnect through the new picks.
api DELETE /connections -m 5 -o /dev/null

refresh_waybar
now=$(api GET /proxies -m 5 | jq -r '.proxies as $p
    | def down($n; $d): if ($p[$n].now // "") != "" and $d < 8 then down($p[$n].now; $d + 1) else $n end;
    down("Proxy"; 0)')
notify "重测完了，现在走 ${now:-?}"
