# Phase 5 — LSM6DSO accel stream

Read accelerometer samples over the I2C already wired and print them on serial. No new wires.

## Firmware

**Changed.** New folder [`firmware/05-accel/`](../../firmware/05-accel/). Leave earlier phase folders untouched.

## Preconditions

- [Checkpoint 4](04-i2c-scan.md) passed at **0x6A**
- Phases 2–4 wiring still on

---

## 5.1 Flash

Stop any serial monitor on COM first.

<div class="run" markdown>

```bash
cd firmware/05-accel
pio run -e esp32-s3-n16r8 -t upload --upload-port /dev/ttyACM0
```

```text {.no-copy}
Connected to ESP32-S3 on /dev/ttyACM0:
…
Hash of data verified.
Hard resetting via RTS pin...
========================= [SUCCESS] Took 13.71 seconds =========================
```

</div>

<div class="run" markdown>

```bash
pio device monitor -b 115200 --port /dev/ttyACM0
```

```text {.no-copy}
seismo accel — phase 5
SDA=GPIO8 SCL=GPIO18 addr=0x6A
WHO_AM_I=0x6C (expect 0x6C)
Watch pitch/roll (degrees) when you tilt — |a| stays ~1 on slow tilt
ax=-0.02 ay=-0.02 az=+1.00  pitch=+1° roll=-1°
```

</div>

Print ~5 Hz. **ax/ay/az** in g. **pitch/roll** in degrees — those are what move when you tilt. A slow tilt does not change magnitude much; watch the angles (tens of degrees).

## 5.2 Validate by hand

1. Resting → `az≈+1`, `pitch/roll≈0°` (this lab: Z up).
2. Tilt the board → **pitch** or **roll** jumps by tens of degrees.
3. Note silk **X/Y** in [lab-log.md](../lab-log.md).

## Checkpoint 5

- [x] Continuous accel lines on serial
- [x] Rest vs tilt visibly different (pitch/roll °)
- [x] Orientation noted for later UI (rest: **Z ≈ +1 g**, X/Y ≈ 0)

**Stop here until checkpoint passes.**

**Next:** [Phase 6 — TFT fill](06-tft-fill.md)
