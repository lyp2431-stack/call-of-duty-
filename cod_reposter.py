import os
import re
import json
import asyncio
from datetime import datetime, timezone
from typing import List, Tuple, Optional

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from telethon.tl import types

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None


# ============================================================
# ENV HELPERS - برای Railway و اجرای لوکال
# ============================================================

def get_env_value(name: str, default=None):
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return value


def get_env_int(name: str, default: int = 0) -> int:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    try:
        return int(value)
    except Exception:
        return default


# ============================================================
# CONFIG - مقادیر اصلی
# ============================================================

API_ID = get_env_int("API_ID", 25721698)

# روی Railway مقدار واقعی API_HASH را داخل Variables بگذار.
API_HASH = get_env_value("API_HASH", "PUT_YOUR_API_HASH_HERE")

SESSION_NAME = get_env_value("SESSION_NAME", "my_telegram_account")

# مقدار TELEGRAM_SESSION_STRING را از generate_session.py بگیر و داخل Railway Variables بگذار.
TELEGRAM_SESSION_STRING = get_env_value("TELEGRAM_SESSION_STRING", "")

# کانال مبدا A
SOURCE_CHANNEL = get_env_value("SOURCE_CHANNEL", "@channelAtes")

# کانال مقصد B
DEST_CHANNEL = get_env_value("DEST_CHANNEL", "@channelBtest")

# حالت اجرا:
# "RUN" برای اجرای اصلی
# "EMOJI_IDS" برای گرفتن document_id ایموجی‌های پرمیوم از Saved Messages
RUN_MODE = get_env_value("RUN_MODE", "RUN")

ONLY_VIDEO = True
USE_TRANSLATOR = True
SKIP_IF_DESCRIPTION_EMPTY = True

# کپشن ویدیو در تلگرام محدودیت دارد.
MAX_CAPTION_LENGTH = 1024

# برای Railway اگر Volume ساختی، DATA_DIR را بگذار /data
DATA_DIR = get_env_value("DATA_DIR", ".")

TEMP_DOWNLOAD_DIR = os.path.join(DATA_DIR, "temp_downloads")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed_messages.json")

# شمارنده اکانت
ACCOUNT_COUNTER_START = get_env_int("ACCOUNT_COUNTER_START", 1882)
ACCOUNT_COUNTER_FILE = os.path.join(DATA_DIR, "account_counter.json")


# ============================================================
# LINKS - لینک‌های آبی فرم خودت
# ============================================================

GROUP_USERNAME = "@M_COD"
GROUP_URL = "https://t.me/M_COD"

MM_USERNAME = "@Reall"
MM_URL = "https://t.me/Reall"

TERMS_URL = "https://t.me/CODProtect"
REVIEWS_URL = "https://t.me/CODVC"
HOW_IT_WORKS_URL = "https://t.me/CODProtect/119"
WEBSITE_URL = "https://codbuysell.vercel.app/"
AD_POSTING_BOT_URL = "https://t.me/COD_ADBOT"

BUY_NOW_URL = "https://t.me/Reall"
SELL_YOUR_ACCOUNT_URL = "https://t.me/Reall"

COD_BUY_SELL_URL = "https://t.me/COD_BUY_SELL"


# ============================================================
# QUOTE SETTINGS
# ============================================================

QUOTE_HASHTAGS = True
QUOTE_ACTION_BUTTONS = True


# ============================================================
# CUSTOM PREMIUM EMOJI IDS
# ============================================================

CUSTOM_EMOJI_IDS = {
    "red_triangle": 5972290052451994935,
    "green_circle": 5215685881989442149,
    "link": 5215441850537618106,
    "outbox": 5873225338984599714,
    "money": 5213094908608392768,
    "chat": 5872886929921413168,
    "person": 5870994129244131212,
    "card": 6041815299412463725,
    "memo": 5960551395730919906,
    "question": 5872996816659681395,
    "globe": 5870718740236079262,
    "robot": 5985780596268339498,
    "mm_badge": 0,
}


# ============================================================
# CALL OF DUTY LOGO - 12 CUSTOM EMOJI PIECES
# ============================================================

COD_LOGO_FALLBACK_EMOJI = "🫧"

COD_LOGO_CUSTOM_EMOJI_IDS = [
    5170359296818414550,
    5170609925340005280,
    5170162050445345727,
    5172460553733408202,
    5172741483249271690,
    5170391461828494206,
    5170674117921211510,
    5170201894856951345,
    5170501662099374770,
    5172766699002266296,
    5172551052989301894,
    5170214878543086497,
]


# ============================================================
# FORM SETTINGS
# ============================================================

ACCOUNT_NUMBER_TAG = "#account_number"

HASHTAGS = "#COD #CODBUY #CODSELL\n#CALLOFDUTY #CALL_OF_DUTY\n#ACCOUNTCOD"

# اگر قیمت پیدا نشود، این متن نوشته می‌شود.
ACCOUNT_PRICE_FALLBACK_TEXT = "DM for price"

# نرخ تبدیل دلار به تومان
USD_RATE_TOMAN = get_env_int("USD_RATE_TOMAN", 160000)


# ============================================================
# SOURCE CAPTION FILTER SETTINGS
# ============================================================

DESCRIPTION_MARKERS = [
    "توضیحات اکانت",
    "توضیحات",
    "📄 توضیحات اکانت",
    "📄 توضیحات",
]

FORBIDDEN_LINE_KEYWORDS = [
    "قیمت",
    "قيمت",
    "تومان",
    "تومن",
    "خرید",
    "فروش",
    "جهت خرید",
    "آیدی",
    "ایدی",
    "واسطه",
    "قانونی",
    "نماد اعتماد",
    "اکتیویژن",
    "اکتی",
    "فیس",
    "فیسبوک",
    "دیس",
    "دیسیبل",
    "لاین",
    "اپل",
    "لینک",
    "لینک شده",
    "price",
    "buy",
    "sell",
    "activision",
    "acti",
    "facebook",
    "fb",
    "apple",
    "line",
    "linked",
    "link",
    "disabled",
    "disable",
]

END_SECTION_KEYWORDS = [
    "قیمت",
    "قيمت",
    "تومان",
    "تومن",
    "جهت خرید",
    "آیدی",
    "ایدی",
    "واسطه",
    "خرید سی پی",
    "خرید cp",
    "💵",
    "💸",
    "💰",
]


# ============================================================
# BASIC UTILITIES
# ============================================================

def parse_entity_ref(value):
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()
        if re.fullmatch(r"-?\d+", value):
            return int(value)
        return value

    return value


SOURCE_ENTITY = parse_entity_ref(SOURCE_CHANNEL)
DEST_ENTITY = parse_entity_ref(DEST_CHANNEL)


def ensure_parent_dir(file_path: str) -> None:
    directory = os.path.dirname(file_path)

    if directory:
        os.makedirs(directory, exist_ok=True)


def load_processed_ids() -> set:
    if not os.path.exists(PROCESSED_FILE):
        return set()

    try:
        with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception:
        return set()


def save_processed_ids(processed_ids: set) -> None:
    ensure_parent_dir(PROCESSED_FILE)

    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f, ensure_ascii=False, indent=2)


def load_account_counter() -> int:
    if not os.path.exists(ACCOUNT_COUNTER_FILE):
        return ACCOUNT_COUNTER_START

    try:
        with open(ACCOUNT_COUNTER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            value = int(data.get("next_account_number", ACCOUNT_COUNTER_START))
            return value
    except Exception:
        return ACCOUNT_COUNTER_START


def save_account_counter(next_number: int) -> None:
    ensure_parent_dir(ACCOUNT_COUNTER_FILE)

    with open(ACCOUNT_COUNTER_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"next_account_number": int(next_number)},
            f,
            ensure_ascii=False,
            indent=2,
        )


def increment_account_counter(current_number: int) -> None:
    save_account_counter(int(current_number) + 1)


def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = {
        "ي": "ی",
        "ك": "ک",
        "\u200c": " ",
        "\u200f": "",
        "\u200e": "",
        "\ufeff": "",
        "‌": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# ============================================================
# PRICE EXTRACTION / TOMAN TO USD
# ============================================================

PERSIAN_ARABIC_DIGITS_MAP = str.maketrans({
    "۰": "0",
    "۱": "1",
    "۲": "2",
    "۳": "3",
    "۴": "4",
    "۵": "5",
    "۶": "6",
    "۷": "7",
    "۸": "8",
    "۹": "9",
    "٠": "0",
    "١": "1",
    "٢": "2",
    "٣": "3",
    "٤": "4",
    "٥": "5",
    "٦": "6",
    "٧": "7",
    "٨": "8",
    "٩": "9",
})

PRICE_HINT_KEYWORDS = [
    "قیمت",
    "قيمت",
    "مبلغ",
    "تومان",
    "تومن",
    "تومنی",
    "ملیون",
    "میلیون",
    "میلیونی",
    "ميليون",
    "میل",
    "مل",
    "فروش",
    "فروشی",
    "price",
    "prc",
    "toman",
    "tomans",
    "tmn",
    "irt",
    "rial",
    "irr",
    "mil",
    "mill",
    "million",
    "mln",
    "$",
    "💰",
    "💵",
    "💸",
]

PRICE_NEGATIVE_KEYWORDS = [
    "uid",
    "آیدی",
    "ایدی",
    "id",
    "اکتیویژن",
    "اکتی",
    "activision",
    "facebook",
    "فیسبوک",
    "فیس",
    "apple",
    "اپل",
    "line",
    "لاین",
    "لینک",
    "link",
    "linked",
]


def normalize_price_text(text: str) -> str:
    text = normalize_text(text)
    text = text.translate(PERSIAN_ARABIC_DIGITS_MAP)

    text = text.replace("٬", ",")
    text = text.replace("٫", ".")
    text = text.replace("،", ",")
    text = re.sub(r"[ـ]+", "", text)
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def line_has_price_hint(line: str) -> bool:
    low = normalize_price_text(line).lower()
    return any(keyword.lower() in low for keyword in PRICE_HINT_KEYWORDS)


def line_has_negative_price_keyword(line: str) -> bool:
    low = normalize_price_text(line).lower()
    return any(keyword.lower() in low for keyword in PRICE_NEGATIVE_KEYWORDS)


def looks_like_uid_or_phone(line: str) -> bool:
    clean = normalize_price_text(line)

    if re.search(r"\buid\b", clean, flags=re.IGNORECASE):
        return True

    if re.search(r"\buser\s*id\b", clean, flags=re.IGNORECASE):
        return True

    # عددهای خیلی بلند معمولا UID / ID / شماره هستند.
    if re.search(r"\d{9,}", clean):
        return True

    return False


def extract_price_candidate_lines(caption: str) -> List[str]:
    caption = normalize_price_text(caption)

    if not caption:
        return []

    lines = [normalize_price_text(x) for x in caption.splitlines()]
    lines = [x for x in lines if x.strip()]

    candidate_lines = []
    take_next = 0

    for line in lines:
        clean_line = line.strip()

        if not clean_line:
            continue

        if looks_like_uid_or_phone(clean_line):
            continue

        has_hint = line_has_price_hint(clean_line)

        if has_hint:
            candidate_lines.append(clean_line)
            take_next = 2
            continue

        if take_next > 0:
            if not line_has_negative_price_keyword(clean_line):
                candidate_lines.append(clean_line)
            take_next -= 1

    if not candidate_lines:
        for line in lines:
            if looks_like_uid_or_phone(line):
                continue

            if "💰" in line or "💵" in line or "💸" in line:
                candidate_lines.append(line)

    return candidate_lines


def parse_number_value(raw_number: str) -> Optional[float]:
    if not raw_number:
        return None

    raw_number = normalize_price_text(raw_number).strip()

    if "." in raw_number and "," in raw_number:
        cleaned = raw_number.replace(",", "").replace(".", "")
        try:
            return float(cleaned)
        except Exception:
            return None

    # مثل 3,00 یا 3.00
    if re.fullmatch(r"\d{1,3}[,.]\d{1,2}", raw_number):
        try:
            return float(raw_number.replace(",", "."))
        except Exception:
            return None

    # مثل 111,111 یا 400.000 یا 3.000
    if re.fullmatch(r"\d{1,3}([,.]\d{3})+", raw_number):
        cleaned = raw_number.replace(",", "").replace(".", "")
        try:
            return float(cleaned)
        except Exception:
            return None

    if "," in raw_number or "." in raw_number:
        try:
            return float(raw_number.replace(",", "."))
        except Exception:
            pass

        cleaned = raw_number.replace(",", "").replace(".", "")
        try:
            return float(cleaned)
        except Exception:
            return None

    try:
        return float(raw_number)
    except Exception:
        return None


def infer_toman_from_number_and_suffix(raw_number: str, suffix: str = "") -> Optional[int]:
    """
    قوانین:
    117 Mil => 117,000,000
    117 میلیون => 117,000,000
    111,111 => 111,000,000
    400.000 => 400,000,000
    400,000 => 400,000,000
    3,00 => 3,000,000
    3.000 => 3,000,000
    7500 => 7,500,000
    8500 => 8,500,000
    4000000 => 400,000,000
    """
    raw_number = normalize_price_text(raw_number)
    suffix = normalize_price_text(suffix).lower()

    value = parse_number_value(raw_number)

    if value is None or value <= 0:
        return None

    million_suffixes = [
        "mil",
        "mill",
        "million",
        "mln",
        "میلیون",
        "ملیون",
        "ميليون",
        "میلیونی",
        "ملیونی",
        "میل",
        "مل",
    ]

    billion_suffixes = [
        "b",
        "bil",
        "billion",
        "میلیارد",
        "مليارد",
    ]

    if any(s in suffix for s in million_suffixes):
        return int(round(value * 1_000_000))

    if any(s in suffix for s in billion_suffixes):
        return int(round(value * 1_000_000_000))

    only_digits = re.sub(r"\D", "", raw_number)
    has_separator = "," in raw_number or "." in raw_number

    if not only_digits:
        return None

    digit_len = len(only_digits)

    # 3,00 یعنی 3 میلیون
    if re.fullmatch(r"\d{1,3}[,.]\d{1,2}", raw_number):
        return int(round(value * 1_000_000))

    # 3.000 / 111,111 / 400.000
    if has_separator:
        grouped_value = parse_number_value(raw_number)

        if grouped_value is None:
            return None

        if grouped_value < 1_000_000:
            first_part = re.split(r"[,.]", raw_number)[0]
            try:
                first_value = float(first_part)
                return int(round(first_value * 1_000_000))
            except Exception:
                pass

        if grouped_value >= 10_000_000:
            return int(round(grouped_value))

        return int(round(grouped_value * 1_000))

    # 117 یعنی 117 میلیون
    if digit_len <= 3:
        return int(round(value * 1_000_000))

    # 7500 یعنی 7.5 میلیون
    if digit_len == 4:
        return int(round(value * 1_000))

    # 111111 یا 400000 یعنی 111 میلیون یا 400 میلیون
    if digit_len in (5, 6):
        return int(round((value / 1000) * 1_000_000))

    # 4000000 یعنی 400 میلیون طبق منطق کانال‌های مبدا
    if digit_len == 7:
        if value < 10_000_000:
            return int(round(value * 100))

        return int(round(value))

    # اعداد 8 رقم به بالا را تومان واقعی می‌گیریم.
    if digit_len >= 8:
        return int(round(value))

    return None


def extract_price_toman_from_line(line: str) -> Optional[int]:
    line = normalize_price_text(line)

    if not line:
        return None

    if looks_like_uid_or_phone(line):
        return None

    pattern_with_suffix = re.compile(
        r"(?P<number>\d+(?:[,.]\d+)*)\s*"
        r"(?P<suffix>"
        r"mil|mill|million|mln|"
        r"میلیون|ملیون|ميليون|میلیونی|ملیونی|میل|مل|"
        r"billion|bil|b|میلیارد|مليارد|"
        r"تومان|تومن|tmn|toman|tomans|irt"
        r")\b",
        flags=re.IGNORECASE,
    )

    matches = list(pattern_with_suffix.finditer(line))

    for match in matches:
        raw_number = match.group("number")
        suffix = match.group("suffix")

        toman = infer_toman_from_number_and_suffix(raw_number, suffix)

        if toman and 1_000_000 <= toman <= 5_000_000_000:
            return toman

    raw_numbers = re.findall(r"\b\d+(?:[,.]\d+)*\b", line)

    possible_prices = []

    for raw_number in raw_numbers:
        toman = infer_toman_from_number_and_suffix(raw_number, "")

        if not toman:
            continue

        if toman < 1_000_000:
            continue

        if toman > 5_000_000_000:
            continue

        possible_prices.append(toman)

    if not possible_prices:
        return None

    return max(possible_prices)


def extract_price_toman_from_source_caption(caption: str) -> Optional[int]:
    caption = normalize_price_text(caption)

    if not caption:
        return None

    candidate_lines = extract_price_candidate_lines(caption)

    for line in candidate_lines:
        toman = extract_price_toman_from_line(line)
        if toman:
            return toman

    for line in caption.splitlines():
        line = normalize_price_text(line)

        if not line:
            continue

        if looks_like_uid_or_phone(line):
            continue

        if line_has_negative_price_keyword(line):
            continue

        toman = extract_price_toman_from_line(line)
        if toman:
            return toman

    return None


def format_usd_price_from_toman(toman: Optional[int]) -> str:
    if not toman or toman <= 0:
        return ACCOUNT_PRICE_FALLBACK_TEXT

    if not USD_RATE_TOMAN or USD_RATE_TOMAN <= 0:
        return ACCOUNT_PRICE_FALLBACK_TEXT

    usd_value = toman / USD_RATE_TOMAN
    formatted = f"{usd_value:,.2f}".rstrip("0").rstrip(".")

    return f"${formatted}"


def extract_account_price_text(source_caption: str) -> str:
    toman = extract_price_toman_from_source_caption(source_caption)

    if not toman:
        return ACCOUNT_PRICE_FALLBACK_TEXT

    return format_usd_price_from_toman(toman)


# ============================================================
# CUSTOM GAME TERMS GLOSSARY
# ============================================================

CUSTOM_TERM_REPLACEMENTS = [
    (r"\bاکانت\s+گاد\b", "God account"),
    (r"\bاک\s+گاد\b", "God account"),
    (r"\bاک\s+خوب\b", "Good account"),
    (r"\bاکانت\s+خوب\b", "Good account"),
    (r"\bاک\s+خفن\b", "Great account"),
    (r"\bاکانت\s+خفن\b", "Great account"),
    (r"\bاک\s+تمیز\b", "Clean account"),
    (r"\bاکانت\s+تمیز\b", "Clean account"),
    (r"\bاک\s+ارزشمند\b", "Valuable account"),
    (r"\bاکانت\s+ارزشمند\b", "Valuable account"),
    (r"\bاک\s+فول\b", "Full account"),
    (r"\bاکانت\s+فول\b", "Full account"),
    (r"\bاک\s+فول\s+آیتم\b", "Full item account"),
    (r"\bاکانت\s+فول\s+آیتم\b", "Full item account"),
    (r"\bاک\s+پر\s+آیتم\b", "High item account"),
    (r"\bاکانت\s+پر\s+آیتم\b", "High item account"),
    (r"\bاکانت\b", "Account"),
    (r"\bاک\b", "Account"),

    (r"\bگادلی\b", "Godly"),
    (r"\bگاد\b", "God"),
    (r"\bخفن\b", "Great"),
    (r"\bتمیز\b", "Clean"),
    (r"\bارزشمند\b", "Valuable"),
    (r"\bارزون\b", "Cheap"),
    (r"\bارزان\b", "Cheap"),
    (r"\bاقتصادی\b", "Budget"),
    (r"\bفول\s+آیتم\b", "Full item"),
    (r"\bپر\s+آیتم\b", "High item"),
    (r"\bپرایتم\b", "High item"),
    (r"\bفولایتم\b", "Full item"),

    (r"\bمتیک\b", "Mythic"),
    (r"\bمیتیک\b", "Mythic"),
    (r"\bمایتیک\b", "Mythic"),
    (r"\bمیثیک\b", "Mythic"),
    (r"\bمیسیک\b", "Mythic"),
    (r"\bمتیک\s+ها\b", "Mythics"),
    (r"\bمتیکها\b", "Mythics"),
    (r"\bمتیک‌ها\b", "Mythics"),

    (r"\bلجندری\b", "Legendary"),
    (r"\bلجنری\b", "Legendary"),
    (r"\bلجند\b", "Legendary"),
    (r"\bلجند\s+ها\b", "Legendaries"),
    (r"\bلجندها\b", "Legendaries"),
    (r"\bلجند‌ها\b", "Legendaries"),

    (r"\bاپیک\b", "Epic"),
    (r"\bایپک\b", "Epic"),
    (r"\bریر\b", "Rare"),
    (r"\bکامن\b", "Common"),
    (r"\bآنکامن\b", "Uncommon"),
    (r"\bپرمیوم\b", "Premium"),

    (r"\bداماسکوس\b", "Damascus"),
    (r"\bداماس\b", "Damascus"),
    (r"\bدمسکس\b", "Damascus"),
    (r"\bدایموند\b", "Diamond"),
    (r"\bدیاموند\b", "Diamond"),
    (r"\bالماس\b", "Diamond"),
    (r"\bگلد\b", "Gold"),
    (r"\bطلایی\b", "Gold"),
    (r"\bپلاتینیوم\b", "Platinum"),
    (r"\bپلاتین\b", "Platinum"),
    (r"\bکامو\b", "Camo"),
    (r"\bکمو\b", "Camo"),

    (r"\bکریت\b", "Crate"),
    (r"\bکرت\b", "Crate"),
    (r"\bباندل\b", "Bundle"),
    (r"\bدراو\b", "Draw"),
    (r"\bلاکی\s+دراو\b", "Lucky Draw"),
    (r"\bلاکیدراو\b", "Lucky Draw"),
    (r"\bگردونه\b", "Draw"),
    (r"\bبتل\s+پس\b", "Battle Pass"),
    (r"\bبتلپس\b", "Battle Pass"),

    (r"\bکاراکتر\b", "Character"),
    (r"\bکارکتر\b", "Character"),
    (r"\bشخصیت\b", "Character"),
    (r"\bاپراتور\b", "Operator"),
    (r"\bاسکین\b", "Skin"),
    (r"\bسکین\b", "Skin"),
    (r"\bایموت\b", "Emote"),
    (r"\bاموت\b", "Emote"),
    (r"\bاوتفیت\b", "Outfit"),
    (r"\bلباس\b", "Outfit"),

    (r"\bگان\b", "Gun"),
    (r"\bگن\b", "Gun"),
    (r"\bاسلحه\b", "Weapon"),
    (r"\bسلاح\b", "Weapon"),
    (r"\bویپن\b", "Weapon"),
    (r"\bاسنایپر\b", "Sniper"),
    (r"\bشاتگان\b", "Shotgun"),
    (r"\bاسمگ\b", "SMG"),

    (r"\bفول\s+مکس\b", "Fully maxed"),
    (r"\bفولمکس\b", "Fully maxed"),
    (r"\bمکس\s+شده\b", "Maxed"),
    (r"\bمکس\b", "Max"),
    (r"\bآپگرید\b", "Upgrade"),
    (r"\bاپگرید\b", "Upgrade"),
    (r"\bلول\b", "Level"),

    (r"\bرنکد\b", "Ranked"),
    (r"\bرنک\b", "Rank"),
    (r"\bبتل\s+رویال\b", "Battle Royale"),
    (r"\bبتلرویال\b", "Battle Royale"),
    (r"\bمولتی\s+پلیر\b", "Multiplayer"),
    (r"\bمولتیپلیر\b", "Multiplayer"),
    (r"\bمولتی\b", "Multiplayer"),
    (r"\bبی\s*آر\b", "BR"),
    (r"\bام\s*پی\b", "MP"),

    (r"\bلوداوت\b", "Loadout"),
    (r"\bلودات\b", "Loadout"),
    (r"\bاینونتوری\b", "Inventory"),
    (r"\bاینوینتوری\b", "Inventory"),
    (r"\bآیتم\b", "Item"),
    (r"\bایتم\b", "Item"),

    (r"\bسی\s*پی\b", "CP"),
    (r"\bسیپی\b", "CP"),
    (r"\bکوین\b", "Coin"),
    (r"\bکردیت\b", "Credit"),

    (r"\bسیف\b", "Safe"),
    (r"\bامن\b", "Safe"),
    (r"\bکلین\b", "Clean"),
    (r"\bبدون\s+مشکل\b", "No issues"),
    (r"\bبدون\s+بن\b", "No ban"),
    (r"\bبن\s+نیست\b", "Not banned"),
    (r"\bبن\s+نشده\b", "Not banned"),
    (r"\bبن\b", "Ban"),

    (r"\bلاگین\b", "Login"),
    (r"\bریجن\b", "Region"),
    (r"\bگلوبال\b", "Global"),
    (r"\bگارنا\b", "Garena"),

    (r"\bکالاف\s+دیوتی\b", "Call of Duty"),
    (r"\bکال\s+آف\s+دیوتی\b", "Call of Duty"),
    (r"\bکالاف\s+موبایل\b", "Call of Duty Mobile"),
    (r"\bکالافموبایل\b", "Call of Duty Mobile"),
    (r"\bکالاف\b", "Call of Duty"),
    (r"\bوارزون\s+موبایل\b", "Warzone Mobile"),
    (r"\bوارزونموبایل\b", "Warzone Mobile"),
    (r"\bوارزون\b", "Warzone"),
    (r"\bکادم\b", "CODM"),
    (r"\bکد\s+ام\b", "CODM"),

    (r"\bچندتا\b", "Several"),
    (r"\bچنتا\b", "Several"),
    (r"\bزیاد\b", "Many"),
    (r"\bخیلی\s+زیاد\b", "A lot of"),
    (r"\bکامل\b", "Complete"),
    (r"\bنسبتا\b", "Relatively"),
    (r"\bتقریبا\b", "Almost"),

    (r"\bباز\s+است\b", "is unlocked"),
    (r"\bباز\s+شده\b", "unlocked"),
    (r"\bباز\b", "unlocked"),
    (r"\bداره\b", "has"),
    (r"\bداراست\b", "has"),
    (r"\bموجوده\b", "available"),
    (r"\bموجود\b", "available"),
]

POST_TRANSLATION_FIXES = [
    (r"\bgad account\b", "God account"),
    (r"\bgad\b", "God"),
    (r"\bmetik\b", "Mythic"),
    (r"\bmatic\b", "Mythic"),
    (r"\bmytic\b", "Mythic"),
    (r"\bmythik\b", "Mythic"),
    (r"\bmitic\b", "Mythic"),
    (r"\bdamas\b", "Damascus"),
    (r"\bdamaskos\b", "Damascus"),
    (r"\bcrite\b", "Crate"),
    (r"\bcrites\b", "Crates"),
    (r"\bbandel\b", "Bundle"),
    (r"\bbundel\b", "Bundle"),
    (r"\blegend\b", "Legendary"),
    (r"\blegendaryy\b", "Legendary"),
    (r"\bload out\b", "Loadout"),
    (r"\bbattlepass\b", "Battle Pass"),
    (r"\blucky draw\b", "Lucky Draw"),
    (r"\bcallaf\b", "Call of Duty"),
    (r"\bcalaf\b", "Call of Duty"),
    (r"\bcall of duty mobile mobile\b", "Call of Duty Mobile"),
    (r"\bcod mobile mobile\b", "COD Mobile"),
    (r"\baccount account\b", "Account"),
    (r"\bgod account account\b", "God account"),
    (r"\bclean account account\b", "Clean account"),
    (r"\bgreat account account\b", "Great account"),
    (r"\bhas has\b", "has"),
]


def apply_custom_game_glossary(text: str) -> str:
    text = normalize_text(text)

    if not text:
        return ""

    for pattern, replacement in CUSTOM_TERM_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return normalize_text(text)


def apply_post_translation_fixes(text: str) -> str:
    text = normalize_text(text)

    if not text:
        return ""

    for pattern, replacement in POST_TRANSLATION_FIXES:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([,.!?;:])([^\s])", r"\1 \2", text)
    text = re.sub(r"\bCP CP\b", "CP", text, flags=re.IGNORECASE)
    text = re.sub(r"\bCOD COD\b", "COD", text, flags=re.IGNORECASE)

    return normalize_text(text)


def remove_source_mentions_hashtags_links(text: str) -> str:
    text = re.sub(r"@\w{3,}", "", text)
    text = re.sub(r"#\w+", "", text)
    text = re.sub(r"https?://\S+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"t\.me/\S+", "", text, flags=re.IGNORECASE)

    return normalize_text(text)


def contains_forbidden_keyword(line: str) -> bool:
    low = line.lower()
    return any(keyword.lower() in low for keyword in FORBIDDEN_LINE_KEYWORDS)


def is_uid_line(line: str) -> bool:
    low = line.lower()

    if "uid" in low:
        return True

    if re.search(r"\d{10,}", line):
        return True

    return False


def is_end_section_line(line: str) -> bool:
    low = line.lower()

    if is_uid_line(line):
        return True

    return any(keyword.lower() in low for keyword in END_SECTION_KEYWORDS)


def clean_description_line(line: str) -> str:
    line = normalize_text(line)

    if not line:
        return ""

    if contains_forbidden_keyword(line):
        return ""

    line = remove_source_mentions_hashtags_links(line)

    return normalize_text(line)


def extract_description_from_source_caption(caption: str) -> str:
    caption = normalize_text(caption)

    if not caption:
        return ""

    lines = caption.splitlines()

    start_index: Optional[int] = None
    seed_line = ""

    for i, line in enumerate(lines):
        clean_line = normalize_text(line)

        for marker in DESCRIPTION_MARKERS:
            if marker in clean_line:
                start_index = i + 1

                after_marker = clean_line.split(marker, 1)[1].strip()
                after_marker = after_marker.strip(":：-–—| ")

                if after_marker:
                    seed_line = after_marker

                break

        if start_index is not None:
            break

    if start_index is None:
        return ""

    description_lines: List[str] = []

    if seed_line:
        cleaned_seed = clean_description_line(seed_line)
        if cleaned_seed:
            description_lines.append(cleaned_seed)

    for line in lines[start_index:]:
        line = normalize_text(line)

        if not line:
            continue

        if is_end_section_line(line):
            break

        cleaned = clean_description_line(line)

        if cleaned:
            description_lines.append(cleaned)

    result = "\n".join(description_lines)
    result = normalize_text(result)

    result_lines = [line.strip() for line in result.splitlines() if line.strip()]

    return "\n".join(result_lines).strip()


def translate_to_english(text: str) -> str:
    if not text:
        return ""

    text = apply_custom_game_glossary(text)

    if not USE_TRANSLATOR:
        return apply_post_translation_fixes(text)

    if GoogleTranslator is None:
        print("Package deep-translator نصب نیست. متن بدون ترجمه ارسال می‌شود.")
        return apply_post_translation_fixes(text)

    try:
        translator = GoogleTranslator(source="auto", target="en")
        translated_lines = []

        for line in text.splitlines():
            line = line.strip()

            if not line:
                translated_lines.append("")
                continue

            line = apply_custom_game_glossary(line)

            try:
                translated = translator.translate(line)
                translated = apply_post_translation_fixes(translated)
                translated_lines.append(translated)
            except Exception:
                translated_lines.append(apply_post_translation_fixes(line))

        final_text = normalize_text("\n".join(translated_lines))
        final_text = apply_post_translation_fixes(final_text)

        return final_text

    except Exception as e:
        print(f"Translation error: {e}")
        return apply_post_translation_fixes(text)


def utf16_length(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


def substring_by_utf16(text: str, offset: int, length: int) -> str:
    data = text.encode("utf-16-le")
    part = data[offset * 2:(offset + length) * 2]
    return part.decode("utf-16-le", errors="ignore")


def is_valid_url(url: str) -> bool:
    if not url:
        return False

    url = url.strip()

    return (
        url.startswith("http://")
        or url.startswith("https://")
        or url.startswith("tg://")
    )


# ============================================================
# CAPTION BUILDER WITH CUSTOM EMOJI, LINKS, QUOTES
# ============================================================

class CaptionBuilder:
    def __init__(self):
        self.text_parts: List[str] = []
        self.entities: List[object] = []

    @property
    def text(self) -> str:
        return "".join(self.text_parts)

    def append(self, value: str) -> None:
        self.text_parts.append(value)

    def append_custom_emoji(self, emoji: str, key: str) -> None:
        document_id = int(CUSTOM_EMOJI_IDS.get(key, 0) or 0)
        self.append_custom_emoji_by_id(emoji, document_id)

    def append_custom_emoji_by_id(self, emoji: str, document_id: int) -> None:
        offset = utf16_length(self.text)
        length = utf16_length(emoji)

        self.text_parts.append(emoji)

        if document_id:
            self.entities.append(
                types.MessageEntityCustomEmoji(
                    offset=offset,
                    length=length,
                    document_id=int(document_id),
                )
            )

    def append_text_link(self, text: str, url: str = "") -> None:
        offset = utf16_length(self.text)
        length = utf16_length(text)

        self.text_parts.append(text)

        if is_valid_url(url):
            self.entities.append(
                types.MessageEntityTextUrl(
                    offset=offset,
                    length=length,
                    url=url.strip(),
                )
            )

    def append_blockquote(self, text: str, url: str = "") -> None:
        offset = utf16_length(self.text)
        length = utf16_length(text)

        self.text_parts.append(text)

        if is_valid_url(url):
            self.entities.append(
                types.MessageEntityTextUrl(
                    offset=offset,
                    length=length,
                    url=url.strip(),
                )
            )

        blockquote_class = getattr(types, "MessageEntityBlockquote", None)

        if blockquote_class is not None:
            try:
                self.entities.append(
                    blockquote_class(
                        offset=offset,
                        length=length,
                    )
                )
            except TypeError:
                try:
                    self.entities.append(
                        blockquote_class(
                            offset=offset,
                            length=length,
                            collapsed=False,
                        )
                    )
                except Exception:
                    pass

    def append_cod_logo(self) -> None:
        ids = COD_LOGO_CUSTOM_EMOJI_IDS[:]

        while len(ids) < 12:
            ids.append(0)

        for i in range(6):
            self.append_custom_emoji_by_id(COD_LOGO_FALLBACK_EMOJI, ids[i])

        self.append("\n")

        for i in range(6, 12):
            self.append_custom_emoji_by_id(COD_LOGO_FALLBACK_EMOJI, ids[i])


# ============================================================
# FINAL CAPTION
# ============================================================

def build_caption_no_trim(
    description_en: str,
    account_number: int,
    account_price_text: str,
) -> Tuple[str, List[object]]:
    now_text = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    account_price_text = normalize_text(account_price_text) or ACCOUNT_PRICE_FALLBACK_TEXT

    b = CaptionBuilder()

    b.append_custom_emoji("🔻", "red_triangle")
    b.append(" Has a barcode to prevent abuse & fraud\n\n")

    b.append(f"{ACCOUNT_NUMBER_TAG}{account_number}\n\n")

    b.append("Status")
    b.append_custom_emoji("🟢", "green_circle")
    b.append("\n\n")

    b.append_custom_emoji("🔗", "link")
    b.append(f" | Synced on: {now_text}\n\n")

    b.append_custom_emoji("📤", "outbox")
    b.append("| Description:\n\n")

    if description_en.strip():
        b.append(description_en.strip())
        b.append("\n\n")

    b.append_cod_logo()
    b.append("\n\n")

    if QUOTE_HASHTAGS:
        b.append_blockquote(HASHTAGS)
    else:
        b.append(HASHTAGS)

    b.append("\n\n")

    if is_valid_url(COD_BUY_SELL_URL):
        b.append_text_link("COD BUY SELL", COD_BUY_SELL_URL)
    else:
        b.append("COD BUY SELL")

    b.append("\n\n")

    b.append_custom_emoji("💰", "money")
    b.append("| Account Price: ")
    b.append(account_price_text)
    b.append("\n\n")

    b.append_custom_emoji("💬", "chat")
    b.append("Group ")
    b.append_text_link(GROUP_USERNAME, GROUP_URL)
    b.append("\n\n")

    b.append_custom_emoji("👤", "person")
    b.append("MM ")
    b.append_text_link(MM_USERNAME, MM_URL)
    b.append(" ")
    b.append_custom_emoji("💳", "card")

    if int(CUSTOM_EMOJI_IDS.get("mm_badge", 0) or 0):
        b.append(" ")
        b.append_custom_emoji("💀", "mm_badge")

    b.append("\n\n")

    b.append_custom_emoji("📝", "memo")
    b.append_text_link("Terms Of Service", TERMS_URL)
    b.append("\n\n")

    b.append_custom_emoji("💬", "chat")
    b.append_text_link("Reviews", REVIEWS_URL)
    b.append("\n\n")

    b.append_custom_emoji("❓", "question")
    b.append_text_link("How does it work?", HOW_IT_WORKS_URL)
    b.append("\n\n")

    b.append_custom_emoji("🌐", "globe")
    b.append_text_link("Website", WEBSITE_URL)
    b.append("\n\n")

    b.append_custom_emoji("🤖", "robot")
    b.append_text_link("Ad Posting Bot", AD_POSTING_BOT_URL)
    b.append("\n\n")

    if QUOTE_ACTION_BUTTONS:
        b.append_blockquote("BUY NOW", BUY_NOW_URL)
    else:
        b.append_text_link("BUY NOW", BUY_NOW_URL)

    b.append("\n\n")

    if QUOTE_ACTION_BUTTONS:
        b.append_blockquote("SELL YOUR ACCOUNT", SELL_YOUR_ACCOUNT_URL)
    else:
        b.append_text_link("SELL YOUR ACCOUNT", SELL_YOUR_ACCOUNT_URL)

    return b.text, b.entities


def build_final_caption(
    description_en: str,
    account_number: int,
    account_price_text: str,
) -> Tuple[str, List[object]]:
    description_en = normalize_text(description_en)
    account_price_text = normalize_text(account_price_text) or ACCOUNT_PRICE_FALLBACK_TEXT

    text, entities = build_caption_no_trim(description_en, account_number, account_price_text)

    if MAX_CAPTION_LENGTH <= 0:
        return text, entities

    if len(text) <= MAX_CAPTION_LENGTH:
        return text, entities

    ellipsis = "\n..."

    low = 0
    high = len(description_en)
    best_description = ""

    while low <= high:
        mid = (low + high) // 2
        candidate = description_en[:mid].rstrip()

        if candidate:
            candidate = candidate + ellipsis

        candidate_text, _ = build_caption_no_trim(candidate, account_number, account_price_text)

        if len(candidate_text) <= MAX_CAPTION_LENGTH:
            best_description = candidate
            low = mid + 1
        else:
            high = mid - 1

    return build_caption_no_trim(best_description, account_number, account_price_text)


# ============================================================
# MESSAGE / MEDIA HELPERS
# ============================================================

def message_has_video(message) -> bool:
    if not message:
        return False

    if getattr(message, "video", None):
        return True

    document = getattr(message, "document", None)
    if not document:
        return False

    mime_type = getattr(document, "mime_type", "") or ""
    return mime_type.startswith("video/")


def get_message_unique_key(message) -> str:
    chat_id = getattr(message, "chat_id", None) or "unknown"
    return f"{chat_id}:{message.id}"


def ensure_temp_dir() -> None:
    os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)


def safe_remove_file(path: Optional[str]) -> None:
    if not path:
        return

    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


# ============================================================
# TELEGRAM CLIENT
# ============================================================

if TELEGRAM_SESSION_STRING:
    client = TelegramClient(StringSession(TELEGRAM_SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

processed_ids = load_processed_ids()
account_counter_lock = asyncio.Lock()


async def print_custom_emoji_ids_from_saved_messages(limit: int = 30) -> None:
    await client.start()

    messages = await client.get_messages("me", limit=limit)

    print("\nChecking Saved Messages for premium custom emojis...\n")

    found = False

    for msg in messages:
        if not msg.message or not msg.entities:
            continue

        for entity in msg.entities:
            if isinstance(entity, types.MessageEntityCustomEmoji):
                found = True
                emoji_text = substring_by_utf16(
                    msg.message,
                    entity.offset,
                    entity.length,
                )

                print("=" * 60)
                print(f"Emoji Text : {emoji_text}")
                print(f"Document ID: {entity.document_id}")
                print(f"Offset     : {entity.offset}")
                print(f"Length     : {entity.length}")

    if not found:
        print("هیچ Premium Custom Emoji در آخرین پیام‌های Saved Messages پیدا نشد.")
        print("یک پیام شامل ایموجی‌های پرمیوم داخل Saved Messages بفرست و دوباره اجرا کن.")

    print("\nDone.\n")


async def send_video_with_new_caption(message, final_caption: str, entities: List[object]) -> None:
    ensure_temp_dir()

    downloaded_path = None

    try:
        print("Downloading media...")
        downloaded_path = await client.download_media(message, file=TEMP_DOWNLOAD_DIR)

        if not downloaded_path:
            raise RuntimeError("Download failed. downloaded_path is empty.")

        print("Uploading to destination channel...")

        await client.send_file(
            entity=DEST_ENTITY,
            file=downloaded_path,
            caption=final_caption,
            formatting_entities=entities,
            supports_streaming=True,
            force_document=False,
        )

    finally:
        safe_remove_file(downloaded_path)


async def process_message(message) -> None:
    unique_key = get_message_unique_key(message)

    if unique_key in processed_ids:
        print(f"Already processed: {unique_key}")
        return

    if ONLY_VIDEO and not message_has_video(message):
        print(f"Skipped non-video message: {unique_key}")
        return

    source_caption = message.message or ""

    if not source_caption:
        print(f"Skipped message without caption: {unique_key}")
        return

    price_toman = extract_price_toman_from_source_caption(source_caption)
    account_price_text = extract_account_price_text(source_caption)

    description = extract_description_from_source_caption(source_caption)

    print("\n" + "=" * 60)
    print(f"New source message: {unique_key}")

    print("- Extracted Price Toman:")
    print(price_toman if price_toman else "[NOT FOUND]")

    print("- Final USD Price Text:")
    print(account_price_text)

    print("- Extracted Description:")
    print(description if description else "[EMPTY]")

    if SKIP_IF_DESCRIPTION_EMPTY and not description:
        print(f"Skipped because description is empty after filtering: {unique_key}")
        return

    description_en = translate_to_english(description)

    print("- Translated Description:")
    print(description_en if description_en else "[EMPTY]")

    if SKIP_IF_DESCRIPTION_EMPTY and not description_en:
        print(f"Skipped because translated description is empty: {unique_key}")
        return

    try:
        async with account_counter_lock:
            if unique_key in processed_ids:
                print(f"Already processed inside lock: {unique_key}")
                return

            account_number = load_account_counter()

            final_caption, entities = build_final_caption(
                description_en,
                account_number,
                account_price_text,
            )

            print("- Account Number:", account_number)
            print("- Final Caption Length:", len(final_caption))
            print("- Entities Count:", len(entities))

            await send_video_with_new_caption(message, final_caption, entities)

            processed_ids.add(unique_key)
            save_processed_ids(processed_ids)

            increment_account_counter(account_number)

            print(f"Posted successfully: {unique_key}")
            print(f"Account number used: {account_number}")
            print(f"Next account number: {account_number + 1}")

    except FloodWaitError as e:
        print(f"FloodWait: sleeping for {e.seconds} seconds")
        await asyncio.sleep(e.seconds + 5)
        await process_message(message)

    except Exception as e:
        print(f"Error while processing {unique_key}: {e}")


@client.on(events.NewMessage(chats=SOURCE_ENTITY))
async def new_message_handler(event):
    await process_message(event.message)


async def main() -> None:
    if not API_ID:
        raise RuntimeError("API_ID را داخل کد یا Railway Variables وارد کن.")

    if not API_HASH or API_HASH == "PUT_YOUR_API_HASH_HERE":
        raise RuntimeError("API_HASH را داخل کد یا Railway Variables وارد کن.")

    if RUN_MODE == "EMOJI_IDS":
        await print_custom_emoji_ids_from_saved_messages()
        return

    if not SOURCE_ENTITY:
        raise RuntimeError("SOURCE_CHANNEL را داخل کد یا Railway Variables وارد کن.")

    if not DEST_ENTITY:
        raise RuntimeError("DEST_CHANNEL را داخل کد یا Railway Variables وارد کن.")

    await client.start()

    me = await client.get_me()

    print("\nTelegram client started.")
    print(f"Logged in as: {me.first_name} / ID: {me.id}")
    print(f"Source channel: {SOURCE_ENTITY}")
    print(f"Destination channel: {DEST_ENTITY}")
    print(f"Data dir: {DATA_DIR}")
    print(f"Counter file: {ACCOUNT_COUNTER_FILE}")
    print(f"Processed file: {PROCESSED_FILE}")
    print(f"Next account number: {load_account_counter()}")
    print(f"USD rate toman: {USD_RATE_TOMAN}")
    print("Listening for new video posts...\n")

    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())