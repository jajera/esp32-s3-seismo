from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_TITLE = ImageFont.truetype(FONT, 34)
F_LBL = ImageFont.truetype(FONT, 22)
F_SM = ImageFont.truetype(FONT, 18)

W, H = 2400, 1560
canvas = Image.new("RGB", (W, H), (245, 245, 242))
d = ImageDraw.Draw(canvas)


def place(fn, crop, scale, at):
    im = Image.open(fn).convert("RGB").crop(crop)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    canvas.paste(im, at)

    def map_xy(x, y):
        return (at[0] + (x - crop[0]) * scale, at[1] + (y - crop[1]) * scale)

    return map_xy


# ESP32-S3 back silk photo; header pin centres measured from the image.
s3 = place("08-esp32s3-pinout.png", (380, 90, 1000, 1260), 1.1, (60, 160))
S3_X = 891
S3_PIN_Y = {"3V3": 285, "GPIO7": 541, "GPIO18": 712, "GPIO8": 755,
            "GPIO9": 882, "GPIO10": 926, "GPIO11": 967, "GPIO12": 1010, "GND": 1181}
s3_pin = {k: s3(S3_X, y) for k, y in S3_PIN_Y.items()}

# LSM6DSO bottom silk photo; pad centres from Hough circle detection.
imu = place("02-lsm6dso-pinout-bottom.png", (180, 200, 610, 580), 1.25, (1480, 150))
IMU_PAD = {"VDD": (533, 239), "GND": (540, 294), "SCL": (544, 350),
           "SDA": (550, 408), "SDO": (558, 468), "CS": (560, 528)}
imu_pad = {k: imu(*v) for k, v in IMU_PAD.items()}

# Estardyn ST7789 front photo; top header pad centres.
tft = place("04-tft-front.png", (130, 120, 655, 950), 0.86, (1500, 760))
TFT_PAD = {"GND": (268, 158), "VDD": (304, 158), "SCL": (338, 158), "SDA": (374, 158),
           "RES": (408, 158), "DC": (444, 158), "CS": (478, 158), "BL": (514, 158)}
tft_pad = {k: tft(*v) for k, v in TFT_PAD.items()}

RED, BLK = (220, 30, 30), (20, 20, 20)
GRN, ORG = (0, 150, 60), (235, 120, 0)
WIDTH = 5


def wire(points, color):
    d.line(points, fill=color, width=WIDTH, joint="curve")
    for p in (points[0], points[-1]):
        d.ellipse((p[0] - 9, p[1] - 9, p[0] + 9, p[1] + 9), outline=color, width=4)


# IMU wires: out of S3 pin -> own vertical lane -> over the top of the IMU -> down the
# right side -> left into the pad (pads sit on the IMU's right edge).
imu_runs = [
    ("3V3", "VDD", RED), ("3V3", "CS", RED), ("GND", "GND", BLK),
    ("GND", "SDO", BLK), ("GPIO18", "SCL", GRN), ("GPIO8", "SDA", GRN),
]
for i, (src, dst, col) in enumerate(imu_runs):
    sx, sy = s3_pin[src]
    px, py = imu_pad[dst]
    lane_x = 760 + i * 28
    top_y = 70 + i * 13
    right_x = 2080 + i * 26
    wire([(sx, sy), (lane_x, sy), (lane_x, top_y), (right_x, top_y),
          (right_x, py), (px, py)], col)

# TFT wires: out of S3 pin -> own vertical lane -> horizontal lane above the TFT -> down into pad.
tft_runs = [
    ("GND", "GND", BLK), ("3V3", "VDD", RED), ("GPIO12", "SCL", ORG), ("GPIO11", "SDA", ORG),
    ("GPIO7", "RES", ORG), ("GPIO9", "DC", ORG), ("GPIO10", "CS", ORG), ("3V3", "BL", RED),
]
for i, (src, dst, col) in enumerate(tft_runs):
    sx, sy = s3_pin[src]
    px, py = tft_pad[dst]
    lane_x = 960 + i * 28
    lane_y = 640 + i * 14
    wire([(sx, sy), (lane_x, sy), (lane_x, lane_y), (px, lane_y), (px, py)], col)

# Labels at the S3 pins (photo silk is small).
for name, (x, y) in s3_pin.items():
    d.rounded_rectangle((x - 175, y - 16, x - 30, y + 16), radius=6, fill=(255, 255, 255), outline=(0, 0, 0))
    d.text((x - 168, y - 13), name, fill=(0, 0, 0), font=F_LBL)

d.text((60, 25), "ESP32-S3 seismo hard-wire: wires drawn pad-to-pad on the board photos", fill=(0, 0, 0), font=F_TITLE)
d.text((60, 75), "ESP32-S3 N16R8 (UNDERSIDE view, back silk)", fill=(0, 0, 0), font=F_LBL)
d.rectangle((1476, 112, 1840, 142), fill=(255, 255, 255))
d.text((1480, 115), "LSM6DSO (underside, pin silk)", fill=(0, 0, 0), font=F_LBL)
d.text((1500, 1490), "ST7789 2.0in (front)", fill=(0, 0, 0), font=F_LBL)
d.text((60, 1470), "Red = 3V3   Black = GND   Green = I2C (0x6A)   Orange = SPI   "
       "IMU left row (INT1..OCS_A): leave unconnected", fill=(0, 0, 0), font=F_SM)
d.text((60, 1500), "S3 photo is the underside: pins are mirrored left/right versus looking at the top. "
       "Match by silk label, not by side.", fill=(150, 0, 0), font=F_SM)

canvas.save("wiring-diagram-real.png")
print("ok")
