"""Part 2: /schedule, /now and /language.

/schedule -> pick a day -> sessions list (with track filter and pages)
/now      -> what is happening right now and what comes next
"""
import logging
import html
from datetime import datetime
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

import config
import db
from helpers import get_lang
from schedule_import import import_csv
from texts import DAY_INFO, KIND_ICONS, day_label, t, track_label

# Telegram allows 4096 characters per message. We stay well below it.
PAGE_LIMIT = 3300
log = logging.getLogger(__name__)


def ensure_schedule_loaded() -> int:
    """Load the configured CSV when the active database has no program rows."""
    count = db.count_sessions()
    if count:
        return count

    csv_path = Path(config.SESSIONS_CSV)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Conference schedule CSV not found: {csv_path}")

    count = import_csv(str(csv_path))
    if not count:
        raise ValueError(f"Conference schedule CSV contains no sessions: {csv_path}")
    return count


# ---------- time ----------
def now_local() -> datetime:
    """Current time in Addis Ababa (or FAKE_NOW from .env while testing)."""
    if config.FAKE_NOW:
        return datetime.strptime(config.FAKE_NOW, "%Y-%m-%d %H:%M").replace(
            tzinfo=config.TIMEZONE
        )
    return datetime.now(config.TIMEZONE)


# ---------- formatting ----------
def fmt_session(row, lang: str, show_track: bool) -> str:
    icon = KIND_ICONS.get(row["kind"], "🎤")
    title = row["title_am"] if lang == "am" and row["title_am"] else row["title_en"]
    line = f"<b>{row['start']}–{row['end']}</b> {icon} {html.escape(title)}"
    if row["speaker"]:
        line += f"\n      👤 {html.escape(row['speaker'])}"
    if show_track and row["track"] not in ("main", "common"):
        line += f"\n      🏷 <i>{html.escape(track_label(row['track'], lang))}</i>"
    return line


def build_pages(rows, lang: str, show_track: bool) -> list:
    """Turn a list of sessions into one or more messages under the size limit."""
    blocks, last_group = [], None
    for row in rows:
        block = ""
        group = row["group_name"]
        if group and group != last_group:
            block += f"\n📚 <b>{html.escape(group)}</b>\n"
            last_group = group
        block += fmt_session(row, lang, show_track)
        blocks.append(block)

    pages, current, size = [], [], 0
    for block in blocks:
        if current and size + len(block) > PAGE_LIMIT:
            pages.append("\n".join(current))
            current, size = [], 0
        current.append(block)
        size += len(block) + 1
    if current:
        pages.append("\n".join(current))
    return pages


# ---------- keyboards ----------
def days_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(day_label(i, lang), callback_data=f"sch:d:{i}:all:0")]
        for i in range(len(DAY_INFO))
    ]
    rows.append(
        [InlineKeyboardButton(t(lang, "menu_back"), callback_data="menu:home")]
    )
    return InlineKeyboardMarkup(rows)


def day_keyboard(lang, day_idx, track, page, pages, tracks) -> InlineKeyboardMarkup:
    rows = []

    # track filter (only when the day has parallel tracks)
    if len(tracks) > 1:
        buttons = []
        for key in ["all"] + tracks:
            label = t(lang, "btn_all_tracks") if key == "all" else track_label(key, lang)
            if key == track:
                label = f"• {label}"
            buttons.append(
                InlineKeyboardButton(label, callback_data=f"sch:d:{day_idx}:{key}:0")
            )
        rows += [buttons[i : i + 2] for i in range(0, len(buttons), 2)]

    # previous / next page
    if pages > 1:
        nav = []
        if page > 0:
            nav.append(
                InlineKeyboardButton(
                    t(lang, "btn_prev"),
                    callback_data=f"sch:d:{day_idx}:{track}:{page - 1}",
                )
            )
        if page < pages - 1:
            nav.append(
                InlineKeyboardButton(
                    t(lang, "btn_next"),
                    callback_data=f"sch:d:{day_idx}:{track}:{page + 1}",
                )
            )
        rows.append(nav)

    rows.append(
        [InlineKeyboardButton(t(lang, "btn_back_days"), callback_data="sch:menu")]
    )
    rows.append(
        [InlineKeyboardButton(t(lang, "menu_back"), callback_data="menu:home")]
    )
    return InlineKeyboardMarkup(rows)


# ---------- /schedule ----------
async def schedule_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    message = update.effective_message
    try:
        ensure_schedule_loaded()
    except (FileNotFoundError, ValueError) as err:
        log.exception("Could not load the conference schedule")
        await message.reply_text(t(lang, "no_schedule"))
        return
    await message.reply_text(
        t(lang, "schedule_pick"),
        parse_mode=ParseMode.HTML,
        reply_markup=days_keyboard(lang),
    )


async def menu_program_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await schedule_cmd(update, context)


async def edit_or_ignore(query, text, keyboard):
    """Edit the message; ignore Telegram's 'message is not modified' error."""
    try:
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )
    except BadRequest as err:
        if "not modified" not in str(err).lower():
            raise


async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(update, context)
    parts = query.data.split(":")  # sch:menu   or   sch:d:<day>:<track>:<page>

    if parts[1] == "menu":
        await edit_or_ignore(query, t(lang, "schedule_pick"), days_keyboard(lang))
        return

    day_idx, track, page = int(parts[2]), parts[3], int(parts[4])
    if not 0 <= day_idx < len(DAY_INFO):
        return
    date = DAY_INFO[day_idx][0]

    rows = db.get_sessions(date, None if track == "all" else track)
    tracks = db.get_tracks(date)
    if not rows:
        await edit_or_ignore(
            query, t(lang, "empty_day"), days_keyboard(lang)
        )
        return

    pages = build_pages(rows, lang, show_track=(track == "all" and len(tracks) > 1))
    page = max(0, min(page, len(pages) - 1))

    header = f"<b>{html.escape(day_label(day_idx, lang))}</b>"
    if track != "all":
        header += f"  ·  {html.escape(track_label(track, lang))}"
    if len(pages) > 1:
        header += "\n" + t(lang, "page_of", page=page + 1, pages=len(pages))
    text = header + "\n\n" + pages[page]

    await edit_or_ignore(
        query, text, day_keyboard(lang, day_idx, track, page, len(pages), tracks)
    )


# ---------- /now ----------
async def now_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    if db.count_sessions() == 0:
        await update.message.reply_text(t(lang, "no_schedule"))
        return

    now = now_local()
    date, hhmm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    dates = [d[0] for d in DAY_INFO]

    if date < dates[0]:
        await update.message.reply_text(t(lang, "before_conf"))
        return
    if date > dates[-1]:
        await update.message.reply_text(t(lang, "after_conf"))
        return
    if date not in dates:  # a date between conference days (not expected)
        await update.message.reply_text(t(lang, "nothing_now"))
        return

    current = db.get_sessions_at(date, hhmm)
    upcoming = db.get_next_sessions(date, hhmm)

    parts = []
    if current:
        parts.append(t(lang, "now_title", time=hhmm))
        parts += [fmt_session(r, lang, show_track=True) for r in current]
    else:
        parts.append(t(lang, "nothing_now"))

    parts.append("")
    if upcoming:
        parts.append(t(lang, "next_title"))
        parts += [fmt_session(r, lang, show_track=True) for r in upcoming]
    else:
        parts.append(t(lang, "nothing_next"))

    day_idx = dates.index(date)
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(t(lang, "btn_today"), callback_data=f"sch:d:{day_idx}:all:0")]]
    )
    await update.message.reply_text(
        "\n".join(parts),
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard,
    )


# ---------- /language ----------
async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="setlang:en"),
                InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="setlang:am"),
            ]
        ]
    )
    await update.message.reply_text(t("en", "language_pick"), reply_markup=keyboard)


async def setlang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split(":")[1]
    context.user_data["lang_pref"] = lang
    db.set_language(update.effective_user.id, lang)  # does nothing if not registered
    await query.edit_message_text(t(lang, "language_set"))


# ---------- connect everything to the bot ----------
def register(app: Application):
    app.add_handler(CommandHandler("schedule", schedule_cmd))
    app.add_handler(
        CallbackQueryHandler(menu_program_callback, pattern=r"^menu:program$"),
        group=1,
    )
    app.add_handler(CommandHandler("now", now_cmd))
    app.add_handler(CommandHandler("language", language_cmd))
    app.add_handler(CallbackQueryHandler(schedule_callback, pattern=r"^sch:"))
    app.add_handler(CallbackQueryHandler(setlang_callback, pattern=r"^setlang:"))