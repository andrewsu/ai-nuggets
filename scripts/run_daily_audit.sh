#!/bin/bash
# Cron wrapper for scripts/daily_audit.py. Sources .env so AWS_*, SES_*,
# and MISTRAL_ADMIN_API_KEY are visible to the python process — cron's
# default environment otherwise omits them.
#
# Idempotency: skips if logs/.audit-sent-YYYY-MM-DD is already present;
# touches the marker on successful send (skipped in --dry-run mode). This
# lets multiple callers race safely:
#   - run_all_shows.sh end-of-main-path trap (when no catchup was spawned)
#   - catchup subshell at its end
#   - 09:00 cron backstop for the crashed-pipeline / host-was-down case
# Whichever fires first sends the email; the others are no-ops.
#
# In-progress gating: the cron backstop skips if run_all_shows.sh is still
# alive at 09:00 (long Slurm queue, big catchup, etc.) — that lets us bump
# PHASE2_TIMEOUT_SECS without the 09:00 cron sending a premature "shows
# need attention" email while the pipeline is still working. Pipeline-side
# callers set AUDIT_FROM_PIPELINE=1 to bypass the gate, since they're
# invoked from inside the shell process pgrep would find.
#
# Crontab (09:00 PT — late enough to cover worst-case catchup finish at
# ~08:20 given CATCHUP_MAX_WAIT_SECS=21600 from a 02:00 start):
#   0 9 * * * /home/asu/Science/ai-nuggets/scripts/run_daily_audit.sh >> /home/asu/Science/ai-nuggets/logs/audit.log 2>&1

set -u
REPO=/home/asu/Science/ai-nuggets
PYTHON=/home/asu/miniforge3/bin/python3
MARKER="$REPO/logs/.audit-sent-$(date +%F)"

if [ -f "$MARKER" ]; then
  exit 0
fi

# Defer to a live pipeline. The [r]un_all_shows.sh char-class prevents
# pgrep from matching its own cmdline. AUDIT_FROM_PIPELINE=1 opts out —
# used by the trap and catchup callers, which are themselves subprocesses
# of a still-live run_all_shows.sh and would self-block otherwise.
if [ -z "${AUDIT_FROM_PIPELINE:-}" ]; then
  if live_pids=$(pgrep -f '[r]un_all_shows.sh'); then
    echo "$(date -Iseconds) run_daily_audit: pipeline still running (pids: $(echo $live_pids | tr '\n' ' ')), deferring"
    exit 0
  fi
fi

if [ -f "$REPO/.env" ]; then
  set -a
  . "$REPO/.env"
  set +a
fi

DRY=0
for a in "$@"; do
  [ "$a" = "--dry-run" ] && DRY=1
done

"$PYTHON" "$REPO/scripts/daily_audit.py" "$@"
rc=$?
if [ "$rc" -eq 0 ] && [ "$DRY" -eq 0 ]; then
  touch "$MARKER"
fi
exit "$rc"
