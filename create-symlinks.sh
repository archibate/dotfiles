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

for item in .bashrc .clang-format .gdbinit .gitconfig .inputrc .p10k.zsh .xprofile .zsh_aliases .zshrc .tmux.conf; do
    link_item "$DOTFILES_DIR/$item" "$HOME/$item"
done

for dir in alacritty atuin clangd dunst fish gtk-2.0 gtk-3.0 i3 i3status keynav kitty lazygit nvim nvimpager openmux polybar rofi tmux warpd wezterm yazi zellij picom.conf screenkey.json; do
    link_item "$DOTFILES_DIR/.config/$dir" "$HOME/.config/$dir"
done

echo "Done! Symlinks created successfully."
