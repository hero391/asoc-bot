"""All bot messages in English (en) and Amharic (am).

To change a message, edit it here - the bot logic stays untouched.
Use t(lang, "key", name="...") to get a message.
"""

TEXTS = {
    "en": {
        "choose_language": "Please choose your language / እባክዎ ቋንቋ ይምረጡ",
        "welcome": (
            "👋 Welcome to the *African Stroke Organization Conference 2026*\n"
            "_Stroke Care Transformation in Africa_\n\n"
            "📅 November 1-4, 2026\n📍 Adawa Victory Hall, Addis Ababa\n\n"
            "Let's register you. You can type /cancel at any time."
        ),
        "ask_name": "1/6 - Please type your *full name* (as it should appear on your certificate):",
        "bad_name": "Please enter your full name (at least 3 characters).",
        "ask_phone": "2/6 - Your *phone number* (example: +251911234567):",
        "bad_phone": "That phone number doesn't look right. Please try again.",
        "ask_email": "3/6 - Your *email address*:",
        "bad_email": "That email doesn't look right. Please try again.",
        "ask_role": "4/6 - Select your *profession*:",
        "ask_institution": "5/6 - Your *institution* (hospital, university, organization):",
        "bad_institution": "Please enter your institution name.",
        "ask_mode": "6/6 - How will you attend?",
        "confirm_title": "Please check your details:",
        "label_name": "Name",
        "label_phone": "Phone",
        "label_email": "Email",
        "label_role": "Profession",
        "label_institution": "Institution",
        "label_mode": "Attendance",
        "btn_confirm": "✅ Confirm",
        "btn_restart": "✏️ Start again",
        "registered": (
            "✅ *Registration complete!*\n\n"
            "🆔 Your ID: `{reg_code}`\n"
            "👤 {name}\n\n"
            "Show this QR code at the entrance each day.\n"
            "You can get it again anytime with /myqr."
        ),
        "already": "You are already registered. Here is your QR code again:",
        "no_reg": "You are not registered yet. Send /start to register.",
        "cancelled": "Registration cancelled. Send /start to begin again.",
        "help": (
            "Available commands:\n"
            "/start - register for the conference\n"
            "/myqr - show my QR code\n"
            "/cancel - cancel registration\n"
            "/schedule - conference program\n"
            "/now - what is on right now\n"
            "/language - change language\n"
            "/help - this message"
        ),
        "main_menu": "Welcome! Choose an option:",
        "menu_register": "📝 Register for the Conference",
        "menu_program": "📅 Conference Program",
        "menu_venue": "📍 Venue & Directions",
        "menu_contact": "📞 Contact the Organizers",
        "menu_myqr": "🪪 My QR Code",
        "menu_back": "⬅️ Back to menu",
        "menu_directions": "🗺️ Open directions in Google Maps",
        "venue_info": "📍 Venue: {venue}\n📅 Dates: {dates}\n\nTap below to open this venue in Google Maps.",
        "contact_info": (
            "📧 Email: ethiopiastrokefoundation@gmail.com\n"
            "📞 Phone: +251963333388 or +251955235523"
        ),
        # ----- Part 2: schedule -----
        "schedule_pick": "📅 <b>Conference schedule</b>\nChoose a day:",
        "page_of": "Page {page}/{pages}",
        "btn_all_tracks": "All",
        "btn_prev": "◀ Prev",
        "btn_next": "Next ▶",
        "btn_back_days": "📅 All days",
        "btn_today": "📅 Full schedule for today",
        "empty_day": "No sessions found for this day.",
        "no_schedule": "The schedule is not loaded yet. Please try again later.",
        "now_title": "🔴 <b>Happening now</b> ({time})",
        "next_title": "⏭ <b>Up next</b>",
        "nothing_now": "No session is running right now.",
        "nothing_next": "That was the last session of the day.",
        "before_conf": (
            "The conference starts on Sunday, November 1 "
            "(registration opens at 12:00). Use /schedule to see the program."
        ),
        "after_conf": "The conference has ended. Thank you for joining ASOC 2026!",
        "language_pick": "Choose your language / ቋንቋ ይምረጡ",
        "language_set": "✅ Language set to English",
    },
    "am": {
        "choose_language": "Please choose your language / እባክዎ ቋንቋ ይምረጡ",
        "welcome": (
            "👋 እንኳን ወደ *የአፍሪካ ስትሮክ ድርጅት ጉባኤ 2026* በደህና መጡ\n"
            "_በአፍሪካ የስትሮክ ሕክምና ለውጥ_\n\n"
            "📅 ኖቬምበር 1-4, 2026\n📍 አዳዋ ቪክትሪ አዳራሽ፣ አዲስ አበባ\n\n"
            "እንመዝግብዎ። በማንኛውም ጊዜ /cancel ብለው መሰረዝ ይችላሉ።"
        ),
        "ask_name": "1/6 - እባክዎ *ሙሉ ስምዎን* ያስገቡ (በምስክር ወረቀትዎ ላይ እንደሚጻፍ)፦",
        "bad_name": "እባክዎ ሙሉ ስምዎን ያስገቡ (ቢያንስ 3 ፊደላት)።",
        "ask_phone": "2/6 - *የስልክ ቁጥርዎን* ያስገቡ (ለምሳሌ +251911234567)፦",
        "bad_phone": "የስልክ ቁጥሩ ትክክል አይመስልም። እባክዎ እንደገና ያስገቡ።",
        "ask_email": "3/6 - *የኢሜይል አድራሻዎን* ያስገቡ፦",
        "bad_email": "ኢሜይሉ ትክክል አይመስልም። እባክዎ እንደገና ያስገቡ።",
        "ask_role": "4/6 - *ሙያዎን* ይምረጡ፦",
        "ask_institution": "5/6 - *የሚሰሩበት ወይም የሚማሩበት ተቋም* (ሆስፒታል፣ ዩኒቨርሲቲ፣ ድርጅት)፦",
        "bad_institution": "እባክዎ የተቋምዎን ስም ያስገቡ።",
        "ask_mode": "6/6 - እንዴት ይሳተፋሉ?",
        "confirm_title": "እባክዎ መረጃዎን ያረጋግጡ፦",
        "label_name": "ስም",
        "label_phone": "ስልክ",
        "label_email": "ኢሜይል",
        "label_role": "ሙያ",
        "label_institution": "ተቋም",
        "label_mode": "ተሳትፎ",
        "btn_confirm": "✅ አረጋግጥ",
        "btn_restart": "✏️ እንደገና ጀምር",
        "registered": (
            "✅ *ምዝገባዎ ተጠናቀቀ!*\n\n"
            "🆔 መለያ ቁጥርዎ፦ `{reg_code}`\n"
            "👤 {name}\n\n"
            "በየቀኑ መግቢያ ላይ ይህንን QR ኮድ ያሳዩ።\n"
            "በማንኛውም ጊዜ በ /myqr እንደገና ማግኘት ይችላሉ።"
        ),
        "already": "አስቀድመው ተመዝግበዋል። QR ኮድዎ እነሆ፦",
        "no_reg": "እስካሁን አልተመዘገቡም። ለመመዝገብ /start ይጠቀሙ።",
        "cancelled": "ምዝገባ ተሰርዟል። እንደገና ለመጀመር /start ይጠቀሙ።",
        "help": (
            "ያሉ ትዕዛዞች፦\n"
            "/start - ለጉባኤው ይመዝገቡ\n"
            "/myqr - QR ኮዴን አሳይ\n"
            "/cancel - ምዝገባን ሰርዝ\n"
            "/schedule - የጉባኤው መርሐ ግብር\n"
            "/now - አሁን እየተካሄደ ያለው\n"
            "/language - ቋንቋ ቀይር\n"
            "/help - ይህ መልእክት"
        ),
        "main_menu": "እንኳን ደህና መጡ! አንድ አማራጭ ይምረጡ፦",
        "menu_register": "📝 ለጉባኤው ይመዝገቡ",
        "menu_program": "📅 የጉባኤው መርሐ ግብር",
        "menu_venue": "📍 ቦታ እና አቅጣጫ",
        "menu_contact": "📞 አዘጋጆችን ያግኙ",
        "menu_myqr": "🪪 የእኔ QR ኮድ",
        "menu_back": "⬅️ ወደ ምናሌው ተመለስ",
        "menu_directions": "🗺️ በGoogle Maps አቅጣጫውን ይክፈቱ",
        "venue_info": "📍 ቦታ፦ {venue}\n📅 ቀናት፦ {dates}\n\nቦታውን በGoogle Maps ለማየት ከታች ይጫኑ።",
        "contact_info": (
            "📧 ኢሜይል: ethiopiastrokefoundation@gmail.com\n"
            "📞 ስልክ: +251963333388 ወይም +251955235523"
        ),
        # ----- Part 2: schedule -----
        "schedule_pick": "📅 <b>የጉባኤው መርሐ ግብር</b>\nቀን ይምረጡ፦",
        "page_of": "ገጽ {page}/{pages}",
        "btn_all_tracks": "ሁሉም",
        "btn_prev": "◀ ቀዳሚ",
        "btn_next": "ቀጣይ ▶",
        "btn_back_days": "📅 ሁሉም ቀናት",
        "btn_today": "📅 የዛሬው ሙሉ መርሐ ግብር",
        "empty_day": "ለዚህ ቀን ምንም ክፍለ ጊዜ አልተገኘም።",
        "no_schedule": "መርሐ ግብሩ ገና አልተጫነም። እባክዎ ቆይተው ይሞክሩ።",
        "now_title": "🔴 <b>አሁን እየተካሄደ ያለ</b> ({time})",
        "next_title": "⏭ <b>ቀጣይ</b>",
        "nothing_now": "በአሁኑ ሰዓት የሚካሄድ ክፍለ ጊዜ የለም።",
        "nothing_next": "ይህ የዛሬው የመጨረሻ ክፍለ ጊዜ ነበር።",
        "before_conf": (
            "ጉባኤው እሑድ ኖቬምበር 1 ይጀምራል (ምዝገባ ከ12:00 ጀምሮ)። "
            "መርሐ ግብሩን ለማየት /schedule ይጠቀሙ።"
        ),
        "after_conf": "ጉባኤው ተጠናቋል። በASOC 2026 ስለተሳተፉ እናመሰግናለን!",
        "language_pick": "Choose your language / ቋንቋ ይምረጡ",
        "language_set": "✅ ቋንቋ ወደ አማርኛ ተቀይሯል",
    },
}

# (key stored in database, English label, Amharic label)
ROLES = [
    ("doctor", "🩺 Doctor", "🩺 ሐኪም"),
    ("nurse", "💉 Nurse", "💉 ነርስ"),
    ("student", "🎓 Medical student", "🎓 የሕክምና ተማሪ"),
    ("researcher", "🔬 Researcher", "🔬 ተመራማሪ"),
    ("administrator", "🏥 Hospital administrator", "🏥 የሆስፒታል አስተዳዳሪ"),
    ("other", "👥 Other healthcare professional", "👥 ሌላ የጤና ባለሙያ"),
]

MODES = [
    ("in_person", "🏛 In person", "🏛 በአካል"),
    ("virtual", "💻 Virtual (online)", "💻 በበይነመረብ"),
]


def t(lang: str, key: str, **kwargs) -> str:
    text = TEXTS.get(lang, TEXTS["en"]).get(key) or TEXTS["en"][key]
    return text.format(**kwargs) if kwargs else text


def label_for(options, key: str, lang: str) -> str:
    """Find the nice label (en/am) for a stored key such as 'doctor'."""
    idx = 2 if lang == "am" else 1
    for option in options:
        if option[0] == key:
            return option[idx]
    return key


# ===== Part 2: schedule constants =====

# (date, English button label, Amharic button label) - Day 0 is the pre-conference
DAY_INFO = [
    ("2026-11-01", "Day 0 · Sun, Nov 1 · Pre-conference", "ቀን 0 · እሑድ፣ ኖቬምበር 1 · ቅድመ ጉባኤ"),
    ("2026-11-02", "Day 1 · Mon, Nov 2", "ቀን 1 · ሰኞ፣ ኖቬምበር 2"),
    ("2026-11-03", "Day 2 · Tue, Nov 3", "ቀን 2 · ማክሰኞ፣ ኖቬምበር 3"),
    ("2026-11-04", "Day 3 · Wed, Nov 4", "ቀን 3 · ረቡዕ፣ ኖቬምበር 4"),
]

# track key -> (English, Amharic). "common" rows (breaks, lunch, registration)
# show under every track and are not listed here.
TRACKS = {
    "main": ("Main program", "ዋና መርሐ ግብር"),
    "workshop": ("Workshops", "ወርክሾፖች"),
    "nursing": ("Nursing symposium", "የነርሶች ሲምፖዚየም"),
    "community": ("Life after stroke", "ከስትሮክ በኋላ ሕይወት"),
    "education": ("Education track", "የትምህርት ክፍለ ጊዜ"),
}

KIND_ICONS = {
    "talk": "🎤",
    "session": "📋",
    "workshop": "🛠",
    "qa": "❓",
    "break": "☕",
    "meal": "🍽",
    "registration": "📝",
    "ceremony": "🏛",
    "debate": "⚔️",
    "award": "🏆",
    "sponsor": "🤝",
}


def track_label(track: str, lang: str) -> str:
    pair = TRACKS.get(track)
    if not pair:
        return track
    return pair[1] if lang == "am" else pair[0]


def day_label(index: int, lang: str) -> str:
    info = DAY_INFO[index]
    return info[2] if lang == "am" else info[1]