#!/usr/bin/env fish

set shot_dir ~/.local/state/brainstack/screenshots
set log_file ~/.local/state/brainstack/entries.tsv

function add_entry
    set date_time $argv[1]
    set text $argv[2]
    set shot_path $argv[3]
    printf "%s\t%s\t%s\n" $date_time $text $shot_path >>$log_file
end

function show_add
    set text (echo -n | rofi -dmenu -p brainstack | tr '\t' ' ' | string trim)
    insert_entry "$text"
end

function show_menu
    if not test -f $log_file
        show_add
        return $status
    end

    set entries (tac $log_file)
    set display_lines (printf "%s\n" $entries | awk -F'\t' '{print $1 " | " $2}')
    set selected_pair (printf "%s\n" $display_lines | rofi -dmenu -p brainstack -format 'i\ts')
    if test -z "$selected_pair"
        return $status
    end
    
    set selected (string split -f 1 '\t' -- $selected_pair)
    set selected_string (string split -f 2 '\t' -- $selected_pair)
    if test "$selected" = "-1"
        insert_entry $selected_string
        return $status
    end

    set entry (printf "%s\n" $entries | sed -n (math $selected + 1)"p")
    # set date_time (echo $entry | cut -f1)
    set text (echo $entry | cut -f2)
    set shot_path (echo $entry | cut -f3)

    set action (printf "Open Screenshot\nOpen in Editor\nDelete Entry\nCopy Text\nAsk AI\nSearch in Web\n" | rofi -dmenu -i -p action)
    
    switch $action
        case "Open Screenshot"
            feh -F $shot_path
        case "Delete Entry"
            set total_lines (wc -l <$log_file)
            set target_line (math $total_lines - $selected)
            sed -i $target_line"d" $log_file
            rm -f $shot_path
            notify-send "brainstack" "Entry deleted: $text"
        case "Copy Text"
            echo -n $text | xclip -selection clipboard
            notify-send "brainstack" "Text copied: $text"
        case "Open in Editor"
            set total_lines (wc -l <$log_file)
            set target_line (math $total_lines - $selected)
            $TERMINAL $EDITOR +$target_line $log_file
        case "Ask AI"
            set output (ask "make a short answer on user question: $text" <&- | tee /tmp/answer.md)
            notify-send "brainstack" $output
        case "Search in Web"
            set encoded_text (echo "$text" | jq -s -R -r @uri)
            chromium "https://www.google.com/search?q=$encoded_text"
            notify-send "brainstack" "Searching for: $text"
    end
end

function insert_entry -a text
    if test -z "$text"
        return 1
    end
    set shot_name (date +"%Y-%m-%d_%H-%M-%S.jpg")
    set date_time (date +"%m-%d %H:%M")
    test -d $shot_dir; or mkdir -p $shot_dir
    set shot_path $shot_dir/$shot_name
    scrot -z $shot_path
    add_entry $date_time $text $shot_path
end

function main
    if test "$argv[1]" = menu
        show_menu
        return
    else if test "$argv[1]" = add
        show_add
    end
end

main $argv
