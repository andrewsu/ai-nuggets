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
# Mirror run_all_shows.sh: retry once on AUP-refusal, since the content
# classifier occasionally flags this prompt.
for attempt in 1 2; do
  tag=""
  [ "$attempt" -gt 1 ] && tag=" (retry $((attempt-1)))"
  out=$(mktemp)
  {
    echo "=== $(date -Iseconds) start $slug$tag ==="
    cat podcasts/PIPELINE.md "podcasts/$slug/PROMPT.md" | /home/asu/.local/bin/claude -p --permission-mode auto
    echo "=== $(date -Iseconds) done  $slug (exit $?)$tag ==="
  } 2>&1 | tee -a "$log" > "$out"
  if [ "$attempt" -eq 1 ] && \
     grep -q "Claude Code is unable to respond to this request, which appears to violate our Usage Policy" "$out"; then
    echo "=== $(date -Iseconds) AUP-refusal detected for $slug; retrying in 180s ===" | tee -a "$log"
    rm -f "$out"
    sleep 180
    continue
  fi
  rm -f "$out"
  break
done
if ! git diff --quiet -- 'podcasts/*/logs/cron.log'; then
  git add 'podcasts/*/logs/cron.log' \
    && git commit -m 'Update cron logs' \
    && git push
fi
