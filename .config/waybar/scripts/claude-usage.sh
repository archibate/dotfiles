#!/usr/bin/env bash
# Waybar module: Claude subscription quota, e.g. "󰊚 16% 9%" = 5h 16%, 7d 9%.
# Data comes from claude-usage (~/.local/bin), which caches the private
# /api/oauth/usage reply for 5 min, so the 60 s poll calls the API at most
# once per 5 min. On any failure the last good values show dimmed ("stale").
# Only Claude Code refreshes the OAuth token; this script never does (a rotated
# refresh token could log Claude Code out), so once the token expires the
# module stays stale until Claude Code runs again.
# Usage: claude-usage.sh          print one waybar JSON line
#        claude-usage.sh --force  refetch now (left click), then redraw
set -uo pipefail

export https_proxy=http://127.0.0.1:7890 # waybar's environment has no proxy
CFG="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CACHE="$CFG/.claude-usage-cache.json"
CRED="$CFG/.credentials.json"
SIGNAL=10
ICON=$'\U000F029A' # nf-md-gauge

now=$(date +%s)
exp_ms=$(jq -r '.claudeAiOauth.expiresAt // 0 | floor' "$CRED" 2>/dev/null)
retry=$(jq -r '.retry_until // 0 | floor' "$CACHE" 2>/dev/null)
token_ok=$(( ${exp_ms:-0} / 1000 > now ))
backoff=$(( ${retry:-0} > now ))

if [ "${1:-}" = --force ]; then
    # --force skips claude-usage's own 429 guard, so check it here.
    if [ "$token_ok" = 1 ] && [ "$backoff" = 0 ]; then
        claude-usage --force --json >/dev/null 2>&1
    fi
    pkill -RTMIN+$SIGNAL -x waybar
    exit 0
fi

err=""
if [ "$token_ok" = 0 ]; then
    err="token 已过期，运行 claude 后恢复" # skip the fetch: it can only 401
elif out=$(claude-usage --json 2>&1); then
    [ "$backoff" = 1 ] && err="被限流，$(( retry - now ))s 后重试"
else
    case $out in
        *"(network)"*) err="连不上 api.anthropic.com" ;;
        *"(http-401)"*) err="token 失效，运行 claude 后恢复" ;;
        *) err=${out##*$'\n'} ;;
    esac
fi

if [ -z "$err" ]; then
    data=$out
else
    data=$(jq -c '.last_good // empty' "$CACHE" 2>/dev/null)
fi
ts=$(jq -r '.timestamp // 0 | floor' "$CACHE" 2>/dev/null)

jq -c --arg err "$err" --argjson ts "${ts:-0}" --arg icon "$ICON" '
    def esc: gsub("&"; "&amp;") | gsub("<"; "&lt;") | gsub(">"; "&gt;");
    def pct: (.utilization // 0) | floor;
    def lpad: ("   " + tostring)[-3:];
    def epoch: try (sub("\\.[0-9]+"; "") | sub("\\+00:00$"; "Z") | fromdateiso8601) catch null;
    def left: (. - now | floor) as $s
        | if $s <= 0 then "已重置"
          elif $s >= 86400 then "\($s / 86400 | floor)d\($s % 86400 / 3600 | floor)h"
          elif $s >= 3600 then "\($s / 3600 | floor)h\($s % 3600 / 60 | floor)m"
          else "\($s / 60 | floor)m" end;
    def row($label; $fmt):
        (.resets_at // "" | epoch) as $t
        | "\($label) \(pct | lpad)%"
          + if $t == null then "" else " · 重置 \($t | strflocaltime($fmt))（\($t | left)）" end;
    if . == null then
        {text: "\($icon) --", class: "stale", tooltip: ("Claude 用量：\($err)" | esc)}
    else
        (.five_hour // {}) as $f | (.seven_day // {}) as $w
        | ([($f | pct), ($w | pct)] | max) as $max
        | {
            text: "\($icon) \($f | pct)% \($w | pct)%",
            class: (if $err != "" then "stale"
                    elif $max >= 90 then "critical"
                    elif $max >= 70 then "warning"
                    else "normal" end),
            tooltip: ([
                (if $err != "" then "数据过期：\($err)" else empty end),
                ($f | row("5h"; "%H:%M")),
                ($w | row("7d"; "%m-%d %H:%M")),
                "更新 \(if $ts > 0 then $ts | strflocaltime("%H:%M") else "?" end) · 左键刷新"
            ] | join("\n") | esc)
          }
    end' <<<"${data:-null}" 2>/dev/null ||
    printf '{"text":"%s --","class":"stale","tooltip":"Claude 用量解析失败"}\n' "$ICON"
