"""Send registration confirmation emails through an authenticated SMTP server."""
import html
import logging
import smtplib
from datetime import datetime
from email.message import EmailMessage

import config
from texts import PROGRAM_DAY_INFO, label_for, MODES, ROLES
from qr_utils import make_qr_png

log = logging.getLogger(__name__)


def registration_confirmation(registration) -> EmailMessage:
    """Create a bilingual confirmation email with the attendee's QR code."""
    name = registration["full_name"]
    safe_name = html.escape(name)
    reg_code = registration["reg_code"]
    dates = [
        f"Day {index} — {datetime.strptime(date, '%Y-%m-%d').strftime('%A, %B')} "
        f"{int(date[-2:])}, {date[:4]}"
        for index, (date, _en, _am) in enumerate(PROGRAM_DAY_INFO)
        if date in registration["attendance_days"].split(",")
    ]
    attendance_days = ", ".join(dates) or "Not specified"
    profession = label_for(ROLES, registration["role"], "en")
    attendance_mode = label_for(MODES, registration["attendance_mode"], "en")
    subject = f"Registration confirmed | ESF 2026 | {reg_code}"
    text = (
        f"Dear {name},\n\n"
        "Your registration for the ESF 2026 Comprehensive Stroke Care Symposium "
        "is confirmed.\n\n"
        f"Registration ID: {reg_code}\n"
        f"Name: {name}\n"
        f"Profession: {profession}\n"
        f"Organization: {registration['institution']}\n"
        f"Attendance: {attendance_mode}\n"
        f"Registered days: {attendance_days}\n\n"
        "Event details\n"
        "November 2 & 3, 2026\n"
        "Adwa Memorial Museum Multi Purpose Hall\n"
        "Addis Ababa, Ethiopia\n\n"
        "Your registration QR code is attached. Please present it at the entrance "
        "for check-in. You can also retrieve it from the Telegram bot using /myqr.\n\n"
        "We look forward to welcoming you.\n"
        "Ethiopian Stroke Foundation\n"
        "ethiopiastrokefoundation@gmail.com | +251963333388 | +251955235523\n\n"
        "---\n"
        "ውድ {name}፣\n\n"
        "ለESF 2026 Comprehensive Stroke Care Symposium ምዝገባዎ ተረጋግጧል።\n"
        f"የምዝገባ መለያ: {reg_code}\n"
        f"የሚሳተፉባቸው ቀናት: {attendance_days}\n"
        "ቀን: ኖቬምበር 2 እና 3፣ 2026\n"
        "ቦታ: Adwa Memorial Museum Multi Purpose Hall፣ አዲስ አበባ\n\n"
        "የምዝገባ QR ኮድዎ ከዚህ ኢሜይል ጋር ተያይዟል። መግቢያ ላይ ለምዝገባ ያሳዩ።\n"
        "ከሰላምታ ጋር፣\n"
        "የኢትዮጵያ ስትሮክ ፋውንዴሽን\n"
        "ethiopiastrokefoundation@gmail.com | +251963333388 | +251955235523\n"
    ).format(name=name)
    body_html = f"""\
<!doctype html>
<html lang="en">
<body style="margin:0;padding:24px;background:#f3f6f5;font-family:Arial,sans-serif;color:#173a33">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;margin:auto;background:#fff;border:1px solid #e2e9e6;border-radius:12px">
    <tr><td style="padding:28px 32px;background:#103c34;color:#fff;border-bottom:4px solid #d9ad58;border-radius:12px 12px 0 0">
      <div style="font-size:12px;letter-spacing:2px;color:#f2d797;font-weight:bold">ETHIOPIAN STROKE FOUNDATION</div>
      <h1 style="margin:12px 0 6px;font-size:24px">Registration confirmed</h1>
      <div style="font-size:15px;color:#d9e8e2">ESF 2026 Comprehensive Stroke Care Symposium</div>
    </td></tr>
    <tr><td style="padding:28px 32px">
      <p style="font-size:16px">Dear {safe_name},</p>
      <p style="line-height:1.6">Your registration is confirmed. We look forward to welcoming you to the symposium.</p>
      <div style="padding:18px 20px;background:#f3f7f5;border-radius:8px;line-height:1.8">
        <strong>Registration ID</strong>: {html.escape(reg_code)}<br>
        <strong>Profession</strong>: {html.escape(profession)}<br>
        <strong>Organization</strong>: {html.escape(registration['institution'])}<br>
        <strong>Attendance</strong>: {html.escape(attendance_mode)}<br>
        <strong>Days</strong>: {html.escape(attendance_days)}
      </div>
      <h2 style="margin:24px 0 8px;font-size:17px">Event details</h2>
      <p style="line-height:1.7;margin:0">November 2 &amp; 3, 2026<br>
      Adwa Memorial Museum Multi Purpose Hall<br>Addis Ababa, Ethiopia</p>
      <p style="margin:24px 0 8px;line-height:1.6">Your registration QR code is attached. Please present it at the entrance for check-in. You can also retrieve it anytime from the Telegram bot with <strong>/myqr</strong>.</p>
      <p style="margin:24px 0 0;line-height:1.6">We look forward to welcoming you.<br><strong>Ethiopian Stroke Foundation</strong></p>
      <hr style="border:0;border-top:1px solid #e2e9e6;margin:24px 0">
      <p style="font-size:14px;line-height:1.8;color:#40564f">ውድ {safe_name}፣ ለESF 2026 Comprehensive Stroke Care Symposium ምዝገባዎ ተረጋግጧል።<br>
      የምዝገባ መለያ: {html.escape(reg_code)}<br>
      የሚሳተፉባቸው ቀናት: {html.escape(attendance_days)}<br>
      የQR ኮድዎን ከዚህ ኢሜይል ጋር ተያይዟል፤ መግቢያ ላይ ለምዝገባ ያሳዩ።</p>
    </td></tr>
    <tr><td style="padding:18px 32px;background:#f7f9f8;color:#586b64;font-size:12px;line-height:1.7;border-radius:0 0 12px 12px">
      Ethiopian Stroke Foundation · Addis Ababa, Ethiopia<br>
      <a href="mailto:ethiopiastrokefoundation@gmail.com" style="color:#145c4c">ethiopiastrokefoundation@gmail.com</a><br>
      +251963333388 · +251955235523
    </td></tr>
  </table>
</body>
</html>
"""
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{config.EMAIL_FROM_NAME} <{config.EMAIL_FROM_ADDRESS}>"
    message["To"] = registration["email"]
    message.set_content(text)
    message.add_alternative(body_html, subtype="html")

    qr_png = make_qr_png(registration["qr_token"])
    message.add_attachment(
        qr_png.getvalue(),
        maintype="image",
        subtype="png",
        filename="ESF-2026-registration-QR.png",
    )
    return message


def send_registration_confirmation(registration) -> bool:
    """Send a confirmation; return False when SMTP settings are not configured."""
    if not config.EMAIL_CONFIRMATIONS_ENABLED:
        return False

    message = registration_confirmation(registration)
    with smtplib.SMTP(
        config.EMAIL_SMTP_HOST, config.EMAIL_SMTP_PORT, timeout=15
    ) as server:
        server.starttls()
        server.login(config.EMAIL_SMTP_USERNAME, config.EMAIL_SMTP_PASSWORD)
        server.send_message(message)
    return True
