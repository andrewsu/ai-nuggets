#!/bin/bash
# Batch TTS job: start vLLM, synthesize all of today's pending episodes
# across all shows, kill vLLM, exit.
#
# Invoked nightly by scripts/run_all_shows.sh on su08:
#   ssh garibaldi 'cd ~/ai-nuggets-stage && sbatch --wait hpc/tts-batch.slurm'
#
# Multi-partition request: Slurm picks whichever has earliest availability.
# rtxa6000 (48GB) is preferred; a100 (40/80GB) is fully sufficient; alphafold
# nodes also work if their partition policy allows external submission.
#
#SBATCH --job-name=tts-batch
#SBATCH --partition=rtxa6000,a100,alphafold
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32gb
#SBATCH --gres=gpu:1
#SBATCH --time=00:45:00
#SBATCH --output=logs/tts-batch_%j.out
#SBATCH --error=logs/tts-batch_%j.err

set -uo pipefail   # no -e: we want to count partial successes, not abort on any one show's failure
cd "$SLURM_SUBMIT_DIR"
mkdir -p logs

source /etc/profile.d/modules.sh
module purge
module load cuda/12.4 ffmpeg/7.0.2
unset PYTHONPATH PYTHONHOME
export PATH="$HOME/.local/bin:$PATH"
source "$HOME/projects/voxtral-tts/.venv/bin/activate"

PORT=8000
TODAY="${TTS_BATCH_DATE:-$(date +%Y-%m-%d)}"
PARALLEL="${TTS_BATCH_PARALLEL:-4}"

echo "=== $(date -Iseconds) tts-batch starting (job $SLURM_JOB_ID on $(hostname)) ==="
echo "TODAY=$TODAY  PARALLEL=$PARALLEL"

# Start vLLM in background.
echo "=== starting vllm serve ==="
vllm serve mistralai/Voxtral-4B-TTS-2603 --omni --host 127.0.0.1 --port "$PORT" --max-model-len 8192 \
  > "logs/vllm_$SLURM_JOB_ID.out" 2> "logs/vllm_$SLURM_JOB_ID.err" &
VLLM_PID=$!
echo "vllm pid=$VLLM_PID"

cleanup() {
  echo "=== $(date -Iseconds) cleanup: SIGTERM vllm pid=$VLLM_PID ==="
  kill -TERM "$VLLM_PID" 2>/dev/null || true
  wait "$VLLM_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Wait for /v1/models 200. Cold-load takes ~5-7 min.
echo "=== waiting for vLLM /v1/models ==="
READY=0
for i in $(seq 1 90); do
  CODE=$(curl -sS -o /dev/null -w "%{http_code}" --max-time 5 "http://127.0.0.1:$PORT/v1/models" 2>/dev/null || echo 000)
  if [ "$CODE" = "200" ]; then
    echo "[t+$((i*10))s] vLLM ready"
    READY=1; break
  fi
  sleep 10
done
if [ "$READY" != "1" ]; then
  echo "ERROR: vLLM never became ready within 15 min" >&2
  tail -30 "logs/vllm_$SLURM_JOB_ID.err" >&2 || true
  exit 1
fi

# Discover today's scripts that don't have an MP3 yet.
shopt -s nullglob
TASKS=()
for show_dir in podcasts/*/; do
  slug=$(basename "$show_dir")
  for script in "${show_dir}scripts/${TODAY}"*.md "${show_dir}scripts/${TODAY}"*.txt; do
    [ -f "$script" ] || continue
    base=$(basename "$script")
    base="${base%.*}"
    output="${show_dir}episodes/${base}.mp3"
    [ -f "$output" ] && continue
    TASKS+=("${slug}|${script}|${output}")
  done
done

echo "=== ${#TASKS[@]} episodes to synthesize ==="
for t in "${TASKS[@]}"; do echo "  $t"; done

if [ "${#TASKS[@]}" -eq 0 ]; then
  echo "no pending scripts for $TODAY; exiting clean"
  exit 0
fi

# Run gen_tts.py concurrently, capped at $PARALLEL.
synth_one() {
  IFS='|' read -r slug script output <<<"$1"
  base=$(basename "$output" .mp3)
  log="podcasts/$slug/logs/tts-batch_${base}.log"
  mkdir -p "$(dirname "$log")" "$(dirname "$output")"
  echo "  [$(date +%H:%M:%S)] synth $slug $(basename "$script") -> $(basename "$output")"
  if python3 gen_tts.py --show "$slug" --provider voxtral "$script" "$output" > "$log" 2>&1; then
    echo "  [$(date +%H:%M:%S)] OK    $slug $(basename "$output")"
  else
    rc=$?
    echo "  [$(date +%H:%M:%S)] FAIL  $slug $(basename "$output") rc=$rc (see $log)"
  fi
}
export -f synth_one

printf '%s\n' "${TASKS[@]}" | xargs -P "$PARALLEL" -I {} bash -c 'synth_one "$@"' _ {}

# Tally results.
SUCCESS=0
FAIL=0
for t in "${TASKS[@]}"; do
  IFS='|' read -r _ _ output <<<"$t"
  if [ -f "$output" ]; then SUCCESS=$((SUCCESS+1)); else FAIL=$((FAIL+1)); fi
done
echo "=== $(date -Iseconds) tts-batch done: $SUCCESS/$((SUCCESS+FAIL)) succeeded ==="

# Exit 0 if anything shipped; nonzero only if everything failed.
[ "$SUCCESS" -gt 0 ] && exit 0 || exit 2
