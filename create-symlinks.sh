#!/usr/bin/env bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

link_item() {
    local src="$1"
    local dest="$2"
    
    if [[ -e "$dest" || -L "$dest" ]]; then
        echo "Backup: $dest -> ${dest}.bak"
        mv "$dest" "${dest}.bak"
    fi
    
    echo "Link: $src -> $dest"
    ln -s "$src" "$dest"
}

mkdir -p "$HOME/.config"

for item in .bashrc .clang-format .gdbinit .inputrc .p10k.zsh .xprofile .zsh_aliases .zshrc .tmux.conf; do
    link_item "$DOTFILES_DIR/$item" "$HOME/$item"
done

for dir in alacritty atuin clangd clash autostart dunst fish fontconfig fuzzel ghostty gtk-2.0 gtk-3.0 gtk-4.0 i3 i3status kanshi keynav kitty lazygit niri nvim nvimpager opencode openmux paru polybar rofi tmux warpd waybar wezterm wl-kbptr xdg-desktop-portal yazi zellij picom.conf screenkey.json user-dirs.dirs user-dirs.locale; do
    link_item "$DOTFILES_DIR/.config/$dir" "$HOME/.config/$dir"
done

if command -v dconf >/dev/null 2>&1; then
    echo "Load: dconf interface settings"
    dconf load /org/gnome/desktop/interface/ < "$DOTFILES_DIR/.config/dconf/interface.ini"
fi

echo "Done! Symlinks created successfully."
