# Voxtral TTS on Garibaldi HPC (batch mode)

Self-hosted text-to-speech using `mistralai/Voxtral-4B-TTS-2603` runs as a
**single Slurm job per night** that starts vLLM, synthesizes all of today's
pending podcast scripts in parallel, and tears the server back down. There
is no persistent server, no SSH tunnel, and no laptop-side state to manage.

`scripts/run_all_shows.sh` calls this remotely via
`ssh garibaldi 'sbatch --wait hpc/tts-batch.slurm'` — see that script and
`scripts/publish_pending.py` for the full Phase 1/2/3 flow.

License note: Voxtral weights are **CC BY-NC 4.0**. The individualized-feed
setup qualifies as non-commercial use.

## GPU partitions on Garibaldi

The job submits to multiple partitions (`#SBATCH --partition=rtxa6000,a100,alphafold`);
Slurm picks whichever has earliest availability.

| Partition | GPU | VRAM | Nodes |
|---|---|---|---|
| `rtxa6000` | A6000 | 48 GB | 8 |
| `a100` | A100 | 40/80 GB | 3 |
| `alphafold` | A6000 / A5000 | 48 / 24 GB | many (may be project-restricted) |
| `gpu` | gtx1080/1080ti | 8-11 GB | many — **too small for Voxtral, do not request** |

Voxtral-4B-TTS needs ≥16 GB VRAM. All three of the first three partitions work.

## One-time setup

**Do not use the stock `python/3.11.4` module.** Its bundled site-packages
bleed into venvs via `PYTHONPATH` (including an outdated `regex` that
crashes `transformers` on import). Use a uv-managed Python instead.

Run the install as a Slurm job, not on the login node (downloads ~5 GB of
wheels + 7.5 GB model):

```bash
ssh garibaldi.scripps.edu
mkdir -p ~/projects/voxtral-tts/logs && cd ~/projects/voxtral-tts
# from your laptop, push the slurm scripts:
#   scp hpc/bootstrap.slurm hpc/tts-batch.slurm garibaldi:~/projects/voxtral-tts/
sbatch bootstrap.slurm   # ~10 min on shared partition
```

`bootstrap.slurm` installs `uv`, downloads its own Python 3.11, creates
`.venv`, pins `vllm==0.22.* vllm-omni==0.22.* fastapi<0.118`, and pre-pulls
the model.

The pin `fastapi<0.118` matters: fastapi 0.118 introduced a
`_IncludedRouter` middleware wrapper that vllm-omni 0.22.0 doesn't expect,
breaking every endpoint with 500s. Don't loosen it without checking a newer
vllm-omni first.

The `tts-batch.slurm` job expects the staged repo at `~/ai-nuggets-stage/`
(populated by `run_all_shows.sh` via `rsync`). The venv lives independently
at `~/projects/voxtral-tts/.venv` and is sourced by the slurm script.

### One-time staged-repo init

`run_all_shows.sh` `rsync`s into `~/ai-nuggets-stage/` each night, but the
directory needs to exist:

```bash
ssh garibaldi.scripps.edu 'mkdir -p ~/ai-nuggets-stage/logs'
```

Subsequent runs overwrite stale scripts and create episode dirs on demand.

## Voices

The 20 open presets ship inside the HF repo at `voice_embedding/*.pt`:

- Language-neutral: `neutral_male`, `neutral_female`, `casual_male`,
  `casual_female`, `cheerful_female`
- Per-language: `ar_male`, `de_{male,female}`, `es_{male,female}`,
  `fr_{male,female}`, `hi_{male,female}`, `it_{male,female}`,
  `nl_{male,female}`, `pt_{male,female}`

We use `neutral_male` at 1.2× speed (set in each `show.toml`'s
`[tts.primary]`). Preview at https://huggingface.co/spaces/mistralai/voxtral-tts-demo.

## Smoke-testing tts-batch.slurm by hand

After staging the repo, you can submit the job directly:

```bash
ssh garibaldi.scripps.edu
cd ~/ai-nuggets-stage
JOB=$(sbatch --parsable hpc/tts-batch.slurm)
echo "job=$JOB"
# Watch:
tail -f logs/tts-batch_${JOB}.out
```

Default behavior: discover all scripts under `podcasts/*/scripts/`
matching today's date (`$(date +%Y-%m-%d)`) that don't have an MP3 yet,
synthesize them all in parallel (4 at a time), exit.

To force a different date: `sbatch --export=ALL,TTS_BATCH_DATE=2026-06-23 hpc/tts-batch.slurm`.

## Troubleshooting

- **Job stuck in PD** → `squeue -j <id> --start` gives an ETA. With three
  partitions in the request you should rarely see this; if you do,
  check `sinfo -p rtxa6000,a100,alphafold` for partition-wide load.
- **vLLM never responds to `/v1/models`** → check
  `logs/vllm_<job>.out`. First run may stall pulling weights if you
  skipped the pre-download step in `bootstrap.slurm`.
- **All shows fail with `connection refused`** → vLLM crashed during
  startup. Check `logs/vllm_<job>.err` for OOM or version mismatch
  (the fastapi pin is the usual culprit).
- **Voice sounds wrong** → check `show.toml` matches a Voxtral preset, not
  a Mistral-API voice id (`en_paul_neutral` belongs to the Mistral API
  only).
- **OOM in vLLM** → reduce `--max-model-len 8192` in the Slurm script, or
  let Slurm pick a larger GPU (the `--partition=rtxa6000,a100,alphafold`
  fan-out already does this opportunistically).
