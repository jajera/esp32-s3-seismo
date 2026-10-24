"""High-level, icon-style block diagram for the landing page.

Three devices drawn as simple line-art icons (chip / sensor / display) joined by
labelled buses. Output is SVG so it stays crisp at any zoom — no raster upscaling.
No pin-level detail; that lives in wiring-diagram-real.png on the Hardware page.

Regenerate: python3 render_overview.py
"""

INK = "#1c1e20"
MUTED = "#6e7376"
BG = "#f5f5f2"
TEAL = "#268080"
RUST = "#ba5c34"
SLATE = "#4a6078"


def chip_icon(cx, cy, color):
    """ESP32-S3 — a QFN chip with pin stubs."""
    s = 34
    x0, y0 = cx - s, cy - s
    legs = []
    for i in range(5):
        off = -s + 13 + i * 11
        legs.append(f'<line x1="{x0-9}" y1="{cy+off}" x2="{x0}" y2="{cy+off}" '
                    f'stroke="{color}" stroke-width="3"/>')
        legs.append(f'<line x1="{x0+2*s}" y1="{cy+off}" x2="{x0+2*s+9}" y2="{cy+off}" '
                    f'stroke="{color}" stroke-width="3"/>')
        legs.append(f'<line x1="{cx+off}" y1="{y0-9}" x2="{cx+off}" y2="{y0}" '
                    f'stroke="{color}" stroke-width="3"/>')
        legs.append(f'<line x1="{cx+off}" y1="{y0+2*s}" x2="{cx+off}" y2="{y0+2*s+9}" '
                    f'stroke="{color}" stroke-width="3"/>')
    return (f'<rect x="{x0}" y="{y0}" width="{2*s}" height="{2*s}" rx="8" '
            f'fill="none" stroke="{color}" stroke-width="3.5"/>'
            f'<circle cx="{x0+12}" cy="{y0+12}" r="4" fill="{color}"/>'
            + "".join(legs))


def sensor_icon(cx, cy, color):
    """LSM6DSO — a small breakout with a chip and a motion arc."""
    w, h = 64, 48
    x0, y0 = cx - w / 2, cy - h / 2
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" '
            f'fill="none" stroke="{color}" stroke-width="3.5"/>'
            f'<rect x="{cx-13}" y="{cy-13}" width="26" height="26" rx="3" '
            f'fill="none" stroke="{color}" stroke-width="3"/>'
            f'<path d="M {cx-7} {cy+4} A 10 10 0 0 1 {cx+7} {cy-4}" '
            f'fill="none" stroke="{color}" stroke-width="2.5"/>'
            f'<circle cx="{cx+7}" cy="{cy-4}" r="2.5" fill="{color}"/>')


def display_icon(cx, cy, color):
    """ST7789 — a framed screen with a waveform."""
    w, h = 70, 54
    x0, y0 = cx - w / 2, cy - h / 2
    ix0, iy0, iw, ih = x0 + 7, y0 + 7, w - 14, h - 14
    cy2 = iy0 + ih / 2
    wave = (f'M {ix0+4} {cy2} '
            f'L {ix0+14} {cy2} L {ix0+20} {cy2-12} '
            f'L {ix0+28} {cy2+12} L {ix0+34} {cy2} L {iw+ix0-4} {cy2}')
    return (f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="6" '
            f'fill="none" stroke="{color}" stroke-width="3.5"/>'
            f'<rect x="{ix0}" y="{iy0}" width="{iw}" height="{ih}" rx="3" '
            f'fill="none" stroke="{color}" stroke-width="2"/>'
            f'<path d="{wave}" fill="none" stroke="{color}" stroke-width="2.5" '
            f'stroke-linejoin="round" stroke-linecap="round"/>')


def card(cx, cy, accent, icon_svg, name, sub):
    w, h = 300, 150
    x0, y0 = cx - w / 2, cy - h / 2
    return f'''
  <g>
    <rect x="{x0+4}" y="{y0+5}" width="{w}" height="{h}" rx="16" fill="#e1e1dd"/>
    <rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="16" fill="#ffffff"
          stroke="{accent}" stroke-width="3"/>
    <rect x="{x0}" y="{y0}" width="{w}" height="10" rx="5" fill="{accent}"/>
    <g transform="translate({x0+56},{cy+8})">{icon_svg}</g>
    <text x="{x0+112}" y="{cy-10}" font-family="DejaVu Sans, sans-serif"
          font-size="27" font-weight="700" fill="{INK}">{name}</text>
    <text x="{x0+112}" y="{cy+16}" font-family="DejaVu Sans, sans-serif"
          font-size="16" fill="{MUTED}">{sub[0]}</text>
    <text x="{x0+112}" y="{cy+38}" font-family="DejaVu Sans, sans-serif"
          font-size="16" fill="{MUTED}">{sub[1]}</text>
  </g>'''


def bus_label(mx, my, color, text):
    tw = len(text) * 11 + 22
    return (f'<rect x="{mx-tw/2}" y="{my-18}" width="{tw}" height="34" rx="9" '
            f'fill="{BG}"/>'
            f'<text x="{mx}" y="{my+6}" text-anchor="middle" '
            f'font-family="DejaVu Sans, sans-serif" font-size="21" '
            f'font-weight="700" fill="{color}">{text}</text>')


W, H = 1180, 560

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}"
     width="{W}" height="{H}" role="img"
     aria-label="Block diagram: ESP32-S3 linked to an LSM6DSO IMU over I2C and an ST7789 display over SPI">
  <rect width="{W}" height="{H}" fill="{BG}"/>

  <text x="48" y="58" font-family="DejaVu Sans, sans-serif" font-size="34"
        font-weight="700" fill="{INK}">How the station fits together</text>
  <text x="50" y="92" font-family="DejaVu Sans, sans-serif" font-size="17"
        fill="{MUTED}">Three devices on one 3V3 star — pin-level detail lives on the Hardware page.</text>

  <!-- buses (drawn under the cards) -->
  <line x1="470" y1="250" x2="760" y2="200" stroke="{TEAL}" stroke-width="6"/>
  <circle cx="470" cy="250" r="6" fill="{TEAL}"/>
  <circle cx="760" cy="200" r="6" fill="{TEAL}"/>
  <line x1="470" y1="330" x2="760" y2="410" stroke="{RUST}" stroke-width="6"/>
  <circle cx="470" cy="330" r="6" fill="{RUST}"/>
  <circle cx="760" cy="410" r="6" fill="{RUST}"/>

  {card(320, 290, SLATE, chip_icon(0, 0, SLATE), "ESP32-S3", ["N16R8 \u00b7 16MB / 8MB", "the brain + USB serial"])}
  {card(910, 200, TEAL, sensor_icon(0, 0, TEAL), "LSM6DSO", ["6-axis IMU", "the motion sensor"])}
  {card(910, 410, RUST, display_icon(0, 0, RUST), "ST7789", ["2.0\u2033 240\u00d7320", "the readout"])}

  {bus_label(615, 225, TEAL, "I2C \u00b7 0x6A")}
  {bus_label(615, 370, RUST, "SPI")}

  <line x1="48" y1="505" x2="{W-48}" y2="505" stroke="#d7d7d3" stroke-width="2"/>
  <text x="50" y="535" font-family="DejaVu Sans, sans-serif" font-size="17"
        fill="{MUTED}">Power: 3V3 only — never 5V on IMU or TFT logic.</text>
</svg>'''

with open("overview-blocks.svg", "w") as f:
    f.write(svg)
print("ok -> overview-blocks.svg")
