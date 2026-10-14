"""ASOC 2026 conference bot - Part 1 (registration + QR) and Part 2 (schedule).

Run with:  python bot.py
"""
import asyncio
import logging
import os
import re
from urllib.parse import quote_plus

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import config
import db
import schedule_handlers
from helpers import get_lang
from qr_utils import make_qr_png
from texts import MODES, ROLES, label_for, t

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
log = logging.getLogger("asoc-bot")

# Conversation steps
LANG, NAME, PHONE, EMAIL, ROLE, INSTITUTION, MODE, CONFIRM = range(8)

PHONE_RE = re.compile(r"^\+?[0-9][0-9 \-]{7,16}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ---------- small helpers ----------
def lang_of(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "en")


def options_keyboard(options, prefix: str, lang: str, per_row: int = 1):
    idx = 2 if lang == "am" else 1
    buttons = [
        InlineKeyboardButton(opt[idx], callback_data=f"{prefix}:{opt[0]}")
        for opt in options
    ]
    rows = [buttons[i : i + per_row] for i in range(0, len(buttons), per_row)]
    return InlineKeyboardMarkup(rows)


def main_menu_keyboard(lang: str, *, registered: bool = False) -> InlineKeyboardMarkup:
    rows = []
    if not registered:
        rows.append(
            [InlineKeyboardButton(t(lang, "menu_register"), callback_data="menu:register")]
        )
    rows.extend(
        [
            [InlineKeyboardButton(t(lang, "menu_program"), callback_data="menu:program")],
            [InlineKeyboardButton(t(lang, "menu_venue"), callback_data="menu:venue")],
            [InlineKeyboardButton(t(lang, "menu_contact"), callback_data="menu:contact")],
        ]
    )
    if registered:
        rows.append(
            [InlineKeyboardButton(t(lang, "menu_myqr"), callback_data="menu:myqr")]
        )
    return InlineKeyboardMarkup(rows)


def back_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t(lang, "menu_back"), callback_data="menu:home")]]
    )


async def send_qr(bot, chat_id: int, reg, text: str):
    """Send the QR image with the main menu available below it."""
    await bot.send_photo(
        chat_id=chat_id,
        photo=make_qr_png(reg["qr_token"]),
        caption=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(reg["language"], registered=True),
    )


# ---------- conversation steps ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reg = db.get_registration(update.effective_user.id)
    lang = reg["language"] if reg else get_lang(update, context)
    await update.effective_message.reply_text(
        t(lang, "main_menu"),
        reply_markup=main_menu_keyboard(lang, registered=reg is not None),
    )
    return ConversationHandler.END


async def register_from_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    reg = db.get_registration(update.effective_user.id)
    if reg:
        lang = reg["language"]
        await query.edit_message_text(t(lang, "already"))
        await send_qr(
            context.bot,
            update.effective_chat.id,
            reg,
            t(lang, "registered", reg_code=reg["reg_code"], name=reg["full_name"]),
        )
        return ConversationHandler.END

    context.user_data.clear()
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
                InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang:am"),
            ]
        ]
    )
    await query.edit_message_text(t("en", "choose_language"), reply_markup=keyboard)
    return LANG


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(update, context)
    action = query.data.split(":")[1]
    reg = db.get_registration(update.effective_user.id)
    if action == "home":
        lang = reg["language"] if reg else lang
        await query.edit_message_text(
            t(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang, registered=reg is not None),
        )
    elif action == "myqr":
        if not reg:
            await query.message.reply_text(t(lang, "no_reg"))
            return
        await send_qr(
            context.bot,
            update.effective_chat.id,
            reg,
            t(
                reg["language"],
                "registered",
                reg_code=reg["reg_code"],
                name=reg["full_name"],
            ),
        )
    elif action == "venue":
        map_url = (
            "https://www.google.com/maps/search/?api=1&query="
            + quote_plus(f"{config.CONFERENCE_VENUE}, Ethiopia")
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(t(lang, "menu_directions"), url=map_url)],
                [InlineKeyboardButton(t(lang, "menu_back"), callback_data="menu:home")],
            ]
        )
        await query.edit_message_text(
            t(lang, "venue_info", venue=config.CONFERENCE_VENUE, dates=config.CONFERENCE_DATES),
            reply_markup=keyboard,
        )
    elif action == "contact":
        await query.edit_message_text(
            t(lang, "contact_unavailable"), reply_markup=back_menu_keyboard(lang)
        )


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(
        t(lang, "welcome"), parse_mode=ParseMode.MARKDOWN
    )
    await query.message.reply_text(t(lang, "ask_name"), parse_mode=ParseMode.MARKDOWN)
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = lang_of(context)
    name = update.message.text.strip()
    if len(name) < 3:
        await update.message.reply_text(t(lang, "bad_name"))
        return NAME
    context.user_data["full_name"] = name
    await update.message.reply_text(t(lang, "ask_phone"), parse_mode=ParseMode.MARKDOWN)
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = lang_of(context)
    phone = update.message.text.strip()
    if not PHONE_RE.match(phone):
        await update.message.reply_text(t(lang, "bad_phone"))
        return PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text(t(lang, "ask_email"), parse_mode=ParseMode.MARKDOWN)
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = lang_of(context)
    email = update.message.text.strip().lower()
    if not EMAIL_RE.match(email):
        await update.message.reply_text(t(lang, "bad_email"))
        return EMAIL
    context.user_data["email"] = email
    await update.message.reply_text(
        t(lang, "ask_role"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=options_keyboard(ROLES, "role", lang),
    )
    return ROLE


async def get_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    context.user_data["role"] = query.data.split(":")[1]
    await query.edit_message_text(
        label_for(ROLES, context.user_data["role"], lang)
    )
    await query.message.reply_text(
        t(lang, "ask_institution"), parse_mode=ParseMode.MARKDOWN
    )
    return INSTITUTION


async def get_institution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = lang_of(context)
    institution = update.message.text.strip()
    if len(institution) < 2:
        await update.message.reply_text(t(lang, "bad_institution"))
        return INSTITUTION
    context.user_data["institution"] = institution
    await update.message.reply_text(
        t(lang, "ask_mode"),
        reply_markup=options_keyboard(MODES, "mode", lang),
    )
    return MODE


async def get_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    d = context.user_data
    d["attendance_mode"] = query.data.split(":")[1]

    summary = (
        f"{t(lang, 'confirm_title')}\n\n"
        f"👤 {t(lang, 'label_name')}: {d['full_name']}\n"
        f"📞 {t(lang, 'label_phone')}: {d['phone']}\n"
        f"✉️ {t(lang, 'label_email')}: {d['email']}\n"
        f"💼 {t(lang, 'label_role')}: {label_for(ROLES, d['role'], lang)}\n"
        f"🏥 {t(lang, 'label_institution')}: {d['institution']}\n"
        f"🎫 {t(lang, 'label_mode')}: {label_for(MODES, d['attendance_mode'], lang)}"
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t(lang, "btn_confirm"), callback_data="confirm:yes"),
                InlineKeyboardButton(t(lang, "btn_restart"), callback_data="confirm:no"),
            ]
        ]
    )
    await query.edit_message_text(summary, reply_markup=keyboard)
    return CONFIRM


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)

    if query.data == "confirm:no":
        await query.edit_message_text(t(lang, "ask_name"), parse_mode=ParseMode.MARKDOWN)
        return NAME

    d = context.user_data
    reg = db.create_registration(
        update.effective_user.id,
        {
            "full_name": d["full_name"],
            "phone": d["phone"],
            "email": d["email"],
            "role": d["role"],
            "institution": d["institution"],
            "language": lang,
            "attendance_mode": d["attendance_mode"],
        },
    )
    await query.edit_message_reply_markup(reply_markup=None)
    await send_qr(
        context.bot,
        update.effective_chat.id,
        reg,
        t(lang, "registered", reg_code=reg["reg_code"], name=reg["full_name"]),
    )
    log.info("New registration: %s (%s)", reg["reg_code"], reg["full_name"])
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = lang_of(context)
    context.user_data.clear()
    await update.message.reply_text(t(lang, "cancelled"))
    return ConversationHandler.END


# ---------- simple commands ----------
async def myqr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reg = db.get_registration(update.effective_user.id)
    if not reg:
        await update.message.reply_text(t("en", "no_reg"))
        return
    lang = reg["language"]
    await send_qr(
        context.bot,
        update.effective_chat.id,
        reg,
        t(lang, "registered", reg_code=reg["reg_code"], name=reg["full_name"]),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    await update.message.reply_text(t(lang, "help"))


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.error("Unhandled error", exc_info=context.error)


# ---------- start the bot ----------
def build_app():
    config.check_config()
    db.init_db()

    # Load the conference program from CSV when the database is empty.
    try:
        count = schedule_handlers.ensure_schedule_loaded()
        log.info("Conference schedule ready: %d sessions", count)
    except (FileNotFoundError, ValueError):
        log.exception("Conference schedule could not be loaded; /schedule will retry")
    app = ApplicationBuilder().token(config.BOT_TOKEN).build()

    text_only = filters.TEXT & ~filters.COMMAND
    registration = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(register_from_menu, pattern=r"^menu:register$"),
        ],
        states={
            LANG: [CallbackQueryHandler(choose_language, pattern=r"^lang:")],
            NAME: [MessageHandler(text_only, get_name)],
            PHONE: [MessageHandler(text_only, get_phone)],
            EMAIL: [MessageHandler(text_only, get_email)],
            ROLE: [CallbackQueryHandler(get_role, pattern=r"^role:")],
            INSTITUTION: [MessageHandler(text_only, get_institution)],
            MODE: [CallbackQueryHandler(get_mode, pattern=r"^mode:")],
            CONFIRM: [CallbackQueryHandler(confirm, pattern=r"^confirm:")],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    app.add_handler(registration)
    app.add_handler(CommandHandler("myqr", myqr))
    app.add_handler(CommandHandler("help", help_command))
    schedule_handlers.register(app)  # Part 2: /schedule, /now, /language
    app.add_handler(
        CallbackQueryHandler(
            menu_callback, pattern=r"^menu:(home|venue|contact|myqr)$"
        ),
        group=1,
    )
    app.add_error_handler(on_error)
    return app


if __name__ == "__main__":
    application = build_app()
    log.info("Bot is running... press Ctrl+C to stop")
    asyncio.set_event_loop(asyncio.new_event_loop())
    application.run_polling()