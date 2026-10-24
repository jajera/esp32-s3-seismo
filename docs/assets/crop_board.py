"""Crop the horizontal components-side board from 09-esp32s3-headers.png,
add generous padding, and upscale 2× for decent resolution.

Regenerate: python3 crop_board.py
"""

from PIL import Image, ImageFilter

src = Image.open("09-esp32s3-headers.png").convert("RGB")

# The top board in 09 sits roughly x: 90–900, y: 10–380.
# Crop tight first, then add padding.
tight = src.crop((90, 10, 900, 380))

# Add whitespace padding so the board isn't edge-to-edge.
pad = 60
bg = (255, 255, 255)
w, h = tight.size
padded = Image.new("RGB", (w + 2 * pad, h + 2 * pad), bg)
padded.paste(tight, (pad, pad))

# Upscale 2× with Lanczos for better display resolution.
final = padded.resize((padded.width * 2, padded.height * 2), Image.Resampling.LANCZOS)

final.save("esp32s3-board-top.png")
print(f"ok -> esp32s3-board-top.png {final.size}")
