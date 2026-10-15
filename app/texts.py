"""All bot messages in English (en) and Amharic (am).

To change a message, edit it here - the bot logic stays untouched.
Use t(lang, "key", name="...") to get a message.
"""

TEXTS = {
    "en": {
        "choose_language": "Please choose your language / እባክዎ ቋንቋ ይምረጡ",
        "welcome": (
            "👋 Welcome to the *ESF 2026 Comprehensive Stroke Care Symposium*\n"
            "_Establishing comprehensive stroke care in low- and middle-income countries_\n\n"
            "📅 November 2 & 3, 2026\n"
            "📍 Adwa Memorial Museum Multi Purpose Hall\n\n"
            "Let's register you. You can type /cancel at any time."
        ),
        "ask_title": "What title should appear with your name?",
        "ask_other_title": "Please type your title:",
        "ask_days": "Which conference day(s) will you attend? Select all that apply, then tap Done.",
        "days_done": "✅ Done",
        "days_need_one": "Please select at least one conference day.",
        "ask_referral": "How did you hear about this event?",
        "ask_other_referral": "Please tell us how you heard about this event:",
        "ask_region": "Which region or city are you from?",
        "ask_trainee": "Are you a student, intern, resident, or fellow?",
        "ask_trainee_category": "Which category best describes you?",
        "yes": "Yes",
        "no": "No",
        "menu_update": "📝 Complete registration details",
        "update_prompt": "Please complete your registration details so we have your full attendee information.",
        "update_saved": "✅ Your registration details have been updated.",
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
            "/start - register for the symposium\n"
            "/myqr - show my QR code\n"
            "/update - complete or update registration details\n"
            "/cancel - cancel registration\n"
            "/schedule - symposium program\n"
            "/now - what is on right now\n"
            "/language - change language\n"
            "/help - this message"
        ),
        "main_menu": "Welcome to the ESF 2026 symposium! Choose an option:",
        "menu_register": "📝 Register for the Symposium",
        "menu_program": "📅 Symposium Program",
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
        "title_other": "Other (type your title)",
        "referral_invitation": "Invitation from the organizers",
        "referral_colleague": "Colleague",
        "referral_organization": "Employer or university",
        "referral_social": "Social media",
        "referral_email": "Email",
        "referral_other": "Other",
        "trainee_student": "Student",
        "trainee_intern": "Intern",
        "trainee_resident": "Resident",
        "trainee_fellow": "Fellow",
        # ----- Part 2: schedule -----
        "schedule_pick": "📅 <b>Symposium schedule</b>\nChoose a day:",
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
            "The symposium starts on Monday, November 2. Use /schedule to see the program."
        ),
        "after_conf": "The symposium has ended. Thank you for joining ESF 2026!",
        "language_pick": "Choose your language / ቋንቋ ይምረጡ",
        "language_set": "✅ Language set to English",
    },
    "am": {
        "choose_language": "Please choose your language / እባክዎ ቋንቋ ይምረጡ",
        "welcome": (
            "👋 እንኳን ወደ *ESF 2026 Comprehensive Stroke Care Symposium* በደህና መጡ\n"
            "_በዝቅተኛና መካከለኛ ገቢ ባላቸው አገሮች የተሟላ የስትሮክ ሕክምና ማቋቋም_\n\n"
            "📅 ኖቬምበር 2 እና 3፣ 2026\n"
            "📍 አድዋ መታሰቢያ ሙዚየም ሁለገብ አዳራሽ\n\n"
            "እንመዝግብዎ። በማንኛውም ጊዜ /cancel ብለው መሰረዝ ይችላሉ።"
        ),
        "ask_title": "ከስምዎ በፊት ምን የክብር መጠሪያ ይጠቀሙ?",
        "ask_other_title": "እባክዎ የክብር መጠሪያዎን ያስገቡ፦",
        "ask_days": "የሚሳተፉባቸውን የጉባኤ ቀን(ዎች) ይምረጡ፤ ከዚያ ተጠናቋልን ይጫኑ።",
        "days_done": "✅ ተጠናቋል",
        "days_need_one": "እባክዎ ቢያንስ አንድ የጉባኤ ቀን ይምረጡ።",
        "ask_referral": "ስለዚህ ዝግጅት እንዴት ሰሙ?",
        "ask_other_referral": "ስለዚህ ዝግጅት እንዴት እንደሰሙ ይጻፉ፦",
        "ask_region": "ከየትኛው ክልል ወይም ከተማ ነዎት?",
        "ask_trainee": "ተማሪ፣ ሰልጣኝ፣ ሬዚደንት ወይም ፌሎው ነዎት?",
        "ask_trainee_category": "ከእነዚህ ውስጥ የትኛው ይመለከትዎታል?",
        "yes": "አዎ",
        "no": "አይ",
        "menu_update": "📝 የምዝገባ መረጃን ያሟሉ",
        "update_prompt": "ሙሉ የተሳታፊ መረጃዎን ለማስቀመጥ እባክዎ የምዝገባ መረጃዎን ያሟሉ።",
        "update_saved": "✅ የምዝገባ መረጃዎ ተዘምኗል።",
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
            "/start - ለሲምፖዚየሙ ይመዝገቡ\n"
            "/myqr - QR ኮዴን አሳይ\n"
            "/update - የምዝገባ መረጃን ያሟሉ ወይም ያዘምኑ\n"
            "/cancel - ምዝገባን ሰርዝ\n"
            "/schedule - የሲምፖዚየሙ መርሐ ግብር\n"
            "/now - አሁን እየተካሄደ ያለው\n"
            "/language - ቋንቋ ቀይር\n"
            "/help - ይህ መልእክት"
        ),
        "main_menu": "እንኳን ደህና መጡ! አንድ አማራጭ ይምረጡ፦",
        "menu_register": "📝 ለሲምፖዚየሙ ይመዝገቡ",
        "menu_program": "📅 የሲምፖዚየሙ መርሐ ግብር",
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
        "title_other": "ሌላ (የክብር መጠሪያዎን ይጻፉ)",
        "referral_invitation": "ከአዘጋጆቹ ግብዣ",
        "referral_colleague": "ከሥራ ባልደረባ",
        "referral_organization": "ከቀጣሪ ወይም ዩኒቨርሲቲ",
        "referral_social": "ማህበራዊ ሚዲያ",
        "referral_email": "ኢሜይል",
        "referral_other": "ሌላ",
        "trainee_student": "ተማሪ",
        "trainee_intern": "ሰልጣኝ",
        "trainee_resident": "ሬዚደንት",
        "trainee_fellow": "ፌሎው",
        # ----- Part 2: schedule -----
        "schedule_pick": "📅 <b>የሲምፖዚየሙ መርሐ ግብር</b>\nቀን ይምረጡ፦",
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
            "ሲምፖዚየሙ ሰኞ ኖቬምበር 2 ይጀምራል። "
            "መርሐ ግብሩን ለማየት /schedule ይጠቀሙ።"
        ),
        "after_conf": "ሲምፖዚየሙ ተጠናቋል። በESF 2026 ስለተሳተፉ እናመሰግናለን!",
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

TITLES = [
    ("dr", "Dr.", "ዶ/ር"),
    ("prof", "Prof.", "ፕሮፌሰር"),
    ("mr", "Mr.", "አቶ"),
    ("ms", "Ms.", "ወ/ሮ"),
    ("mrs", "Mrs.", "ወ/ወ"),
    ("other", "Other (type your title)", "ሌላ (የክብር መጠሪያዎን ይጻፉ)"),
]

REFERRAL_SOURCES = [
    ("invitation", "Invitation from the organizers", "ከአዘጋጆቹ ግብዣ"),
    ("colleague", "Colleague", "ከሥራ ባልደረባ"),
    ("organization", "Employer or university", "ከቀጣሪ ወይም ዩኒቨርሲቲ"),
    ("social", "Social media", "ማህበራዊ ሚዲያ"),
    ("email", "Email", "ኢሜይል"),
    ("other", "Other", "ሌላ"),
]

TRAINEE_CATEGORIES = [
    ("student", "Student", "ተማሪ"),
    ("intern", "Intern", "ሰልጣኝ"),
    ("resident", "Resident", "ሬዚደንት"),
    ("fellow", "Fellow", "ፌሎው"),
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

# All dates present in the supplied program, including archived pre/post-symposium rows.
PROGRAM_DAY_INFO = [
    ("2026-11-01", "Day 0 · Sun, Nov 1 · Pre-conference", "ቀን 0 · እሑድ፣ ኖቬምበር 1 · ቅድመ ጉባኤ"),
    ("2026-11-02", "Day 1 · Mon, Nov 2", "ቀን 1 · ሰኞ፣ ኖቬምበር 2"),
    ("2026-11-03", "Day 2 · Tue, Nov 3", "ቀን 2 · ማክሰኞ፣ ኖቬምበር 3"),
    ("2026-11-04", "Day 3 · Wed, Nov 4", "ቀን 3 · ረቡዕ፣ ኖቬምበር 4"),
]
DAY_INFO = PROGRAM_DAY_INFO[1:3]

# track key -> (English, Amharic). "common" rows (breaks, lunch, registration)
# show under every track and are not listed here.
TRACKS = {
    "main": ("Main program", "ዋና መርሐ ግብር"),
    "workshop": ("Workshops", "ወርክሾፖች"),
    "nursing": ("Nursing symposium", "የነርሶች ሲምፖዚየም"),
    "community": ("Life after stroke", "ከስትሮክ በኋላ ሕይወት"),
    "education": ("Education track", "የትምህርት ክፍለ ጊዜ"),
    "symposium": (
        "ESF Comprehensive Stroke Care Symposium",
        "የኢትዮጵያ ስትሮክ ፋውንዴሽን የተሟላ የስትሮክ ሕክምና ሲምፖዚየም",
    ),
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