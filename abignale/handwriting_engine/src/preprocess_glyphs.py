# src/preprocess_glyphs.py
from PIL import Image, ImageOps
import os
from config import GLYPH_RAW_DIR, GLYPH_PROCESSED_DIR


def preprocess_one_image(in_path, out_path):
    img = Image.open(in_path).convert("L")  # grayscale

    # 1) Binarize: white vs black
    # You can experiment with threshold value (e.g. 200)
    threshold = 200
    bw = img.point(lambda x: 255 if x > threshold else 0, 'L')

    # 2) Trim white borders
    inverted = ImageOps.invert(bw)
    bbox = inverted.getbbox()
    if bbox:
        bw = bw.crop(bbox)

    # 3) Convert to RGBA and make white transparent
    rgba = bw.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            # white → transparent
            if r == 255 and g == 255 and b == 255:
                pixels[x, y] = (255, 255, 255, 0)
            else:
                pixels[x, y] = (0, 0, 0, 255)  # black ink

    # 4) Save processed glyph
    rgba.save(out_path)


def main():
    os.makedirs(GLYPH_PROCESSED_DIR, exist_ok=True)

    for fname in os.listdir(GLYPH_RAW_DIR):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        in_path = os.path.join(GLYPH_RAW_DIR, fname)
        out_path = os.path.join(GLYPH_PROCESSED_DIR, fname)
        preprocess_one_image(in_path, out_path)
        print(f"Processed: {fname}")


if __name__ == "__main__":
    main()

