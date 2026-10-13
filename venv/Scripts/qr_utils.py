"""QR helpers.

The QR code contains a SIGNED token like:  ASOC-0042.a1b2c3d4e5
 - "ASOC-0042" is the registration code
 - "a1b2c3d4e5" is a signature made with your secret key
Anyone can read the code, but nobody can create a valid one without the secret.
"""
import hashlib
import hmac
from io import BytesIO

import qrcode

import config


def _sign(reg_code: str) -> str:
    digest = hmac.new(
        config.QR_SECRET.encode(), reg_code.encode(), hashlib.sha256
    ).hexdigest()
    return digest[:10]


def make_token(reg_code: str) -> str:
    return f"{reg_code}.{_sign(reg_code)}"


def verify_token(token: str):
    """Return the registration code if the token is genuine, otherwise None."""
    try:
        reg_code, signature = token.strip().rsplit(".", 1)
    except ValueError:
        return None
    if hmac.compare_digest(signature, _sign(reg_code)):
        return reg_code
    return None


def make_qr_png(token: str) -> BytesIO:
    """Create the QR image in memory and return it ready to send."""
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(token)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    buf.name = "registration_qr.png"
    return buf