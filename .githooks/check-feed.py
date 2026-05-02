#!/usr/bin/env python3
"""Validate one RSS feed read from stdin.

Used by .githooks/pre-commit. Reports feed XML well-formedness and pubDate
weekday correctness. Exit 0 = clean, 1 = error (with messages on stderr).
"""
import datetime
import re
import sys
import xml.etree.ElementTree as ET

WD = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu",
      4: "Fri", 5: "Sat", 6: "Sun"}
MONTHS = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
          "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "<stdin>"
    text = sys.stdin.read()
    errors: list[str] = []

    try:
        ET.fromstring(text)
    except ET.ParseError as e:
        errors.append(f"  {label}: XML parse error: {e}")

    for m in re.finditer(r"<pubDate>(\w{3}), (\d{2}) (\w{3}) (\d{4})", text):
        claimed, day, mon, year = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
        try:
            actual = WD[datetime.date(year, MONTHS[mon], day).weekday()]
        except (KeyError, ValueError) as e:
            errors.append(f"  {label}: bad pubDate '{m.group(0)}': {e}")
            continue
        if claimed != actual:
            errors.append(
                f"  {label}: pubDate '{claimed}, {day:02d} {mon} {year}' "
                f"-> weekday should be '{actual}'"
            )

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
