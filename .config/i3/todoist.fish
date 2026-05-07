#!/usr/bin/env fish

# Quick-capture for Todoist via rofi.
# Mirrors brainstack.fish UX. Token comes from ~/.config/fish/.env (TODOIST_TOKEN).

set -q TODOIST_TOKEN; or set -gx TODOIST_TOKEN (rg '^TODOIST_TOKEN=' ~/.config/fish/.env | string replace 'TODOIST_TOKEN=' '')

set api https://api.todoist.com/api/v1

function _api -a method path
    curl -sS -X $method \
        -H "Authorization: Bearer $TODOIST_TOKEN" \
        -H 'Content-Type: application/json' \
        $argv[3..] $api$path
end

function add_task
    set text (echo -n | rofi -dmenu -p todoist -mesg "支持自然语言: '买菜 tomorrow p1 #购物'" | string trim)
    test -z "$text"; and return

    set body (jq -nc --arg t "$text" '{text:$t}')
    set resp (_api POST /tasks/quick -d $body)
    set content (echo $resp | jq -r '.content // empty')
    if test -n "$content"
        notify-send "todoist" "✓ $content"
    else
        notify-send -u critical "todoist" (echo $resp | jq -r '.error // "unknown error"')
    end
end

function show_menu
    set tasks_json (_api GET /tasks?limit=50)
    set lines (echo $tasks_json | jq -r '.results[]? | [.id, .content] | @tsv')

    if test -z "$lines"
        add_task
        return
    end

    set selected (printf "%s\n" $lines | awk -F'\t' '{print $2}' | rofi -dmenu -i -p todoist -format 'i\ts')
    test -z "$selected"; and return

    set idx (string split -f 1 \t -- $selected)
    set typed (string split -f 2 \t -- $selected)

    if test "$idx" = -1
        # Custom text → quick-add
        set body (jq -nc --arg t "$typed" '{text:$t}')
        set resp (_api POST /tasks/quick -d $body)
        notify-send "todoist" "✓ "(echo $resp | jq -r '.content')
        return
    end

    set entry (printf "%s\n" $lines | sed -n (math $idx + 1)"p")
    set task_id (echo $entry | cut -f1)
    set task_text (echo $entry | cut -f2)

    set action (printf "Complete\nDelete\nOpen in Browser\nCopy Text\n" | rofi -dmenu -i -p $task_text)

    switch $action
        case Complete
            _api POST /tasks/$task_id/close >/dev/null
            notify-send "todoist" "✓ done: $task_text"
        case Delete
            _api DELETE /tasks/$task_id >/dev/null
            notify-send "todoist" "🗑 deleted: $task_text"
        case "Open in Browser"
            xdg-open "https://app.todoist.com/app/task/$task_id"
        case "Copy Text"
            echo -n $task_text | xclip -selection clipboard
            notify-send "todoist" "📋 $task_text"
    end
end

function main
    switch "$argv[1]"
        case menu
            show_menu
        case add ''
            add_task
    end
end

main $argv
