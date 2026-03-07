#!/bin/bash

# Pick a color using xcolor (outputs hex code like #RRGGBB)
color=$(xcolor)

# Exit if no color was selected (user cancelled)
[ -z "$color" ] && exit 0

# Copy hex code to clipboard using xclip
echo -n "$color" | xclip -selection clipboard

# Notify user with the selected color
dunstify -r 24539 -a "Color Picker" "Copied: $color"
