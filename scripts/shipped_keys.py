#!/usr/bin/env python3
"""Dedup-ledger helper for the per-show `state/shipped.jsonl` files.

The ledger records every item a show has already aired, one JSON object per
episode. It exists so a run can drop candidates it has covered before. It is
NOT reference material: it grows ~1.7 KB per episode, so the runner should
never read it into context. Pipe candidate keys through this script instead —
the ledger stays on disk and only the survivors come back.

Filtering (the common case). One candidate per line on stdin, either a bare
key or `key<TAB>title`. Unshipped lines are echoed verbatim to stdout; the
summary and any warnings go to stderr, so it composes in a pipeline:

    printf 'doi:10.1038/x\tSome title\n' | scripts/shipped_keys.py receptor-and-reason

Keys are matched after normalization, so these all collide: `doi:10.1038/X`
and `doi:10.1038/x`; `arxiv:2608.01234v2` and `arxiv:2608.01234`; a bioRxiv
DOI (`doi:10.64898/2026.08.21.745777`) and its bare form
(`biorxiv:2026.08.21.745777`); a URL with and without `www.`, a query string,
a fragment, or utm_* params; `nct:NCT01234567` in any case.

When titles are supplied, a candidate whose *title* matches a shipped title
is dropped even if its key differs. That is the Nature-family RSS trap: an
article's accepted-manuscript DOI is shipped, then RSS surfaces it days later
under a different DOI and it looks fresh. Use --keep-title-matches to pass
those through (marked on stderr) when you know it is a genuine follow-up.

Appending (after picks are final). Reads the same `key<TAB>title` lines, so
the filter's output format feeds straight back in:

    scripts/shipped_keys.py receptor-and-reason --append \
        --basename 2026-08-28-receptor-and-reason < picks.tsv

The whole ledger must parse before anything is written. If any line is
corrupt the append is refused (exit 3) and the file is left untouched, so the
existing data can be recovered by hand.

Exit codes:
  0  success
  2  usage / show-not-found error
  3  ledger corrupt (append refused)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl, urlunsplit, urlencode

REPO = Path(__file__).resolve().parent.parent
PODCASTS = REPO / "podcasts"

KNOWN_SCHEMES = ("doi", "arxiv", "biorxiv", "medrxiv", "url", "nct")
DOI_URL_RE = re.compile(r"^https?://(dx\.)?doi\.org/", re.I)
ARXIV_URL_RE = re.compile(r"^https?://arxiv\.org/(abs|pdf)/", re.I)
ARXIV_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
ARXIV_VERSION_RE = re.compile(r"v\d+$")
# bioRxiv / medRxiv DOI suffix, e.g. 2026.08.21.745777
PREPRINT_SUFFIX_RE = re.compile(r"\d{4}\.\d{2}\.\d{2}\.\d{6,}")
TRACKING_RE = re.compile(r"^(utm_|fbclid$|gclid$|mc_[ce]id$|ref$)", re.I)
NONWORD_RE = re.compile(r"[^a-z0-9]+")
NCT_RE = re.compile(r"nct\d{8}", re.I)


def die(msg: str, code: int = 2) -> None:
    print(f"shipped_keys: {msg}", file=sys.stderr)
    raise SystemExit(code)


def ledger_path(slug: str) -> Path:
    show_dir = PODCASTS / slug
    if not (show_dir / "show.toml").exists():
        die(f"no such show: {slug} (expected {show_dir}/show.toml)")
    return show_dir / "state" / "shipped.jsonl"


def variants(raw: str) -> set[str]:
    """Every normalized form a key can be matched under.

    Two keys are the same item if their variant sets intersect. bioRxiv is the
    reason this returns a set rather than one string: the ledger stores those
    as `doi:`, but a candidate pulled from the API may arrive as `biorxiv:`,
    and only the shared DOI suffix connects them.
    """
    k = raw.strip()
    if not k:
        return set()

    scheme, sep, val = k.partition(":")
    scheme, val = scheme.lower(), val.strip()
    if not sep or scheme not in KNOWN_SCHEMES:
        # Bare key — infer the scheme from its shape.
        val = k
        if DOI_URL_RE.match(k) or k.lower().startswith("10."):
            scheme = "doi"
        elif ARXIV_URL_RE.match(k) or ARXIV_ID_RE.match(k):
            scheme = "arxiv"
        elif k.lower().startswith(("http://", "https://")):
            scheme = "url"
        else:
            return {k.lower()}

    if scheme == "doi":
        v = DOI_URL_RE.sub("", val).lower().rstrip("/")
        forms = {f"doi:{v}"}
        m = PREPRINT_SUFFIX_RE.search(v)
        if m:  # bioRxiv/medRxiv DOI — also match the bare-id form
            forms.add(f"preprint:{m.group(0)}")
        return forms

    if scheme == "arxiv":
        v = ARXIV_URL_RE.sub("", val).lower().rstrip("/")
        v = v[:-4] if v.endswith(".pdf") else v
        return {f"arxiv:{ARXIV_VERSION_RE.sub('', v)}"}

    if scheme in ("biorxiv", "medrxiv"):
        m = PREPRINT_SUFFIX_RE.search(val)
        return {f"preprint:{m.group(0)}"} if m else {f"{scheme}:{val.lower()}"}

    if scheme == "nct":
        m = NCT_RE.search(val)
        return {f"nct:{m.group(0).lower()}"} if m else {f"nct:{val.lower()}"}

    # url — normalize the incidental differences, keep the meaningful ones.
    parts = urlsplit(val)
    if not parts.netloc:
        return {f"url:{val.lower().rstrip('/')}"}
    host = parts.netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    query = urlencode([(a, b) for a, b in parse_qsl(parts.query) if not TRACKING_RE.match(a)])
    path = parts.path.rstrip("/") or "/"
    base = (parts.scheme.lower(), host, path)
    # Also match the query-free form: PROMPT.md tells the runner to strip query
    # strings, but candidates often arrive carrying them.
    return {"url:" + urlunsplit((*base, query, "")),
            "url:" + urlunsplit((*base, "", ""))}


def norm_title(t: str) -> str:
    return NONWORD_RE.sub(" ", (t or "").lower()).strip()


def read_ledger(path: Path) -> tuple[list[dict], list[str]]:
    """Return (records, corrupt_line_reports). Missing file is an empty set."""
    if not path.exists():
        return [], []
    records, corrupt = [], []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            corrupt.append(f"line {n}: {e}")
            continue
        if not isinstance(rec, dict) or not isinstance(rec.get("items"), list):
            corrupt.append(f"line {n}: not an episode record")
            continue
        records.append(rec)
    return records, corrupt


def index(records: list[dict]) -> tuple[dict[str, dict], dict[str, dict]]:
    """Map every key variant, and every normalized title, to its episode."""
    by_key, by_title = {}, {}
    for rec in records:
        for item in rec["items"]:
            where = {"date": rec.get("date", "?"), "key": item.get("key", ""),
                     "title": item.get("title", "")}
            for v in variants(item.get("key", "")):
                by_key.setdefault(v, where)
            t = norm_title(item.get("title", ""))
            if t:
                by_title.setdefault(t, where)
    return by_key, by_title


def parse_candidates(stream) -> list[tuple[str, str, str]]:
    """Read `key` or `key<TAB>title` lines -> [(line, key, title)]."""
    out = []
    for line in stream:
        line = line.rstrip("\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, title = line.partition("\t")
        out.append((line, key.strip(), title.strip()))
    return out


def cmd_filter(args, path: Path) -> int:
    records, corrupt = read_ledger(path)
    if corrupt:
        # Per PROMPT.md: log the gap, treat as empty for the run, never
        # overwrite. Filtering still runs so the episode can be produced.
        for c in corrupt:
            print(f"shipped_keys: CORRUPT LEDGER {path}: {c}", file=sys.stderr)
        print("shipped_keys: treating ledger as EMPTY for this run; nothing was "
              "written; --append will refuse until this is repaired", file=sys.stderr)
        records = []

    by_key, by_title = index(records)
    candidates = parse_candidates(sys.stdin)

    seen: set[str] = set()
    kept = dupes = key_hits = title_hits = 0
    for line, key, title in candidates:
        forms = variants(key)
        if not forms:
            print(f"shipped_keys: skipping line with no key: {line!r}", file=sys.stderr)
            continue
        if forms & seen:
            dupes += 1
            continue
        seen |= forms

        hit = next((by_key[v] for v in forms if v in by_key), None)
        if hit:
            key_hits += 1
            if title and norm_title(title) != norm_title(hit["title"]):
                print(f"shipped_keys: WARNING key collision, titles differ: {key}\n"
                      f"  candidate: {title}\n"
                      f"  shipped {hit['date']}: {hit['title']}", file=sys.stderr)
            continue

        thit = by_title.get(norm_title(title)) if title else None
        if thit:
            title_hits += 1
            verb = "keeping" if args.keep_title_matches else "dropping"
            print(f"shipped_keys: TITLE MATCH under a different key ({verb}): {key}\n"
                  f"  shipped {thit['date']} as {thit['key']}: {thit['title']}",
                  file=sys.stderr)
            if not args.keep_title_matches:
                continue

        kept += 1
        print(line)

    print(f"shipped_keys: {len(candidates)} candidates -> {kept} fresh "
          f"({key_hits} already shipped, {title_hits} title matches, {dupes} "
          f"repeated in input) against {len(by_key)} ledger keys from "
          f"{len(records)} episodes", file=sys.stderr)
    return 0


def cmd_stats(args, path: Path) -> int:
    records, corrupt = read_ledger(path)
    by_key, _ = index(records)
    items = sum(len(r["items"]) for r in records)
    uniq = len({i.get("key", "").strip().lower() for r in records for i in r["items"]})
    span = f"{records[0].get('date')} -> {records[-1].get('date')}" if records else "empty"
    print(f"{path.relative_to(REPO)}: {len(records)} episodes, {items} items, "
          f"{uniq} unique keys ({len(by_key)} match forms), {span}"
          + (f", {len(corrupt)} CORRUPT LINES" if corrupt else ""))
    for c in corrupt:
        print(f"  corrupt: {c}", file=sys.stderr)
    return 0


def cmd_verify(args, path: Path) -> int:
    _, corrupt = read_ledger(path)
    if corrupt:
        for c in corrupt:
            print(f"shipped_keys: CORRUPT {path}: {c}", file=sys.stderr)
        return 3
    print(f"shipped_keys: {path.relative_to(REPO)} parses clean")
    return 0


def cmd_append(args, path: Path) -> int:
    records, corrupt = read_ledger(path)
    if corrupt:
        for c in corrupt:
            print(f"shipped_keys: CORRUPT {path}: {c}", file=sys.stderr)
        die("refusing to append to a corrupt ledger; repair it by hand first", 3)

    candidates = parse_candidates(sys.stdin)
    if not candidates:
        die("nothing to append: stdin had no `key<TAB>title` lines")

    by_key, _ = index(records)
    items, seen = [], set()
    for line, key, title in candidates:
        forms = variants(key)
        if not forms:
            die(f"unparseable key on line: {line!r}")
        if forms & seen:
            print(f"shipped_keys: WARNING dropping key repeated in this "
                  f"record: {key}", file=sys.stderr)
            continue
        seen |= forms
        if not title:
            print(f"shipped_keys: WARNING no title for {key} (append the "
                  f"episode title after a tab)", file=sys.stderr)
        hit = next((by_key[v] for v in forms if v in by_key), None)
        if hit:
            print(f"shipped_keys: WARNING {key} was already shipped "
                  f"{hit['date']} — appending anyway, but check the run's "
                  f"dedup step", file=sys.stderr)
        items.append({"key": key, "title": title})

    record = {"date": args.date, "basename": args.basename, "items": items}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    total = len(records) + 1
    print(f"shipped_keys: appended {len(items)} keys for {args.basename} "
          f"({total} episodes in ledger)", file=sys.stderr)
    return 0


def main() -> int:
    p = argparse.ArgumentParser(
        description="Filter candidates against, or append to, a show's dedup ledger.")
    p.add_argument("slug", help="show slug, e.g. receptor-and-reason")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--append", action="store_true",
                      help="append one episode record built from stdin")
    mode.add_argument("--stats", action="store_true",
                      help="print ledger size without dumping keys")
    mode.add_argument("--verify", action="store_true",
                      help="parse-check the ledger; exit 3 if corrupt")
    p.add_argument("--basename", help="episode basename (required with --append)")
    p.add_argument("--date", default=date.today().isoformat(),
                   help="episode date, YYYY-MM-DD (default: today)")
    p.add_argument("--keep-title-matches", action="store_true",
                   help="pass through candidates that match a shipped title "
                        "under a different key, instead of dropping them")
    args = p.parse_args()

    path = ledger_path(args.slug)
    if args.stats:
        return cmd_stats(args, path)
    if args.verify:
        return cmd_verify(args, path)
    if args.append:
        if not args.basename:
            die("--append requires --basename (e.g. 2026-08-28-receptor-and-reason)")
        return cmd_append(args, path)
    return cmd_filter(args, path)


if __name__ == "__main__":
    sys.exit(main())
