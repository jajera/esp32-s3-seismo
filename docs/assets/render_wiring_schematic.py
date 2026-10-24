"""Clean schematic wiring diagram (SVG) for the Hardware page.

Replaces the busy photo-overlay wiring-diagram-real.png with a readable
schematic: three device blocks, every pin labelled, nets drawn pad-to-pad in
colour. Crisp at any zoom. The photo overlay is kept for reference but the page
now shows this instead.

Regenerate: python3 render_wiring_schematic.py
"""

INK = "#1c1e20"
MUTED = "#6e7376"
BG = "#f5f5f2"

# Power keeps convention; every signal gets its own colour so each wire is
# traceable end to end.
RED = "#c0392b"      # 3V3
BLK = "#2b2d2f"      # GND
C_SCL_I = "#1f8a70"  # I2C SCL  (teal)
C_SDA_I = "#2e86de"  # I2C SDA  (blue)
C_SCK = "#e67e22"    # SPI SCK  (orange)
C_MOSI = "#8e44ad"   # SPI MOSI (purple)
C_CS = "#16a085"     # SPI CS   (green-teal)
C_DC = "#d81b60"     # SPI DC   (magenta)
C_RES = "#f1c40f"    # SPI RES  (yellow)

FONT = "DejaVu Sans, sans-serif"

# --- layout -----------------------------------------------------------------
W, H = 1180, 820
S3_X, S3_W = 70, 250
IMU_X, IMU_W = 820, 250
TFT_X, TFT_W = 820, 250
ROW_H = 34
TOP = 150

# S3 pins (left block), in draw order with their net colour.
s3_pins = ["3V3", "GND", "GPIO8", "GPIO18", "GPIO11", "GPIO12",
           "GPIO10", "GPIO9", "GPIO7", "GPIO21"]
imu_pins = ["VDD", "CS", "GND", "SDO", "SCL", "SDA"]
tft_pins = ["VDD", "BL", "GND", "SCL", "SDA", "CS", "DC", "RES"]

# net definitions: (s3 pin, dest block, dest pin, colour)
nets = [
    ("3V3", "imu", "VDD", RED), ("3V3", "imu", "CS", RED),
    ("GND", "imu", "GND", BLK), ("GND", "imu", "SDO", BLK),
    ("GPIO18", "imu", "SCL", C_SCL_I), ("GPIO8", "imu", "SDA", C_SDA_I),
    ("3V3", "tft", "VDD", RED),
    ("GND", "tft", "GND", BLK),
    ("GPIO12", "tft", "SCL", C_SCK), ("GPIO11", "tft", "SDA", C_MOSI),
    ("GPIO10", "tft", "CS", C_CS), ("GPIO9", "tft", "DC", C_DC),
    ("GPIO7", "tft", "RES", C_RES), ("GPIO21", "tft", "BL", RED),
]

# legend entries: (colour, label)
legend = [
    (RED, "3V3"), (BLK, "GND"),
    (C_SCL_I, "I2C SCL"), (C_SDA_I, "I2C SDA"),
    (C_SCK, "SPI SCK"), (C_MOSI, "SPI MOSI"), (C_CS, "SPI CS"),
    (C_DC, "SPI DC"), (C_RES, "SPI RES"),
]


def block(x, y, w, pins, title, accent):
    h = ROW_H * len(pins) + 46
    out = [f'<rect x="{x+4}" y="{y+5}" width="{w}" height="{h}" rx="12" fill="#e1e1dd"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#ffffff" '
           f'stroke="{accent}" stroke-width="3"/>',
           f'<rect x="{x}" y="{y}" width="{w}" height="34" rx="12" fill="{accent}"/>',
           f'<rect x="{x}" y="{y+18}" width="{w}" height="16" fill="{accent}"/>',
           f'<text x="{x+w/2}" y="{y+24}" text-anchor="middle" font-family="{FONT}" '
           f'font-size="19" font-weight="700" fill="#ffffff">{title}</text>']
    pin_y = {}
    for i, p in enumerate(pins):
        py = y + 46 + i * ROW_H + ROW_H / 2
        pin_y[p] = py
    return "".join(out), pin_y, h


svg_parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
    f'height="{H}" role="img" aria-label="Schematic wiring: ESP32-S3 to LSM6DSO '
    f'(I2C) and ST7789 (SPI), with 3V3 and GND nets">',
    f'<rect width="{W}" height="{H}" fill="{BG}"/>',
    f'<text x="48" y="54" font-family="{FONT}" font-size="30" font-weight="700" '
    f'fill="{INK}">Wiring — pad to pad</text>',
    f'<text x="50" y="86" font-family="{FONT}" font-size="16" fill="{MUTED}">'
    f'One colour per net \u2014 trace each wire end to end. '
    f'IMU left row (INT1\u2026OCS_A): leave open.</text>',
]

# per-net swatch legend row
lx, ly = 50, 108
for col, lab in legend:
    svg_parts.append(f'<rect x="{lx}" y="{ly}" width="26" height="6" rx="3" fill="{col}"/>')
    svg_parts.append(f'<text x="{lx+32}" y="{ly+8}" font-family="{FONT}" '
                     f'font-size="14" fill="{INK}">{lab}</text>')
    lx += 32 + len(lab) * 8 + 22

s3_svg, s3y, s3h = block(S3_X, TOP, S3_W, s3_pins, "ESP32-S3 (N16R8)", "#4a6078")
imu_svg, imuy, imuh = block(IMU_X, TOP, IMU_W, imu_pins, "LSM6DSO (IMU)", C_SCL_I)
tft_top = TOP + imuh + 36
tft_svg, tfty, tfth = block(TFT_X, tft_top, TFT_W, tft_pins, "ST7789 (TFT)", C_SCK)

# nets first (under the blocks' pin dots but over the cards is fine)
for src, dst, dpin, col in nets:
    sy = s3y[src]
    dy = imuy[dpin] if dst == "imu" else tfty[dpin]
    sx = S3_X + S3_W
    dx = IMU_X if dst == "imu" else TFT_X
    midx = (sx + dx) / 2
    svg_parts.append(
        f'<path d="M {sx} {sy} C {midx} {sy}, {midx} {dy}, {dx} {dy}" '
        f'fill="none" stroke="{col}" stroke-width="3.5" opacity="0.9"/>')
    svg_parts.append(f'<circle cx="{sx}" cy="{sy}" r="5" fill="{col}"/>')
    svg_parts.append(f'<circle cx="{dx}" cy="{dy}" r="5" fill="{col}"/>')

svg_parts += [s3_svg, imu_svg, tft_svg]

# pin labels (drawn after blocks so they sit on the cards)
for p, py in s3y.items():
    svg_parts.append(f'<text x="{S3_X+S3_W-14}" y="{py+5}" text-anchor="end" '
                     f'font-family="{FONT}" font-size="16" fill="{INK}">{p}</text>')
for p, py in imuy.items():
    svg_parts.append(f'<text x="{IMU_X+14}" y="{py+5}" font-family="{FONT}" '
                     f'font-size="16" fill="{INK}">{p}</text>')
for p, py in tfty.items():
    svg_parts.append(f'<text x="{TFT_X+14}" y="{py+5}" font-family="{FONT}" '
                     f'font-size="16" fill="{INK}">{p}</text>')

svg_parts.append(f'<text x="50" y="{H-24}" font-family="{FONT}" font-size="15" '
                 f'fill="{MUTED}">BL to 3V3 or GPIO21 \u00b7 don\u2019t tie TFT SDA to '
                 f'IMU SDA \u00b7 S3 underside silk is mirrored vs top.</text>')
svg_parts.append("</svg>")

with open("wiring-schematic.svg", "w") as f:
    f.write("\n".join(svg_parts))
print("ok -> wiring-schematic.svg")
