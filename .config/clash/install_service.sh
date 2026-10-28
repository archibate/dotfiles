mkdir -p ~/.config/systemd/user
cp clash.service clash-healthlog.service clash-healthlog.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now clash clash-healthlog.timer
