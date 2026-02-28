cp clash.service ~/.config/systemd/user/clash.service
systemctl daemon-reload
systemctl enable clash --now --user
