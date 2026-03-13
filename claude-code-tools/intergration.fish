# Auto-detect script directory
function claude
    set -l CLAUDE_TOOLS_DIR (path dirname (status --filename))
    # if test -d $CLAUDE_TOOLS_DIR
    #     set -fx EDITOR $CLAUDE_TOOLS_DIR/tmux_popup_edit.py
    # end
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
    claude --model sonnet "review CLAUDE.md for any vague, ambigious, contradiction, typo, duplicate or over-emphersized sections. report your findings. update it to be compact and informative."
end

function commit
    timeout -v -s INT 80s claude -p --model haiku --max-turns 50 "Make a git commit with commit message briefly describing what changed in the codebase. Stage and commit all changed files (including untracked ones). If some stagable files looks like should appear in .gitignore, add the file name pattern to .gitignore before stage. Do not edit files in this conversation."
end
