```bash

sudo pacman -S i3-wm i3status
sudo pacman -S sddm
sudo pacman -S lxappearance
sudo pacman -S flameshot
sudo pacman -S feh
sudo pacman -S scrot
sudo pacman -S thunar
sudo pacman -S kitty wezterm alacritty
sudo pacman -S adwaita-icon-theme adwaita-cursor
sudo pacman -S fcitx5 fcitx5-configtool fcitx5-rime
sudo pacman -S pipewire
sudo pacman -S mplayer vlc
sudo pacman -S mpv mpv-mpris
sudo pacman -S playerctl
sudo pacman -S picom
sudo pacman -S nerd-fonts
sudo pacman -S tmux
sudo pacman -S zellij
sudo pacman -S rofi
sudo pacman -S zenity
sudo pacman -S yazi
sudo pacman -S perl-image-exiftool
sudo pacman -S exiftool
sudo pacman -S fish fisher
sudo pacman -S autojump
sudo pacman -S dunst
sudo pacman -S lazygit tig
sudo pacman -S bat fzf ripgrep
sudo pacman -S fd bat exa
sudo pacman -S python python-pip
sudo pacman -S py3status
sudo pacman -S uv python-uv
sudo pacman -S ruff stylua
sudo pacman -S nodejs npm
sudo pacman -S neovim python-pynvim
sudo pacman -S direnv
sudo pacman -S atuin
sudo pacman -S zoxide
sudo pacman -S gum glow
paru -S i3lock-color
paru -S warpd
paru -S nitrogen
paru -S nvimpager
paru -S projectdo
paru -S oscclip
paru -S ttf-seto
paru -S rofi-themes-collection

# https://github.com/Reverier-Xu/Ori-fcitx5
paru -S fcitx5-skin-ori-git
# https://github.com/Reverier-Xu/Fluent-fcitx5
paru -S fcitx5-skin-fluentdark-git
paru -S fcitx5-skin-fluentlight-git
# then switch them in:
fcitx5-configtool

# https://wiki.archlinux.org/title/GTK#Dark_theme_variant
gsettings set org.gnome.desktop.interface color-scheme prefer-dark

# https://github.com/alacritty/alacritty-theme
# git clone https://github.com/alacritty/alacritty-theme /tmp/alacritty-theme
# mkdir -p ~/.config/alacritty/themes
# cp -r /tmp/alacritty-theme/themes/*.toml ~/.config/alacritty/themes

# other fonts: https://github.com/lxgw/kose-font/releases
```
