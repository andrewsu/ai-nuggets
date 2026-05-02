#!/usr/bin/env python3
"""Rewrite <enclosure> URLs in a podcast feed.xml to point at the Worker.

Usage:
    python3 scripts/update_feed_for_worker.py \\
        --worker-url https://podcast.<sub>.workers.dev \\
        --podcast biomedical-agentic-ai \\
        --user-id andrew \\
        --feed podcasts/biomedical-agentic-ai/feed.xml \\
        [--dry-run]

For each <enclosure url="..."> element, replaces the URL with:
    <worker-url>/p/<podcast>/u/<user-id>/<basename-without-extension>.mp3

The basename is derived from whatever path the existing URL ends with, so this
works regardless of whether the current enclosures point at GitHub raw, R2, or
some prior Worker URL.

Idempotent: re-running with the same args is a no-op.
"""
import argparse
import difflib
import re
import sys

ENCLOSURE_RE = re.compile(r'(<enclosure\b[^>]*\burl=")([^"]+)(")', re.IGNORECASE)
MP3_BASENAME_RE = re.compile(r'/([^/]+?)\.mp3$', re.IGNORECASE)


def rewrite(text: str, worker_url: str, podcast: str, user_id: str) -> tuple[str, int]:
    base = worker_url.rstrip("/")
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        prefix, old_url, suffix = m.group(1), m.group(2), m.group(3)
        bm = MP3_BASENAME_RE.search(old_url)
        if not bm:
            print(f"WARN: could not extract mp3 basename from {old_url!r}; leaving as-is", file=sys.stderr)
            return m.group(0)
        basename = bm.group(1)
        new_url = f"{base}/p/{podcast}/u/{user_id}/{basename}.mp3"
        if new_url != old_url:
            count += 1
        return f"{prefix}{new_url}{suffix}"

    new_text = ENCLOSURE_RE.sub(repl, text)
    return new_text, count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--worker-url", required=True, help="e.g. https://podcast.<sub>.workers.dev")
    ap.add_argument("--podcast", required=True, help="podcast slug, e.g. biomedical-agentic-ai")
    ap.add_argument("--user-id", required=True, help="per-listener token, free-form")
    ap.add_argument("--feed", required=True, help="path to feed.xml")
    ap.add_argument("--dry-run", action="store_true", help="print unified diff instead of writing")
    args = ap.parse_args()

    with open(args.feed, "r", encoding="utf-8") as f:
        original = f.read()

    rewritten, changed = rewrite(original, args.worker_url, args.podcast, args.user_id)

    if args.dry_run:
        diff = difflib.unified_diff(
            original.splitlines(keepends=True),
            rewritten.splitlines(keepends=True),
            fromfile=args.feed,
            tofile=f"{args.feed} (rewritten)",
            n=1,
        )
        sys.stdout.writelines(diff)
        print(f"\n[dry-run] would change {changed} enclosure URL(s)")
        return 0

    if changed == 0:
        print(f"No changes needed; {args.feed} already points at the Worker (or has no enclosures).")
        return 0

    with open(args.feed, "w", encoding="utf-8") as f:
        f.write(rewritten)
    print(f"Updated {changed} enclosure URL(s) in {args.feed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
