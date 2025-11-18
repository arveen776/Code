# src/renderer.py
from PIL import Image
import random


def measure_text(text, glyphs, line_spacing=10):
    lines = text.split("\n")
    max_width = 0
    total_height = 0

    # base height = tallest glyph we have
    max_char_height = 0
    for variations in glyphs.values():
        w, h = variations[0].size
        max_char_height = max(max_char_height, h)

    # approximate space width (half of an average character)
    if len(glyphs) > 0:
        any_char = next(iter(glyphs))
        w_ref, _ = glyphs[any_char][0].size
        space_width = int(w_ref * 0.5)
    else:
        space_width = 10

    for line in lines:
        line_width = 0
        for ch in line:
            if ch == " " and " " not in glyphs:
                line_width += space_width
            elif ch in glyphs:
                # use one variation width (they should be similar)
                w, _ = glyphs[ch][0].size
                line_width += w
            else:
                line_width += space_width
        max_width = max(max_width, line_width)
        total_height += max_char_height + line_spacing

    total_height -= line_spacing  # remove last extra spacing

    return max_width, total_height, max_char_height, space_width


def render_text(text, glyphs, bg_color=(255, 255, 255, 255), line_spacing=10):
    width, height, line_height, space_width = measure_text(text, glyphs, line_spacing)

    canvas = Image.new("RGBA", (width, height), bg_color)

    y = 0
    lines = text.split("\n")
    for line_idx, line in enumerate(lines):
        x = 0
        for ch in line:
            if ch == " " and " " not in glyphs:
                x += space_width
                continue

            if ch in glyphs:
                glyph_img = random.choice(glyphs[ch])
                w, h = glyph_img.size
                canvas.alpha_composite(glyph_img, dest=(x, y))
                x += w
            else:
                x += space_width

        if line_idx < len(lines) - 1:
            y += line_height + line_spacing

    return canvas

