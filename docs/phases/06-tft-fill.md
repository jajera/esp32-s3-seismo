# Phase 6 — Wire TFT SPI + fill screen

Add five SPI wires and prove the panel draws. Power (Phase 2) and IMU I2C (Phases 3–4) stay on. **BL** is already on **3V3** — no new backlight wire.

## Firmware

**Changed.** New folder [`firmware/06-tft-fill/`](../../firmware/06-tft-fill/).

## Preconditions

- [Checkpoint 5](05-accel-stream.md) passed
- Unplug USB while seating SPI jumpers

---

## 6.1 SPI wires

![Phase 6 — TFT SPI](../assets/wiring-phase6-tft.svg)

| S3 | TFT |
|----|-----|
| **GPIO12** | **SCL** (SCK) |
| **GPIO11** | **SDA** (MOSI) |
| **GPIO10** | **CS** |
| **GPIO9** | **DC** |
| **GPIO7** | **RES** |

Do **not** tie TFT SDA to IMU SDA. All five or the panel stays blank.

---

## 6.2 Flash

Stop any serial monitor on COM first.

<div class="run" markdown>

```bash
cd firmware/06-tft-fill
pio run -e esp32-s3-n16r8 -t upload --upload-port /dev/ttyACM0
```

```text {.no-copy}
Connected to ESP32-S3 on /dev/ttyACM0:
…
Hash of data verified.
Hard resetting via RTS pin...
========================= [SUCCESS] Took 34.13 seconds =========================
```

</div>

<div class="run" markdown>

```bash
pio device monitor -b 115200 --port /dev/ttyACM0
```

```text {.no-copy}
seismo tft-fill — phase 6
SPI SCK=12 MOSI=11 CS=10 DC=9 RST=7  BL=3V3(phase2)
IMU WHO_AM_I=0x6C (expect 0x6C) — buses coexist
cycling red → green → blue every 1 s
fill RED
fill GREEN
fill BLUE
```

</div>

Panel should cycle full-screen **red → green → blue**.

## 6.3 If blank

- Confirm 4-SPI jumpers on the module (silk R3+R5)
- BL still powered (Phase 2)
- CS/DC/RST not swapped
- All five SPI wires seated

## Checkpoint 6

- [x] Visible full-screen color change on TFT
- [x] Serial shows `WHO_AM_I=0x6C` (I2C still up with SPI)
- [x] Logged in [lab-log.md](../lab-log.md)

**Stop here until checkpoint passes.**

**Next:** [Phase 7 — Intensity UI](07-intensity-ui.md)
