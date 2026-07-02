#!/usr/bin/env python3
"""Report per-show pause/resume verdicts from Cloudflare D1 activity.

Read-only. Queries D1 for MAX(ts) per podcast (non-bot GETs), reads each
show's state/pause.json if present, and prints a JSON verdict object to
stdout. Does NOT mutate any state — a later --apply pass (or the runner)
is responsible for acting on the verdicts.

Verdicts:
  active              normal generation
  pause_now           not currently paused, but should be
  paused_still_cold   currently paused, no new activity since paused_at
  resume              currently paused, new GET arrived after paused_at

Bootstrapping: a show with no D1 GETs ever (MAX(ts) IS NULL) is treated
as 'active' — you can't be away if you were never here.

Env:
  CLOUDFLARE_API_TOKEN                required (cron wrapper sources .env)
  CLOUDFLARE_ACCOUNT_ID               optional; auto-discovered if unset
  CLOUDFLARE_D1_PODCAST_DATABASE_ID   optional; defaults to prod DB id
  PAUSE_THRESHOLD_DAYS                optional; default 14

Exit codes:
  0  success (verdicts printed)
  2  configuration error (missing token)
  3  D1 query error
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PODCASTS = REPO / "podcasts"

DEFAULT_DB_ID = "458dc35f-a6be-4c8d-95df-7e30229e02de"
DEFAULT_THRESHOLD_DAYS = 14


def list_slugs() -> list[str]:
    return sorted(
        p.parent.name for p in PODCASTS.glob("*/PROMPT.md") if p.is_file()
    )


def _cf(token: str, path: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4{path}",
        data=data,
        headers=headers,
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def resolve_account_id(token: str) -> str:
    env = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if env:
        return env
    accounts = _cf(token, "/accounts")
    results = accounts.get("result") or []
    if not results:
        raise RuntimeError("no Cloudflare accounts visible to token")
    return results[0]["id"]


def fetch_last_get_by_podcast(
    token: str, account_id: str, db_id: str
) -> dict[str, int]:
    """Return {podcast: max_ts_unix} for every podcast with a non-bot GET."""
    sql = (
        "SELECT podcast, MAX(ts) AS last_get "
        "FROM requests "
        "WHERE is_bot = 0 AND method = 'GET' "
        "GROUP BY podcast"
    )
    payload = _cf(
        token,
        f"/accounts/{account_id}/d1/database/{db_id}/query",
        {"sql": sql},
    )
    if not payload.get("success"):
        raise RuntimeError(f"D1 query failed: {payload.get('errors')}")
    rows = payload["result"][0]["results"]
    return {r["podcast"]: r["last_get"] for r in rows}


def read_pause_state(slug: str) -> dict | None:
    p = REPO / "podcasts" / slug / "state" / "pause.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def verdict_for(
    now: int,
    last_get: int | None,
    pause_state: dict | None,
    threshold_secs: int,
) -> dict:
    days_since = None if last_get is None else round((now - last_get) / 86400, 2)
    base = {
        "last_get_ts": last_get,
        "days_since_last_get": days_since,
        "paused_at": pause_state["paused_at"] if pause_state else None,
    }
    if pause_state is None:
        if last_get is None:
            return {"verdict": "active", **base}
        if (now - last_get) >= threshold_secs:
            return {"verdict": "pause_now", **base}
        return {"verdict": "active", **base}
    paused_at = pause_state["paused_at"]
    if last_get is not None and last_get > paused_at:
        return {"verdict": "resume", **base}
    return {"verdict": "paused_still_cold", **base}


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--threshold-days",
        type=int,
        default=int(os.environ.get("PAUSE_THRESHOLD_DAYS", DEFAULT_THRESHOLD_DAYS)),
        help="days of no downloads before pause (default: 14)",
    )
    parser.add_argument(
        "--slug",
        help="only report on this slug (default: all shows)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "tsv"),
        default="json",
        help="output format (default: json). tsv emits one line per show: "
        "slug<TAB>verdict<TAB>days_since_last_get<TAB>paused_at",
    )
    args = parser.parse_args()

    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print("CLOUDFLARE_API_TOKEN not set", file=sys.stderr)
        return 2

    db_id = os.environ.get("CLOUDFLARE_D1_PODCAST_DATABASE_ID", DEFAULT_DB_ID)

    try:
        account_id = resolve_account_id(token)
        last_gets = fetch_last_get_by_podcast(token, account_id, db_id)
    except (urllib.error.URLError, RuntimeError, TimeoutError) as e:
        print(f"D1 query failed: {e}", file=sys.stderr)
        return 3

    now = int(time.time())
    threshold_secs = args.threshold_days * 86400

    slugs = [args.slug] if args.slug else list_slugs()
    per_show = {
        slug: verdict_for(
            now,
            last_gets.get(slug),
            read_pause_state(slug),
            threshold_secs,
        )
        for slug in slugs
    }

    if args.format == "tsv":
        for slug, info in per_show.items():
            print(
                slug,
                info["verdict"],
                "" if info["days_since_last_get"] is None else info["days_since_last_get"],
                "" if info["paused_at"] is None else info["paused_at"],
                sep="\t",
            )
        return 0

    print(json.dumps(
        {"generated_at": now, "threshold_days": args.threshold_days, "shows": per_show},
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
