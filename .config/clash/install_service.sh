mkdir -p ~/.config/systemd/user
cp clash.service ~/.config/systemd/user/clash.service
systemctl --user daemon-reload
systemctl --user enable --now clash
