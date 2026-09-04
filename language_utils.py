"""Language Detection & Translation — Hindi / Hinglish support for safety reports."""

import re


# Hindi safety vocabulary mapping (common phrases seen in Indian oil & gas reports)
HINDI_SAFETY_MAP = {
    # Slips / Falls
    "gir": "slip",
    "gira": "fell",
    "girna": "falling",
    "phasal": "slippery",
    "phisal": "slippery",
    "slip": "slippery",
    # PPE
    "ppe": "PPE",
    "helmet": "helmet",
    "safeti": "safety",
    "suraksha": "safety",
    "bachav": "protection",
    # Equipment
    "pump": "pump",
    "compressor": "compressor",
    "valve": "valve",
    "pipeline": "pipeline",
    "tank": "tank",
    "well": "well",
    "rig": "rig",
    "separator": "separator",
    # Hazards
    "aag": "fire",
    "gas": "gas",
    "leak": "leak",
    "dhua": "smoke",
    "lekin": "but",
    "kyunki": "because",
    "bahut": "very",
    "zyada": "excessive",
    "khatarnak": "dangerous",
    "kharab": "faulty/broken",
    "toot": "broken",
    "tuta": "broken",
    "toota": "broken",
    # Actions
    "band": "shutdown",
    "chal": "running",
    "ruk": "stop",
    "ruka": "stopped",
    "chalu": "running",
    "repair": "repair",
    "thik": "fixed",
    # Locations
    "ghar": "house",
    "kamra": "room",
    "area": "area",
    "floor": "floor",
    "chhat": "roof",
    "neechay": "below",
    "upar": "above",
    "pass": "near",
    "andar": "inside",
    "bahar": "outside",
    # Conditions
    "gila": "wet",
    "geela": "wet",
    "sukha": "dry",
    "garam": "hot",
    "thanda": "cold",
    "andhera": "dark",
    "raat": "night",
    "din": "day",
    "shift": "shift",
    # Misc
    "bhai": "brother",
    "sir": "sir",
    "report": "report",
    "incident": "incident",
    "bhi": "also",
    "hai": "is",
    "tha": "was",
    "hoga": "will happen",
    "ho": "be",
    "mein": "in",
    "pe": "on",
    "se": "from",
    "ko": "to",
    "ka": "of",
    "ki": "of",
    "nahi": "not",
    "ya": "or",
    "aur": "and",
    "main": "in/I",
    "hum": "we",
    "kya": "what",
    "kab": "when",
    "kaise": "how",
    "kyun": "why",
}


def detect_language(text):
    """Detect if text is Hindi, English, or Hinglish.
    Returns: 'hindi', 'english', or 'hinglish'
    """
    if not text or not text.strip():
        return "english"

    # Check for Devanagari Unicode characters
    devanagari_count = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    total_alpha = sum(1 for ch in text if ch.isalpha())

    if total_alpha == 0:
        return "english"

    devanagari_pct = devanagari_count / total_alpha

    if devanagari_pct > 0.5:
        return "hindi"
    elif devanagari_pct > 0:
        return "hinglish"
    else:
        # Check for romanized Hindi words
        words = text.lower().split()
        hindi_words_found = sum(1 for w in words if w in HINDI_SAFETY_MAP)
        if hindi_words_found >= 2 and len(words) <= 15:
            return "hinglish"
        return "english"


def translate_hinglish(text):
    """Best-effort translation of Hinglish text to English for NLP processing.
    Preserves the original text alongside translations.
    """
    if not text or not text.strip():
        return text, False

    lang = detect_language(text)
    if lang == "english":
        return text, False

    words = text.lower().split()
    translated_words = []
    changes = 0

    for word in words:
        # Clean punctuation for matching
        clean = re.sub(r'[^\w]', '', word)
        if clean in HINDI_SAFETY_MAP:
            translation = HINDI_SAFETY_MAP[clean]
            # Keep original case and punctuation
            translated_words.append(translation)
            changes += 1
        else:
            translated_words.append(word)

    translated_text = " ".join(translated_words)

    # Build combined text for better NLP extraction
    combined = f"{translated_text} | {text}"

    return combined, changes > 0


def get_language_info(text):
    """Return language detection info for the API response."""
    lang = detect_language(text)
    return {
        "detected_language": lang,
        "is_multilingual": lang != "english",
        "script": "devanagari" if lang == "hindi" else "latin",
    }
