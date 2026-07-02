#!/usr/bin/env python3
"""Write a goodbye-episode script + RSS/commit stubs + state/pause.json for a
show whose subscriber has stopped downloading. See scripts/check_activity.py
for the pause verdict this handles.

The three stub files are the same triple every Phase-1 Claude run writes
(see podcasts/PIPELINE.md 'SKIP_TTS mode') — putting them on disk before
Phase 1 skips this show lets the normal Phase 2 (Garibaldi batch TTS) and
Phase 3 (publish_pending.py) publish the goodbye episode without any
custom publish path.

Files written:
  podcasts/<slug>/scripts/<date>-goodbye.md
  podcasts/<slug>/scripts/<date>-goodbye.rss-item.xml
  podcasts/<slug>/scripts/<date>-goodbye.commit-msg
  podcasts/<slug>/state/pause.json

Refuses to run if any of those already exist (avoids double-publish on
rerun; delete them by hand to force a rewrite).

Usage:
  prepare_goodbye.py --slug scripps-biomed-brief
  prepare_goodbye.py --slug foo --date 2026-07-15
"""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PODCASTS = REPO / "podcasts"

GOODBYE_SCRIPT = (
    "I see you haven't been listening. No problem — once you start "
    "accessing the podcast again, we'll resume generating your daily "
    "podcast. Talk to you soon."
)

# Kept generic across shows so the goodbye reads the same for everyone.
RSS_TITLE = "Paused — download an episode to resume your daily briefing"
RSS_BODY = (
    "Your daily briefing has been paused because no downloads have been "
    "detected in about two weeks. As soon as you download an episode, "
    "generation will automatically resume."
)


def extract_user_id(feed_xml: Path) -> str:
    """Read the user token from the show's existing feed enclosures.

    Each show's feed has enclosure URLs of the form
    https://podcast.<sub>.workers.dev/p/<slug>/u/<user>/<basename>.mp3 —
    that <user> is the per-listener token the Worker uses to key requests.
    """
    src = feed_xml.read_text()
    m = re.search(r'<enclosure\s+url="[^"]*/u/([^/"]+)/', src)
    if not m:
        raise RuntimeError(
            f"no enclosure URL with /u/<user>/ segment in {feed_xml} — "
            "cannot derive the per-listener token"
        )
    return m.group(1)


def extract_worker_base(feed_xml: Path) -> str:
    """Return the Worker origin (scheme + host) from the first enclosure URL."""
    src = feed_xml.read_text()
    m = re.search(r'<enclosure\s+url="(https?://[^/]+)/p/', src)
    if not m:
        raise RuntimeError(f"no Worker origin in {feed_xml} enclosures")
    return m.group(1)


def extract_channel_title(feed_xml: Path) -> str:
    """Return the show's <channel><title>...</title>."""
    src = feed_xml.read_text()
    m = re.search(r"<channel>.*?<title>(.*?)</title>", src, re.DOTALL)
    if not m:
        raise RuntimeError(f"no <channel><title> in {feed_xml}")
    return m.group(1).strip()


def build_rss_item(slug: str, basename: str, user: str, worker_base: str) -> str:
    """RSS <item> with __LENGTH__ / __DURATION__ tokens per PIPELINE.md."""
    pub_date = email.utils.format_datetime(
        dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    )
    enclosure_url = f"{worker_base}/p/{slug}/u/{user}/{basename}.mp3"
    link = f"https://github.com/andrewsu/ai-nuggets/tree/main/podcasts/{slug}"
    return (
        "<item>\n"
        f"    <title>{RSS_TITLE}</title>\n"
        f"    <description>{RSS_BODY}</description>\n"
        f"    <link>{link}</link>\n"
        f'    <guid isPermaLink="false">{basename}</guid>\n'
        f"    <pubDate>{pub_date}</pubDate>\n"
        f'    <enclosure url="{enclosure_url}" length="__LENGTH__" type="audio/mpeg"/>\n'
        "    <itunes:duration>__DURATION__</itunes:duration>\n"
        f"    <itunes:summary>{RSS_BODY}</itunes:summary>\n"
        "</item>\n"
    )


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--slug", required=True)
    ap.add_argument(
        "--date",
        default=dt.date.today().isoformat(),
        help="YYYY-MM-DD; defaults to today (host local date)",
    )
    args = ap.parse_args()

    show_dir = PODCASTS / args.slug
    if not show_dir.is_dir():
        print(f"no such show: {show_dir}", file=sys.stderr)
        return 2

    feed_xml = show_dir / "feed.xml"
    scripts_dir = show_dir / "scripts"
    state_dir = show_dir / "state"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)

    basename = f"{args.date}-goodbye"
    script_path = scripts_dir / f"{basename}.md"
    rss_stub = scripts_dir / f"{basename}.rss-item.xml"
    msg_stub = scripts_dir / f"{basename}.commit-msg"
    pause_state = state_dir / "pause.json"

    for existing in (script_path, rss_stub, msg_stub):
        if existing.exists():
            print(
                f"refusing to overwrite existing {existing.relative_to(REPO)} "
                "(delete it manually if you want to regenerate)",
                file=sys.stderr,
            )
            return 3

    user = extract_user_id(feed_xml)
    worker_base = extract_worker_base(feed_xml)
    show_title = extract_channel_title(feed_xml)

    script_path.write_text(GOODBYE_SCRIPT + "\n")
    rss_stub.write_text(build_rss_item(args.slug, basename, user, worker_base))
    msg_stub.write_text(
        f"Episode: {show_title} paused ({args.date}) — no downloads in ~14 days\n"
    )
    pause_state.write_text(
        json.dumps(
            {"paused_at": int(time.time()), "goodbye_episode_id": basename},
            indent=2,
        )
        + "\n"
    )

    print(basename)
    return 0


if __name__ == "__main__":
    sys.exit(main())
