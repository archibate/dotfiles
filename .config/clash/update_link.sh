cd $(dirname $(realpath "$0"))
test -f sublink.txt || (echo ERROR: please fill sublink.txt with your subscription link; exit)
https_proxy= http_proxy= all_proxy= curl "$(cat sublink.txt)" -o config.yaml -A clash-verge/2.0.0
sudo systemctl restart clash
