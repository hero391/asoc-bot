"""Load the conference program from a CSV file into the database.

Edit data/sessions.csv (in Excel: Save As -> "CSV UTF-8"), then run:

    python schedule_import.py            # uses data/sessions.csv
    python schedule_import.py my_file.csv

The whole file is checked first. If anything is wrong you get a list of
problems with the row numbers, and the database is NOT changed.
"""
import csv
import re
import sys

import config
import db
from texts import KIND_ICONS, PROGRAM_DAY_INFO, TRACKS

REQUIRED = ["date", "start", "end", "track", "kind", "title_en"]
OPTIONAL = ["group", "title_am", "speaker"]
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VALID_DATES = {d[0] for d in PROGRAM_DAY_INFO}
VALID_TRACKS = set(TRACKS) | {"common"}
VALID_KINDS = set(KIND_ICONS)


def read_and_check(path: str):
    """Return (rows_ready_for_db, list_of_problems)."""
    problems, rows = [], []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        header = [h.strip() for h in (reader.fieldnames or [])]
        missing = [c for c in REQUIRED if c not in header]
        if missing:
            return [], [f"Missing column(s): {', '.join(missing)}"]

        for number, raw in enumerate(reader, start=2):  # row 1 is the header
            r = {k.strip(): (v or "").strip() for k, v in raw.items() if k}
            if not any(r.values()):
                continue  # empty line

            def bad(msg):
                problems.append(f"Row {number}: {msg}")

            if not DATE_RE.match(r["date"]) or r["date"] not in VALID_DATES:
                bad(f"date '{r['date']}' must be one of {sorted(VALID_DATES)}")
            if not TIME_RE.match(r["start"]):
                bad(f"start '{r['start']}' must look like 08:15 (24-hour)")
            if not TIME_RE.match(r["end"]):
                bad(f"end '{r['end']}' must look like 08:20 (24-hour)")
            if TIME_RE.match(r["start"]) and TIME_RE.match(r["end"]) and r["end"] <= r["start"]:
                bad(f"end {r['end']} must be later than start {r['start']}")
            if r["track"] not in VALID_TRACKS:
                bad(f"track '{r['track']}' must be one of {sorted(VALID_TRACKS)}")
            if r["kind"] not in VALID_KINDS:
                bad(f"kind '{r['kind']}' must be one of {sorted(VALID_KINDS)}")
            if not r["title_en"]:
                bad("title_en is empty")

            rows.append(
                {
                    "date": r["date"],
                    "start": r["start"],
                    "end": r["end"],
                    "track": r["track"],
                    "kind": r["kind"],
                    "group_name": r.get("group", ""),
                    "title_en": r["title_en"],
                    "title_am": r.get("title_am", ""),
                    "speaker": r.get("speaker", ""),
                }
            )
    return rows, problems


def import_csv(path: str = None) -> int:
    """Validate and load. Returns the number of sessions saved."""
    path = path or config.SESSIONS_CSV
    rows, problems = read_and_check(path)
    if problems:
        raise ValueError("Problems in " + path + ":\n - " + "\n - ".join(problems))
    db.init_db()
    db.replace_sessions(rows)
    return len(rows)


if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else config.SESSIONS_CSV
    try:
        total = import_csv(file_path)
    except (ValueError, FileNotFoundError) as err:
        raise SystemExit(f"\nERROR: {err}\n")

    print(f"\nLoaded {total} sessions from {file_path}\n")
    for date, en, _am in PROGRAM_DAY_INFO:
        count = len(db.get_sessions(date))
        print(f"   {en}: {count} items")
    print("\nRestart the bot to be safe, then try /schedule in Telegram.")