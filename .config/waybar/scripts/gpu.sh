#!/usr/bin/env bash
# waybar custom/gpu — streams one JSON line per nvidia-smi sample (every 2s).
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,name \
    --format=csv,noheader,nounits -l 2 |
while IFS=', ' read -r util used total temp power name; do
    if (( util >= 90 )); then class=critical
    elif (( util >= 70 )); then class=warning
    else class=normal
    fi
    printf '{"text":"󰢮 %3d%%","tooltip":"%s\\n%s / %s MiB · %s°C · %s W","class":"%s","percentage":%d}\n' \
        "$util" "$name" "$used" "$total" "$temp" "$power" "$class" "$util"
done
