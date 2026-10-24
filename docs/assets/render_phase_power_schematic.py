"""Clean schematic wiring diagrams (SVG) for Phases 2, 3, 4 and 6.

Same look and colour code as the Hardware-page schematic:
  3V3 = red, GND = black, I2C/SPI signals each their own colour.
Only the wires added in that phase are drawn; earlier pins are greyed.

Regenerate: python3 render_phase_power_schematic.py
"""

INK = "#1c1e20"
MUTED = "#6e7376"
BG = "#f5f5f2"
RED = "#c0392b"      # 3V3
BLK = "#2b2d2f"      # GND
C_SCL = "#1f8a70"    # I2C SCL (teal)
C_SDA = "#2e86de"    # I2C SDA (blue)
C_SCK = "#e67e22"    # SPI SCK  (orange)
C_MOSI = "#8e44ad"   # SPI MOSI (purple)
C_CS = "#16a085"     # SPI CS   (green-teal)
C_DC = "#d81b60"     # SPI DC   (magenta)
C_RES = "#f1c40f"    # SPI RES  (yellow)
S3_ACCENT = "#4a6078"
TFT_ACCENT = "#e67e22"
IMU_ACCENT = "#1f8a70"

FONT = "DejaVu Sans, sans-serif"
ROW_H = 40


def block(x, y, w, pins, title, accent, dim=()):
    """pins: list of names. dim: names drawn greyed (present but unused)."""
    h = ROW_H * len(pins) + 50
    parts = [
        f'<rect x="{x+4}" y="{y+5}" width="{w}" height="{h}" rx="12" fill="#e1e1dd"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="#ffffff" '
        f'stroke="{accent}" stroke-width="3"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="36" rx="12" fill="{accent}"/>',
        f'<rect x="{x}" y="{y+20}" width="{w}" height="16" fill="{accent}"/>',
        f'<text x="{x+w/2}" y="{y+25}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="18" font-weight="700" fill="#ffffff">{title}</text>',
    ]
    pin_y = {}
    for i, p in enumerate(pins):
        py = y + 50 + i * ROW_H + ROW_H / 2
        pin_y[p] = py
        col = "#b9bdbf" if p in dim else INK
        parts.append(f'<text x="{x+w/2}" y="{py+5}" text-anchor="middle" '
                     f'font-family="{FONT}" font-size="16" fill="{col}">{p}</text>')
    return "".join(parts), pin_y, h


def render(out, title, sub, s3_pins, dev_name, dev_accent, dev_pins, dev_dim,
           nets, footer, legend=((RED, "3V3"), (BLK, "GND"))):
    W = 940
    s3x, s3w = 70, 230
    devx, devw = 640, 230
    top = 150

    s3_svg, s3y, s3h = block(s3x, top, s3w, s3_pins, "ESP32-S3 (N16R8)", S3_ACCENT)
    dev_svg, devy, devh = block(devx, top, devw, dev_pins, dev_name, dev_accent, dev_dim)
    H = top + max(s3h, devh) + 90

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="{title}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<text x="48" y="52" font-family="{FONT}" font-size="27" '
        f'font-weight="700" fill="{INK}">{title}</text>',
        f'<text x="50" y="82" font-family="{FONT}" font-size="15" '
        f'fill="{MUTED}">{sub}</text>',
    ]
    # legend swatches
    lx = 50
    for col, lab in legend:
        parts.append(f'<rect x="{lx}" y="108" width="26" height="6" rx="3" fill="{col}"/>')
        parts.append(f'<text x="{lx+32}" y="116" font-family="{FONT}" '
                     f'font-size="14" fill="{INK}">{lab}</text>')
        lx += 32 + len(lab) * 8 + 24

    # nets
    for src, dpin, col in nets:
        sy = s3y[src]
        dy = devy[dpin]
        sx = s3x + s3w
        dx = devx
        midx = (sx + dx) / 2
        parts.append(f'<path d="M {sx} {sy} C {midx} {sy}, {midx} {dy}, {dx} {dy}" '
                     f'fill="none" stroke="{col}" stroke-width="4"/>')
        parts.append(f'<circle cx="{sx}" cy="{sy}" r="5" fill="{col}"/>')
        parts.append(f'<circle cx="{dx}" cy="{dy}" r="5" fill="{col}"/>')

    parts += [s3_svg, dev_svg]
    parts.append(f'<text x="50" y="{H-26}" font-family="{FONT}" font-size="14" '
                 f'fill="{MUTED}">{footer}</text>')
    parts.append("</svg>")

    with open(out, "w") as f:
        f.write("\n".join(parts))
    print("ok ->", out)


# --- Phase 2: TFT power -----------------------------------------------------
render(
    out="wiring-phase2-tft.svg",
    title="Phase 2 — power the TFT",
    sub="Three wires. IMU stays unwired. TFT SPI pins stay open.",
    s3_pins=["3V3", "GND"],
    dev_name="ST7789 (TFT)",
    dev_accent=TFT_ACCENT,
    dev_pins=["VDD", "BL", "GND", "SCL", "SDA", "RES", "DC", "CS"],
    dev_dim=["SCL", "SDA", "RES", "DC", "CS"],
    nets=[("3V3", "VDD", RED), ("3V3", "BL", RED), ("GND", "GND", BLK)],
    footer="Greyed pins (SCL\u2026CS) are the SPI bus \u2014 wired in Phase 6, not now.",
)

# --- Phase 3: IMU power + address straps ------------------------------------
render(
    out="wiring-phase3-imu.svg",
    title="Phase 3 — power the IMU",
    sub="Four wires: supply + CS/SDO address straps. TFT power from Phase 2 stays.",
    s3_pins=["3V3", "GND"],
    dev_name="LSM6DSO (IMU)",
    dev_accent=IMU_ACCENT,
    dev_pins=["VDD", "CS", "GND", "SDO", "SCL", "SDA"],
    dev_dim=["SCL", "SDA"],
    nets=[("3V3", "VDD", RED), ("3V3", "CS", RED),
          ("GND", "GND", BLK), ("GND", "SDO", BLK)],
    footer="CS\u21923V3 and SDO\u2192GND set I2C address 0x6A. SCL/SDA wired in Phase 4.",
)

# --- Phase 4: IMU I2C data wires --------------------------------------------
render(
    out="wiring-phase4-i2c.svg",
    title="Phase 4 — IMU I2C data",
    sub="Two data wires. Power + CS/SDO straps from Phases 2\u20133 stay on.",
    s3_pins=["GPIO18", "GPIO8"],
    dev_name="LSM6DSO (IMU)",
    dev_accent=IMU_ACCENT,
    dev_pins=["VDD", "CS", "GND", "SDO", "SCL", "SDA"],
    dev_dim=["VDD", "CS", "GND", "SDO"],
    nets=[("GPIO18", "SCL", C_SCL), ("GPIO8", "SDA", C_SDA)],
    footer="Both wires or nothing \u2014 one alone scans as none. Expect 0x6A.",
    legend=((C_SCL, "SCL"), (C_SDA, "SDA")),
)

# --- Phase 6: TFT SPI wires -------------------------------------------------
render(
    out="wiring-phase6-tft.svg",
    title="Phase 6 — TFT SPI",
    sub="Five SPI wires. Power (Phase 2) + IMU I2C (Phases 3\u20134) stay on. BL already on 3V3.",
    s3_pins=["GPIO12", "GPIO11", "GPIO10", "GPIO9", "GPIO7"],
    dev_name="ST7789 (TFT)",
    dev_accent=TFT_ACCENT,
    dev_pins=["VDD", "BL", "GND", "SCL", "SDA", "RES", "DC", "CS"],
    dev_dim=["VDD", "BL", "GND"],
    nets=[("GPIO12", "SCL", C_SCK), ("GPIO11", "SDA", C_MOSI),
          ("GPIO10", "CS", C_CS), ("GPIO9", "DC", C_DC), ("GPIO7", "RES", C_RES)],
    footer="All five or the panel stays blank. Don\u2019t tie TFT SDA to IMU SDA.",
    legend=((C_SCK, "SCK"), (C_MOSI, "MOSI"), (C_CS, "CS"),
            (C_DC, "DC"), (C_RES, "RES")),
)
