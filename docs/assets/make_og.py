"""Build the social/Open Graph preview image from the Phase 7 as-built photo.

OG wants 1200x630 (1.91:1) and a modest file size. We fit the enhanced photo
onto a 1200x630 dark canvas (letterboxed so nothing important is cropped) and
save a compressed JPEG.

Regenerate: python3 make_og.py
"""

from PIL import Image

OG_W, OG_H = 1200, 630
BG = (10, 12, 14)

src = Image.open("07-intensity-ui-demo.png").convert("RGB")

# Scale to fit inside the OG box, preserving aspect ratio.
scale = min(OG_W / src.width, OG_H / src.height)
new = src.resize((int(src.width * scale), int(src.height * scale)),
                 Image.Resampling.LANCZOS)

canvas = Image.new("RGB", (OG_W, OG_H), BG)
canvas.paste(new, ((OG_W - new.width) // 2, (OG_H - new.height) // 2))

canvas.save("og-image.jpg", quality=82, optimize=True, progressive=True)
print(f"ok -> og-image.jpg {canvas.size}")
