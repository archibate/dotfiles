#!/usr/bin/env fish

# Quick-capture for Todoist via rofi.
# Mirrors brainstack.fish UX. Token comes from ~/.config/fish/.env (TODOIST_TOKEN).

set -q TODOIST_TOKEN; or set -gx TODOIST_TOKEN (rg '^TODOIST_TOKEN=' ~/.config/fish/.env | string replace 'TODOIST_TOKEN=' '')

set api https://api.todoist.com/api/v1
set source_label i3   # auto-tag for every task added via this script

function _quick_add -a text
    # /tasks/quick parses date / priority / #project but ignores @label,
    # so create first, then patch labels in a second call.
    set body (jq -nc --arg t "$text" '{text:$t}')
    set resp (_api POST /tasks/quick -d $body)
    set tid (echo $resp | jq -r '.id // empty')
    test -z "$tid"; and echo $resp; and return 1

    set patch (jq -nc --arg l $source_label '{labels:[$l]}')
    _api POST /tasks/$tid -d $patch
end

function _api -a method path
    curl -sS -X $method \
        -H "Authorization: Bearer $TODOIST_TOKEN" \
        -H 'Content-Type: application/json' \
        $argv[3..] $api$path
end

function add_task
    set text (echo -n | rofi -dmenu -p todoist -mesg "自然语言: '买菜 tomorrow p1 #购物' (auto-tagged @$source_label)" | string trim)
    test -z "$text"; and return

    set resp (_quick_add $text)
    set content (echo $resp | jq -r '.content // empty')
    if test -n "$content"
        set due (echo $resp | jq -r '.due.string // empty')
        set prio (echo $resp | jq -r '.priority // 1')   # API: 4=p1,3=p2,2=p3,1=p4
        set summary "✓ $content @$source_label"
        test -n "$due"; and set summary "$summary"\n"📅 $due"
        test "$prio" != 1; and set summary "$summary  p"(math 5 - $prio)
        notify-send "todoist" $summary
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
        # Custom text → quick-add (auto-tagged)
        set resp (_quick_add $typed)
        set content (echo $resp | jq -r '.content // empty')
        set due (echo $resp | jq -r '.due.string // empty')
        set prio (echo $resp | jq -r '.priority // 1')
        set summary "✓ $content @$source_label"
        test -n "$due"; and set summary "$summary"\n"📅 $due"
        test "$prio" != 1; and set summary "$summary  p"(math 5 - $prio)
        notify-send "todoist" $summary
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
