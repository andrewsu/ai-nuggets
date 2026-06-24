#!/bin/bash
# One-time install for Voxtral TTS on Garibaldi.
# Submits to the shared partition (no GPU needed for install — vllm wheels are prebuilt).
# Pre-downloads the model so the first server job doesn't time out fetching weights.
#
# Usage: sbatch bootstrap.slurm
# Re-runnable: nukes and recreates .venv from scratch.
#
#SBATCH --job-name=voxtral-bootstrap
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=12gb
#SBATCH --time=00:45:00
#SBATCH --output=logs/bootstrap_%j.out
#SBATCH --error=logs/bootstrap_%j.err

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p logs

# Do NOT module-load python — its site-packages pollute the venv.
source /etc/profile.d/modules.sh
module purge
unset PYTHONPATH PYTHONHOME

echo "=== install uv (if not present) ==="
if [ ! -x "$HOME/.local/bin/uv" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv --version

echo "=== install python 3.11 under uv ==="
uv python install 3.11

echo "=== (re)create .venv ==="
rm -rf .venv
uv venv .venv --python 3.11
source .venv/bin/activate
python --version

echo "=== install vllm/vllm-omni + fastapi pin ==="
uv pip install 'vllm==0.22.*' 'vllm-omni==0.22.*' huggingface_hub
# fastapi 0.118+ broke vllm-omni 0.22.0 middleware (every route returns 500).
uv pip install 'fastapi>=0.115,<0.118'

echo "=== verify ==="
python -c "import vllm; print('vllm', vllm.__version__)"
python -c "import vllm_omni; print('vllm_omni', vllm_omni.__version__)"
python -c "import fastapi; print('fastapi', fastapi.__version__)"
python -c "import mistral_common; print('mistral_common', mistral_common.__version__)"

echo "=== pre-download model weights (~7.5GB) ==="
time hf download mistralai/Voxtral-4B-TTS-2603

echo "=== final disk usage ==="
du -sh ~/.cache/huggingface .venv
echo "=== done ==="
