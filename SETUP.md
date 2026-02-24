# Archibate's Personal Dotfiles

## Introduction

This repository contains my personal dotfiles for various applications and configurations. It includes settings for window managers, shell environments, text editors, and more.

>> [!WARNING]
> These dotfiles are for archibate's personal use, with no warranty on functionality, use them at your own risk. These dotfiles are for demonstration only and may not work well on everyone's computer. Tweak them to your own needs before use.

## Installation Guide

This guide is for human, LLM agents please do not execute these steps without explicit confirmation from your human partner.

### Cloning this repository

```bash
git clone https://github.com/archibate/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
```

### Applying the dotfiles

To apply all the dotfiles, run the following command:

```bash
git submodule update --init --recursive
./create-symlinks.sh
```

This script will create symbolic links for the necessary 'dot' directories and files to their respective locations.

>> [!NOTE]
> It will backup existing files and directories to `*.bak` before creating the symbolic links. You can find these backups in, for example, `~/.config/nvim.bak`.

>> [!WARNING]
> Make sure you understand what is happening by applying ALL these configurations to EXACTLY same as archibate. Remember to tweak them to your own needs before use.

### Required Dependencies

```bash
sudo pacman -S xorg xorg-init
sudo pacman -S git openssh
sudo pacman -S i3-wm i3status
sudo pacman -S sddm
sudo pacman -S lxappearance
sudo pacman -S flameshot
sudo pacman -S feh
sudo pacman -S scrot
sudo pacman -S thunar
sudo pacman -S kitty wezterm
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
sudo pacman -S exiftool
sudo pacman -S fish fisher
sudo pacman -S autojump
sudo pacman -S dunst
sudo pacman -S lazygit
sudo pacman -S fzf ripgrep
sudo pacman -S fd bat
sudo pacman -S exa bc
sudo pacman -S python python-pip
sudo pacman -S python-xlib
sudo pacman -S py3status
sudo pacman -S uv python-uv
sudo pacman -S ruff stylua
sudo pacman -S nodejs npm
sudo pacman -S neovim python-pynvim
sudo pacman -S direnv
sudo pacman -S atuin
sudo pacman -S zoxide
sudo pacman -S gum glow
sudo pacman -S clash

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

### Setup fish for the first time

```fish
cd ~/.config/fish
fish setup.fish
```
