#!/usr/bin/env python3
"""Scaffold a new podcast under podcasts/<slug>/.

Usage:
    python3 scripts/new_show.py <slug> --title "Display Title" \\
        [--description "..."] [--owner "Name <email>"] [--host "Nigel"]

Creates podcasts/<slug>/ with show.toml, PROMPT.md, README.md, an empty
feed.xml skeleton, and empty episodes/ scripts/ logs/ directories.

Refuses to overwrite an existing show directory. After scaffolding:

  1. Edit podcasts/<slug>/PROMPT.md to fill in the audience and search strategy.
  2. Add <slug> to worker/wrangler.toml ALLOWED_PODCASTS, redeploy the Worker.
  3. Decide TTS voice: edit [tts.primary] / [tts.fallback] in show.toml.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PODCASTS_DIR = REPO_ROOT / "podcasts"

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")

SHOW_TOML_TEMPLATE = """\
slug          = "{slug}"
title         = "{title}"
description   = "{description}"
host          = "{host}"
owner         = "{owner}"
podcast_slug  = "{slug}"

[paths]
prompt   = "PROMPT.md"
feed     = "feed.xml"
episodes = "episodes"
scripts  = "scripts"
logs     = "logs"

[rss]
base_url = "https://github.com/andrewsu/ai-nuggets/raw/main"
link     = "https://github.com/andrewsu/ai-nuggets"

# TTS providers. Edit to match this show's voice. Supported providers:
# "mistral", "elevenlabs".
[tts.primary]
provider = "elevenlabs"
voice    = "hpp4J3VqNfWAUOO0d1Us"
model    = "eleven_flash_v2_5"

[tts.primary.settings]
speed            = 1.1
stability        = 0.5
similarity_boost = 0.75
"""

PROMPT_TEMPLATE = """\
You are creating a personalized podcast called "{title}" (slug:
`{slug}`). It lives under `podcasts/{slug}/`.

# 1. Audience

(Who is this podcast for? Role, interests, what they care about, what they
already know.)

## What they like

-

## What to avoid

-

## Past feedback

-

# 2. Search strategy

(Where should the AI look for stories? Sources, queries, cadence.)

# 3. Format

- 3–5 sentences for the main summary; punchy, opinionated.
- Real, verified URLs only.

# 4. TTS & distribution

Voice config lives in `show.toml`. API keys in repo-root `.env`. Don't write
your own TTS code — use `gen_tts.py --show {slug}`.

# 5. Daily execution

1. Write script to `podcasts/{slug}/scripts/YYYY-MM-DD-slug.md` with a
   `## Script` heading.
2. Generate audio:
   ```
   python3 gen_tts.py --show {slug} \\
     podcasts/{slug}/scripts/YYYY-MM-DD-slug.md \\
     podcasts/{slug}/episodes/YYYY-MM-DD-slug.mp3
   ```
3. Add a new `<item>` to `podcasts/{slug}/feed.xml` with real byte size and
   ffprobe duration. Enclosure URLs point at the Worker.
4. `git add -A && git commit -m 'Episode: <title>' && git push`
"""

README_TEMPLATE = """\
# {title}

{description}

**Subscribe:**
```
https://raw.githubusercontent.com/andrewsu/ai-nuggets/main/podcasts/{slug}/feed.xml
```

See `PROMPT.md` for the editorial brief, `show.toml` for technical
configuration.
"""

FEED_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{title}</title>
    <description>{description}</description>
    <link>https://github.com/andrewsu/ai-nuggets</link>
    <language>en-us</language>
    <itunes:author>{host}</itunes:author>
    <itunes:owner>
      <itunes:name>{owner_name}</itunes:name>
    </itunes:owner>
    <itunes:explicit>false</itunes:explicit>
    <itunes:category text="Technology"/>
  </channel>
</rss>
"""


def parse_owner(owner: str) -> str:
    """Strip an email from `Name <email>` to get just the name."""
    m = re.match(r"^\s*(.+?)\s*<.*>\s*$", owner)
    return m.group(1) if m else owner


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", help="lowercase, hyphen-separated, e.g. 'my-new-show'")
    ap.add_argument("--title", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--host", default="Nigel")
    ap.add_argument("--owner", default="", help="e.g. 'Jane Doe <jane@example.com>'")
    args = ap.parse_args()

    if not SLUG_RE.match(args.slug):
        print(f"ERROR: slug {args.slug!r} must match {SLUG_RE.pattern}", file=sys.stderr)
        return 2

    show_dir = PODCASTS_DIR / args.slug
    if show_dir.exists():
        print(f"ERROR: {show_dir} already exists", file=sys.stderr)
        return 2

    show_dir.mkdir(parents=True)
    (show_dir / "episodes").mkdir()
    (show_dir / "scripts").mkdir()
    (show_dir / "logs").mkdir()

    fmt = dict(
        slug=args.slug,
        title=args.title,
        description=args.description,
        host=args.host,
        owner=args.owner,
        owner_name=parse_owner(args.owner),
    )

    (show_dir / "show.toml").write_text(SHOW_TOML_TEMPLATE.format(**fmt))
    (show_dir / "PROMPT.md").write_text(PROMPT_TEMPLATE.format(**fmt))
    (show_dir / "README.md").write_text(README_TEMPLATE.format(**fmt))
    (show_dir / "feed.xml").write_text(FEED_TEMPLATE.format(**fmt))

    print(f"Scaffolded {show_dir}")
    print(f"\nNext steps:")
    print(f"  1. Edit {show_dir}/PROMPT.md")
    print(f"  2. Edit {show_dir}/show.toml (especially [tts.primary])")
    print(f"  3. Add '{args.slug}' to ALLOWED_PODCASTS in worker/wrangler.toml")
    print(f"  4. Redeploy Worker: (cd worker && npm run deploy)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
