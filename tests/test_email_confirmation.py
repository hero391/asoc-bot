import base64
import json
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
            patch.object(
                config,
                "EMAIL_FROM_NAME",
                "ESF 2026 Comprehensive Stroke Care Symposium",
            ),
            patch.object(
                email_utils,
                "make_qr_png",
                return_value=MagicMock(getvalue=lambda: b"\x89PNG test"),
            ),
        ):
            message = email_utils.registration_confirmation(self.registration)

        self.assertEqual(
            message["subject"], "Registration confirmed | ESF 2026 | ASOC-0042"
        )
        self.assertEqual(message["to"], "attendee@example.org")
        self.assertEqual(
            message["from_name"],
            "ESF 2026 Comprehensive Stroke Care Symposium",
        )
        self.assertEqual(message["reply_to"], "ethiopiastrokefoundation@gmail.com")
        self.assertIn("November 2 & 3, 2026", message["text"])
        self.assertIn("Day 1 — Monday, November 2, 2026", message["text"])
        self.assertIn("Day 2 — Tuesday, November 3, 2026", message["text"])
        self.assertIn("Adwa Memorial Museum Multi Purpose Hall", message["text"])
        self.assertIn("registration QR code is attached", message["text"])
        self.assertIn("Registration confirmed", message["html"])
        attachment = message["attachments"][0]
        self.assertEqual(attachment["filename"], "ESF-2026-registration-QR.png")
        self.assertEqual(attachment["content_type"], "image/png")
        self.assertTrue(base64.b64decode(attachment["content"]).startswith(b"\x89PNG"))

    def test_sending_uses_secret_protected_https_relay(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"ok":true}'
        response_context = MagicMock()
        response_context.__enter__.return_value = response

        with (
            patch.object(config, "EMAIL_CONFIRMATIONS_ENABLED", True),
            patch.object(config, "GMAIL_RELAY_URL", "https://script.google.com/macros/s/id/exec"),
            patch.object(config, "GMAIL_RELAY_SECRET", "test-relay-secret"),
            patch.object(
                config,
                "EMAIL_FROM_NAME",
                "ESF 2026 Comprehensive Stroke Care Symposium",
            ),
            patch.object(
                email_utils,
                "make_qr_png",
                return_value=MagicMock(getvalue=lambda: b"\x89PNG test"),
            ),
            patch.object(email_utils, "urlopen", return_value=response_context) as post,
        ):
            result = email_utils.send_registration_confirmation(self.registration)

        self.assertTrue(result)
        request = post.call_args.args[0]
        self.assertEqual(
            request.full_url, "https://script.google.com/macros/s/id/exec"
        )
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(post.call_args.kwargs, {"timeout": 15})
        payload = json.loads(request.data)
        self.assertEqual(payload["secret"], "test-relay-secret")
        self.assertEqual(payload["to"], "attendee@example.org")
        self.assertEqual(
            payload["reply_to"], "ethiopiastrokefoundation@gmail.com"
        )
        self.assertTrue(
            base64.b64decode(payload["attachments"][0]["content"]).startswith(
                b"\x89PNG"
            )
        )

    def test_sending_is_skipped_without_relay_configuration(self):
        with (
            patch.object(config, "EMAIL_CONFIRMATIONS_ENABLED", False),
            patch.object(email_utils, "urlopen") as post,
        ):
            self.assertFalse(
                email_utils.send_registration_confirmation(self.registration)
            )

        post.assert_not_called()

    def test_relay_rejection_is_reported(self):
        response = MagicMock()
        response.status = 200
        response.read.return_value = b'{"ok":false,"error":"Unauthorized"}'
        response_context = MagicMock()
        response_context.__enter__.return_value = response

        with (
            patch.object(config, "EMAIL_CONFIRMATIONS_ENABLED", True),
            patch.object(config, "GMAIL_RELAY_URL", "https://relay.example/exec"),
            patch.object(config, "GMAIL_RELAY_SECRET", "wrong-secret"),
            patch.object(
                email_utils, "make_qr_png", return_value=MagicMock(getvalue=lambda: b"png")
            ),
            patch.object(email_utils, "urlopen", return_value=response_context),
        ):
            with self.assertRaisesRegex(OSError, "Gmail relay rejected.*Unauthorized"):
                email_utils.send_registration_confirmation(self.registration)


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
                new=AsyncMock(side_effect=OSError("Gmail relay unavailable")),
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
