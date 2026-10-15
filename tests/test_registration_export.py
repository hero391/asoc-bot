import sys
import sqlite3
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from openpyxl import load_workbook

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import checkin_app
import bot
import schedule_import
import schedule_handlers
from telegram.ext import ConversationHandler
from texts import DAY_INFO, t


class RegistrationExportTests(unittest.TestCase):
    def setUp(self):
        self.client = checkin_app.app.test_client()

    def authenticate(self):
        with self.client.session_transaction() as session:
            session["staff_authenticated"] = True
            session["csrf_token"] = "test-csrf"

    def test_export_requires_staff_login(self):
        response = self.client.get("/export/registrations.xlsx")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login")

    def test_export_downloads_formatted_attendee_workbook(self):
        self.authenticate()
        registration = {
            "created_at": "2026-10-14 12:59:13",
            "reg_code": "ASOC-0001",
            "status": "confirmed",
            "full_name": "=2+2",
            "role": "doctor",
            "institution": "Addis Ababa University",
            "email": "attendee@example.org",
            "phone": "+251963333388",
            "attendance_mode": "in_person",
            "title": "Dr.",
            "attendance_days": "2026-11-02,2026-11-03",
            "referral_source": "invitation",
            "region": "Addis Ababa",
            "trainee_status": "no",
        }
        with patch.object(
            checkin_app.db,
            "get_registrations_for_export",
            return_value=[registration],
        ):
            response = self.client.get("/export/registrations.xlsx")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.mimetype,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn("ESF-2026-registrations-", response.headers["Content-Disposition"])
        self.assertEqual(response.headers["Cache-Control"], "no-store")

        workbook = load_workbook(BytesIO(response.data), data_only=False)
        self.assertEqual(
            workbook.properties.title,
            "ESF 2026 Comprehensive Stroke Care Symposium Registration List",
        )
        worksheet = workbook["Registrations"]
        self.assertEqual(worksheet.freeze_panes, "A2")
        self.assertEqual(worksheet.auto_filter.ref, "A1:N2")
        self.assertEqual(
            [worksheet.cell(1, col).value for col in range(1, 12)],
            [
                "Timestamp",
                "Title",
                "Full name, including your grandfather’s name.",
                "Profession",
                "Organization",
                "Email",
                "Phone number",
                "Which conference day will you attend",
                "How did you hear about this event",
                "Region",
                "Are you a student, intern, resident, or fellow",
            ],
        )
        self.assertEqual(worksheet["A2"].value.isoformat(), "2026-10-14T15:59:13")
        self.assertEqual(worksheet["C2"].value, "=2+2")
        self.assertEqual(worksheet["C2"].data_type, "s")
        self.assertEqual(worksheet["E2"].value, "Addis Ababa University")
        self.assertEqual(worksheet["G2"].value, "+251963333388")
        self.assertEqual(worksheet["B2"].value, "Dr.")
        self.assertEqual(
            worksheet["H2"].value,
            "Day 1 — Monday, November 2, 2026, Day 2 — Tuesday, November 3, 2026",
        )
        self.assertEqual(
            checkin_app.export_attendance_days("2026-11-01,2026-11-04"),
            "Day 0 — Sunday, November 1, 2026, Day 3 — Wednesday, November 4, 2026",
        )
        self.assertEqual(worksheet["I2"].value, "Invitation from the organizers")
        self.assertEqual(worksheet["J2"].value, "Addis Ababa")
        self.assertEqual(worksheet["K2"].value, "No")
        self.assertEqual(worksheet["L2"].value, "ASOC-0001")
        self.assertEqual(worksheet["D2"].value, "Doctor")
        self.assertEqual(worksheet["N2"].value, "In person")
        self.assertTrue(worksheet["A1"].font.bold)
        self.assertTrue(worksheet["A1"].fill.fgColor.rgb.endswith("145C4C"))

    def test_staff_home_page_offers_excel_export(self):
        self.authenticate()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Download Excel report", response.data)
        self.assertIn(b"/export/registrations.xlsx", response.data)

    def test_schedule_keyboards_offer_back_to_main_menu(self):
        day_list_keyboard = schedule_handlers.days_keyboard("en")
        schedule_day_keyboard = schedule_handlers.day_keyboard(
            "en", 0, "all", 0, 1, ["main"]
        )

        self.assertEqual(
            day_list_keyboard.inline_keyboard[-1][0].callback_data, "menu:home"
        )
        self.assertEqual(
            schedule_day_keyboard.inline_keyboard[-1][0].callback_data, "menu:home"
        )

    def test_schedule_and_registration_only_offer_poster_dates(self):
        self.assertEqual(
            [date for date, _english, _amharic in DAY_INFO],
            ["2026-11-02", "2026-11-03"],
        )
        registration_keyboard = bot.days_keyboard("en", set(), "days")
        self.assertEqual(
            [row[0].text for row in registration_keyboard.inline_keyboard[:-1]],
            ["Day 1 · Mon, Nov 2", "Day 2 · Tue, Nov 3"],
        )
        keyboard = schedule_handlers.days_keyboard("en")
        self.assertEqual(
            [row[0].text for row in keyboard.inline_keyboard[:-1]],
            ["Day 1 · Mon, Nov 2", "Day 2 · Tue, Nov 3"],
        )

    def test_schedule_csv_refreshes_existing_database(self):
        with (
            patch.object(schedule_handlers, "_loaded_schedule_signature", None),
            patch.object(schedule_handlers.db, "count_sessions", return_value=87),
            patch.object(schedule_handlers, "import_csv", return_value=90) as importer,
        ):
            count = schedule_handlers.ensure_schedule_loaded()

        self.assertEqual(count, 90)
        importer.assert_called_once_with(bot.config.SESSIONS_CSV)

    def test_updated_csv_keeps_archived_rows_but_accepts_new_symposium_track(self):
        rows, problems = schedule_import.read_and_check(bot.config.SESSIONS_CSV)

        self.assertEqual(problems, [])
        self.assertIn("2026-11-01", {row["date"] for row in rows})
        self.assertIn("2026-11-04", {row["date"] for row in rows})
        self.assertIn("symposium", {row["track"] for row in rows})

    def test_registered_menu_offers_update_details(self):
        keyboard = bot.main_menu_keyboard("en", registered=True)

        self.assertEqual(
            keyboard.inline_keyboard[-1][0].callback_data, "menu:update"
        )

    def test_legacy_registration_is_detected_as_incomplete(self):
        registration = {
            "title": "",
            "attendance_days": "",
            "referral_source": "",
            "region": "",
            "trainee_status": "",
        }
        self.assertTrue(bot.registration_details_incomplete(registration))
        registration.update(
            {
                "title": "Dr.",
                "attendance_days": "2026-11-02",
                "referral_source": "invitation",
                "region": "Addis Ababa",
                "trainee_status": "no",
            }
        )
        self.assertFalse(bot.registration_details_incomplete(registration))

    def test_bot_registers_all_registration_and_update_conversation_states(self):
        with (
            patch.object(bot.config, "BOT_TOKEN", "123456:test-token"),
            patch.object(bot.config, "check_config"),
            patch.object(bot.db, "init_db"),
            patch.object(bot.schedule_handlers, "ensure_schedule_loaded", return_value=87),
        ):
            application = bot.build_app()

        self.assertIs(application.post_init, bot.set_bot_name)
        conversations = [
            handler
            for handlers in application.handlers.values()
            for handler in handlers
            if isinstance(handler, ConversationHandler)
        ]
        registration = next(handler for handler in conversations if bot.TITLE in handler.states)
        update_details = next(
            handler for handler in conversations if bot.UPDATE_TITLE in handler.states
        )
        self.assertIn(bot.DAYS, registration.states)
        self.assertIn(bot.REFERRAL, registration.states)
        self.assertIn(bot.REGION, registration.states)
        self.assertIn(bot.TRAINEE_CATEGORY, registration.states)
        self.assertIn(bot.UPDATE_DAYS, update_details.states)
        self.assertIn(bot.UPDATE_REGION, update_details.states)
        self.assertIn(bot.UPDATE_TRAINEE_CATEGORY, update_details.states)

    def test_contact_details_are_available_in_both_languages(self):
        for language in ("en", "am"):
            contact = t(language, "contact_info")
            self.assertIn("ethiopiastrokefoundation@gmail.com", contact)
            self.assertIn("+251963333388", contact)
            self.assertIn("+251955235523", contact)

    def test_database_export_query_returns_registration_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "test.db"
            with patch.object(checkin_app.db.config, "DB_PATH", str(database_path)):
                checkin_app.db.init_db()
                checkin_app.db.create_registration(
                    123,
                    {
                        "full_name": "Test Attendee",
                        "phone": "+251963333388",
                        "email": "test@example.org",
                        "role": "doctor",
                        "institution": "Test Hospital",
                        "language": "en",
                        "attendance_mode": "in_person",
                        "title": "Prof.",
                        "attendance_days": "2026-11-01,2026-11-02",
                        "referral_source": "colleague",
                        "region": "Oromia",
                        "trainee_status": "fellow",
                    },
                )

                registrations = checkin_app.db.get_registrations_for_export()

        self.assertEqual(len(registrations), 1)
        self.assertEqual(registrations[0]["full_name"], "Test Attendee")
        self.assertEqual(registrations[0]["institution"], "Test Hospital")
        self.assertEqual(registrations[0]["attendance_mode"], "in_person")
        self.assertEqual(registrations[0]["title"], "Prof.")
        self.assertEqual(
            registrations[0]["attendance_days"], "2026-11-01,2026-11-02"
        )
        self.assertEqual(registrations[0]["referral_source"], "colleague")
        self.assertEqual(registrations[0]["region"], "Oromia")
        self.assertEqual(registrations[0]["trainee_status"], "fellow")

    def test_existing_registration_details_can_be_completed(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "test.db"
            with patch.object(checkin_app.db.config, "DB_PATH", str(database_path)):
                checkin_app.db.init_db()
                checkin_app.db.create_registration(
                    456,
                    {
                        "full_name": "Existing Attendee",
                        "phone": "+251963333388",
                        "email": "existing@example.org",
                        "role": "nurse",
                        "institution": "Test Clinic",
                        "language": "en",
                        "attendance_mode": "virtual",
                        "title": "",
                        "attendance_days": "",
                        "referral_source": "",
                        "region": "",
                        "trainee_status": "",
                    },
                )

                updated = checkin_app.db.update_registration_details(
                    456,
                    {
                        "title": "Dr.",
                        "attendance_days": "2026-11-02,2026-11-04",
                        "referral_source": "social",
                        "region": "Amhara",
                        "trainee_status": "resident",
                    },
                )

        self.assertEqual(updated["title"], "Dr.")
        self.assertEqual(updated["attendance_days"], "2026-11-02,2026-11-04")
        self.assertEqual(updated["referral_source"], "social")
        self.assertEqual(updated["region"], "Amhara")
        self.assertEqual(updated["trainee_status"], "resident")

    def test_legacy_database_gets_blank_optional_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "legacy.db"
            connection = sqlite3.connect(database_path)
            try:
                connection.executescript(
                    """
                    CREATE TABLE users (
                        telegram_id INTEGER PRIMARY KEY,
                        full_name TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        email TEXT NOT NULL,
                        role TEXT NOT NULL,
                        institution TEXT NOT NULL,
                        language TEXT NOT NULL DEFAULT 'en',
                        attendance_mode TEXT NOT NULL,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE TABLE registrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        reg_code TEXT UNIQUE,
                        telegram_id INTEGER UNIQUE NOT NULL,
                        qr_token TEXT,
                        status TEXT NOT NULL DEFAULT 'confirmed',
                        checked_in_at TEXT,
                        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
                    INSERT INTO users (
                        telegram_id, full_name, phone, email, role,
                        institution, attendance_mode
                    ) VALUES (789, 'Legacy Attendee', '+251911111111',
                              'legacy@example.org', 'doctor', 'Old Clinic',
                              'in_person');
                    INSERT INTO registrations (reg_code, telegram_id, qr_token)
                    VALUES ('ASOC-0001', 789, 'legacy-qr-token');
                    """
                )
            finally:
                connection.close()

            with patch.object(checkin_app.db.config, "DB_PATH", str(database_path)):
                checkin_app.db.init_db()
                registration = checkin_app.db.get_registration(789)

        self.assertEqual(registration["title"], "")
        self.assertEqual(registration["attendance_days"], "")
        self.assertEqual(registration["referral_source"], "")
        self.assertEqual(registration["region"], "")
        self.assertEqual(registration["trainee_status"], "")


if __name__ == "__main__":
    unittest.main()
