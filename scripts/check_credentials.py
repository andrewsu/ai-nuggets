#!/usr/bin/env python3
"""Report how much life is left in the Claude CLI's OAuth refresh token.

Read-only. Reads ~/.claude/.credentials.json and reports on
claudeAiOauth.refreshTokenExpiresAt, which each interactive `/login` sets
~28 days out and which CANNOT be renewed from cron. When it lapses,
`claude -p` prints "Failed to authenticate: OAuth session expired and
could not be refreshed" and exits 0 — indistinguishable from an empty run
unless you go looking (see the 2026-09-15 outage: six shows, 36 identical
failures, 65 minutes, zero episodes).

Used three ways:
  - run_all_shows.sh calls this pre-flight and aborts Phase 1 on EXPIRED
    rather than burning the retry ladder on every show;
  - daily_audit.py imports credential_note() to put the warning in the
    daily email while there's still runway;
  - run it by hand any time to see the date.

Verdicts (stdout, one line):
  OK <days> days left (expires <iso>)
  WARN <days> days left (expires <iso>)
  EXPIRED <days> days ago (expired <iso>)

Exit codes:
  0   OK — plenty of runway
  10  WARN — inside --warn-days, run /login soon
  20  EXPIRED, or credentials missing/malformed — runs will fail
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

DEFAULT_CREDENTIALS = Path.home() / ".claude" / ".credentials.json"
# Env override so run_all_shows.sh and daily_audit.py can be dialled
# together without passing --warn-days through both call sites.
DEFAULT_WARN_DAYS = int(os.environ.get("CRED_WARN_DAYS", 5))

# Two short lines so both the CLI output and the indented audit-email note
# stay inside 80 columns.
LOGIN_HINT = (
    "Fix: run `claude` on the pipeline host, type /login, and complete the\n"
    "browser flow. Nothing in cron can renew it."
)


def _indent(text: str, pad: str) -> str:
    return ("\n" + pad).join(text.split("\n"))


def read_expiry(path: Path = DEFAULT_CREDENTIALS) -> dt.datetime:
    """Return refreshTokenExpiresAt as a local-time datetime.

    Raises ValueError with a human-readable reason if the file is missing,
    unreadable, or lacks a usable field.
    """
    try:
        payload = json.loads(path.read_text())
    except FileNotFoundError:
        raise ValueError(f"{path} not found — has anyone ever logged in on this host?")
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path} unreadable: {exc}")

    oauth = payload.get("claudeAiOauth")
    if not isinstance(oauth, dict):
        raise ValueError(f"{path} has no claudeAiOauth object")
    raw = oauth.get("refreshTokenExpiresAt")
    if not isinstance(raw, (int, float)):
        raise ValueError(f"{path} has no numeric claudeAiOauth.refreshTokenExpiresAt")
    # Field is epoch milliseconds.
    return dt.datetime.fromtimestamp(raw / 1000)


def classify(
    path: Path = DEFAULT_CREDENTIALS, warn_days: int = DEFAULT_WARN_DAYS
) -> tuple[str, float, str]:
    """Return (verdict, days_left, detail). Never raises.

    verdict is "OK", "WARN", or "EXPIRED"; days_left is negative once the
    token has lapsed, and 0.0 when the credentials can't be read at all.
    """
    try:
        expires = read_expiry(path)
    except ValueError as exc:
        return "EXPIRED", 0.0, str(exc)

    days = (expires - dt.datetime.now()).total_seconds() / 86400.0
    iso = expires.isoformat(timespec="seconds")
    if days <= 0:
        return "EXPIRED", days, f"expired {iso}"
    if days < warn_days:
        return "WARN", days, f"expires {iso}"
    return "OK", days, f"expires {iso}"


def credential_note(
    path: Path = DEFAULT_CREDENTIALS, warn_days: int = DEFAULT_WARN_DAYS
) -> str | None:
    """A short multi-line note for the daily audit email, or None when the
    token has plenty of runway and there's nothing worth saying."""
    verdict, days, detail = classify(path, warn_days)
    if verdict == "OK":
        return None
    if verdict == "WARN":
        return (
            f"NOTE: Claude OAuth session expires in {days:.1f} days ({detail}).\n"
            f"      Nightly runs hard-fail after that — every show reports\n"
            f"      no_output and nothing publishes.\n"
            f"      {_indent(LOGIN_HINT, '      ')}"
        )
    when = f"{abs(days):.1f} days ago" if days else "unknown"
    return (
        f"ALERT: Claude OAuth session is EXPIRED ({detail}, {when}).\n"
        f"       Nightly runs cannot produce anything until this is fixed.\n"
        f"       {_indent(LOGIN_HINT, '       ')}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        default=DEFAULT_CREDENTIALS,
        help=f"credentials file (default: {DEFAULT_CREDENTIALS})",
    )
    parser.add_argument(
        "--warn-days",
        type=int,
        default=DEFAULT_WARN_DAYS,
        help=f"warn when fewer than this many days remain "
        f"(default: {DEFAULT_WARN_DAYS}, env CRED_WARN_DAYS)",
    )
    args = parser.parse_args()

    verdict, days, detail = classify(args.credentials, args.warn_days)
    if verdict == "EXPIRED" and not days:
        print(f"EXPIRED unreadable: {detail}")
        return 20
    if verdict == "EXPIRED":
        print(f"EXPIRED {abs(days):.1f} days ago ({detail})")
        return 20
    print(f"{verdict} {days:.1f} days left ({detail})")
    return 10 if verdict == "WARN" else 0


if __name__ == "__main__":
    sys.exit(main())
