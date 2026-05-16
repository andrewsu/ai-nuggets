#!/usr/bin/env python3
"""Validate bioRxiv and arXiv URLs introduced by the staged commit.

Used by .githooks/pre-commit. Pulls every line newly added by this commit
(across staged files), extracts bioRxiv and arXiv preprint URLs, and
verifies each one resolves to a real paper. Catches the two recurring
failure modes:

  1. Wrong bioRxiv DOI prefix — bioRxiv uses 10.1101/ for legacy posts and
     10.64898/ for newer ones; generators that hardcode 10.1101/ on a
     newer DOI yield a real-looking URL that 404s.
  2. Fabricated preprint — URL points at an ID that doesn't exist on the
     server.

Network failures (timeout, DNS, 5xx) are reported as warnings, not
errors — we don't want a flaky bioRxiv to block commits. Only definite
"not found" answers fail the commit. Set GUIDE_SKIP_URL_CHECK=1 to skip.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

BIORXIV_RE = re.compile(
    r"https?://(?:www\.)?biorxiv\.org/content/"
    r"(?P<prefix>10\.[0-9]+)/(?P<id>\d{4}\.\d{2}\.\d{2}\.\d+)(?:v\d+)?"
)
ARXIV_RE = re.compile(
    r"https?://arxiv\.org/abs/(?P<id>\d{4}\.\d{4,5})(?:v\d+)?"
)

TIMEOUT = 8


def newly_added_lines() -> list[str]:
    """Return lines added by the staged diff (no context, no removals)."""
    out = subprocess.check_output(
        ["git", "diff", "--cached", "--no-color", "-U0"],
        text=True,
    )
    added: list[str] = []
    for line in out.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added.append(line[1:])
    return added


def check_biorxiv(prefix: str, paper_id: str) -> tuple[bool, str]:
    """Return (ok, message). ok=False means definite 'not found'."""
    url = f"https://api.biorxiv.org/details/biorxiv/{prefix}/{paper_id}"
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        return True, f"warn: bioRxiv API unreachable ({e}); skipping"
    messages = data.get("messages") or []
    if messages and messages[0].get("status") == "ok" and data.get("collection"):
        return True, "ok"
    # API returned a definite answer: this DOI is not on bioRxiv.
    # Probe the alternate prefix to suggest the fix.
    alt_prefix = "10.64898" if prefix == "10.1101" else "10.1101"
    alt_url = f"https://api.biorxiv.org/details/biorxiv/{alt_prefix}/{paper_id}"
    suggestion = ""
    try:
        with urllib.request.urlopen(alt_url, timeout=TIMEOUT) as resp:
            alt = json.loads(resp.read())
        if (alt.get("messages") or [{}])[0].get("status") == "ok" and alt.get("collection"):
            suggestion = f" — paper exists under prefix {alt_prefix}/, not {prefix}/"
    except Exception:
        pass
    return False, f"bioRxiv DOI {prefix}/{paper_id} not found{suggestion}"


def check_arxiv(paper_id: str) -> tuple[bool, str]:
    url = f"https://arxiv.org/abs/{paper_id}"
    req = urllib.request.Request(url, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            if 200 <= resp.status < 300:
                return True, "ok"
            return False, f"arXiv {paper_id} returned HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, f"arXiv {paper_id} not found (HTTP 404)"
        return True, f"warn: arXiv {paper_id} HTTP {e.code}; skipping"
    except (urllib.error.URLError, TimeoutError) as e:
        return True, f"warn: arXiv unreachable ({e}); skipping"


def main() -> int:
    if os.environ.get("GUIDE_SKIP_URL_CHECK"):
        return 0

    lines = newly_added_lines()
    if not lines:
        return 0

    biorxiv_hits: set[tuple[str, str]] = set()
    arxiv_hits: set[str] = set()
    for line in lines:
        for m in BIORXIV_RE.finditer(line):
            biorxiv_hits.add((m.group("prefix"), m.group("id")))
        for m in ARXIV_RE.finditer(line):
            arxiv_hits.add(m.group("id"))

    if not biorxiv_hits and not arxiv_hits:
        return 0

    errors: list[str] = []
    warnings: list[str] = []
    for prefix, paper_id in sorted(biorxiv_hits):
        ok, msg = check_biorxiv(prefix, paper_id)
        if not ok:
            errors.append(msg)
        elif msg.startswith("warn"):
            warnings.append(msg)
    for paper_id in sorted(arxiv_hits):
        ok, msg = check_arxiv(paper_id)
        if not ok:
            errors.append(msg)
        elif msg.startswith("warn"):
            warnings.append(msg)

    for w in warnings:
        print(f"  {w}", file=sys.stderr)
    for e in errors:
        print(f"  ERROR: {e}", file=sys.stderr)

    if errors:
        print(
            "\nFix the URL(s) and re-stage, or set GUIDE_SKIP_URL_CHECK=1 to "
            "bypass (e.g. offline).",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
