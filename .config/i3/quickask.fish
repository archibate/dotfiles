#!/usr/bin/env fish

set prompt (echo -n | rofi -dmenu -p quickask | string trim)
if test -z "$prompt"
    return 0
end
set output (ask "make a short answer on user question: $prompt" <&- | tee /tmp/answer.md)
notify-send "quickask" "$output"
