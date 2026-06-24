#!/usr/bin/env python3
"""Generate TTS audio for a podcast episode.

Usage:
    python3 gen_tts.py --show <slug> <script.md> <output.mp3>

By default, voice/model/provider come from podcasts/<slug>/show.toml
([tts.primary], falling back to [tts.fallback] on error).

To force a single provider with no fallback chain (used by the batch
pipeline — Voxtral on HPC, Mistral on su08 gap-fill):

    python3 gen_tts.py --show <slug> --provider voxtral <script.md> <output.mp3>
    python3 gen_tts.py --show <slug> --provider mistral <script.md> <output.mp3>

The provider name must match the `provider` field of either [tts.primary]
or [tts.fallback] in show.toml.

Reads MISTRAL_API_KEY from .env (or environment).

Includes a per-chunk duration sanity check: if a synthesized chunk runs
shorter than chars / MAX_CHARS_PER_SECOND seconds, it's retried up to
CHUNK_RETRIES times. Aborts non-zero if a chunk still fails.
"""
import argparse
import base64
import os
import re
import subprocess
import sys
import tempfile

import requests

from lib.show import load as load_show

MISTRAL_URL = "https://api.mistral.ai/v1/audio/speech"
MISTRAL_CHUNK_MAX = 3000
CHUNK_RETRIES = 2

VOXTRAL_DEFAULT_URL = "http://localhost:8000/v1/audio/speech"
VOXTRAL_CHUNK_MAX = 3000

# Voices typically run 14-21 chars/sec depending on chunk size and
# punctuation density. 25 tolerates natural speed variance while still
# catching truncation that drops >~35% of a chunk.
MAX_CHARS_PER_SECOND = 25

# Used only when --show is not given (manual one-off invocations).
DEFAULT_PRIMARY = {
    "provider": "voxtral",
    "model": "mistralai/Voxtral-4B-TTS-2603",
    "voice": "neutral_male",
    "speed": 1.2,
}
DEFAULT_FALLBACK = {
    "provider": "mistral",
    "model": "voxtral-mini-tts-2603",
    "voice": "en_paul_neutral",
}


def load_env():
    env = dict(os.environ)
    repo_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(repo_env):
        for line in open(repo_env):
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return env


# Spellings the TTS mispronounces. Replaced before synthesis. The phonetic
# forms ("archive" / "med-archive" / "bio-archive") are read naturally by
# both Mistral Paul and Voxtral neutral_male.
PRONUNCIATION_SUBS = [
    (re.compile(r"\bbiorxiv\b", re.IGNORECASE), "bio-archive"),
    (re.compile(r"\bmedrxiv\b", re.IGNORECASE), "med-archive"),
    (re.compile(r"\barxiv\b", re.IGNORECASE), "archive"),
]


def apply_pronunciation_subs(text):
    for pattern, replacement in PRONUNCIATION_SUBS:
        text = pattern.sub(replacement, text)
    return text


def extract_script_body(path):
    text = open(path).read()
    if "## Script" in text:
        text = text.split("## Script", 1)[1]
    lines = [l for l in text.strip().split("\n") if not l.strip().startswith("Paper link:")]
    return apply_pronunciation_subs("\n".join(lines).strip())


def chunk_text(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    chunks, current = [], ""
    for para in text.split("\n\n"):
        if len(current) + len(para) > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current = current + "\n\n" + para if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks


def stitch(parts, output, speed=1.0):
    # Voxtral and Mistral both have within-utterance loudness drift (Mistral
    # drops 15-25 dB through a paragraph). Final ffmpeg pass: dynaudnorm
    # smooths within-file drift, loudnorm targets EBU R128 podcast loudness
    # (-16 LUFS integrated, -1 dBTP peak).
    af = "dynaudnorm=f=200:g=15,loudnorm=I=-16:TP=-1:LRA=11"
    if speed != 1.0:
        # atempo changes tempo without pitch shift; valid range 0.5-2.0.
        af = f"atempo={speed}," + af
    with tempfile.TemporaryDirectory() as tmp:
        if len(parts) == 1:
            raw = os.path.join(tmp, "raw.mp3")
            open(raw, "wb").write(parts[0])
        else:
            manifest = os.path.join(tmp, "list.txt")
            raw = os.path.join(tmp, "raw.mp3")
            with open(manifest, "w") as mf:
                for j, part in enumerate(parts):
                    pp = os.path.join(tmp, f"part{j}.mp3")
                    open(pp, "wb").write(part)
                    mf.write(f"file '{pp}'\n")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest, "-c", "copy", raw],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            )
        subprocess.run(
            ["ffmpeg", "-y", "-i", raw,
             "-af", af,
             "-ac", "1", "-ar", "22050", "-b:a", "64k", output],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        )


def mp3_bytes_duration(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
        tf.write(audio_bytes)
        path = tf.name
    try:
        return duration_seconds(path)
    finally:
        os.unlink(path)


def mistral_synthesize(chunk, api_key, model, voice):
    r = requests.post(
        MISTRAL_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "input": chunk, "voice_id": voice, "response_format": "mp3"},
        timeout=300,
    )
    r.raise_for_status()
    data = r.json()
    audio_b64 = data.get("audio_data") or data.get("data")
    if not audio_b64:
        raise RuntimeError(f"Mistral response missing audio_data; keys={list(data.keys())}")
    return base64.b64decode(audio_b64)


def voxtral_synthesize(chunk, base_url, model, voice):
    r = requests.post(
        base_url,
        json={"model": model, "input": chunk, "voice": voice, "response_format": "mp3"},
        timeout=600,
    )
    r.raise_for_status()
    return r.content


def synthesize_chunks(chunks, synth_fn, label):
    parts = []
    for i, chunk in enumerate(chunks):
        min_dur = len(chunk) / MAX_CHARS_PER_SECOND
        last_err = None
        for attempt in range(1, CHUNK_RETRIES + 2):
            try:
                audio = synth_fn(chunk)
                dur = mp3_bytes_duration(audio)
                if dur < min_dur:
                    last_err = f"chunk duration {dur:.1f}s < floor {min_dur:.1f}s (likely truncated)"
                    print(f"  [{label}] chunk {i+1}/{len(chunks)} attempt {attempt} FAILED: {last_err}")
                    continue
                print(f"  [{label}] chunk {i+1}/{len(chunks)} ({len(chunk)} chars) -> {dur:.1f}s ✓")
                parts.append(audio)
                break
            except Exception as e:
                last_err = str(e)
                print(f"  [{label}] chunk {i+1}/{len(chunks)} attempt {attempt} error: {e}")
        else:
            raise RuntimeError(f"{label} chunk {i+1} failed after retries: {last_err}")
    return parts


def synthesize_with_provider(provider_cfg, text, output, env):
    name = provider_cfg["provider"]
    if name == "mistral":
        api_key = env.get("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY not set")
        model = provider_cfg["model"]
        voice = provider_cfg["voice"]
        speed = float(provider_cfg.get("speed", 1.0))
        chunks = chunk_text(text, MISTRAL_CHUNK_MAX)
        parts = synthesize_chunks(
            chunks, lambda c: mistral_synthesize(c, api_key, model, voice), f"mistral:{voice}",
        )
        stitch(parts, output, speed=speed)
    elif name == "voxtral":
        base_url = provider_cfg.get("url", VOXTRAL_DEFAULT_URL)
        model = provider_cfg.get("model", "mistralai/Voxtral-4B-TTS-2603")
        voice = provider_cfg["voice"]
        speed = float(provider_cfg.get("speed", 1.0))
        chunks = chunk_text(text, VOXTRAL_CHUNK_MAX)
        parts = synthesize_chunks(
            chunks, lambda c: voxtral_synthesize(c, base_url, model, voice), f"voxtral:{voice}",
        )
        stitch(parts, output, speed=speed)
    else:
        raise ValueError(f"unknown TTS provider: {name!r}")


def duration_seconds(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path]
    ).decode().strip()
    return float(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--show", help="show slug; loads voice config from podcasts/<slug>/show.toml")
    ap.add_argument("--provider", help="force a specific provider (voxtral|mistral); no fallback chain")
    ap.add_argument("script")
    ap.add_argument("output")
    args = ap.parse_args()

    if args.show:
        show = load_show(args.show)
        primary = show.tts_primary or DEFAULT_PRIMARY
        fallback = show.tts_fallback  # may be None
    else:
        primary = DEFAULT_PRIMARY
        fallback = DEFAULT_FALLBACK

    env = load_env()
    text = extract_script_body(args.script)

    # --provider <name>: locate that provider's config in show.toml and use
    # it standalone (no fallback). Used by the batch pipeline so each tier
    # of the recovery chain runs in its own process.
    if args.provider:
        forced = None
        for cfg in (primary, fallback):
            if cfg and cfg.get("provider") == args.provider:
                forced = cfg
                break
        if not forced:
            print(f"ERROR: --provider {args.provider!r} not configured in show {args.show!r}", file=sys.stderr)
            sys.exit(2)
        print(f"Script body: {len(text)} chars; forced={args.provider}")
        try:
            synthesize_with_provider(forced, text, args.output, env)
        except Exception as e:
            print(f"ERROR: forced provider {args.provider} failed: {e}", file=sys.stderr)
            sys.exit(3)
        used = args.provider
    else:
        print(f"Script body: {len(text)} chars; primary={primary['provider']}"
              f"{' fallback=' + fallback['provider'] if fallback else ''}")
        used = None
        try:
            synthesize_with_provider(primary, text, args.output, env)
            used = primary["provider"]
        except Exception as e:
            print(f"Primary ({primary['provider']}) failed: {e}")
            if not fallback:
                print("ERROR: no fallback configured", file=sys.stderr)
                sys.exit(3)
            print(f"Falling back to {fallback['provider']}.")
            try:
                synthesize_with_provider(fallback, text, args.output, env)
                used = fallback["provider"]
            except Exception as e2:
                print(f"ERROR: both primary and fallback failed: {e2}", file=sys.stderr)
                sys.exit(3)

    dur = duration_seconds(args.output)
    size = os.path.getsize(args.output)
    print(f"Done: {args.output} [{used}] {size:,} bytes, {dur:.1f}s")


if __name__ == "__main__":
    main()
