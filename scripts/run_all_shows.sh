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
#   MAX_RESET_WAIT_SECS=N  on a session-limit hit, the runner parses the
#                          reset time from the CLI's error message and
#                          sleeps until then (+60s buffer). If the reset is
#                          further than this many seconds away it falls
#                          back to the standard 180s retry sleep (default
#                          3600 = 60 min).
#   PAUSE_INACTIVE=1       consult scripts/check_activity.py before Phase 1
#                          and skip shows whose subscriber hasn't
#                          downloaded in the last N days (see PAUSE_THRESHOLD_DAYS).
#                          On the transition day, scripts/prepare_goodbye.py
#                          writes a goodbye episode + state/pause.json so
#                          Phase 2/3 publish the goodbye like any other
#                          episode. Resume is automatic when a fresh GET
#                          lands after paused_at; to force-resume manually,
#                          `rm podcasts/<slug>/state/pause.json`. Off by default.
#
# Deferred-catchup: shows that hit session-limit on every Phase-1 attempt
# get added to a DEFERRED set. After the main Phase 2/3 runs for the
# SUCCEEDED set, a backgrounded catchup subshell is spawned that:
#   1. Sleeps until the latest reset across the DEFERRED shows
#      (+CATCHUP_BUFFER_SECS).
#   2. Re-runs Phase 1 for just the deferred slugs.
#   3. Re-runs Phase 2 (rsync up, sbatch tts-batch.slurm, rsync mp3s back).
#   4. Re-runs Phase 3 (publish_pending.py — pushes the new episodes).
# The subshell is disowned so the parent cron job exits promptly. The
# subshell does NOT recursively re-defer if it also hits session-limit;
# audit catches that the next morning. Override knobs:
#   CATCHUP_BUFFER_SECS=N    seconds past the reset wallclock before the
#                            catchup wakes (default 300 = 5 min).
#   CATCHUP_MAX_WAIT_SECS=N  upper bound on catchup sleep duration. If the
#                            computed wait exceeds this, the catchup is
#                            skipped entirely (defensive; the typical
#                            session window is 5h, so 6h is the default).
#
# Add a new show by creating podcasts/<slug>/PROMPT.md — no edit here
# needed.

set -u

REPO=/home/asu/Science/ai-nuggets
CLAUDE=/home/asu/.local/bin/claude
STAGGER_SECONDS=${STAGGER_SECONDS:-600}
SHOWS_LIMIT=${SHOWS_LIMIT:-0}
PHASE2_TIMEOUT_SECS=${PHASE2_TIMEOUT_SECS:-3600}
MAX_RESET_WAIT_SECS=${MAX_RESET_WAIT_SECS:-3600}
CATCHUP_BUFFER_SECS=${CATCHUP_BUFFER_SECS:-300}
CATCHUP_MAX_WAIT_SECS=${CATCHUP_MAX_WAIT_SECS:-21600}
LEGACY_TTS=${LEGACY_TTS:-0}

GARIBALDI_HOST=garibaldi.scripps.edu
GARIBALDI_STAGE_DIR=ai-nuggets-stage   # relative to remote $HOME

# Per-show outcome from Phase 1 lands in this directory, one file per show.
# Read after `wait` to build SUCCEEDED / DEFERRED / FAILED sets. Date-stamped
# so mid-day reruns don't see stale state from prior days.
STATUS_DIR="$REPO/logs/.phase1-status-$(date +%F)"

# TODAY is the date of this run as captured at script start. Used by Phase 2
# (TTS_BATCH_DATE), Phase 3 (--date), and the deferred-catchup subshell —
# the subshell must use the original date so it doesn't accidentally produce
# tomorrow's episode if it sleeps past midnight (cron at 2am is safely
# inside one day, but capture anyway).
TODAY=$(date +%F)

# Audit-send bookkeeping. The main-path EXIT trap fires run_daily_audit.sh
# unless a catchup subshell was successfully spawned — in that case the
# subshell will fire the audit when it finishes so the email reflects
# post-catchup state. `run_daily_audit.sh` self-gates on logs/.audit-sent-*
# so the 09:00 backstop cron and any duplicate trap fires can't produce
# multiple emails. Historical bug this fixes: static 05:30 audit cron sent
# "N shows FAILED" while catchup was still asleep waiting for the 7am
# session-limit reset; the shows published cleanly ~08:00 with no follow-up.
CATCHUP_SPAWNED=0
audit_on_exit() {
  local rc=$?
  if [ "${CATCHUP_SPAWNED:-0}" -eq 0 ]; then
    AUDIT_FROM_PIPELINE=1 "$REPO/scripts/run_daily_audit.sh" >> "$REPO/logs/audit.log" 2>&1 || true
  fi
  return "$rc"
}
trap audit_on_exit EXIT

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

# Sleep until the wallclock time named in a session-limit CLI message
# (e.g. "resets 2:30am") with a 60s buffer, capped at MAX_RESET_WAIT_SECS.
# Falls back to a 180s sleep if the reset can't be parsed or is too far
# out — that mirrors the legacy behaviour so a parse miss never blocks
# the pipeline indefinitely.
sleep_until_reset() {
  local out_file="$1" log="$2"
  local reset_str target_epoch now_epoch sleep_secs
  reset_str=$(grep -oE 'session limit · resets [0-9]{1,2}(:[0-9]{2})?(am|pm)' "$out_file" \
                | head -1 | sed 's/.*resets //')
  if [ -z "$reset_str" ]; then
    echo "=== $(date -Iseconds) session-limit detected but no reset time parsed; sleeping 180s ===" | tee -a "$log"
    sleep 180; return
  fi
  target_epoch=$(date -d "$reset_str today" +%s 2>/dev/null) || target_epoch=""
  if [ -z "$target_epoch" ]; then
    echo "=== $(date -Iseconds) couldn't parse reset '$reset_str'; sleeping 180s ===" | tee -a "$log"
    sleep 180; return
  fi
  now_epoch=$(date +%s)
  if [ "$target_epoch" -le "$now_epoch" ]; then
    target_epoch=$((target_epoch + 86400))
  fi
  sleep_secs=$((target_epoch - now_epoch + 60))
  if [ "$sleep_secs" -gt "$MAX_RESET_WAIT_SECS" ]; then
    echo "=== $(date -Iseconds) session-limit reset at $reset_str is ${sleep_secs}s away (>${MAX_RESET_WAIT_SECS}s cap); sleeping 180s ===" | tee -a "$log"
    sleep 180; return
  fi
  echo "=== $(date -Iseconds) session-limit hit; sleeping ${sleep_secs}s until $reset_str (+60s buffer) ===" | tee -a "$log"
  sleep "$sleep_secs"
}

# Spawn a backgrounded catchup subshell for the DEFERRED set. Reads the
# global DEFERRED array (entries are "slug:reset-string"), computes the
# latest reset wallclock, sleeps until then plus CATCHUP_BUFFER_SECS, then
# re-runs Phase 1 → Phase 2 → Phase 3 for just those slugs. Disowned so
# the parent script exits promptly. Logs to its own file under logs/.
spawn_catchup() {
  local slugs=() entry slug reset_str epoch
  local now_epoch latest_reset_epoch=0
  now_epoch=$(date +%s)

  for entry in "${DEFERRED[@]}"; do
    slug="${entry%%:*}"
    reset_str="${entry#*:}"
    slugs+=("$slug")
    epoch=$(date -d "$reset_str today" +%s 2>/dev/null) || epoch=""
    if [ -n "$epoch" ]; then
      [ "$epoch" -le "$now_epoch" ] && epoch=$((epoch + 86400))
      [ "$epoch" -gt "$latest_reset_epoch" ] && latest_reset_epoch=$epoch
    fi
  done

  if [ "$latest_reset_epoch" -eq 0 ]; then
    echo "$(date -Iseconds) catchup: couldn't parse any reset time across DEFERRED [${slugs[*]}]; skipping"
    return
  fi

  local wait_secs=$((latest_reset_epoch - now_epoch + CATCHUP_BUFFER_SECS))
  if [ "$wait_secs" -gt "$CATCHUP_MAX_WAIT_SECS" ]; then
    echo "$(date -Iseconds) catchup: computed wait ${wait_secs}s exceeds CATCHUP_MAX_WAIT_SECS=${CATCHUP_MAX_WAIT_SECS}s; skipping (audit will surface the failure)"
    return
  fi

  local catchup_log="$REPO/logs/catchup-$(date +%Y%m%dT%H%M%S).log"
  local target_iso
  target_iso=$(date -d "@$((latest_reset_epoch + CATCHUP_BUFFER_SECS))" -Iseconds)
  echo "$(date -Iseconds) spawning catchup subshell for [${slugs[*]}]; wakes at $target_iso; log=$catchup_log"

  (
    exec >> "$catchup_log" 2>&1
    echo "=== $(date -Iseconds) catchup start for [${slugs[*]}], target wake $target_iso ==="

    local secs=$((latest_reset_epoch - $(date +%s) + CATCHUP_BUFFER_SECS))
    if [ "$secs" -gt 0 ]; then
      echo "=== sleeping ${secs}s ==="
      sleep "$secs"
    fi

    echo "=== $(date -Iseconds) catchup Phase 1 (re-run) for [${slugs[*]}] ==="
    cd "$REPO" || exit 1
    local s prompt
    for s in "${slugs[@]}"; do
      prompt="$REPO/podcasts/$s/PROMPT.md"
      [ -f "$prompt" ] && run_show "$prompt" "$s" &
    done
    wait

    echo "=== $(date -Iseconds) catchup Phase 2: rsync up + sbatch ==="
    rsync -a --delete \
      --exclude='.git' --exclude='/.venv/' --exclude='node_modules' \
      --exclude='podcasts/*/episodes' --exclude='podcasts/*/logs' \
      --exclude='podcasts/*/feed.xml' --exclude='podcasts/*/audio' \
      "$REPO/" "$GARIBALDI_HOST:$GARIBALDI_STAGE_DIR/"

    set +e
    timeout "$PHASE2_TIMEOUT_SECS" \
      ssh "$GARIBALDI_HOST" \
        "cd $GARIBALDI_STAGE_DIR && sbatch --wait --export=ALL,TTS_BATCH_DATE=$TODAY hpc/tts-batch.slurm"
    set -e
    echo "=== $(date -Iseconds) catchup sbatch exited rc=$? ==="

    rsync -av \
      --include='podcasts/' --include='podcasts/*/' \
      --include='podcasts/*/episodes/' --include='podcasts/*/episodes/*.mp3' \
      --exclude='*' \
      "$GARIBALDI_HOST:$GARIBALDI_STAGE_DIR/" "$REPO/"

    echo "=== $(date -Iseconds) catchup Phase 3: publish_pending.py ==="
    python3 "$REPO/scripts/publish_pending.py" --date "$TODAY"

    # Catch any straggling cron.log changes from the catchup's Phase 1.
    if ! git diff --quiet -- 'podcasts/*/logs/cron.log'; then
      git add 'podcasts/*/logs/cron.log' && git commit -m 'Update cron logs (catchup)' || true
      git push || true
    fi
    echo "=== $(date -Iseconds) catchup done ==="

    # Fire the daily audit now that Phase 3 for the deferred set is done.
    # run_daily_audit.sh is idempotent (marker-gated) so this is a no-op
    # if the 09:00 backstop cron or an earlier fire already sent it.
    # AUDIT_FROM_PIPELINE=1 opts out of the in-progress pgrep gate — we
    # ARE the pipeline, and the parent run_all_shows.sh is still alive.
    AUDIT_FROM_PIPELINE=1 "$REPO/scripts/run_daily_audit.sh" >> "$REPO/logs/audit.log" 2>&1 || true
  ) &
  disown
  CATCHUP_SPAWNED=1
}

# AUP-retry / model-ladder wrapper. Returns when:
#  - Claude exits 0 AND an mp3 was produced (legacy mode) OR a script
#    stub set was produced (SKIP_TTS mode); or
#  - all retries are exhausted (logs "FAILED: ...").
run_show() {
  local prompt="$1"
  local slug="$2"
  local log="$REPO/podcasts/$slug/logs/cron.log"
  local status_file="$STATUS_DIR/$slug"
  mkdir -p "$(dirname "$log")" "$STATUS_DIR"
  rm -f "$status_file"  # clear stale entry from a mid-day rerun

  local attempt tag out model_arg today produced script base
  # Outcome bookkeeping. Updated by every iteration's failure-classification
  # so the value left after the loop reflects the LAST failure mode — that's
  # what determines whether this show is deferrable.
  local last_failure="" last_reset=""
  today=$(date +%F)
  for attempt in 1 2 3 4 5 6; do
    case "$attempt" in
      1|2) model_arg="" ;;
      3|4) model_arg="--model claude-sonnet-5" ;;
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
    if grep -q "session limit · resets" "$out"; then
      last_failure="session_limit"
      last_reset=$(grep -oE 'session limit · resets [0-9]{1,2}(:[0-9]{2})?(am|pm)' "$out" \
                     | head -1 | sed 's/.*resets //')
      if [ "$attempt" -lt 6 ]; then
        echo "=== $(date -Iseconds) session-limit detected for $slug; computing reset-aware sleep ===" | tee -a "$log"
        sleep_until_reset "$out" "$log"
        rm -f "$out"
        continue
      fi
    elif grep -q "Claude Code is unable to respond to this request, which appears to violate our Usage Policy" "$out"; then
      last_failure="aup"
      last_reset=""
      if [ "$attempt" -lt 6 ]; then
        echo "=== $(date -Iseconds) AUP-refusal detected for $slug; retrying in 180s ===" | tee -a "$log"
        rm -f "$out"
        sleep 180
        continue
      fi
    else
      last_failure=""
      last_reset=""
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
      [ -z "$last_failure" ] && last_failure="no_output"
      echo "=== $(date -Iseconds) no usable output for $slug; retrying in 180s ===" | tee -a "$log"
      rm -f "$out"
      sleep 180
      continue
    fi
    if [ -z "$produced" ]; then
      [ -z "$last_failure" ] && last_failure="no_output"
      echo "=== $(date -Iseconds) FAILED: no usable output for $slug after all retries ===" | tee -a "$log"
    fi
    rm -f "$out"
    break
  done

  # Write per-show outcome for the post-Phase-1 collector. One line:
  #   "SUCCESS"
  #   "DEFER <reset-string>"        e.g. "DEFER 5am"
  #   "FAIL <last-failure-mode>"    e.g. "FAIL aup", "FAIL no_output"
  if [ -n "$produced" ]; then
    echo "SUCCESS" > "$status_file"
  elif [ "$last_failure" = "session_limit" ] && [ -n "$last_reset" ]; then
    echo "DEFER $last_reset" > "$status_file"
  else
    echo "FAIL ${last_failure:-unknown}" > "$status_file"
  fi
}

##############################################################################
# Pre-flight (PAUSE_INACTIVE=1): scripts/check_activity.py queries D1 for the
# last non-bot GET per podcast. Verdicts we act on:
#   paused_still_cold  already paused, still cold  → skip Phase 1 entirely,
#                                                    write a SKIP status file
#                                                    so the outcome collector
#                                                    doesn't flag as FAILED
#   resume             was paused, fresh GET seen → delete state/pause.json,
#                                                    run normally today
#   pause_now          just crossed threshold      → call scripts/prepare_goodbye.py
#                                                    to write today's goodbye
#                                                    script + stubs + pause.json,
#                                                    then skip Phase 1 for this
#                                                    show (Phase 2/3 publish the
#                                                    goodbye like any other episode)
# Fails open: any error from check_activity.py logs a warning and lets Phase 1
# proceed for all shows (better a spurious daily than a wrong pause).
##############################################################################
PAUSE_INACTIVE=${PAUSE_INACTIVE:-0}
declare -A SKIP_SLUGS=()

if [ "$PAUSE_INACTIVE" = "1" ]; then
  mkdir -p "$STATUS_DIR"
  activity_stdout=$(mktemp)
  activity_stderr=$(mktemp)
  (
    if [ -f "$REPO/.env" ]; then
      set -a; . "$REPO/.env"; set +a
    fi
    python3 "$REPO/scripts/check_activity.py" --format tsv
  ) > "$activity_stdout" 2> "$activity_stderr"
  activity_rc=$?
  if [ "$activity_rc" -ne 0 ]; then
    echo "$(date -Iseconds) PAUSE_INACTIVE=1 but check_activity.py exited $activity_rc; failing open (no skips)"
    cat "$activity_stderr"
  else
    while IFS=$'\t' read -r slug verdict days_since paused_at; do
      case "$verdict" in
        paused_still_cold)
          SKIP_SLUGS[$slug]=1
          mkdir -p "$REPO/podcasts/$slug/logs"
          echo "SKIP paused" > "$STATUS_DIR/$slug"
          echo "=== $(date -Iseconds) paused $slug (${days_since}d cold, paused_at=$paused_at) ===" \
            | tee -a "$REPO/podcasts/$slug/logs/cron.log"
          ;;
        resume)
          rm -f "$REPO/podcasts/$slug/state/pause.json"
          mkdir -p "$REPO/podcasts/$slug/logs"
          echo "=== $(date -Iseconds) resumed $slug (fresh GET after pause; removed pause.json) ===" \
            | tee -a "$REPO/podcasts/$slug/logs/cron.log"
          ;;
        pause_now)
          mkdir -p "$REPO/podcasts/$slug/logs"
          if goodbye_out=$(python3 "$REPO/scripts/prepare_goodbye.py" --slug "$slug" --date "$TODAY" 2>&1); then
            SKIP_SLUGS[$slug]=1
            echo "SKIP pause_now:$goodbye_out" > "$STATUS_DIR/$slug"
            echo "=== $(date -Iseconds) paused $slug (${days_since}d cold; goodbye episode $goodbye_out prepared for Phase 2/3) ===" \
              | tee -a "$REPO/podcasts/$slug/logs/cron.log"
          else
            echo "$(date -Iseconds) PAUSE_INACTIVE: prepare_goodbye.py failed for $slug (${days_since}d cold), running normally: $goodbye_out"
          fi
          ;;
      esac
    done < "$activity_stdout"
    echo "$(date -Iseconds) PAUSE_INACTIVE=1: skipping ${#SKIP_SLUGS[@]} show(s)${SKIP_SLUGS[*]:+: ${!SKIP_SLUGS[*]}}"
  fi
  rm -f "$activity_stdout" "$activity_stderr"
fi

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
  if [ -n "${SKIP_SLUGS[$slug]:-}" ]; then
    continue
  fi
  if [ "$first" -eq 0 ]; then
    sleep "$STAGGER_SECONDS"
  fi
  first=0
  run_show "$prompt" "$slug" &
done
wait

# Collect Phase 1 outcomes into three sets. (No behaviour change yet — this
# is the data-collection foundation for the deferred-catchup architecture.
# Phases 2 and 3 still run on whatever produced scripts, unchanged.)
SUCCEEDED=()
DEFERRED=()   # entries are "slug:reset-string"
FAILED=()     # entries are "slug:failure-mode"
SKIPPED=()    # entries are "slug:reason"
for prompt in podcasts/*/PROMPT.md; do
  [ -f "$prompt" ] || continue
  slug=$(basename "$(dirname "$prompt")")
  status_file="$STATUS_DIR/$slug"
  if [ ! -f "$status_file" ]; then
    FAILED+=("$slug:no_status_file")
    continue
  fi
  read -r kind rest < "$status_file"
  case "$kind" in
    SUCCESS) SUCCEEDED+=("$slug") ;;
    DEFER)   DEFERRED+=("$slug:$rest") ;;
    FAIL)    FAILED+=("$slug:$rest") ;;
    SKIP)    SKIPPED+=("$slug:$rest") ;;
    *)       FAILED+=("$slug:unknown_status[$kind]") ;;
  esac
done
echo "$(date -Iseconds) Phase 1 outcomes: ${#SUCCEEDED[@]} succeeded, ${#DEFERRED[@]} deferrable, ${#FAILED[@]} failed, ${#SKIPPED[@]} skipped"
[ "${#SUCCEEDED[@]}" -gt 0 ] && echo "  succeeded: ${SUCCEEDED[*]}"
[ "${#DEFERRED[@]}" -gt 0 ]  && echo "  deferrable (session-limit): ${DEFERRED[*]}"
[ "${#FAILED[@]}" -gt 0 ]    && echo "  failed: ${FAILED[*]}"
[ "${#SKIPPED[@]}" -gt 0 ]   && echo "  skipped (paused): ${SKIPPED[*]}"

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

if [ "${#SUCCEEDED[@]}" -gt 0 ]; then
  echo "$(date -Iseconds) Phase 2: batch TTS on Garibaldi for SUCCEEDED [${SUCCEEDED[*]}]"
else
  echo "$(date -Iseconds) Phase 2: batch TTS on Garibaldi (no SUCCEEDED set — Garibaldi will discover and exit clean)"
fi

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

# Spawn the deferred-catchup subshell *after* the main Phase 3 push, so it
# starts from a clean working tree. The subshell will sleep, then re-run
# Phase 1/2/3 for the deferred slugs and do its own push.
if [ "${#DEFERRED[@]}" -gt 0 ]; then
  spawn_catchup
fi

echo "$(date -Iseconds) run_all_shows.sh done (phase3 rc=$PHASE3_RC)"
exit $PHASE3_RC
