#!/usr/bin/env bash
# Waybar module: Kimi subscription quota, e.g. "󰊚 16% 9%" = 5h 16%, 1m 9%.
# Reads the existing Kimi Code credential and caches the last successful response.
set -uo pipefail

KIMI_HOME="${KIMI_CODE_HOME:-$HOME/.kimi-code}"
CREDENTIALS="$KIMI_HOME/credentials/kimi-code.json"
BASE_URL="${KIMI_CODE_BASE_URL:-https://api.kimi.com/coding/v1}"
DIR="/run/user/$UID/kimi-usage"
CACHE="$DIR/usage.json"
LIVE=300
ICON=$'\U000F029A' # nf-md-gauge

umask 077
mkdir -p "$DIR"

token=$(jq -r '.access_token // empty' "$CREDENTIALS" 2>/dev/null)
response=""
if [[ -n "$token" ]]; then
    response=$(printf 'header = "Authorization: Bearer %s"\n' "$token" |
        curl -sS --fail --max-time 8 --config - "${BASE_URL%/}/usages" 2>/dev/null) || response=""
fi

if [[ -n "$response" ]] && jq -e '.usages | type == "object"' >/dev/null 2>&1 <<<"$response"; then
    printf '%s\n' "$response" >"$CACHE.$$" && mv -f "$CACHE.$$" "$CACHE"
fi

newest=0
[[ -f "$CACHE" ]] && newest=$(stat -c %Y "$CACHE" 2>/dev/null)

jq -c --argjson newest "${newest:-0}" --argjson live "$LIVE" --arg icon "$ICON" '
    def epoch: if type == "number" then .
        else try (sub("\\.[0-9]+"; "") | sub("\\+00:00$"; "Z") | fromdateiso8601) catch null end;
    def win($k): .usages[$k] as $w
        | ($w.used_ratio | if type == "number" then . else try tonumber catch null end) as $r
        | if ($w | type) != "object" or $r == null then null else
            {p: (if $r <= 0 then 0 elif $r >= 1 then 100 else ($r * 100 | round) end),
             t: ($w.reset_time | epoch)}
            | if .t != null and .t <= now then .p = 0 else . end
          end;
    def left: (. - now | floor) as $s
        | if $s >= 86400 then "\($s / 86400 | floor)d\($s % 86400 / 3600 | floor)h"
          elif $s >= 3600 then "\($s / 3600 | floor)h\($s % 3600 / 60 | floor)m"
          else "\($s / 60 | floor)m" end;
    def row($label; $fmt): "\($label) \(("   " + (.p | tostring))[-3:])%"
        + if .t == null then ""
          elif .t <= now then " · 已重置"
          else " · 重置 \(.t | strflocaltime($fmt))（\(.t | left)）" end;
    (. | win("limit_5h")) as $f
    | (. | win("limit_month_total")) as $w
    | ($newest < now - $live) as $stale
    | if $f == null and $w == null then
        {text: "\($icon) --", class: "stale", tooltip: "暂无 Kimi 用量数据"}
      else
        ([$f.p, $w.p] | map(. // 0) | max) as $max
        | {
            text: "\($icon) \($f.p | if . == null then "-" else "\(.)%" end) \($w.p | if . == null then "-" else "\(.)%" end)",
            class: (if $stale then "stale"
                    elif $max >= 90 then "critical"
                    elif $max >= 70 then "warning"
                    else "normal" end),
            tooltip: ([
                (if $stale then "用量更新失败（数据截至 \($newest | strflocaltime("%m-%d %H:%M"))）" else empty end),
                (if $f then $f | row("5h"; "%H:%M") else "5h   -" end),
                (if $w then $w | row("1m"; "%m-%d %H:%M") else "1m   -" end)
            ] | join("\n"))
          }
      end' "$CACHE" 2>/dev/null ||
    printf '{"text":"%s --","class":"stale","tooltip":"Kimi 用量不可用"}\n' "$ICON"
