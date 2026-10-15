"""Database layer (SQLite). One file, no server needed."""
import sqlite3
from contextlib import contextmanager

import config
from qr_utils import make_token


@contextmanager
def get_conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                telegram_id     INTEGER PRIMARY KEY,
                full_name       TEXT NOT NULL,
                phone           TEXT NOT NULL,
                email           TEXT NOT NULL,
                role            TEXT NOT NULL,
                institution     TEXT NOT NULL,
                language        TEXT NOT NULL DEFAULT 'en',
                attendance_mode TEXT NOT NULL,
                created_at      TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS registrations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                reg_code    TEXT UNIQUE,
                telegram_id INTEGER UNIQUE NOT NULL REFERENCES users(telegram_id),
                qr_token    TEXT,
                status      TEXT NOT NULL DEFAULT 'confirmed',
                checked_in_at TEXT,
                created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                date       TEXT NOT NULL,      -- 2026-11-03
                start      TEXT NOT NULL,      -- 08:15 (24-hour)
                end        TEXT NOT NULL,      -- 08:20
                track      TEXT NOT NULL,      -- main, workshop, nursing, ... or common
                kind       TEXT NOT NULL,      -- talk, break, meal, ...
                group_name TEXT NOT NULL DEFAULT '',
                title_en   TEXT NOT NULL,
                title_am   TEXT NOT NULL DEFAULT '',
                speaker    TEXT NOT NULL DEFAULT ''
            );
            CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date, start);

            CREATE TABLE IF NOT EXISTS attendance (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                registration_id INTEGER NOT NULL REFERENCES registrations(id),
                attendance_date TEXT NOT NULL,
                checked_in_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (registration_id, attendance_date)
            );
            CREATE INDEX IF NOT EXISTS idx_attendance_date
                ON attendance(attendance_date);
            """
        )
        registration_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(registrations)").fetchall()
        }
        if "checked_in_at" not in registration_columns:
            conn.execute("ALTER TABLE registrations ADD COLUMN checked_in_at TEXT")


def get_registration(telegram_id: int):
    """Return one row with user + registration info, or None."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT r.reg_code, r.qr_token, r.status,
                   u.full_name, u.phone, u.email, u.role,
                   u.institution, u.language, u.attendance_mode
            FROM registrations r
            JOIN users u ON u.telegram_id = r.telegram_id
            WHERE r.telegram_id = ?
            """,
            (telegram_id,),
        ).fetchone()


def create_registration(telegram_id: int, data: dict):
    """Save the user, create the registration, return the saved row."""
    existing = get_registration(telegram_id)
    if existing:
        return existing

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO users (telegram_id, full_name, phone, email, role,
                               institution, language, attendance_mode)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                telegram_id,
                data["full_name"],
                data["phone"],
                data["email"],
                data["role"],
                data["institution"],
                data["language"],
                data["attendance_mode"],
            ),
        )
        cur = conn.execute(
            "INSERT INTO registrations (telegram_id) VALUES (?)", (telegram_id,)
        )
        reg_id = cur.lastrowid
        reg_code = f"ASOC-{reg_id:04d}"
        conn.execute(
            "UPDATE registrations SET reg_code = ?, qr_token = ? WHERE id = ?",
            (reg_code, make_token(reg_code), reg_id),
        )

    return get_registration(telegram_id)


def count_registrations() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM registrations").fetchone()[0]


def get_registrations_for_export():
    """Return registration and attendee details for the staff export."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT r.created_at, r.reg_code, r.status, u.full_name, u.role,
                   u.institution, u.email, u.phone, u.attendance_mode
            FROM registrations r
            JOIN users u ON u.telegram_id = r.telegram_id
            ORDER BY r.created_at, r.id
            """
        ).fetchall()


def get_registration_by_code(reg_code: str, attendance_date: str):
    """Return the minimal attendee details needed for staff QR verification."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT r.id AS registration_id, r.reg_code, r.qr_token, r.status,
                   a.attendance_date, a.checked_in_at,
                   u.full_name, u.role, u.institution, u.attendance_mode
            FROM registrations r
            JOIN users u ON u.telegram_id = r.telegram_id
            LEFT JOIN attendance a
                ON a.registration_id = r.id AND a.attendance_date = ?
            WHERE r.reg_code = ?
            """,
            (attendance_date, reg_code),
        ).fetchone()


def check_in_registration(reg_code: str, attendance_date: str):
    """Check in a confirmed registration once per day."""
    with get_conn() as conn:
        cursor = conn.execute(
            """
            INSERT OR IGNORE INTO attendance (registration_id, attendance_date)
            SELECT id, ? FROM registrations
            WHERE reg_code = ? AND status = 'confirmed'
            """,
            (attendance_date, reg_code),
        )
        attendee = conn.execute(
            """
            SELECT r.id AS registration_id, r.reg_code, r.qr_token, r.status,
                   a.attendance_date, a.checked_in_at,
                   u.full_name, u.role, u.institution, u.attendance_mode
            FROM registrations r
            JOIN users u ON u.telegram_id = r.telegram_id
            LEFT JOIN attendance a
                ON a.registration_id = r.id AND a.attendance_date = ?
            WHERE r.reg_code = ?
            """,
            (attendance_date, reg_code),
        ).fetchone()
        return attendee, cursor.rowcount == 1


# ===================== Part 2: schedule =====================
def set_language(telegram_id: int, lang: str):
    with get_conn() as conn:
        conn.execute(
            "UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id)
        )


def replace_sessions(rows: list):
    """Delete the old program and save the new one (all or nothing)."""
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions")
        conn.executemany(
            """
            INSERT INTO sessions (date, start, end, track, kind, group_name,
                                  title_en, title_am, speaker)
            VALUES (:date, :start, :end, :track, :kind, :group_name,
                    :title_en, :title_am, :speaker)
            """,
            rows,
        )


def count_sessions() -> int:
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]


def get_sessions(date: str, track: str = None):
    """All sessions of a day. With a track: that track + shared rows (breaks, lunch)."""
    with get_conn() as conn:
        if track:
            return conn.execute(
                """SELECT * FROM sessions
                   WHERE date = ? AND (track = ? OR track = 'common')
                   ORDER BY start, end, track, id""",
                (date, track),
            ).fetchall()
        return conn.execute(
            "SELECT * FROM sessions WHERE date = ? ORDER BY start, end, track, id",
            (date,),
        ).fetchall()


def get_tracks(date: str):
    """Tracks that exist on a day (without the shared 'common' rows)."""
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT DISTINCT track FROM sessions
               WHERE date = ? AND track != 'common' ORDER BY track""",
            (date,),
        ).fetchall()
    return [r["track"] for r in rows]


def get_sessions_at(date: str, hhmm: str):
    """Sessions running at this moment (start <= now < end)."""
    with get_conn() as conn:
        return conn.execute(
            """SELECT * FROM sessions
               WHERE date = ? AND start <= ? AND end > ?
               ORDER BY start, track, id""",
            (date, hhmm, hhmm),
        ).fetchall()


def get_next_sessions(date: str, hhmm: str):
    """Everything that starts at the next start time after now."""
    with get_conn() as conn:
        nxt = conn.execute(
            "SELECT MIN(start) FROM sessions WHERE date = ? AND start > ?",
            (date, hhmm),
        ).fetchone()[0]
        if not nxt:
            return []
        return conn.execute(
            "SELECT * FROM sessions WHERE date = ? AND start = ? ORDER BY track, id",
            (date, nxt),
        ).fetchall()