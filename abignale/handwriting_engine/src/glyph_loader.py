# src/glyph_loader.py
import os
from PIL import Image
from config import GLYPH_PROCESSED_DIR

ALIAS_MAP = {
    "space": " ",
    "quote": "\"",
    "backslash": "\\",
    "colon": ":",
    "semicolon": ";"
    # add more aliases if needed
}


def load_glyphs():
    glyphs = {}

    for fname in os.listdir(GLYPH_PROCESSED_DIR):
        if not fname.lower().endswith(".png"):
            continue

        name, _ = os.path.splitext(fname)  # e.g. "a_1"
        if "_" not in name:
            continue

        char_part, _ = name.split("_", 1)

        if len(char_part) == 1:
            ch = char_part
        else:
            if char_part not in ALIAS_MAP:
                continue
            ch = ALIAS_MAP[char_part]

        path = os.path.join(GLYPH_PROCESSED_DIR, fname)
        img = Image.open(path).convert("RGBA")
        glyphs.setdefault(ch, []).append(img)

    return glyphs

