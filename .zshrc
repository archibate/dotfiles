[[ $- == *i* ]] || return

P10K=1

if [[ "x$P10K" != "x" ]] && [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Znap packages manager
[[ -r ~/Codes/repos/znap/znap.zsh ]] ||
    git clone --depth 1 -- \
        https://github.com/marlonrichert/zsh-snap.git ~/Codes/repos/znap
source ~/Codes/repos/znap/znap.zsh  # Start Znap

# Path to your oh-my-zsh installation.
# export ZSH="/home/bate/.oh-my-zsh"

# Set name of the theme to load --- if set to "random", it will
# load a random theme each time oh-my-zsh is loaded, in which case,
# to know which specific one was loaded, run: echo $RANDOM_THEME
# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

# Set list of themes to pick from when loading at random
# Setting this variable when ZSH_THEME=random will cause zsh to load
# a theme from this variable instead of looking in $ZSH/themes/
# If set to an empty array, this variable will have no effect.
# ZSH_THEME_RANDOM_CANDIDATES=( "robbyrussell" "agnoster" )

# Uncomment the following line to use case-sensitive completion.
# CASE_SENSITIVE="true"

# Uncomment the following line to use hyphen-insensitive completion.
# Case-sensitive completion must be off. _ and - will be interchangeable.
# HYPHEN_INSENSITIVE="true"

# Uncomment one of the following lines to change the auto-update behavior
# zstyle ':omz:update' mode disabled  # disable automatic updates
# zstyle ':omz:update' mode auto      # update automatically without asking
# zstyle ':omz:update' mode reminder  # just remind me to update when it's time

# Uncomment the following line to change how often to auto-update (in days).
# zstyle ':omz:update' frequency 13

# Uncomment the following line if pasting URLs and other text is messed up.
# DISABLE_MAGIC_FUNCTIONS="true"

# Uncomment the following line to disable colors in ls.
# DISABLE_LS_COLORS="true"

# Uncomment the following line to disable auto-setting terminal title.
# DISABLE_AUTO_TITLE="true"

# Uncomment the following line to enable command auto-correction.
# ENABLE_CORRECTION="true"

# Uncomment the following line to display red dots whilst waiting for completion.
# You can also set it to another string to have that shown instead of the default red dots.
# e.g. COMPLETION_WAITING_DOTS="%F{yellow}waiting...%f"
# Caution: this setting can cause issues with multiline prompts in zsh < 5.7.1 (see #5765)
# COMPLETION_WAITING_DOTS="true"

# Uncomment the following line if you want to disable marking untracked files
# under VCS as dirty. This makes repository status check for large repositories
# much, much faster.
# DISABLE_UNTRACKED_FILES_DIRTY="true"

# Uncomment the following line if you want to change the command execution time
# stamp shown in the history command output.
# You can set one of the optional three formats:
# "mm/dd/yyyy"|"dd.mm.yyyy"|"yyyy-mm-dd"
# or set a custom format using the strftime function format specifications,
# see 'man strftime' for details.
# HIST_STAMPS="mm/dd/yyyy"

# Would you like to use another custom folder than $ZSH/custom?
# ZSH_CUSTOM=/path/to/new-custom-folder

# FUCK UPDATE!
DISABLE_AUTO_UPDATE="true"

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
# Example format: plugins=(rails git textmate ruby lighthouse)
# Add wisely, as too many plugins slow down shell startup.
plugins=(
	sudo
	# git
	# autojump
	# zsh-syntax-highlighting
	# zsh-autosuggestions
    # fzf-zsh-plugin
    # fzf-tab
    fzf
    copypath
    archlinux
    # ripgrep
    # zsh-navigation-tools
    direnv
 direnv)

znap source zsh-users/zsh-syntax-highlighting
znap source zsh-users/zsh-autosuggestions
znap source zsh-users/zsh-history-substring-search
# znap source zdharma-continuum/history-search-multi-word
# znap source marlonrichert/zsh-autocomplete
if [[ "x$P10K" != "x" ]]; then
    znap source romkatv/powerlevel10k
fi

znap source ohmyzsh/ohmyzsh

# User configuration

# export MANPATH="/usr/local/man:$MANPATH"

# You may need to manually set your language environment
# export LANG=en_US.UTF-8

# Preferred editor for local and remote sessions
# if [[ -n $SSH_CONNECTION ]]; then
#   export EDITOR='vim'
# else
#   export EDITOR='nvim'
# fi

# Compilation flags
# export ARCHFLAGS="-arch x86_64"

if [[ ! -o interactive ]]; then
    return
fi

export FZF_COMPLETION_TRIGGER='**'
export FZF_DEFAULT_COMMAND='fd --type f'

# Set personal aliases, overriding those provided by oh-my-zsh libs,
# plugins, and themes. Aliases can be placed here, though oh-my-zsh
# users are encouraged to define aliases within the ZSH_CUSTOM folder.
# For a full list of active aliases, run `alias`.
#
# Example aliases
alias zshconfig="mate ~/.zshrc"
alias ohmyzsh="mate ~/.oh-my-zsh"

# bindkey '^I' menu-select
# bindkey "$terminfo[kcbt]" menu-select
# bindkey -M menuselect '^I' menu-complete
# bindkey -M menuselect "$terminfo[kcbt]" reverse-menu-complete
# bindkey "$terminfo[kcuu1]" up-line-or-history
# bindkey "$terminfo[kcud1]" down-line-or-history

[[ -s /etc/profile.d/autojump.sh ]] && source /etc/profile.d/autojump.sh
[[ -f ~/.zsh_aliases ]] && . ~/.zsh_aliases

if [[ -n $P10K ]]; then
    [[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh
fi

bloop() {
    export LOOPCOMMAND=1
    while ! nvim $@; do; done;
    unset LOOPCOMMAND
    export LOOPCOMMAND
}

clangdpioesp() {
> .clangd << EOF
CompileFlags:
  Remove:
    - -mlongcalls
    - -fno-shrink-wrap
    - -fno-tree-switch-conversion
    - -fstrict-volatile-bitfields
    - -mfix-esp32-psram-cache-issue
    - -fipa-pta
    - -free
    - -mtext-section-literals
  Add:
    - -fgnuc-version=12.3.1
EOF
    fw=framework-arduinoespressif32
    if grep framework-arduinoespressif8266 compile_commands.json > /dev/null; then
        fw=framework-arduinoespressif8266
    fi
    for x in $(ls -d ~/.platformio/packages/$fw/libraries/*/); do
        if [ -d ${x}src ]; then
            echo "    - -isystem${x}src" >> .clangd
        else
            echo "    - -isystem${x}" >> .clangd
        fi
    done
    if grep xtensa- compile_commands.json > /dev/null; then
>> .clangd << EOF
    - -D__XTENSA__=1
    - -D__machine_ssize_t_defined=1
    - -D_ssize_t=int
EOF
    fi
}

happypio() {
    pio project init --board ${1-nanoatmega328}
    > src/main.cpp << EOF
#include <Arduino.h>

void setup() {
    Serial.begin(115200);
}

void loop() {
}
EOF
    > compiledb_flags.py << EOF
Import("env")

env.Replace(COMPILATIONDB_INCLUDE_TOOLCHAIN=True)
EOF
    >> .gitignore << EOF
.cache/
src/secrets.h
EOF
    >> platformio.ini << EOF
extra_scripts = pre:compiledb_flags.py
build_unflags =
    -std=gnu++11
build_flags =
    -std=gnu++17
monitor_speed = 115200
lib_deps =
EOF
    pio run --target compiledb
}

dbpio() {
    pio run --target compiledb
    if grep toolchain-xtensa-esp compile_commands.json > /dev/null; then
        sed -i 's/ -I\S*toolchain-riscv32-esp\S*//g' compile_commands.json
        if test -f .clangd && ! grep __XTENSA__ .clangd > /dev/null; then
            echo "    - -D__XTENSA__=1" >> .clangd
        fi
    fi
}

happyidf() {
    . ~/esp/esp-idf/export.sh
}

glibcver() {
    strings "$@" | grep '^GLIBC_[0-9]' | sort -V | tail -n1
}

[ ! -f ~/.config/tmux/scripts/tmux_aliases.sh ] || source ~/.config/tmux/scripts/tmux_aliases.sh
