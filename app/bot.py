"""ESF 2026 symposium bot - Part 1 (registration + QR) and Part 2 (schedule).

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
from texts import (
    DAY_INFO,
    MODES,
    REFERRAL_SOURCES,
    ROLES,
    TITLES,
    TRAINEE_CATEGORIES,
    day_label,
    label_for,
    t,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
log = logging.getLogger("asoc-bot")

# Conversation steps
(
    LANG,
    TITLE,
    TITLE_OTHER,
    NAME,
    PHONE,
    EMAIL,
    ROLE,
    INSTITUTION,
    MODE,
    DAYS,
    REFERRAL,
    REFERRAL_OTHER,
    REGION,
    TRAINEE,
    TRAINEE_CATEGORY,
    CONFIRM,
) = range(16)
(
    UPDATE_TITLE,
    UPDATE_TITLE_OTHER,
    UPDATE_DAYS,
    UPDATE_REFERRAL,
    UPDATE_REFERRAL_OTHER,
    UPDATE_REGION,
    UPDATE_TRAINEE,
    UPDATE_TRAINEE_CATEGORY,
) = range(16, 24)

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
        rows.append(
            [InlineKeyboardButton(t(lang, "menu_update"), callback_data="menu:update")]
        )
    return InlineKeyboardMarkup(rows)


def registration_details_incomplete(registration) -> bool:
    return any(
        not registration[field].strip()
        for field in (
            "title",
            "attendance_days",
            "referral_source",
            "region",
            "trainee_status",
        )
    )


def back_menu_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(t(lang, "menu_back"), callback_data="menu:home")]]
    )


def days_keyboard(lang: str, selected_days: set[str], prefix: str):
    rows = []
    for index, (date, _english_label, _amharic_label) in enumerate(DAY_INFO):
        marker = "✅ " if date in selected_days else ""
        rows.append(
            [
                InlineKeyboardButton(
                    marker + day_label(index, lang),
                    callback_data=f"{prefix}:toggle:{index}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                t(lang, "days_done"), callback_data=f"{prefix}:done"
            )
        ]
    )
    return InlineKeyboardMarkup(rows)


def ordered_days(selected_days: set[str]) -> str:
    return ",".join(date for date, _en, _am in DAY_INFO if date in selected_days)


async def ask_days(message, context, *, prefix: str, selected_days=None):
    lang = lang_of(context)
    active_dates = {date for date, _en, _am in DAY_INFO}
    selected_days = set(selected_days or ()) & active_dates
    context.user_data["selected_days"] = selected_days
    await message.reply_text(
        t(lang, "ask_days"),
        reply_markup=days_keyboard(lang, selected_days, prefix),
    )


async def ask_name(message, context):
    await message.reply_text(
        t(lang_of(context), "ask_name"), parse_mode=ParseMode.MARKDOWN
    )


async def ask_update_days(message, context):
    await ask_days(
        message,
        context,
        prefix="update_days",
        selected_days=context.user_data.get("selected_days", set()),
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


async def edit_menu_message(query, text: str, reply_markup=None, parse_mode=None):
    """Edit either the text menu or the caption menu attached to a QR photo."""
    message = query.message
    if message and message.text is None and message.caption is not None:
        await query.edit_message_caption(
            caption=text, parse_mode=parse_mode, reply_markup=reply_markup
        )
        return
    await query.edit_message_text(
        text, parse_mode=parse_mode, reply_markup=reply_markup
    )


# ---------- conversation steps ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reg = db.get_registration(update.effective_user.id)
    lang = reg["language"] if reg else get_lang(update, context)
    if reg and registration_details_incomplete(reg):
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        t(lang, "menu_update"), callback_data="menu:update"
                    )
                ]
            ]
        )
        with config.SYMPOSIUM_POSTER.open("rb") as poster:
            await update.effective_message.reply_photo(
                photo=poster, caption=t(lang, "update_prompt"), reply_markup=keyboard
            )
        return ConversationHandler.END
    with config.SYMPOSIUM_POSTER.open("rb") as poster:
        await update.effective_message.reply_photo(
            photo=poster,
            caption=t(lang, "main_menu"),
            reply_markup=main_menu_keyboard(lang, registered=reg is not None),
        )
    return ConversationHandler.END


async def register_from_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    reg = db.get_registration(update.effective_user.id)
    if reg:
        lang = reg["language"]
        await edit_menu_message(query, t(lang, "already"))
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
    await edit_menu_message(query, t("en", "choose_language"), reply_markup=keyboard)
    return LANG


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(update, context)
    action = query.data.split(":")[1]
    reg = db.get_registration(update.effective_user.id)
    if action == "home":
        lang = reg["language"] if reg else lang
        await edit_menu_message(
            query,
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
            "https://www.google.com/maps/dir/?api=1&destination="
            + quote_plus(f"{config.CONFERENCE_VENUE}, Ethiopia")
        )
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(t(lang, "menu_directions"), url=map_url)],
                [InlineKeyboardButton(t(lang, "menu_back"), callback_data="menu:home")],
            ]
        )
        await edit_menu_message(
            query,
            t(lang, "venue_info", venue=config.CONFERENCE_VENUE, dates=config.CONFERENCE_DATES),
            reply_markup=keyboard,
        )
    elif action == "contact":
        await edit_menu_message(
            query,
            t(lang, "contact_info"), reply_markup=back_menu_keyboard(lang)
        )


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    context.user_data["lang"] = lang
    await edit_menu_message(
        query,
        t(lang, "welcome"),
        reply_markup=None,
        parse_mode=ParseMode.MARKDOWN,
    )
    await query.message.reply_text(
        t(lang, "ask_title"),
        reply_markup=options_keyboard(TITLES, "title", lang),
    )
    return TITLE


async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    title = query.data.split(":")[1]
    if title == "other":
        await query.edit_message_text(t(lang, "ask_other_title"))
        return TITLE_OTHER
    context.user_data["title"] = label_for(TITLES, title, "en")
    await query.edit_message_text(context.user_data["title"])
    await ask_name(query.message, context)
    return NAME


async def get_other_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text.strip()
    if not title:
        await update.message.reply_text(t(lang_of(context), "ask_other_title"))
        return TITLE_OTHER
    context.user_data["title"] = title
    await ask_name(update.message, context)
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
    await query.edit_message_text(
        t(lang, "ask_days"),
        reply_markup=days_keyboard(lang, set(), "days"),
    )
    return DAYS


async def handle_days_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    prefix: str,
    next_state: int,
):
    query = update.callback_query
    lang = lang_of(context)
    selected_days = context.user_data.setdefault("selected_days", set())
    parts = query.data.split(":")
    if parts[-1] == "done":
        if not selected_days:
            await query.answer(t(lang, "days_need_one"), show_alert=True)
            return next_state
        context.user_data["attendance_days"] = ordered_days(selected_days)
        await query.answer()
        if prefix == "update_days":
            await query.edit_message_text(
                t(lang, "ask_referral"),
                reply_markup=options_keyboard(REFERRAL_SOURCES, "update_referral", lang),
            )
        else:
            await query.edit_message_text(
                t(lang, "ask_referral"),
                reply_markup=options_keyboard(REFERRAL_SOURCES, "referral", lang),
            )
        return REFERRAL if prefix == "days" else UPDATE_REFERRAL

    day_index = int(parts[-1])
    if not 0 <= day_index < len(DAY_INFO):
        await query.answer(t(lang, "days_need_one"), show_alert=True)
        return next_state
    date = DAY_INFO[day_index][0]
    if date in selected_days:
        selected_days.remove(date)
    else:
        selected_days.add(date)
    await query.answer()
    await query.edit_message_reply_markup(
        reply_markup=days_keyboard(lang, selected_days, prefix)
    )
    return next_state


async def get_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_days_callback(
        update, context, prefix="days", next_state=DAYS
    )


async def get_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    referral = query.data.split(":")[1]
    if referral == "other":
        await query.edit_message_text(t(lang, "ask_other_referral"))
        return REFERRAL_OTHER
    context.user_data["referral_source"] = referral
    await query.edit_message_text(t(lang, "ask_region"))
    return REGION


async def get_other_referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    referral = update.message.text.strip()
    if not referral:
        await update.message.reply_text(t(lang_of(context), "ask_other_referral"))
        return REFERRAL_OTHER
    context.user_data["referral_source"] = referral
    await update.message.reply_text(t(lang_of(context), "ask_region"))
    return REGION


async def get_region(update: Update, context: ContextTypes.DEFAULT_TYPE):
    region = update.message.text.strip()
    if not region:
        await update.message.reply_text(t(lang_of(context), "ask_region"))
        return REGION
    context.user_data["region"] = region
    lang = lang_of(context)
    await update.message.reply_text(
        t(lang, "ask_trainee"), reply_markup=yes_no_keyboard(lang, "trainee")
    )
    return TRAINEE


def trainee_keyboard(lang: str):
    return options_keyboard(TRAINEE_CATEGORIES, "trainee_category", lang)


def registration_confirmation_keyboard(lang: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t(lang, "btn_confirm"), callback_data="confirm:yes"),
                InlineKeyboardButton(t(lang, "btn_restart"), callback_data="confirm:no"),
            ]
        ]
    )


def display_option(options, value: str, lang: str) -> str:
    if any(option[0] == value for option in options):
        return label_for(options, value, lang)
    return value


def registration_summary(data: dict, lang: str) -> str:
    days = [
        day_label(index, lang)
        for index, (date, _en, _am) in enumerate(DAY_INFO)
        if date in data["attendance_days"].split(",")
    ]
    trainee_status = (
        t(lang, "no")
        if data["trainee_status"] == "no"
        else display_option(TRAINEE_CATEGORIES, data["trainee_status"], lang)
    )
    return (
        f"{t(lang, 'confirm_title')}\n\n"
        f"👤 {data['title']} {data['full_name']}\n"
        f"📞 {t(lang, 'label_phone')}: {data['phone']}\n"
        f"✉️ {t(lang, 'label_email')}: {data['email']}\n"
        f"💼 {t(lang, 'label_role')}: {label_for(ROLES, data['role'], lang)}\n"
        f"🏥 {t(lang, 'label_institution')}: {data['institution']}\n"
        f"🎫 {t(lang, 'label_mode')}: {label_for(MODES, data['attendance_mode'], lang)}\n"
        f"📅 {', '.join(days)}\n"
        f"🔎 {display_option(REFERRAL_SOURCES, data['referral_source'], lang)}\n"
        f"🌍 {data['region']}\n"
        f"👩‍⚕️ {trainee_status}"
    )


async def ask_trainee_category(query, lang: str):
    await query.edit_message_text(
        t(lang, "ask_trainee_category"),
        reply_markup=trainee_keyboard(lang),
    )


def yes_no_keyboard(lang: str, prefix: str):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(t(lang, "yes"), callback_data=f"{prefix}:yes"),
                InlineKeyboardButton(t(lang, "no"), callback_data=f"{prefix}:no"),
            ]
        ]
    )


async def get_trainee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    if query.data == "trainee:yes":
        await ask_trainee_category(query, lang)
        return TRAINEE_CATEGORY
    context.user_data["trainee_status"] = "no"
    await query.edit_message_text(
        registration_summary(context.user_data, lang),
        reply_markup=registration_confirmation_keyboard(lang),
    )
    return CONFIRM


async def get_trainee_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    context.user_data["trainee_status"] = query.data.split(":")[1]
    await query.edit_message_text(
        registration_summary(context.user_data, lang),
        reply_markup=registration_confirmation_keyboard(lang),
    )
    return CONFIRM


async def start_update_details(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    if query:
        await query.answer()
    reg = db.get_registration(update.effective_user.id)
    if not reg:
        await update.effective_message.reply_text(
            t(get_lang(update, context), "no_reg")
        )
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data["lang"] = reg["language"]
    context.user_data["selected_days"] = set(
        filter(None, reg["attendance_days"].split(","))
    )
    await update.effective_message.reply_text(
        t(reg["language"], "ask_title"),
        reply_markup=options_keyboard(TITLES, "update_title", reg["language"]),
    )
    return UPDATE_TITLE


async def get_update_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    title = query.data.split(":")[1]
    if title == "other":
        await query.edit_message_text(t(lang, "ask_other_title"))
        return UPDATE_TITLE_OTHER
    context.user_data["title"] = label_for(TITLES, title, "en")
    await ask_update_days(query.message, context)
    return UPDATE_DAYS


async def get_update_other_title(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    title = update.message.text.strip()
    if not title:
        await update.message.reply_text(t(lang_of(context), "ask_other_title"))
        return UPDATE_TITLE_OTHER
    context.user_data["title"] = title
    await ask_update_days(update.message, context)
    return UPDATE_DAYS


async def get_update_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await handle_days_callback(
        update, context, prefix="update_days", next_state=UPDATE_DAYS
    )


async def get_update_referral(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    referral = query.data.split(":")[1]
    if referral == "other":
        await query.edit_message_text(t(lang, "ask_other_referral"))
        return UPDATE_REFERRAL_OTHER
    context.user_data["referral_source"] = referral
    await query.edit_message_text(t(lang, "ask_region"))
    return UPDATE_REGION


async def get_update_other_referral(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    referral = update.message.text.strip()
    if not referral:
        await update.message.reply_text(t(lang_of(context), "ask_other_referral"))
        return UPDATE_REFERRAL_OTHER
    context.user_data["referral_source"] = referral
    await update.message.reply_text(t(lang_of(context), "ask_region"))
    return UPDATE_REGION


async def get_update_region(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    region = update.message.text.strip()
    if not region:
        await update.message.reply_text(t(lang_of(context), "ask_region"))
        return UPDATE_REGION
    context.user_data["region"] = region
    lang = lang_of(context)
    await update.message.reply_text(
        t(lang, "ask_trainee"),
        reply_markup=yes_no_keyboard(lang, "update_trainee"),
    )
    return UPDATE_TRAINEE


async def finish_update_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    reg = db.update_registration_details(
        update.effective_user.id,
        {
            "title": data["title"],
            "attendance_days": data["attendance_days"],
            "referral_source": data["referral_source"],
            "region": data["region"],
            "trainee_status": data["trainee_status"],
        },
    )
    if not reg:
        await update.effective_message.reply_text(t(lang_of(context), "no_reg"))
        context.user_data.clear()
        return ConversationHandler.END
    await send_qr(
        context.bot,
        update.effective_chat.id,
        reg,
        t(reg["language"], "update_saved"),
    )
    context.user_data.clear()
    return ConversationHandler.END


async def get_update_trainee(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    if query.data == "update_trainee:yes":
        await query.edit_message_text(
            t(lang, "ask_trainee_category"),
            reply_markup=trainee_keyboard(lang),
        )
        return UPDATE_TRAINEE_CATEGORY
    context.user_data["trainee_status"] = "no"
    return await finish_update_details(update, context)


async def get_update_trainee_category(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)
    context.user_data["trainee_status"] = query.data.split(":")[1]
    return await finish_update_details(update, context)


async def confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = lang_of(context)

    if query.data == "confirm:no":
        context.user_data.clear()
        context.user_data["lang"] = lang
        await query.edit_message_text(
            t(lang, "ask_title"),
            reply_markup=options_keyboard(TITLES, "title", lang),
        )
        return TITLE

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
            "title": d["title"],
            "attendance_days": d["attendance_days"],
            "referral_source": d["referral_source"],
            "region": d["region"],
            "trainee_status": d["trainee_status"],
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
async def set_bot_name(application):
    await application.bot.set_my_name(config.CONFERENCE_NAME)


def build_app():
    config.check_config()
    db.init_db()

    # Refresh the program when the CSV changes, including on a new deployment.
    try:
        count = schedule_handlers.ensure_schedule_loaded()
        log.info("Conference schedule ready: %d sessions", count)
    except (FileNotFoundError, ValueError):
        log.exception("Conference schedule could not be loaded; /schedule will retry")
    app = (
        ApplicationBuilder()
        .token(config.BOT_TOKEN)
        .post_init(set_bot_name)
        .build()
    )

    text_only = filters.TEXT & ~filters.COMMAND
    registration = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CallbackQueryHandler(register_from_menu, pattern=r"^menu:register$"),
        ],
        states={
            LANG: [CallbackQueryHandler(choose_language, pattern=r"^lang:")],
            TITLE: [CallbackQueryHandler(get_title, pattern=r"^title:")],
            TITLE_OTHER: [MessageHandler(text_only, get_other_title)],
            NAME: [MessageHandler(text_only, get_name)],
            PHONE: [MessageHandler(text_only, get_phone)],
            EMAIL: [MessageHandler(text_only, get_email)],
            ROLE: [CallbackQueryHandler(get_role, pattern=r"^role:")],
            INSTITUTION: [MessageHandler(text_only, get_institution)],
            MODE: [CallbackQueryHandler(get_mode, pattern=r"^mode:")],
            DAYS: [CallbackQueryHandler(get_days, pattern=r"^days:")],
            REFERRAL: [CallbackQueryHandler(get_referral, pattern=r"^referral:")],
            REFERRAL_OTHER: [MessageHandler(text_only, get_other_referral)],
            REGION: [MessageHandler(text_only, get_region)],
            TRAINEE: [CallbackQueryHandler(get_trainee, pattern=r"^trainee:")],
            TRAINEE_CATEGORY: [
                CallbackQueryHandler(
                    get_trainee_category, pattern=r"^trainee_category:"
                )
            ],
            CONFIRM: [CallbackQueryHandler(confirm, pattern=r"^confirm:")],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )

    app.add_handler(registration)
    update_details = ConversationHandler(
        entry_points=[
            CommandHandler("update", start_update_details),
            CallbackQueryHandler(start_update_details, pattern=r"^menu:update$"),
        ],
        states={
            UPDATE_TITLE: [
                CallbackQueryHandler(get_update_title, pattern=r"^update_title:")
            ],
            UPDATE_TITLE_OTHER: [
                MessageHandler(text_only, get_update_other_title)
            ],
            UPDATE_DAYS: [
                CallbackQueryHandler(get_update_days, pattern=r"^update_days:")
            ],
            UPDATE_REFERRAL: [
                CallbackQueryHandler(
                    get_update_referral, pattern=r"^update_referral:"
                )
            ],
            UPDATE_REFERRAL_OTHER: [
                MessageHandler(text_only, get_update_other_referral)
            ],
            UPDATE_REGION: [MessageHandler(text_only, get_update_region)],
            UPDATE_TRAINEE: [
                CallbackQueryHandler(
                    get_update_trainee, pattern=r"^update_trainee:"
                )
            ],
            UPDATE_TRAINEE_CATEGORY: [
                CallbackQueryHandler(
                    get_update_trainee_category, pattern=r"^trainee_category:"
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )
    app.add_handler(update_details)
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