sudo cp clash.service /etc/systemd/system/clash.service
sudo systemctl daemon-reload
sudo systemctl enable clash --now
