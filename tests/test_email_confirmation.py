import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

import config
import bot
import email_utils


class RegistrationConfirmationEmailTests(unittest.TestCase):
    def setUp(self):
        self.registration = {
            "full_name": "Aster Example",
            "reg_code": "ASOC-0042",
            "email": "attendee@example.org",
            "role": "doctor",
            "institution": "Addis Ababa University",
            "attendance_mode": "in_person",
            "attendance_days": "2026-11-02,2026-11-03",
            "qr_token": "ASOC-0042.signature",
        }

    def test_confirmation_contains_event_details_and_qr_attachment(self):
        with (
            patch.object(config, "EMAIL_FROM_ADDRESS", "bot@example.org"),
            patch.object(
                config,
                "EMAIL_FROM_NAME",
                "ESF 2026 Comprehensive Stroke Care Symposium",
            ),
        ):
            message = email_utils.registration_confirmation(self.registration)

        self.assertEqual(
            message["Subject"], "Registration confirmed | ESF 2026 | ASOC-0042"
        )
        self.assertEqual(message["To"], "attendee@example.org")
        self.assertEqual(
            message["From"],
            "ESF 2026 Comprehensive Stroke Care Symposium <bot@example.org>",
        )
        body = message.get_body(preferencelist=("plain",)).get_content()
        self.assertIn("November 2 & 3, 2026", body)
        self.assertIn("Day 1 — Monday, November 2, 2026", body)
        self.assertIn("Day 2 — Tuesday, November 3, 2026", body)
        self.assertIn("Adwa Memorial Museum Multi Purpose Hall", body)
        self.assertIn("registration QR code is attached", body)
        qr_attachment = next(
            attachment
            for attachment in message.iter_attachments()
            if attachment.get_filename() == "ESF-2026-registration-QR.png"
        )
        self.assertEqual(qr_attachment.get_content_type(), "image/png")
        self.assertTrue(qr_attachment.get_payload(decode=True).startswith(b"\x89PNG"))

    def test_confirmation_uses_tls_and_authenticated_smtp(self):
        server = MagicMock()
        server_context = MagicMock()
        server_context.__enter__.return_value = server

        with (
            patch.object(config, "EMAIL_CONFIRMATIONS_ENABLED", True),
            patch.object(config, "EMAIL_SMTP_HOST", "smtp.example.org"),
            patch.object(config, "EMAIL_SMTP_PORT", 587),
            patch.object(config, "EMAIL_SMTP_USERNAME", "bot@example.org"),
            patch.object(config, "EMAIL_SMTP_PASSWORD", "app-password"),
            patch.object(config, "EMAIL_FROM_ADDRESS", "bot@example.org"),
            patch.object(
                config,
                "EMAIL_FROM_NAME",
                "ESF 2026 Comprehensive Stroke Care Symposium",
            ),
            patch.object(email_utils.smtplib, "SMTP", return_value=server_context) as smtp,
            patch.object(email_utils, "make_qr_png", return_value=MagicMock(getvalue=lambda: b"png")),
        ):
            result = email_utils.send_registration_confirmation(self.registration)

        self.assertTrue(result)
        smtp.assert_called_once_with("smtp.example.org", 587, timeout=15)
        server.starttls.assert_called_once_with()
        server.login.assert_called_once_with("bot@example.org", "app-password")
        sent_message = server.send_message.call_args.args[0]
        self.assertEqual(sent_message["To"], "attendee@example.org")

    def test_sending_is_skipped_without_smtp_configuration(self):
        with (
            patch.object(config, "EMAIL_CONFIRMATIONS_ENABLED", False),
            patch.object(email_utils.smtplib, "SMTP") as smtp,
        ):
            self.assertFalse(
                email_utils.send_registration_confirmation(self.registration)
            )

        smtp.assert_not_called()


class RegistrationEmailHandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_email_failure_does_not_block_registration_or_qr(self):
        registration = {
            "reg_code": "ASOC-0042",
            "qr_token": "ASOC-0042.signature",
            "language": "en",
            "full_name": "Aster Example",
        }
        query = MagicMock()
        query.data = "confirm:yes"
        query.answer = AsyncMock()
        query.edit_message_reply_markup = AsyncMock()
        update = MagicMock(
            callback_query=query,
            effective_user=MagicMock(id=42),
            effective_chat=MagicMock(id=42),
        )
        context = MagicMock()
        context.user_data = {
            "lang": "en",
            "title": "Dr.",
            "full_name": "Aster Example",
            "phone": "+251900000000",
            "email": "attendee@example.org",
            "role": "doctor",
            "institution": "Example Hospital",
            "attendance_mode": "in_person",
            "attendance_days": "2026-11-02",
            "referral_source": "invitation",
            "region": "Addis Ababa",
            "trainee_status": "no",
        }

        with (
            patch.object(bot.db, "create_registration", return_value=registration),
            patch.object(
                bot.asyncio,
                "to_thread",
                new=AsyncMock(side_effect=OSError("SMTP unavailable")),
            ) as send_email,
            patch.object(bot, "send_qr", new=AsyncMock()) as send_qr,
        ):
            result = await bot.confirm(update, context)

        self.assertEqual(result, bot.ConversationHandler.END)
        send_email.assert_awaited_once_with(
            email_utils.send_registration_confirmation, registration
        )
        send_qr.assert_awaited_once()
        self.assertEqual(context.user_data, {})


if __name__ == "__main__":
    unittest.main()
