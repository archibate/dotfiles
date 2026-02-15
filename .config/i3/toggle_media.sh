#!/bin/bash

log_file="$HOME/.cache/mpv_toggle.log"
echo "$(date): toggle_media.sh started" >> "$log_file"

if pgrep -x vlc > /dev/null; then
    echo "vlc is running, killing it" >> "$log_file"
    pkill -x vlc
else
    echo "vlc is not running, starting it" >> "$log_file"
    vlc -I dummy "$HOME/音乐" --random --loop >> "$log_file" 2>&1 &
    echo "vlc started with PID $!" >> "$log_file"
fi
