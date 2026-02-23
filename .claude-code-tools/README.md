# Claude Code OpenRouter Statusline

Tracks your OpenRouter API costs in the Claude Code statusline.

## Setup

1. Make the script executable:
   ```bash
   chmod +x statusline.sh
   ```

2. Add to `~/.claude/settings.json`:
   ```json
   {
     "statusLine": {
       "type": "command",
       "command": "/path/to/statusline.sh"
     }
   }
   ```

The script uses your existing `ANTHROPIC_AUTH_TOKEN` or `ANTHROPIC_API_KEY` from Claude Code's config.
