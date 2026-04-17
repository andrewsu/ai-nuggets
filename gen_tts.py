#!/usr/bin/env python3
"""Generate TTS for both episodes using Mistral API."""
import json, base64, sys, os, requests

API_KEY = os.environ.get("MISTRAL_API_KEY") or "gQPyWOYm6znc7v8yG7S99MUWnJJhFUJR"

episodes = [
    {
        "script": "scripts/2026-04-16-mozi-drug-discovery-agents.md",
        "output": "episodes/2026-04-16-mozi-drug-discovery-agents.mp3",
    },
    {
        "script": "scripts/2026-04-16-omics-data-discovery-agents.md",
        "output": "episodes/2026-04-16-omics-data-discovery-agents.mp3",
    },
]

def extract_script(path):
    with open(path) as f:
        text = f.read()
    # Extract just the script body (after ## Script)
    if "## Script" in text:
        text = text.split("## Script", 1)[1]
    # Remove the paper link line
    lines = [l for l in text.strip().split("\n") if not l.strip().startswith("Paper link:")]
    return "\n".join(lines).strip()

def generate_tts(text, output_path):
    # Split if > 10000 chars
    chunks = []
    if len(text) > 10000:
        # Split at paragraph boundaries
        paras = text.split("\n\n")
        current = ""
        for p in paras:
            if len(current) + len(p) > 9500 and current:
                chunks.append(current.strip())
                current = p
            else:
                current = current + "\n\n" + p if current else p
        if current.strip():
            chunks.append(current.strip())
    else:
        chunks = [text]

    audio_parts = []
    for i, chunk in enumerate(chunks):
        print(f"  Generating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
        resp = requests.post(
            "https://api.mistral.ai/v1/audio/speech",
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "voxtral-mini-tts-2603",
                "input": chunk,
                "voice_id": "en_paul_neutral",
                "response_format": "mp3",
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        audio_b64 = data.get("audio_data") or data.get("data")
        if not audio_b64:
            print(f"  ERROR: No audio_data in response keys: {list(data.keys())}")
            sys.exit(1)
        audio_parts.append(base64.b64decode(audio_b64))

    if len(audio_parts) == 1:
        with open(output_path, "wb") as f:
            f.write(audio_parts[0])
    else:
        # Stitch with ffmpeg
        import tempfile, subprocess
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = os.path.join(tmpdir, "list.txt")
            with open(manifest, "w") as mf:
                for j, part in enumerate(audio_parts):
                    part_path = os.path.join(tmpdir, f"part{j}.mp3")
                    with open(part_path, "wb") as pf:
                        pf.write(part)
                    mf.write(f"file '{part_path}'\n")
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest, "-c", "copy", output_path],
                check=True, capture_output=True,
            )

    size = os.path.getsize(output_path)
    print(f"  ✓ {output_path} ({size:,} bytes)")
    return size

base = "/home/ubuntu/.openclaw/workspace/ai-nuggets"
os.chdir(base)

for ep in episodes:
    print(f"\n=== {ep['output']} ===")
    script = extract_script(ep["script"])
    print(f"  Script length: {len(script)} chars")
    generate_tts(script, ep["output"])

print("\nDone!")
