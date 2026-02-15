```bash

sudo pacman -S i3-wm i3status
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
sudo pacman -S python python-pip uv
sudo pacman -S nodejs npm
sudo pacman -S neovim python-pynvim
sudo pacman -S direnv
sudo pacman -S atuin
sudo pacman -S zoxide
paru -S i3lock-color
paru -S warpd
paru -S nitrogen
paru -S nvimpager
paru -S projectdo
paru -S oscclip

# https://github.com/Reverier-Xu/Ori-fcitx5
paru -S fcitx5-skin-ori-git

# https://github.com/Reverier-Xu/Fluent-fcitx5
paru -S fcitx5-skin-fluentdark-git
paru -S fcitx5-skin-fluentlight-git


# https://wiki.archlinux.org/title/GTK#Dark_theme_variant
gsettings set org.gnome.desktop.interface color-scheme prefer-dark

# https://github.com/newmanls/rofi-themes-collection
git clone https://github.com/lr-tech/rofi-themes-collection.git /tmp/rofi-themes-collection
mkdir -p ~/.local/share/rofi/themes/
cp /tmp/rofi-themes-collection/themes/*.rasi ~/.local/share/rofi/themes/
cp -r /tmp/rofi-themes-collection/themes/templates ~/.local/share/rofi/themes/

# https://github.com/alacritty/alacritty-theme
# git clone https://github.com/alacritty/alacritty-theme /tmp/alacritty-theme
# mkdir -p ~/.config/alacritty/themes
# cp -r /tmp/alacritty-theme/themes/*.toml ~/.config/alacritty/themes

# fonts: https://github.com/lxgw/kose-font/releases
```
