#!/bin/bash
# Three-phase nightly pipeline.
#
# Phase 1: For every show under podcasts/<slug>/, run Claude with SKIP_TTS=1
#   (concurrent with a stagger between launches). Each Claude session writes
#   the script + an .rss-item.xml stub + a .commit-msg stub, but does NOT
#   call gen_tts.py, update feed.xml, or commit. See podcasts/PIPELINE.md
#   "SKIP_TTS mode" for the contract.
#
# Phase 2: rsync the new scripts to Garibaldi and submit a single
#   tts-batch.slurm job that brings up vLLM, synthesizes every pending
#   script in parallel, and tears the server back down. Outer timeout 60
#   min — if Garibaldi can't deliver in that window, abort and let Phase
#   2.5 (Mistral fallback inside publish_pending.py) carry the night.
#
# Phase 3: publish_pending.py runs the Mistral gap-fill (Phase 2.5), then
#   per show: render the RSS-item stub with real mp3 length/duration,
#   insert into feed.xml, upload mp3 to R2, git commit, delete stubs.
#   Single git push at the end.
#
# Override knobs:
#   STAGGER_SECONDS=N      seconds between successive Phase-1 launches
#   SHOWS_LIMIT=N          only run the first N shows alphabetically (0 =
#                          all). Useful for narrower manual test runs.
#   LEGACY_TTS=1           bypass new architecture: each show does TTS +
#                          publish + commit inline as before, single push
#                          at the end
#   PHASE2_TIMEOUT_SECS=N  outer cap on `ssh garibaldi sbatch --wait`
#                          (default 3600 = 60 min)
#
# Add a new show by creating podcasts/<slug>/PROMPT.md — no edit here
# needed.

set -u

REPO=/home/asu/Science/ai-nuggets
CLAUDE=/home/asu/.local/bin/claude
STAGGER_SECONDS=${STAGGER_SECONDS:-600}
SHOWS_LIMIT=${SHOWS_LIMIT:-0}
PHASE2_TIMEOUT_SECS=${PHASE2_TIMEOUT_SECS:-3600}
LEGACY_TTS=${LEGACY_TTS:-0}

GARIBALDI_HOST=garibaldi.scripps.edu
GARIBALDI_STAGE_DIR=ai-nuggets-stage   # relative to remote $HOME

# Cron's PATH is /usr/bin:/bin only. publish_episode.sh calls `npx wrangler`
# which lives under nvm. Prepend the current node bin so child processes
# (publish_pending.py → publish_episode.sh) see npx. Update on node upgrade.
export PATH="$HOME/.nvm/versions/node/v24.14.0/bin:$HOME/.local/bin:$PATH"

# Capture all output to a per-run log when not running interactively (e.g.
# under cron). The 1AM cron previously dropped Phase 2/3 logs entirely,
# which made debugging the npx-not-found failure impossible.
if [ ! -t 1 ]; then
  mkdir -p "$REPO/logs"
  RUN_LOG="$REPO/logs/run_all_shows-$(date +%Y%m%dT%H%M%S).log"
  exec >> "$RUN_LOG" 2>&1
  echo "=== $(date -Iseconds) run_all_shows.sh start (log: $RUN_LOG) ==="
fi

cd "$REPO" || exit 1

PIPELINE="$REPO/podcasts/PIPELINE.md"
if [ ! -f "$PIPELINE" ]; then
  echo "ERROR: $PIPELINE not found" >&2
  exit 1
fi

git pull origin main || echo "WARN: git pull origin main failed; continuing" >&2

# Pre-fetch arXiv listing once for the whole run so multiple shows don't
# burst the same IP and trip a tarpit. The category union covers every
# show's needs (cs.AI, cs.CL, cs.MA, q-bio supercategory). Each show's
# PROMPT.md tells Claude to read from this cache instead of curling arXiv.
ARXIV_CACHE=/tmp/ai-nuggets-arxiv-cache.xml
if [ -z "$(find "$ARXIV_CACHE" -newermt "$(date +%F)" 2>/dev/null)" ]; then
  rm -f "$ARXIV_CACHE"
  curl -s --max-time 90 \
    -A 'ai-nuggets/1.0 (https://github.com/andrewsu/ai-nuggets)' \
    'https://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.CL+OR+cat:cs.MA+OR+cat:q-bio&sortBy=submittedDate&sortOrder=descending&max_results=500' \
    -o "$ARXIV_CACHE.tmp" \
    && mv "$ARXIV_CACHE.tmp" "$ARXIV_CACHE" \
    || rm -f "$ARXIV_CACHE.tmp"
fi

# AUP-retry / model-ladder wrapper. Returns when:
#  - Claude exits 0 AND an mp3 was produced (legacy mode) OR a script
#    stub set was produced (SKIP_TTS mode); or
#  - all retries are exhausted (logs "FAILED: ...").
run_show() {
  local prompt="$1"
  local slug="$2"
  local log="$REPO/podcasts/$slug/logs/cron.log"
  mkdir -p "$(dirname "$log")"

  local attempt tag out model_arg today produced script base
  today=$(date +%F)
  for attempt in 1 2 3 4 5 6; do
    case "$attempt" in
      1|2) model_arg="" ;;
      3|4) model_arg="--model claude-sonnet-4-6" ;;
      5|6) model_arg="--model claude-haiku-4-5-20251001" ;;
    esac
    tag=""
    [ "$attempt" -gt 1 ] && tag=" (retry $((attempt-1))${model_arg:+, $model_arg})"
    out=$(mktemp)
    {
      echo "=== $(date -Iseconds) start $slug$tag ==="
      printf 'You are producing today'\''s episode of a daily podcast for slug %s. Please read the production guide at podcasts/PIPELINE.md and the show'\''s editorial brief at %s, then follow the instructions in those files to publish today'\''s episode.\n' "$slug" "$prompt" \
        | "$CLAUDE" -p --permission-mode auto $model_arg
      echo "=== $(date -Iseconds) done  $slug (exit $?)$tag ==="
    } 2>&1 | tee -a "$log" > "$out"
    if [ "$attempt" -lt 6 ] && \
       grep -q "Claude Code is unable to respond to this request, which appears to violate our Usage Policy" "$out"; then
      echo "=== $(date -Iseconds) AUP-refusal detected for $slug; retrying in 180s ===" | tee -a "$log"
      rm -f "$out"
      sleep 180
      continue
    fi
    # "Did the show actually produce something useful?" check. In SKIP_TTS
    # mode that means a script file *and* both stubs; in legacy mode it
    # means an mp3.
    produced=""
    if [ "$LEGACY_TTS" = "1" ]; then
      produced=$(compgen -G "$REPO/podcasts/$slug/episodes/$today*.mp3" 2>/dev/null | head -1 || true)
    else
      # Look for any today's script whose .rss-item.xml + .commit-msg stubs
      # both exist. Iterate over .md and .txt separately — `compgen -G` only
      # honors the *last* -G when multiple are passed.
      shopt -s nullglob
      for script in "$REPO/podcasts/$slug/scripts/$today"*.md "$REPO/podcasts/$slug/scripts/$today"*.txt; do
        base="${script%.*}"
        if [ -f "${base}.rss-item.xml" ] && [ -f "${base}.commit-msg" ]; then
          produced="$script"
          break
        fi
      done
      shopt -u nullglob
    fi
    if [ "$attempt" -lt 6 ] && [ -z "$produced" ]; then
      echo "=== $(date -Iseconds) no usable output for $slug; retrying in 180s ===" | tee -a "$log"
      rm -f "$out"
      sleep 180
      continue
    fi
    if [ -z "$produced" ]; then
      echo "=== $(date -Iseconds) FAILED: no usable output for $slug after all retries ===" | tee -a "$log"
    fi
    rm -f "$out"
    break
  done
}

##############################################################################
# Phase 1: write scripts (and stubs if !LEGACY_TTS) — parallel across shows.
##############################################################################
if [ "$LEGACY_TTS" = "1" ]; then
  echo "$(date -Iseconds) Phase 1: legacy end-to-end mode (each show does TTS + commit inline)"
else
  echo "$(date -Iseconds) Phase 1: script-only mode (SKIP_TTS=1)"
  export SKIP_TTS=1
fi

first=1
count=0
for prompt in podcasts/*/PROMPT.md; do
  [ -f "$prompt" ] || continue
  if [ "$SHOWS_LIMIT" -gt 0 ] && [ "$count" -ge "$SHOWS_LIMIT" ]; then
    break
  fi
  count=$((count + 1))
  slug=$(basename "$(dirname "$prompt")")
  if [ "$first" -eq 0 ]; then
    sleep "$STAGGER_SECONDS"
  fi
  first=0
  run_show "$prompt" "$slug" &
done
wait

##############################################################################
# Phase 2 + 3 (skipped in LEGACY_TTS mode — each show already committed).
##############################################################################
if [ "$LEGACY_TTS" = "1" ]; then
  if ! git diff --quiet -- 'podcasts/*/logs/cron.log'; then
    git add 'podcasts/*/logs/cron.log' && git commit -m 'Update cron logs'
  fi
  git push
  exit 0
fi

echo "$(date -Iseconds) Phase 2: batch TTS on Garibaldi"
TODAY=$(date +%F)

# rsync today's scripts (and stubs) up. Exclude episodes/, feed.xml, logs,
# and .git — Phase 2 only needs the inputs.
rsync -a --delete \
  --exclude='.git' \
  --exclude='/.venv/' \
  --exclude='node_modules' \
  --exclude='podcasts/*/episodes' \
  --exclude='podcasts/*/logs' \
  --exclude='podcasts/*/feed.xml' \
  --exclude='podcasts/*/audio' \
  "$REPO/" "$GARIBALDI_HOST:$GARIBALDI_STAGE_DIR/"
echo "$(date -Iseconds) rsync up complete"

# Submit + wait with an outer timeout. `timeout` will SIGTERM the local ssh
# if exceeded — but the remote sbatch job keeps running, so we explicitly
# scancel below.
set +e
timeout "$PHASE2_TIMEOUT_SECS" \
  ssh "$GARIBALDI_HOST" \
    "cd $GARIBALDI_STAGE_DIR && sbatch --wait --export=ALL,TTS_BATCH_DATE=$TODAY hpc/tts-batch.slurm"
PHASE2_RC=$?
set -e
echo "$(date -Iseconds) Phase 2 ssh exited rc=$PHASE2_RC"

# If we timed out, kill any leftover tts-batch jobs we own.
if [ "$PHASE2_RC" -eq 124 ]; then
  echo "$(date -Iseconds) Phase 2 hit outer timeout; scancelling any leftover tts-batch jobs"
  ssh "$GARIBALDI_HOST" \
    "squeue -u \$USER -h -o '%i %j' | awk '\$2 == \"tts-batch\" {print \$1}' | xargs -r scancel" \
    || true
fi

# Pull whatever MP3s exist back, regardless of Phase 2 exit code. Partial
# success is still useful — publish_pending.py will gap-fill the rest.
rsync -av \
  --include='podcasts/' --include='podcasts/*/' \
  --include='podcasts/*/episodes/' --include='podcasts/*/episodes/*.mp3' \
  --exclude='*' \
  "$GARIBALDI_HOST:$GARIBALDI_STAGE_DIR/" "$REPO/"
echo "$(date -Iseconds) rsync down complete"

echo "$(date -Iseconds) Phase 3: publish_pending.py"
python3 "$REPO/scripts/publish_pending.py" --date "$TODAY"
PHASE3_RC=$?

# Catch any straggling log changes (cron.log tee'd after Claude exited).
if ! git diff --quiet -- 'podcasts/*/logs/cron.log'; then
  git add 'podcasts/*/logs/cron.log' && git commit -m 'Update cron logs' || true
  git push || true
fi

echo "$(date -Iseconds) run_all_shows.sh done (phase3 rc=$PHASE3_RC)"
exit $PHASE3_RC
