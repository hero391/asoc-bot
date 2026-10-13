"""Run the Telegram bot and staff check-in site in one Railway service."""
import asyncio
import logging
import os
import threading

import bot
import checkin_app
import config


def main():
    if not config.CHECKIN_PASSWORD or len(config.CHECKIN_PASSWORD) < 16:
        raise SystemExit(
            "Set a CHECKIN_PASSWORD of at least 16 characters in Railway variables."
        )
    if not config.QR_SECRET:
        raise SystemExit("Set QR_SECRET in Railway variables.")

    application = bot.build_app()
    port = int(os.environ.get("PORT", "8080"))
    web_thread = threading.Thread(
        target=checkin_app.serve,
        kwargs={"app": checkin_app.app, "host": "0.0.0.0", "port": port},
        name="check-in-web",
        daemon=True,
    )
    web_thread.start()

    logging.getLogger("asoc-bot").info(
        "Staff check-in site is starting on port %s", port
    )
    asyncio.set_event_loop(asyncio.new_event_loop())
    application.run_polling()


if __name__ == "__main__":
    main()
