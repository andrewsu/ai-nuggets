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

PIPELINE="$REPO/podcasts/PIPELINE.md"
if [ ! -f "$PIPELINE" ]; then
  echo "ERROR: $PIPELINE not found" >&2
  exit 1
fi

for prompt in podcasts/*/PROMPT.md; do
  [ -f "$prompt" ] || continue
  slug=$(basename "$(dirname "$prompt")")
  log="$REPO/podcasts/$slug/logs/cron.log"
  mkdir -p "$(dirname "$log")"
  {
    echo "=== $(date -Iseconds) start $slug ==="
    cat "$PIPELINE" "$prompt" | "$CLAUDE" -p --permission-mode auto
    echo "=== $(date -Iseconds) done  $slug (exit $?) ==="
  } >> "$log" 2>&1
done

# Claude's per-episode commit happens mid-run, before the closing "done"
# line is written above. Pick up any straggling log changes as a follow-up
# commit so they don't accumulate untracked between cron runs.
if ! git diff --quiet -- 'podcasts/*/logs/cron.log'; then
  git add 'podcasts/*/logs/cron.log' \
    && git commit -m 'Update cron logs' \
    && git push
fi
