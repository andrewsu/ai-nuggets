#!/usr/bin/env python3
"""Phase 2.5 + Phase 3 of the nightly pipeline.

Phase 2.5 (gap-fill): for any of today's scripts that don't have a matching
MP3 (either because the Garibaldi tts-batch.slurm never ran or because some
shows failed within it), retry with Mistral as a tier-2 provider.

Phase 3 (publish): for each show that now has an MP3, render its RSS item
stub (Claude wrote it in Phase 1 with __LENGTH__ and __DURATION__
placeholders), insert into feed.xml, push the MP3 to R2 via
publish_episode.sh, and git-commit the show's directory. Single git push
at the end.

Stub files Phase 1 writes alongside each script:
    podcasts/<slug>/scripts/<basename>.rss-item.xml   — full <item>...</item>
                                                        with __LENGTH__ and
                                                        __DURATION__ tokens
    podcasts/<slug>/scripts/<basename>.commit-msg     — full commit message
                                                        (prefix + title)

Both are transient; this script removes them before committing.

Usage:
    scripts/publish_pending.py                # uses today's date
    scripts/publish_pending.py --date 2026-06-23
    scripts/publish_pending.py --skip-gap-fill  # publish only, no Mistral
    scripts/publish_pending.py --skip-push      # commit but don't push
"""

import argparse
import datetime
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GIT_LOCK = "/tmp/ai-nuggets-git.lock"


def log(msg):
    print(msg, flush=True)


def discover_pending(today):
    """Return [(slug, script_path, mp3_path, basename), ...] for today's scripts."""
    results = []
    for show_dir in sorted((REPO / "podcasts").iterdir()):
        if not show_dir.is_dir():
            continue
        slug = show_dir.name
        scripts_dir = show_dir / "scripts"
        if not scripts_dir.exists():
            continue
        for ext in (".md", ".txt"):
            for script in sorted(scripts_dir.glob(f"{today}*{ext}")):
                basename = script.stem
                mp3 = show_dir / "episodes" / f"{basename}.mp3"
                results.append((slug, script, mp3, basename))
    return results


def gap_fill_mistral(items):
    """Run gen_tts.py --provider mistral for any item whose MP3 doesn't exist yet."""
    missing = [it for it in items if not it[2].exists()]
    if not missing:
        log("Phase 2.5: all MP3s present, nothing to gap-fill")
        return
    log(f"Phase 2.5: {len(missing)} MP3(s) missing, attempting Mistral fallback...")
    for slug, script, mp3, base in missing:
        log(f"  mistral gap-fill: {slug} / {base}")
        mp3.parent.mkdir(parents=True, exist_ok=True)
        log_path = REPO / "podcasts" / slug / "logs" / f"mistral-gapfill_{base}.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w") as logfp:
            r = subprocess.run(
                ["python3", str(REPO / "gen_tts.py"),
                 "--show", slug, "--provider", "mistral",
                 str(script), str(mp3)],
                cwd=REPO, stdout=logfp, stderr=subprocess.STDOUT,
            )
        if r.returncode != 0:
            log(f"    FAIL rc={r.returncode} (see {log_path.relative_to(REPO)})")
        else:
            log(f"    OK")


def insert_feed_item(feed_path, item_xml):
    """Insert <item>...</item> after channel metadata, before any existing items."""
    src = feed_path.read_text()
    # Indent the item to match existing siblings (4 spaces).
    indented = "\n".join("    " + line if line.strip() else line
                          for line in item_xml.strip().split("\n"))
    if "<item>" in src:
        out = src.replace("<item>", indented + "\n\n    <item>", 1)
    else:
        # First item ever for this show — insert before </channel>.
        out = src.replace("</channel>", indented + "\n  </channel>", 1)
    feed_path.write_text(out)


def mp3_duration_seconds(mp3):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(mp3)]
    ).decode().strip()
    return round(float(out))


def publish_one(slug, script, mp3, basename):
    """Returns True if a commit was made, False if skipped."""
    show_dir = REPO / "podcasts" / slug
    stub_xml = show_dir / "scripts" / f"{basename}.rss-item.xml"
    stub_msg = show_dir / "scripts" / f"{basename}.commit-msg"
    feed_xml = show_dir / "feed.xml"

    if not mp3.exists():
        log(f"  skip {slug}/{basename}: no MP3 even after gap-fill")
        return False
    if not stub_xml.exists():
        log(f"  skip {slug}/{basename}: no rss-item stub")
        return False
    if not stub_msg.exists():
        log(f"  skip {slug}/{basename}: no commit-msg stub")
        return False

    # Render the RSS item with real length + duration.
    length_bytes = mp3.stat().st_size
    duration_secs = mp3_duration_seconds(mp3)
    item_xml = stub_xml.read_text() \
        .replace("__LENGTH__", str(length_bytes)) \
        .replace("__DURATION__", str(duration_secs))

    # Insert into feed.xml (in memory edit, then write).
    insert_feed_item(feed_xml, item_xml)

    # Upload to R2.
    log(f"  publish_episode.sh {slug} {basename}")
    r = subprocess.run(
        [str(REPO / "scripts" / "publish_episode.sh"), slug, basename],
        cwd=REPO, capture_output=True, text=True,
    )
    if r.returncode != 0:
        log(f"  FAIL: publish_episode.sh rc={r.returncode}")
        if r.stderr:
            log(f"  stderr: {r.stderr[:400]}")
        return False

    commit_msg = stub_msg.read_text().strip()

    add_target = str((show_dir.relative_to(REPO)))
    # Exclude the transient stubs from `git add` via pathspec so they never
    # enter the index. Leaving them on disk until *after* the commit succeeds
    # means a rejected commit (e.g. pre-commit hook) doesn't destroy the
    # commit message the next retry needs.
    #
    # flock so concurrent invocations don't stomp the index. (Not strictly
    # required in this script — we publish serially — but cheap insurance.)
    r = subprocess.run(
        ["flock", GIT_LOCK, "bash", "-c",
         f"git add {add_target} "
         f"':(exclude,glob){add_target}/scripts/*.rss-item.xml' "
         f"':(exclude,glob){add_target}/scripts/*.commit-msg' "
         f"&& git commit -m \"$(cat <<'GITCOMMITEOF'\n{commit_msg}\nGITCOMMITEOF\n)\""],
        cwd=REPO, capture_output=True, text=True,
    )
    if r.returncode != 0:
        log(f"  FAIL: git commit rc={r.returncode}")
        log(f"  stderr: {r.stderr[:400]}")
        return False

    stub_xml.unlink()
    stub_msg.unlink()
    log(f"  committed {slug}/{basename}")
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default=os.environ.get("TTS_BATCH_DATE", datetime.date.today().isoformat()),
                    help="YYYY-MM-DD; defaults to today")
    ap.add_argument("--skip-gap-fill", action="store_true",
                    help="don't try Mistral for missing MP3s")
    ap.add_argument("--skip-push", action="store_true",
                    help="commit but don't push")
    args = ap.parse_args()

    log(f"=== publish_pending.py date={args.date} ===")
    items = discover_pending(args.date)
    log(f"discovered {len(items)} script(s)")
    for slug, _, mp3, base in items:
        log(f"  {slug}/{base} — mp3 {'YES' if mp3.exists() else 'NO'}")

    if not args.skip_gap_fill:
        gap_fill_mistral(items)

    log(f"=== Phase 3: publish ===")
    published = 0
    for slug, script, mp3, base in items:
        if publish_one(slug, script, mp3, base):
            published += 1

    log(f"=== {published}/{len(items)} published ===")

    if published == 0:
        log("nothing to push")
        return 0

    if args.skip_push:
        log("--skip-push: skipping git push")
        return 0

    log("git push")
    r = subprocess.run(["git", "push"], cwd=REPO)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
