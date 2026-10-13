"""Small helpers shared by several files."""
import db


def get_lang(update, context) -> str:
    """Language to answer in: chosen with /language, else registration, else English."""
    pref = context.user_data.get("lang_pref")
    if pref:
        return pref
    reg = db.get_registration(update.effective_user.id)
    return reg["language"] if reg else "en"