#!/bin/bash
# Run the daily Claude pipeline for every show under podcasts/<slug>/.
# A "show" is any directory containing a PROMPT.md.
#
# Sequential on purpose: avoids TTS API contention and races on `git push`.
# Add a new show by creating podcasts/<slug>/PROMPT.md — no crontab edit needed.

set -u

REPO=/home/asu/Science/ai-nuggets
CLAUDE=/home/asu/.local/bin/claude

cd "$REPO" || exit 1

for prompt in podcasts/*/PROMPT.md; do
  [ -f "$prompt" ] || continue
  slug=$(basename "$(dirname "$prompt")")
  log="$REPO/podcasts/$slug/logs/cron.log"
  mkdir -p "$(dirname "$log")"
  {
    echo "=== $(date -Iseconds) start $slug ==="
    "$CLAUDE" -p --permission-mode auto < "$prompt"
    echo "=== $(date -Iseconds) done  $slug (exit $?) ==="
  } >> "$log" 2>&1
done
