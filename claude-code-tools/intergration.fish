# Auto-detect script directory
function claude
    set -l CLAUDE_TOOLS_DIR (path dirname (status --filename))
    if test -d $CLAUDE_TOOLS_DIR
        set -lx EDITOR $CLAUDE_TOOLS_DIR/tmux_split_nvim.py
    end
    $CLAUDE_TOOLS_DIR/claude_router.py $argv
end

function glm
    claude glm --model sonnet $argv
end

function haiku
    claude --model haiku $argv
end

function sonnet
    claude --model sonnet $argv
end

function opus
    claude --model opus $argv
end

function compact_claude_md
    claude glm --model sonnet "please check my CLAUDE.md, if there are any duplicate or over-emphersized sections. making it compact and informative."
end

function commit
    timeout -v -s INT 80s claude glm -p --model haiku --max-turns 50 "Make a git commit with commit message briefly describing what changed in the codebase. Stage and commit all changed files (including untracked ones). If some stagable files looks like should appear in .gitignore, add the file name pattern to .gitignore before stage. Do not edit files in this conversation."
end
