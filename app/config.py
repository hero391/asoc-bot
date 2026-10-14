import os
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / "venv" / "Scripts" / ".env")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
QR_SECRET = os.getenv("QR_SECRET", "")
CHECKIN_PASSWORD = os.getenv("CHECKIN_PASSWORD", "")
CHECKIN_COOKIE_SECURE = os.getenv("CHECKIN_COOKIE_SECURE", "").lower() in {
    "1",
    "true",
    "yes",
}


def project_path(value: str) -> str:
    path = Path(value)
    return str(path if path.is_absolute() else PROJECT_ROOT / path)


DB_PATH = project_path(os.getenv("DB_PATH", "aso.db"))
SESSIONS_CSV = project_path(os.getenv("SESSIONS_CSV", "data/sessions.csv"))

# Conference time zone (Addis Ababa, UTC+3)
TIMEZONE = ZoneInfo("Africa/Addis_Ababa")

# FOR TESTING ONLY: pretend it is this moment, e.g.  FAKE_NOW=2026-11-03 10:15
# Leave empty (or delete the line in .env) when the bot goes live.
FAKE_NOW = os.getenv("FAKE_NOW", "").strip()

CONFERENCE_NAME = "African Stroke Organization Conference 2026"
CONFERENCE_THEME = "Stroke Care Transformation in Africa"
CONFERENCE_DATES = "November 1-4, 2026"
CONFERENCE_VENUE = "Adawa Victory Hall, Addis Ababa"


def check_config():
    """Stop early with a clear message if something is missing."""
    problems = []
    if not BOT_TOKEN or "PASTE" in BOT_TOKEN:
        problems.append("BOT_TOKEN is missing in your .env file")
    if not QR_SECRET or "PASTE" in QR_SECRET:
        problems.append("QR_SECRET is missing in your .env file")
    if problems:
        raise SystemExit("Config error:\n - " + "\n - ".join(problems))