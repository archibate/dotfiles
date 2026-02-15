export PATH="$PATH:$HOME/.local/bin"
[[ -f ~/.bashenv ]] && source ~/.bashenv
[[ $- == *i* ]] || return

export LANG=C.UTF-8

alias grep='grep --color=auto'
alias ls='ls --color=auto'
alias la='ls -la'
alias l='ls -lt'
alias s='ls'
alias gs='git status'
alias ga='git add --all'
alias gad='git add'
alias gc='git commit -m'
alias gco='git checkout'
alias gcm='git commit'
alias gca='git commit --amend'
alias gq='git pull'
alias gk='git reset'
alias gkh='git reset --hard'
alias gkha='git reset --hard HEAD^'
alias gp='git push'
alias gg='git switch'
alias ggo='git switch -c'
alias grs='git restore --staged'
alias grc='git rm --cached'
alias gr='git restore'
alias gd='git diff'
alias gdc='git diff --cached'
alias gda='git diff HEAD^'
alias gm='git merge'
alias gl='git log'
alias gll='git log --graph --oneline --decorate'
alias gt='git stash'
alias gtp='git stash pop'
alias gcl='git clone'
alias gcl1='git clone --depth=1'
alias gsmu='git submodule update --init --recursive'
alias g='git'
alias p='python'
alias b='nvim'
alias sup='sudo pacman'

if [[ -f /usr/share/git/completion/git-prompt.sh ]]; then
    source /usr/share/git/completion/git-prompt.sh
else
    __git_ps1() {
        true
    }
fi

__exit_status() {
    local x="$?"
    if [[ "x$x" != "x0" ]]; then
        printf "$1" "$x"
    fi
}
__afb1="$(tput bold)$(tput setaf 1)"
__afb4="$(tput bold)$(tput setaf 4)"
__af7="$(tput setaf 7)"
__cuf999="$(tput cuf 999)"
__cub999="$(tput cub 999)"
__cub1="$(tput cub 1)"
__af6="$(tput setaf 6)"
__af5="$(tput setaf 5)"
__af4="$(tput setaf 4)"
__af3="$(tput setaf 3)"
__af2="$(tput setaf 2)"
__af1="$(tput setaf 1)"
__rst="$(tput sgr0)"

__bash_root_pid="${BASHPID}"
__cmd_start() {
    date +%s.%N > "/dev/shm/${USER}.bashtime.${__bash_root_pid}"
}
__cmd_end() {
    file="/dev/shm/${USER}.bashtime.${__bash_root_pid}"
    if [[ -f "${file}" ]]; then
        endtime="$(date +%s.%N)"
        starttime="$(< "${file}")"
        rm "${file}"
        x="$(echo "m=$endtime-$starttime;s=2;if(m>=10)s=1;h=0.5;scale=s+1;t=1000;if(m<0)h=-0.5;a=m*t+h;scale=s;a=a/t;if(a>0.1)a;" | bc)"
        if [[ "$x" == .* ]]; then
            x="0$x"
        fi
        if [ "x$x" != "x" ]; then
            printf "$1" "$x"
        fi
    fi
}

__mem_usage() {
    echo "$[100 - $(awk '/MemFree/{print $2}' /proc/meminfo) * 100 / $(awk '/MemTotal/{print $2}' /proc/meminfo)]%"
}

export PS1='\[${__rst}\]$(__exit_status "\[${__afb1}\]%s\[${__rst}\] ")$(__cmd_end "\[${__af6}\]%ss\[${__rst}\] ")\[${__afb4}\]\W\[${__rst}\]$(__git_ps1 " \[${__af2}\](%s)\[${__rst}\]") \[${__af3}\]\$\[${__rst}\] '
export PS0='$(__cmd_start)\[${__rst}\]'

eval "$(fzf --bash)"

# export FZF_DEFAULT_COMMAND='fd --type f --strip-cwd-prefix'
# export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_DEFAULT_OPTS='--bind "tab:down" --bind "btab:up" --cycle --reverse --walker=file,dir,follow --scheme=path'
export FZF_COMPLETION_TRIGGER="**"
export FZF_COMPLETION_AUTO_COMMON_PREFIX=true
export FZF_COMPLETION_AUTO_COMMON_PREFIX_PART=true

# _fzf_compgen_path() {
#     fd "$1" --hidden --type f --strip-cwd-prefix --follow
# }
#
# _fzf_compgen_dir() {
#     fd "$1" --hidden --type d --strip-cwd-prefix --follow
# }

# _fzf_compgen_history() {
#     local output opts script
#     script='BEGIN { getc; $/ = "\n\t"; $HISTCOUNT = $ENV{last_hist} + 1 } s/^[ *]//; print $HISTCOUNT - $. . "\t$_" if !$seen{$_}++'
#     output=$(set +o pipefail; builtin fc -lnr -2147483648 | last_hist=$(HISTTIMEFORMAT='' builtin history 1) command perl -n -e "$script") || return
#     echo "${output#*$'\t'}"
# }

_fzf_comprun() {
  local command=$1
  shift
  case "$command" in
    export|unset) fzf --preview "eval 'echo \$'{}" "$@" ;;
    ssh|telnet)   fzf --preview 'ping -c3 {}' "$@" ;;
    *)            fzf --preview '([[ -f {} ]] && bat --style=changes --color=always {}) || ([[ -d {} ]] && ls --color=always -lA {})' "$@" ;;
  esac
}

# __fzf_compfile() {
#     if [[ "x$1" == "x_EmptycmD_" ]]; then
#         COMP_WORDS=()
#     else
#         _fzf_complete --reverse -- "$@" < <(_fzf_compgen_path)
#     fi
# }

# __fzf_comphist() {
#     COMP_WORDS=()
#     # if [[ "x$1" == "x_EmptycmD_" ]]; then
#         # echo ".[$COMP_WORDS]" >&2
#     # fi
#     # _fzf_complete --reverse -- "" < <(builtin history | tac | command sed '/^[[:space:]]*$/d' | command sed 's/^\s\s[0-9]\+\s\s//' | command sed '/^\s/d' | uniq)
#     # echo ".[$COMP_WORDS]" >&2
# }

complete -D -F _fzf_path_completion -o default -o bashdefault _fzf_path_completion
# complete -I -F __fzf_compcomd -o default -o bashdefault __fzf_compcomd
# complete -E -F __fzf_comphist -o default -o bashdefault __fzf_comphist

__j_cd() {
    builtin cd "$@" || return
    if [[ "$OLDPWD" != "$PWD" ]]; then
        [[ -f ~/.bash_history_cd ]] && sed -i "/^$(printf '%s\n' "$PWD" | sed -e 's/[]\/$*.^[]/\\&/g')$/d" ~/.bash_history_cd
        echo "$PWD" >> ~/.bash_history_cd
        [[ -f .bash_localrc ]] && source .bash_localrc
        [[ -f venv/bin/activate ]] && source venv/bin/activate
        true
    fi
}

__j_fzf() {
    file="/dev/shm/${USER}.fzf-${RANDOM}.${__bash_root_pid}"
    if [[ "$(tee $file | wc -l)" -le 1 ]]; then
        cat $file
    else
        fzf --reverse < $file
    fi
}

j() {
    [[ "$#" -ne 0 ]] && __j_cd "$@" 2> /dev/null && return
    if [[ -f ~/.bash_history_cd ]]; then
        local dir="$(cat ~/.bash_history_cd | grep -Gv "^$(printf '%s\n' "$PWD" | sed -e 's/[]$*.^[]/\\&/g')$" | grep -G -- "$1[^/]*$" | __j_fzf)"
        if [[ -n "$dir" ]]; then
            __j_cd "$dir"
        fi
    fi
}

cd() {
    __j_cd "$@"
}

if (( BASH_VERSINFO[0] >= 4 )); then

    __toggle_sudo() {
        if [[ -z $READLINE_LINE ]]; then
            READLINE_LINE="$(fc -ln -1 | command sed 's/^[[:space:]]\{1,\}//')"
            READLINE_POINT=${#READLINE_LINE}
            [[ "$READLINE_LINE" = 'sudo '* ]] && return
        fi
        if [[ "$READLINE_LINE" = 'sudo '* ]]; then
            READLINE_LINE="${READLINE_LINE#sudo }"
            ((READLINE_POINT -= 5))
        else
            READLINE_LINE="sudo $READLINE_LINE"
            ((READLINE_POINT += 5))
        fi
        ((READLINE_POINT < 0)) && READLINE_POINT=0
    }

    bind -m vi-insert -x '"\C-x": __toggle_sudo'

    __toggle_complete() {
        if [[ -z $READLINE_LINE ]] || [[ "$READLINE_LINE" != *" "* ]] || [[ "$READLINE_LINE" == *'$'* ]]; then
            __dismiss_complete
            return
        fi
        # if [[ -z $READLINE_LINE ]]; then
        #     READLINE_LINE="$(fc -ln -1 | command sed 's/^[[:space:]]\{1,\}//')"
        #     READLINE_POINT=${#READLINE_LINE}
        #     return
        # fi
        if [[ "$READLINE_LINE" = *"$FZF_COMPLETION_TRIGGER" ]]; then
            READLINE_LINE="${READLINE_LINE%"$FZF_COMPLETION_TRIGGER"}"
            READLINE_POINT=${#READLINE_LINE}
        elif [[ "$READLINE_LINE" = *"$FZF_COMPLETION_TRIGGER"\  ]]; then
            READLINE_LINE="${READLINE_LINE%"$FZF_COMPLETION_TRIGGER "}"
            READLINE_POINT=${#READLINE_LINE}
        else
            READLINE_LINE="$READLINE_LINE$FZF_COMPLETION_TRIGGER"
            READLINE_POINT=${#READLINE_LINE}
        fi
    }

    __dismiss_complete() {
        if [[ "$READLINE_LINE" = *\  ]]; then
            READLINE_LINE="${READLINE_LINE%\ }"
            READLINE_POINT=${#READLINE_LINE}
        fi
        if [[ "$READLINE_LINE" = *"$FZF_COMPLETION_TRIGGER" ]]; then
            READLINE_LINE="${READLINE_LINE%"$FZF_COMPLETION_TRIGGER"}"
            READLINE_POINT=${#READLINE_LINE}
        fi
    }

    bind -m vi-insert '"\e[1T": complete'
    bind -m vi-insert -x '"\e[2T": __toggle_complete'
    bind -m vi-insert '"\e[3T": redraw-current-line'
    bind -m vi-insert -x '"\e[4T": __dismiss_complete'
    bind -m vi-insert 'Tab: "\e[2T\e[1T"'
    bind -m vi-insert '"\e[0n": "\e[3T\e[4T"'

else
    # bind -m vi-insert '"\e[Z": complete'
    # bind -m vi-insert 'Tab: "'$FZF_COMPLETION_TRIGGER'\e[Z"'
    bind -m vi-insert 'Tab: complete'
    bind -m vi-insert '"\e[0n": redraw-current-line'
fi

set -o vi
bind -m vi-command '"\e": "\C-k\C-u\C-k\C-u\C-d"'
bind -m vi-command 'q: "\C-d"'
bind -m vi-command 'K: history-search-backward'
bind -m vi-command 'J: history-search-forward'
bind -m vi-command 'H: beginning-of-line'
bind -m vi-command 'L: end-of-line'
bind -m vi-command '"\C-r": vi-redo'
bind -m vi-insert '"\C-l": clear-screen'
bind -m vi-insert '"\M-[A": previous-history'
bind -m vi-insert '"\M-[B": next-history'
bind -m vi-insert '"\M-[D": backward-char'
bind -m vi-insert '"\M-[C": forward-char'
bind -m vi-insert '"\e[1;5A": history-search-backward'
bind -m vi-insert '"\e[1;5B": history-search-forward'
bind -m vi-insert '"\e[1;5D": backward-word'
bind -m vi-insert '"\e[1;5C": forward-word'
bind -m vi-insert '"\C-a": beginning-of-line'
bind -m vi-insert '"\C-e": end-of-line'
bind -m vi-insert '"\C-k": kill-line'
bind -m vi-insert '"\C-u": backward-kill-line'
# bind -m vi-insert '"\C-q": kill-word'
# bind -m vi-insert '"\C-w": backward-kill-word'
bind -m vi-insert '"\C-w": " \edBxi"'
bind -m vi-insert '"\C-p": history-search-backward'
bind -m vi-insert '"\C-n": history-search-forward'
bind -m vi-insert '"\C-b": backward-word'
bind -m vi-insert '"\C-f": forward-word'
bind 'set completion-ignore-case on'
bind 'set show-mode-in-prompt on'
bind 'set vi-ins-mode-string \1\e[6 q\2'
bind 'set vi-cmd-mode-string \1\e[2 q'"$__cuf999$__cub1$__af7:)$__rst$__cub999"'\2'
bind 'set keyseq-timeout 10'
bind 'set match-hidden-files off'
bind 'set bell-style visible'
bind 'set colored-completion-prefix on'
bind 'set show-all-if-unmodified on'

[[ -f .bash_localrc ]] && source .bash_localrc
true
