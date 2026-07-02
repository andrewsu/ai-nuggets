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


def biorxiv_page_reachable(prefix: str, paper_id: str) -> bool | None:
    """Fetch the bioRxiv paper page through the r.jina.ai reader proxy
    (Cloudflare 403s direct HEAD requests) and decide whether it renders
    to a real preprint. r.jina.ai prepends a `Title:` header derived from
    the page's <title> — real paper pages carry the paper title, while
    bioRxiv's 'no such preprint' shell renders as `Title: | bioRxiv` with
    an empty paper name, so that's the discriminator.

    Returns True (real paper), False (bioRxiv shell / no preprint at this
    ID), or None (fetch failed — treat as inconclusive by the caller).
    """
    url = (
        f"https://r.jina.ai/https://www.biorxiv.org/content/"
        f"{prefix}/{paper_id}v1"
    )
    # r.jina.ai 403s clients that don't send a browser-shaped User-Agent,
    # and passes the UA through to the upstream bioRxiv fetch, so a real
    # browser UA also gives the best chance of getting past bioRxiv's own
    # Cloudflare challenge. Matches scripts/fetch_preprint.py.
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/markdown",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as e:
        return None
    title_match = re.search(r"^Title:\s*(.*?)\s*$", body, re.MULTILINE)
    if not title_match:
        return None  # unexpected r.jina.ai shape — don't block the commit
    title = title_match.group(1)
    # bioRxiv "no such preprint" shell renders as `Title: | bioRxiv`
    # (empty paper name, site suffix only). Real papers render as
    # `Title: <paper title>`.
    return bool(title) and not title.startswith("|")


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
    # API returned a definite answer for this prefix: no such DOI.
    # Probe the alternate prefix — if the paper lives there, this is the
    # "wrong prefix" bug the hook was built to catch, and we can fail with
    # a concrete suggested fix.
    alt_prefix = "10.64898" if prefix == "10.1101" else "10.1101"
    alt_url = f"https://api.biorxiv.org/details/biorxiv/{alt_prefix}/{paper_id}"
    try:
        with urllib.request.urlopen(alt_url, timeout=TIMEOUT) as resp:
            alt = json.loads(resp.read())
        if (alt.get("messages") or [{}])[0].get("status") == "ok" and alt.get("collection"):
            return False, (
                f"bioRxiv DOI {prefix}/{paper_id} not found — "
                f"paper exists under prefix {alt_prefix}/, not {prefix}/"
            )
    except Exception:
        pass
    # Neither prefix is in the details API. The API is known to miss
    # records that still render fine on the site (e.g.
    # 10.64898/2026.06.28.735058 was API-invisible for days after
    # posting), so before failing the commit fall back to the paper page
    # itself via r.jina.ai.
    page_status = biorxiv_page_reachable(prefix, paper_id)
    if page_status is True:
        return True, (
            f"warn: bioRxiv API has no record of {prefix}/{paper_id} "
            f"but the paper page renders — accepting"
        )
    if page_status is None:
        return True, (
            f"warn: bioRxiv API has no record of {prefix}/{paper_id} "
            f"and r.jina.ai fallback was unreachable; skipping"
        )
    return False, (
        f"bioRxiv DOI {prefix}/{paper_id} not found "
        f"(missing from details API and paper page did not render)"
    )


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
