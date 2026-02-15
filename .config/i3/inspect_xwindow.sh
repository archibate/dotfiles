wmclass=$(xdotool getwindowfocus getwindowclassname)

dunstify -r 24538 -a "WM Class" "$wmclass"
