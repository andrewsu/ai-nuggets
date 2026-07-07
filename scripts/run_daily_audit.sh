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
