#!/usr/bin/env python3
"""Generate TTS audio for a podcast episode.

Usage:
    # With per-show config (preferred):
    python3 gen_tts.py --show <slug> <script.md> <output.mp3>

    # Without --show (default voice config: Mistral primary, ElevenLabs fallback):
    python3 gen_tts.py <script.md> <output.mp3>

When --show is given, voice/model/provider come from
podcasts/<slug>/show.toml ([tts.primary] and optional [tts.fallback]).
Otherwise the legacy defaults are used (back-compat).

Reads MISTRAL_API_KEY and ELEVENLABS_API_KEY from .env (or environment).

Includes a per-chunk duration sanity check: if a synthesized chunk runs
shorter than chars / MAX_CHARS_PER_SECOND seconds, it's retried up to
MISTRAL_CHUNK_RETRIES times. Aborts non-zero if a chunk still fails.
"""
import argparse
import base64
import os
import subprocess
import sys
import tempfile

import requests

from lib.show import load as load_show

MISTRAL_URL = "https://api.mistral.ai/v1/audio/speech"
MISTRAL_CHUNK_MAX = 3000
MISTRAL_CHUNK_RETRIES = 2

ELEVENLABS_CHUNK_MAX = 3000

# Paul Neutral typically runs 14-21 chars/sec depending on chunk size and
# punctuation density. 25 tolerates natural speed variance while still
# catching truncation that drops >~35% of a chunk. Used for both providers.
MAX_CHARS_PER_SECOND = 25

DEFAULT_PRIMARY = {
    "provider": "mistral",
    "model": "voxtral-mini-tts-2603",
    "voice": "en_paul_neutral",
}
DEFAULT_FALLBACK = {
    "provider": "elevenlabs",
    "voice": "hpp4J3VqNfWAUOO0d1Us",
    "model": "eleven_flash_v2_5",
    "settings": {"speed": 1.1, "stability": 0.5, "similarity_boost": 0.75},
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


def extract_script_body(path):
    text = open(path).read()
    if "## Script" in text:
        text = text.split("## Script", 1)[1]
    lines = [l for l in text.strip().split("\n") if not l.strip().startswith("Paper link:")]
    return "\n".join(lines).strip()


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


def stitch(parts, output):
    if len(parts) == 1:
        open(output, "wb").write(parts[0])
        return
    with tempfile.TemporaryDirectory() as tmp:
        manifest = os.path.join(tmp, "list.txt")
        with open(manifest, "w") as mf:
            for j, part in enumerate(parts):
                pp = os.path.join(tmp, f"part{j}.mp3")
                open(pp, "wb").write(part)
                mf.write(f"file '{pp}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest, "-c", "copy", output],
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


def elevenlabs_synthesize(chunk, api_key, voice, model, settings):
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": chunk, "model_id": model, "voice_settings": settings},
        timeout=300,
    )
    r.raise_for_status()
    return r.content


def synthesize_chunks(chunks, synth_fn, label):
    parts = []
    for i, chunk in enumerate(chunks):
        min_dur = len(chunk) / MAX_CHARS_PER_SECOND
        last_err = None
        for attempt in range(1, MISTRAL_CHUNK_RETRIES + 2):
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
        chunks = chunk_text(text, MISTRAL_CHUNK_MAX)
        parts = synthesize_chunks(
            chunks, lambda c: mistral_synthesize(c, api_key, model, voice), f"mistral:{voice}",
        )
        stitch(parts, output)
    elif name == "elevenlabs":
        api_key = env.get("ELEVENLABS_API_KEY")
        if not api_key:
            raise RuntimeError("ELEVENLABS_API_KEY not set")
        voice = provider_cfg["voice"]
        model = provider_cfg["model"]
        settings = provider_cfg.get("settings", DEFAULT_FALLBACK["settings"])
        chunks = chunk_text(text, ELEVENLABS_CHUNK_MAX)
        parts = synthesize_chunks(
            chunks, lambda c: elevenlabs_synthesize(c, api_key, voice, model, settings), f"elevenlabs:{voice}",
        )
        stitch(parts, output)
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
