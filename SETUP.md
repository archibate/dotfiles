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
sudo pacman -S --needed base-devel
sudo pacman -S xorg xorg-init
sudo pacman -S git openssh
sudo pacman -S bc jq
sudo pacman -S netcat lsof
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
sudo pacman -S dex
sudo pacman -S dunst
sudo pacman -S lazygit
sudo pacman -S fzf ripgrep
sudo pacman -S fd bat
sudo pacman -S exa
sudo pacman -S python python-pip
sudo pacman -S python-xlib python-requests
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
sudo pacman -S cargo
sudo pacman -S chromium
sudo pacman -S noto-fonts noto-fonts-cjk noto-fonts-extra noto-fonts-emoji
sudo pacman -S ncdu
sudo pacman -S pkgconf

git clone https://aur.archlinux.org/paru.git ~/paru
cd ~/paru
makepkg -si

paru -S catppuccin-gtk-theme-frappe catppuccin-gtk-theme-latte catppuccin-gtk-theme-mocha catppuccin-gtk-theme-macchiato
# then switch to catppuccin-macchiato-blue-standard+default in:
lxappearance

paru -S warpd
paru -S nvimpager
paru -S projectdo
paru -S nitrogen
paru -S ttf-seto
# paru -S oscclip
# paru -S rofi-themes-collection

paru -S fcitx5-skin-ori-git
paru -S fcitx5-skin-fluentdark-git fcitx5-skin-fluentlight-git
# then switch to OriDark in:
fcitx5-configtool

# https://wiki.archlinux.org/title/GTK#Dark_theme_variant
gsettings set org.gnome.desktop.interface color-scheme prefer-dark
```

### Setup fish for the first time

```fish
cd ~/.config/fish
fish setup.fish
```
