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

#### Arch Linux Installation (if you haven't)

Assume you are in Windows. You want to setup a typical Win-Arch dual system.

Here's my tour:

- First press Win+X -> click 'Disk Manager'.
- In Disk Manager, shrink the `D:` partition, to reserve space for Linux file system installation. (skip this if you use a fresh free disk for Arch Linux installation)
- Following instructions in [Arch Linux Wiki](https://wiki.archlinux.org/title/Netboot), I downloaded [ipxe-arch.efi](https://archlinux.org/static/netboot/ipxe-arch.efi).
- Use Easy UEFI 'Power' option -> 'reboot into UEFI BIOS'. In BIOS settings, disable **Secure Boot** and **Fast Boot**. Then 'Save and Exit'.
- Booting into Windows again. Use Easy UEFI -> Create EFI record -> add previously downloaded ipxe-arch.efi. Then move this EFI entry to the top.
- Reboot now. You will boot into the net boot image now.
- After net boot success, run `archinstall` to configure installation settings.
- In order to keep Windows as-is: I use 'Manual Partition' in 'Disk Partition' configuration, create `/boot` (800 MiB) and `/` (maximum) in the free space we just reserved from the `D:` partition. (skip this if you want to completely fuck Wendous up).
- Remember to set root password and create a default user (I namely `bate`), make sure the default user is a `sudo` user.
- Press 'Install' in `archinstall` interface, wait for complete.
- Reboot if installation complete, you will be in a grub loader, wait 5 seconds to boot into default - now a bare Arch Linux is installed.
- Configure sudoers by editing, e.g. `sudo -e /etc/sudoers.d/00_bate`, content should be `bate ALL=(ALL) NOPASSWD: ALL` to prevent password hinting.
- Optionally `passwd -d bate` to cancel password for `bate` user.

#### Packages from Official

Type these into your bare terminal:

```bash
sudo pacman -S --needed base-devel
sudo pacman -S xorg xorg-init
sudo pacman -S git openssh
sudo pacman -S netcat lsof
sudo pacman -S i3-wm i3status
sudo pacman -S sddm
sudo pacman -S lxappearance
sudo pacman -S flameshot
sudo pacman -S feh
sudo pacman -S scrot
sudo pacman -S thunar
sudo pacman -S kitty wezterm
sudo pacman -S adwaita-icon-theme adwaita-cursor breeze-icons
sudo pacman -S fcitx5 fcitx5-configtool fcitx5-rime
sudo pacman -S pipewire
sudo pacman -S mplayer vlc
sudo pacman -S mpv mpv-mpris
sudo pacman -S playerctl
sudo pacman -S picom
sudo pacman -S noto-fonts noto-fonts-cjk noto-fonts-extra noto-fonts-emoji
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
sudo pacman -S imagemagick
sudo pacman -S dunst
sudo pacman -S lazygit
sudo pacman -S fzf ripgrep
sudo pacman -S fd bat
sudo pacman -S exa sd
sudo pacman -S git-delta github-cli
sudo pacman -S ast-grep hyperfine
sudo pacman -S dust bottom
sudo pacman -S tldr just
sudo pacman -S bc jq yq
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
sudo pacman -S ncdu
sudo pacman -S pkgconf
```

#### Packages from AUR

##### Installing Paru - AUR Package Manager

```bash
git clone https://aur.archlinux.org/paru.git ~/paru
cd ~/paru
makepkg -si
```

##### Installing Packages From AUR

```bash
paru -S warpd
paru -S nvimpager
paru -S projectdo
paru -S timg
paru -S nitrogen
```

##### Installing Beautiful GTK Themes

```bash
paru -S catppuccin-gtk-theme-frappe catppuccin-gtk-theme-latte catppuccin-gtk-theme-mocha catppuccin-gtk-theme-macchiato
```
then switch to `catppuccin-macchiato-blue-standard+default` (or any one you like) in:
```bash
lxappearance
```

##### Installing Fcitx5 Input Method Themes

```bash
paru -S fcitx5-skin-ori-git
paru -S fcitx5-skin-fluentdark-git fcitx5-skin-fluentlight-git
```
then switch to OriDark in:
```bash
fcitx5-configtool
```

##### GNOME Desktop Global Dark Mode Preferences

```bash
# https://wiki.archlinux.org/title/GTK#Dark_theme_variant
gsettings set org.gnome.desktop.interface color-scheme prefer-dark
```

#### Application Setup

##### Setup nvim for the first time

Simply enter `nvim`. All declared plugins will be automatically installed and updated on the first enter of nvim (thanks to the magic of lazy.nvim).

```fish
nvim
```

##### Setup tmux for the first time

```fish
cd ~/.config/tmux
bash install.sh
tmux
```

In tmux, press `Ctrl-b` then `I` to install plugins.

##### Setup fish for the first time

```fish
cd ~/.config/fish
fish setup.fish
sudo chsh $USER -s $(which fish)
# set up your environment variables (secret API keys) in ~/.config/fish/.env
```

##### Setup WeChat

```bash
paru -S wechat-appimage
```
