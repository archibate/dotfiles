#!/bin/bash

# 获取文件锁，防止并发执行
exec 9>/tmp/volume_brightness.lock
flock -n 9 || exit 1

# See https://github.com/Nmoleo64/i3-volume-brightness-indicator/blob/main/README.md for usage instructions
volume_step=1
brightness_step=5
max_volume=100
notification_timeout=3000
download_album_art=true
show_album_art=true
show_music_in_volume_indicator=true

# Brightness control requires xbacklight

# Uses regex to get volume from pactl
function get_volume {
    pactl get-sink-volume @DEFAULT_SINK@ | grep -Po '[0-9]{1,3}(?=%)' | head -1
}

# Uses regex to get mute status from pactl
function get_mute {
    pactl get-sink-mute @DEFAULT_SINK@ | grep -Po '(?<=Mute: )(yes|no)'
}

# Uses regex to get brightness from xbacklight
function get_brightness {
    if ! command -v xbacklight &> /dev/null; then
        echo "0"
        return
    fi
    
    local raw brightness
    raw=$(xbacklight -get 2>/dev/null)
    
    # Extract integer percentage
    if [[ -n "$raw" ]]; then
        brightness=$(echo "$raw" | grep -Po '[0-9]{1,3}' | head -n 1)
        if [[ -n "$brightness" ]]; then
            echo "$brightness"
            return
        fi
    fi
    
    echo "0"
}

function urldecode {
    if command -v python3 &> /dev/null; then
        python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.argv[1]))" "$1"
    else
        echo "$1"
    fi
}

# Returns a mute icon, a volume-low icon, or a volume-high icon, depending on the volume
function get_volume_icon {
    volume=$(get_volume)
    mute=$(get_mute)
    if [ "$volume" -eq 0 ] || [ "$mute" == "yes" ] ; then
        volume_icon="audio-volume-muted-symbolic"
    elif [ "$volume" -lt 50 ]; then
        volume_icon="audio-volume-low-symbolic"
    else
        volume_icon="audio-volume-high-symbolic"
    fi
}

# Always returns the same icon - I couldn't get the brightness-low icon to work with fontawesome
function get_brightness_icon {
    brightness_icon="display-brightness-symbolic"
}

function get_album_art {
    if ! command -v playerctl &> /dev/null; then
        album_art=""
        return
    fi
    
    url=$(playerctl -f "{{mpris:artUrl}}" metadata 2>/dev/null || true)
    if [[ $url == "file://"* ]]; then
        album_art=$(urldecode "${url/file:\/\//}")
    elif [[ $url == "http://"* ]] && [[ $download_album_art == "true" ]]; then
        # Identify filename from URL
        filename="$(echo $url | sed "s/.*\///")"

        # Download file to /tmp if it doesn't exist
        if [ ! -f "/tmp/$filename" ]; then
            wget -O "/tmp/$filename" "$url"
        fi

        album_art="/tmp/$filename"
    elif [[ $url == "https://"* ]] && [[ $download_album_art == "true" ]]; then
        # Identify filename from URL
        filename="$(echo $url | sed "s/.*\///")"
        
        # Download file to /tmp if it doesn't exist
        if [ ! -f "/tmp/$filename" ]; then
            wget -O "/tmp/$filename" "$url"
        fi

        album_art="/tmp/$filename"
    else
        album_art=""
    fi
}

# Displays a volume notification
function show_volume_notif {
    volume=$(get_volume)
    get_volume_icon

    if [[ $show_music_in_volume_indicator == "true" ]]; then
        current_song=$(playerctl -f "{{title}} - {{artist}}" metadata 2>/dev/null || true)

        if [[ $show_album_art == "true" ]]; then
            get_album_art
        fi

        # Use album art if available, otherwise use volume icon
        local icon_to_use="$volume_icon"
        if [[ -n "$album_art" && -f "$album_art" ]]; then
            icon_to_use="$album_art"
        fi

        if [[ -n "$current_song" ]]; then
            dunstify -a "Volume" -r 234560 -t $notification_timeout -h string:x-dunst-stack-tag:volume_notif -h int:value:$volume -i "$icon_to_use" "$volume%" "$current_song"
        else
            dunstify -a "Volume" -r 234560 -t $notification_timeout -h string:x-dunst-stack-tag:volume_notif -h int:value:$volume -i "$volume_icon" "$volume%"
        fi
    else
        dunstify -a "Volume" -r 234560 -t $notification_timeout -h string:x-dunst-stack-tag:volume_notif -h int:value:$volume -i "$volume_icon" "$volume%"
    fi
}

# Displays a music notification
function show_music_notif {
    song_title=$(playerctl -f "{{title}}" metadata)
    song_artist=$(playerctl -f "{{artist}}" metadata)
    song_album=$(playerctl -f "{{album}}" metadata)

    if [[ $show_album_art == "true" ]]; then
        get_album_art
    fi

    dunstify -a "Music" -r 234560 -t $notification_timeout -h string:x-dunst-stack-tag:music_notif -i "$album_art" "$song_title" "$song_artist - $song_album"
}

# Displays a brightness notification using dunstify
function show_brightness_notif {
    brightness=$(get_brightness)
    echo $brightness
    get_brightness_icon
    dunstify -a "Brightness" -r 234560 -t $notification_timeout -h string:x-dunst-stack-tag:brightness_notif -h int:value:$brightness -i "$brightness_icon" "$brightness%"
}

# Main function - Takes user input, "volume_up", "volume_down", "brightness_up", or "brightness_down"
case $1 in
    volume_up)
    # Unmutes and increases volume, then displays the notification
    pactl set-sink-mute @DEFAULT_SINK@ 0
    volume=$(get_volume)
    if [ $(( "$volume" + "$volume_step" )) -gt $max_volume ]; then
        pactl set-sink-volume @DEFAULT_SINK@ $max_volume%
    else
        pactl set-sink-volume @DEFAULT_SINK@ +$volume_step%
    fi
    show_volume_notif
    ;;

    volume_down)
    # Raises volume and displays the notification
    pactl set-sink-volume @DEFAULT_SINK@ -$volume_step%
    show_volume_notif
    ;;

    volume_mute)
    # Toggles mute and displays the notification
    pactl set-sink-mute @DEFAULT_SINK@ toggle
    show_volume_notif
    ;;

    brightness_up)
    # Increases brightness and displays the notification
    if ! command -v xbacklight &> /dev/null; then
        dunstify -a "Brightness" -r 234560 -t $notification_timeout "Error" "xbacklight not found"
        exit 1
    fi
    
    xbacklight -inc $brightness_step
    show_brightness_notif
    ;;

    brightness_down)
    # Decreases brightness and displays the notification
    if ! command -v xbacklight &> /dev/null; then
        dunstify -a "Brightness" -r 234560 -t $notification_timeout "Error" "xbacklight not found"
        exit 1
    fi
    
    xbacklight -dec $brightness_step
    show_brightness_notif
    ;;

    next_track)
    # Skips to the next song and displays the notification
    if ! command -v playerctl &> /dev/null; then
        dunstify -a "Music" -r 234560 -t $notification_timeout "Error" "playerctl not found"
        exit 1
    fi
    playerctl next
    sleep 0.5 && show_music_notif
    ;;

    prev_track)
    # Skips to the previous song and displays the notification
    if ! command -v playerctl &> /dev/null; then
        dunstify -a "Music" -r 234560 -t $notification_timeout "Error" "playerctl not found"
        exit 1
    fi
    playerctl previous
    sleep 0.5 && show_music_notif
    ;;

    play_pause)
    if ! command -v playerctl &> /dev/null; then
        dunstify -a "Music" -r 234560 -t $notification_timeout "Error" "playerctl not found"
        exit 1
    fi
    playerctl play-pause
    show_music_notif
    # Pauses/resumes playback and displays the notification
    ;;
esac
