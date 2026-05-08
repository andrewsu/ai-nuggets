#!/bin/bash
# One-off rerun for biomedical-agentic-ai, mirroring run_all_shows.sh.
set -u
# Mirror cron's clean env: an invalid ANTHROPIC_API_KEY in the interactive
# shell shadows the valid ~/.claude/.credentials.json that cron relies on.
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN \
      CLAUDE_CODE_SESSION_ID CLAUDE_CODE_ENTRYPOINT \
      CLAUDE_CODE_EXECPATH CLAUDECODE AI_AGENT
cd /home/asu/Science/ai-nuggets || exit 1
slug=biomedical-agentic-ai
log="podcasts/$slug/logs/cron.log"
mkdir -p "$(dirname "$log")"
{
  echo "=== $(date -Iseconds) start $slug ==="
  cat podcasts/PIPELINE.md "podcasts/$slug/PROMPT.md" | /home/asu/.local/bin/claude -p --permission-mode auto
  echo "=== $(date -Iseconds) done  $slug (exit $?) ==="
} >> "$log" 2>&1
if ! git diff --quiet -- 'podcasts/*/logs/cron.log'; then
  git add 'podcasts/*/logs/cron.log' \
    && git commit -m 'Update cron logs' \
    && git push
fi
