# src/main.py
from glyph_loader import load_glyphs
from renderer import render_text
from config import OUTPUT_DIR
import os


def main():
    glyphs = load_glyphs()

    if len(glyphs) == 0:
        print("Warning: No glyphs loaded! Make sure you have processed glyphs in ../glyphs/")
        print("Run preprocess_glyphs.py first if you have raw glyphs in ../glyph_raw/")
        return

    text = "hey how are you doing today"

    img = render_text(text, glyphs, bg_color=(255, 255, 255, 255), line_spacing=15)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "example.png")
    img.save(out_path)
    print("Saved:", out_path)


if __name__ == "__main__":
    main()

