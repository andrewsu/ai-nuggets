#!/usr/bin/env python3
"""Daily audit: scan each podcast's cron.log for the day's run and email a summary.

Designed to run from cron a few hours after run_all_shows.sh has finished —
late enough that even worst-case retry ladders (6 attempts × ~3-min sleep +
per-attempt Claude runs) are complete, early enough that the report lands
before the user starts looking for episodes.

For each podcast (directory under podcasts/<slug>/ containing PROMPT.md):
  1. Parse the show's logs/cron.log for events on the audit date.
  2. Cross-check that an mp3 was actually produced
     (episodes/<date>*.mp3) — exit-0 is not proof of an episode, since
     the Haiku-fallback rung of the model ladder has been seen to
     exit 0 without writing a file.
  3. Classify as SUCCESS / FAILED / NO_RUN / HUNG and count retries.

Email goes out via AWS SES (boto3), reusing the verified-sender pattern
from coPI: SES_FROM_EMAIL, AWS_REGION, AWS_ACCESS_KEY_ID,
AWS_SECRET_ACCESS_KEY. If creds are absent, the summary is printed to
stdout (dev mode) — convenient for testing.

Usage:
  daily_audit.py                 # audit today (host local date)
  daily_audit.py --date 2026-06-22
  daily_audit.py --dry-run       # print summary, don't send
"""

import argparse
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PODCASTS = REPO / "podcasts"

# Lines emitted by run_all_shows.sh that we scan for. Examples:
#   === 2026-06-23T02:00:01-07:00 start receptor-and-reason ===
#   === 2026-06-23T02:09:42-07:00 done  receptor-and-reason (exit 0) ===
#   === 2026-06-23T02:09:42-07:00 done  receptor-and-reason (exit 0) (retry 2, --model claude-sonnet-4-6) ===
#   === 2026-06-22T03:42:30-07:00 no episode produced for receptor-and-reason; retrying in 180s ===
#   === 2026-06-22T03:57:49-07:00 FAILED: no episode produced for receptor-and-reason after all retries ===
#   === 2026-06-22T03:40:11-07:00 AUP-refusal detected for receptor-and-reason; retrying in 180s ===
EVENT_RE = re.compile(
    r"^===\s+(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})\s+"
    r"(?P<rest>.+?)\s+===\s*$"
)


def parse_ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s)


def show_slugs() -> list[str]:
    return sorted(
        p.parent.name for p in PODCASTS.glob("*/PROMPT.md") if p.is_file()
    )


def events_for_date(log_path: Path, target_date: dt.date) -> list[tuple[dt.datetime, str]]:
    """Return (timestamp, message) tuples whose local-date matches target_date."""
    if not log_path.exists():
        return []
    out: list[tuple[dt.datetime, str]] = []
    for line in log_path.read_text(errors="replace").splitlines():
        m = EVENT_RE.match(line)
        if not m:
            continue
        ts = parse_ts(m.group("ts"))
        if ts.astimezone().date() != target_date:
            continue
        out.append((ts, m.group("rest")))
    return out


def committed_feed_source(feed_path: Path) -> str | None:
    """Return the HEAD-committed contents of feed_path, or None if git can't
    resolve it (not a git repo, path never committed, etc.).

    publish_pending.py inserts the RSS item into the working-tree feed.xml
    *before* running the commit, so the working tree can carry a "published"
    item that the commit — and therefore `git push`, and therefore the URL
    subscribers fetch — never received. In 2026-07 a stale pre-commit-hook
    failure blocked publish commits for four straight days while the working
    tree kept growing. Checking HEAD instead of the working tree is what
    catches that.
    """
    try:
        rel = feed_path.relative_to(REPO)
    except ValueError:
        return None
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{rel.as_posix()}"],
            cwd=REPO, capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def unpublished_basenames(feed_path: Path, mp3s: list[Path]) -> list[str]:
    """Return the subset of mp3 basenames (stems) that aren't in the committed
    feed.xml.

    publish_pending.py writes the basename into the RSS <guid> and enclosure
    URL, so a substring test is enough. We check the HEAD-committed version
    rather than the working tree because the working tree lies during a
    publish outage (see committed_feed_source docstring). If git can't tell
    us what's committed, fall back to the working tree — better than
    erroring out of the daily audit.
    """
    feed_src = committed_feed_source(feed_path)
    if feed_src is None:
        if not feed_path.exists():
            return [m.stem for m in mp3s]
        try:
            feed_src = feed_path.read_text(errors="replace")
        except OSError:
            return [m.stem for m in mp3s]
    return [m.stem for m in mp3s if m.stem not in feed_src]


def classify(slug: str, target_date: dt.date) -> dict:
    log_path = PODCASTS / slug / "logs" / "cron.log"
    evts = events_for_date(log_path, target_date)
    episodes_dir = PODCASTS / slug / "episodes"
    feed_path = PODCASTS / slug / "feed.xml"
    pause_state = PODCASTS / slug / "state" / "pause.json"
    mp3s = sorted(episodes_dir.glob(f"{target_date.isoformat()}*.mp3"))
    unpublished = unpublished_basenames(feed_path, mp3s)

    starts = [(ts, msg) for ts, msg in evts if msg.startswith(f"start {slug}")]
    dones = [(ts, msg) for ts, msg in evts if msg.startswith(f"done  {slug}")]
    failed = [(ts, msg) for ts, msg in evts if msg.startswith(f"FAILED:")]
    no_episode = [(ts, msg) for ts, msg in evts if msg.startswith(f"no episode produced for {slug}")]
    aup = [(ts, msg) for ts, msg in evts if msg.startswith(f"AUP-refusal detected for {slug}")]

    # The mp3 is the canonical local artifact, but the subscriber-visible
    # artifact is a matching item in feed.xml. Both must be present for
    # SUCCESS. Historically the audit checked only the mp3, which silently
    # green-lit a two-day publish outage in 2026-07 when a pre-commit hook
    # cascade blocked every commit in publish_pending.py — mp3s landed on
    # disk but no feed ever updated. Split those cases apart with
    # NOT_PUBLISHED. A show with state/pause.json and no attempted run
    # (paused_still_cold from scripts/check_activity.py) is PAUSED, not
    # NO_RUN — it was skipped by design because the subscriber has stopped
    # downloading.
    if mp3s and not unpublished:
        status = "SUCCESS"
    elif mp3s:
        status = "NOT_PUBLISHED"
    elif pause_state.exists() and not starts:
        status = "PAUSED"
    elif not starts:
        status = "NO_RUN"
    elif failed:
        status = "FAILED"
    elif starts and not dones:
        status = "HUNG"
    else:
        status = "NO_EPISODE"

    first_start = starts[0][0] if starts else None
    last_event = max((ts for ts, _ in evts), default=None)
    retries = max(0, len(starts) - 1)

    return {
        "slug": slug,
        "status": status,
        "first_start": first_start,
        "last_event": last_event,
        "retries": retries,
        "aup_count": len(aup),
        "no_episode_count": len(no_episode),
        "mp3s": [p.name for p in mp3s],
        "unpublished": unpublished,
        "log_path": log_path,
    }


STATUS_ICON = {
    "SUCCESS": "OK  ",
    "PAUSED":  "PAUS",
    "FAILED": "FAIL",
    "HUNG": "HUNG",
    "NO_RUN": "MISS",
    "NO_EPISODE": "NOEP",
    "NOT_PUBLISHED": "UNPB",
}


def fmt_time(ts: dt.datetime | None) -> str:
    if ts is None:
        return "--:--"
    return ts.astimezone().strftime("%H:%M")


def render_summary(reports: list[dict], target_date: dt.date) -> tuple[str, str]:
    # PAUSED is intentional (subscriber went cold; scripts/check_activity.py
    # skipped generation by design), so it doesn't count as "needs attention"
    # for the daily subject line or the diagnostics tail.
    bad = [r for r in reports if r["status"] not in ("SUCCESS", "PAUSED")]
    subject = f"[ai-nuggets] {target_date.isoformat()} audit: "
    if not bad:
        subject += f"all {len(reports)} shows OK"
    else:
        subject += f"{len(bad)}/{len(reports)} shows need attention"

    lines = [f"Daily audit {target_date.isoformat()}", ""]
    for r in reports:
        icon = STATUS_ICON.get(r["status"], r["status"])
        extras = []
        if r["retries"]:
            extras.append(f"{r['retries']} retr{'y' if r['retries'] == 1 else 'ies'}")
        if r["aup_count"]:
            extras.append(f"{r['aup_count']} AUP")
        if r["no_episode_count"]:
            extras.append(f"{r['no_episode_count']} no-ep")
        if r["unpublished"]:
            extras.append(f"{len(r['unpublished'])} not in feed")
        extra = f" ({', '.join(extras)})" if extras else ""
        when = fmt_time(r["last_event"])
        lines.append(f"  {icon}  {r['slug']:30s}  {when} PT{extra}")

    lines.append("")
    if bad:
        lines.append("Diagnostics for non-SUCCESS shows:")
        lines.append("")
        for r in bad:
            lines.append(f"--- {r['slug']} ({r['status']}) ---")
            # NOT_PUBLISHED means the mp3 exists but the item never made it
            # into feed.xml — cron.log will read like a success, so the
            # useful signal is the missing basenames plus the tail of the
            # nightly run_all_shows-*.log where Phase 3 lives.
            if r["status"] == "NOT_PUBLISHED":
                for b in r["unpublished"]:
                    lines.append(f"  mp3 on disk but not in feed.xml: {b}")
                lines.append(
                    "  check the most recent logs/run_all_shows-*.log for "
                    "Phase 3 (publish_pending.py) errors"
                )
            else:
                try:
                    tail = r["log_path"].read_text(errors="replace").splitlines()[-40:]
                except FileNotFoundError:
                    tail = ["(log file not found)"]
                lines.extend(tail)
            lines.append("")
    body = "\n".join(lines) + "\n"
    return subject, body


def fetch_download_stats(target_date: dt.date) -> str | None:
    """Return a per-show 7-day rolling download summary from the Cloudflare
    D1 'podcast' database, or None if not configured.

    Window is anchored on target_date: [target_date - 6 days, target_date]
    inclusive (7 calendar days). Bot UAs and HEAD probes are excluded so the
    numbers match real listener fetches.

    Reads CLOUDFLARE_API_TOKEN from env (already sourced from .env by the
    cron wrapper). Account id is auto-discovered via the /accounts endpoint
    on the first call; override with CLOUDFLARE_ACCOUNT_ID if the token sees
    more than one account. Database id is fixed to the 'podcast' DB created
    in worker/wrangler.toml; override with CLOUDFLARE_D1_PODCAST_DATABASE_ID
    if it's ever recreated.
    """
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        return None

    db_id = os.environ.get(
        "CLOUDFLARE_D1_PODCAST_DATABASE_ID",
        "458dc35f-a6be-4c8d-95df-7e30229e02de",
    )
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

    def _cf(path: str, body: dict | None = None) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": f"Bearer {token}"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            f"https://api.cloudflare.com/client/v4{path}",
            data=data, headers=headers,
            method="POST" if body is not None else "GET",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())

    try:
        if not account_id:
            accounts = _cf("/accounts")
            results = accounts.get("result") or []
            if not results:
                return "Download stats: no Cloudflare accounts visible to token"
            account_id = results[0]["id"]

        date_iso = target_date.isoformat()
        sql = (
            "SELECT podcast, COUNT(*) AS downloads, "
            "COUNT(DISTINCT ip_hash) AS uniq "
            "FROM requests "
            f"WHERE ts >= unixepoch('{date_iso}', '-6 days') "
            f"  AND ts <  unixepoch('{date_iso}', '+1 day') "
            "  AND is_bot = 0 AND method = 'GET' "
            "GROUP BY podcast ORDER BY downloads DESC"
        )
        payload = _cf(
            f"/accounts/{account_id}/d1/database/{db_id}/query",
            {"sql": sql},
        )
    except urllib.error.HTTPError as e:
        return f"Download stats: HTTP {e.code} ({e.reason})"
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        return f"Download stats: fetch failed ({e})"

    if not payload.get("success"):
        return f"Download stats: D1 query failed ({payload.get('errors')})"

    try:
        rows = payload["result"][0]["results"]
    except (KeyError, IndexError):
        return "Download stats: unexpected D1 response shape"

    lines = [
        f"Download stats — 7 days through {target_date.isoformat()} "
        "(non-bot GETs):"
    ]
    if not rows:
        lines.append("  (no downloads recorded)")
        return "\n".join(lines)

    lines.append(f"  {'show':<25} {'downloads':>10} {'unique':>8}")
    total_dl = 0
    for r in rows:
        lines.append(
            f"  {r['podcast']:<25} {r['downloads']:>10} {r['uniq']:>8}"
        )
        total_dl += r["downloads"]
    lines.append(f"  {'TOTAL':<25} {total_dl:>10}")
    return "\n".join(lines)


def fetch_mistral_usage(target_date: dt.date) -> str | None:
    """Return a short text block describing month-to-date Mistral usage, or
    None if there's nothing to report.

    Calls GET https://api.mistral.ai/api/admin/usage?month=MM&year=YYYY with
    MISTRAL_ADMIN_API_KEY (a workspace/inference key is rejected — the
    endpoint requires an Admin-scoped key). On any failure, returns a single
    diagnostic line rather than raising — usage stats are nice-to-have, not
    a reason to block the audit email.
    """
    key = os.environ.get("MISTRAL_ADMIN_API_KEY")
    if not key:
        return None  # silently omit when not configured

    url = (
        "https://api.mistral.ai/api/admin/usage"
        f"?month={target_date.month:02d}&year={target_date.year}"
    )
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return f"Mistral usage: HTTP {e.code} ({e.reason})"
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
        return f"Mistral usage: fetch failed ({e})"

    # The schema buries cost data under sections like audio.models[model][ws]
    # = [ { ...open-shape entry... } ]. Field names for the dollar value have
    # varied (cost / total_cost / amount / spent) across observed payloads,
    # so walk recursively and sum any field whose name hints at money. Same
    # idea for token/character counters under the audio section.
    money_keys = {"cost", "total_cost", "amount", "spent", "price_total", "total_price"}
    token_keys = {"tokens", "total_tokens", "token_count"}
    char_keys = {"characters", "total_characters", "audio_characters", "character_count"}
    sec_keys = {"seconds", "audio_seconds", "total_seconds", "duration_seconds"}

    def sum_keys(node, names: set[str]) -> float:
        if isinstance(node, dict):
            total = 0.0
            for k, v in node.items():
                if k in names and isinstance(v, (int, float)):
                    total += float(v)
                else:
                    total += sum_keys(v, names)
            return total
        if isinstance(node, list):
            return sum(sum_keys(x, names) for x in node)
        return 0.0

    sections = ("chat", "completion", "audio", "ocr", "connectors", "fine_tuning", "libraries_api")
    sym = payload.get("currency_symbol") or payload.get("currency") or "$"
    total_cost = sum_keys(payload, money_keys)
    lines = [f"Mistral usage — month-to-date ({target_date.year}-{target_date.month:02d}):"]
    lines.append(f"  Total billed: {sym}{total_cost:.2f}")
    for s in sections:
        if s in payload:
            sc = sum_keys(payload[s], money_keys)
            if sc > 0:
                extra = ""
                if s == "audio":
                    chars = sum_keys(payload[s], char_keys)
                    secs = sum_keys(payload[s], sec_keys)
                    bits = []
                    if chars:
                        bits.append(f"{int(chars):,} chars")
                    if secs:
                        bits.append(f"{int(secs):,} s")
                    if bits:
                        extra = "  (" + ", ".join(bits) + ")"
                lines.append(f"  {s:14s} {sym}{sc:.2f}{extra}")
    vibe = payload.get("vibe_usage")
    if isinstance(vibe, (int, float)) and vibe:
        lines.append(f"  vibe_usage     {vibe}")
    return "\n".join(lines)


def send_email(subject: str, body: str) -> None:
    sender = (
        os.environ.get("SES_FROM_EMAIL")
        or os.environ.get("SES_SENDER_EMAIL")
        or "notifications@copi.science"
    )
    recipient = os.environ.get("AUDIT_TO_EMAIL", "asu@scripps.edu")
    region = os.environ.get("AWS_REGION", "us-east-1")

    if not (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")):
        print(f"[dev] no AWS creds; would email {recipient} from {sender}")
        print(f"[dev] subject: {subject}")
        print(body)
        return

    try:
        import boto3
    except ImportError:
        print("ERROR: boto3 not installed. Run: pip install --user boto3", file=sys.stderr)
        print(f"[dev fallback] subject: {subject}")
        print(body)
        sys.exit(2)

    client = boto3.client("ses", region_name=region)
    client.send_email(
        Source=sender,
        Destination={"ToAddresses": [recipient]},
        Message={
            "Subject": {"Data": subject, "Charset": "UTF-8"},
            "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
        },
    )
    print(f"sent to {recipient}: {subject}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--date", help="YYYY-MM-DD (default: today, host local)")
    ap.add_argument("--dry-run", action="store_true", help="print, don't send")
    args = ap.parse_args()

    if args.date:
        target_date = dt.date.fromisoformat(args.date)
    else:
        target_date = dt.datetime.now().date()

    reports = [classify(slug, target_date) for slug in show_slugs()]
    subject, body = render_summary(reports, target_date)

    downloads_block = fetch_download_stats(target_date)
    if downloads_block:
        body = body + "\n" + downloads_block + "\n"

    mistral_block = fetch_mistral_usage(target_date)
    if mistral_block:
        body = body + "\n" + mistral_block + "\n"

    if args.dry_run:
        print(f"subject: {subject}")
        print(body)
        return 0

    send_email(subject, body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
