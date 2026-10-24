"""Crop + enhance the Phase 7 as-built photo.

Source IMG_0389.jpeg is a dark, wide phone shot (power bank + lots of black
background). Crop to the breadboard assembly (TFT + S3 + IMU) and lift
brightness/contrast/colour so the SEISMO readout is legible.

Regenerate: python3 enhance_phase7.py
"""

from PIL import Image, ImageEnhance, ImageFilter

src = Image.open("07-intensity-ui-src.jpeg").convert("RGB")
W, H = src.size  # 4032 x 3024

# Crop to the breadboard row: drop the empty top, the power bank below, and
# trim the far-left/right dead space. Values are fractions of the frame.
left = int(W * 0.02)
right = int(W * 0.90)
top = int(H * 0.11)
bottom = int(H * 0.66)
img = src.crop((left, top, right, bottom))

# Tone: lift the dark exposure, then add contrast and a little colour/sharpness.
img = ImageEnhance.Brightness(img).enhance(1.7)
img = ImageEnhance.Contrast(img).enhance(1.25)
img = ImageEnhance.Color(img).enhance(1.2)
img = ImageEnhance.Sharpness(img).enhance(1.4)

# Keep it a sensible web width.
target_w = 1600
if img.width > target_w:
    ratio = target_w / img.width
    img = img.resize((target_w, int(img.height * ratio)), Image.Resampling.LANCZOS)

img.save("07-intensity-ui-demo.png")
print(f"ok -> 07-intensity-ui-demo.png {img.size}")
