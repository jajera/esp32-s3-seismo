# Firmware

Each phase that needs an app gets its **own folder** under [`firmware/`](../firmware/). That folder is a frozen snapshot: later phases add a new directory instead of rewriting an old one.

```text
firmware/
  01-hello/          # Phase 1 (+ kept for Phases 2–3)
  04-i2c-scan/       # Phase 4
  05-accel/          # Phase 5
  06-tft-fill/       # Phase 6
  07-intensity-ui/   # Phase 7
```

Phase 0 has no app (erased chip). Phases 2–3 keep flashing `01-hello` unchanged.

---

## On the board now

**`firmware/07-intensity-ui`** — Phase 7 STA/LTA event + PGA→MMI (Wald 1999) demo UI.

Previous: **`firmware/06-tft-fill`** · **`firmware/05-accel`** · **`firmware/04-i2c-scan`** · **`firmware/01-hello`**.

| Setting | Value |
|---------|-------|
| Port | COM `/dev/ttyACM0` (CH343) |
| MAC | `28:84:85:8C:D0:40` |
| Flash / PSRAM | 16MB / 8MB |

CDC off so `Serial` is on COM. Sources: [`07-intensity-ui/src/main.cpp`](../firmware/07-intensity-ui/src/main.cpp) · [`07-intensity-ui/platformio.ini`](../firmware/07-intensity-ui/platformio.ini)

---

## Build and flash

Same pattern for every phase: `cd` into the phase folder, build with env `esp32-s3-n16r8`, then upload to the COM port. Phase 1 as the worked example —

<div class="run" markdown>

```bash
cd firmware/01-hello
pio run -e esp32-s3-n16r8
```

```text {.no-copy}
RAM:   [=         ]   8.1% (used 26700 bytes from 327680 bytes)
Flash: [=         ]   5.8% (used 380669 bytes from 6553600 bytes)
========================= [SUCCESS] Took 10.19 seconds =========================
```

</div>

<div class="run" markdown>

```bash
pio run -e esp32-s3-n16r8 -t upload --upload-port /dev/ttyACM0
```

```text {.no-copy}
Connected to ESP32-S3 on /dev/ttyACM0:
…
Hash of data verified.
Hard resetting via RTS pin...
========================= [SUCCESS] Took 10.32 seconds =========================
```

</div>

Serial: [Phase 1, section 1.3](phases/01-hello-flash.md#13-serial).

---

## Stage map

| Phase | Folder | On the chip |
|-------|--------|-------------|
| 0 | — | empty (erased) |
| **1** | **`01-hello`** | hello |
| 2 | `01-hello` | same image, not edited |
| 3 | `01-hello` | same image, not edited |
| 4 | `04-i2c-scan` | I2C scan |
| 5 | `05-accel` | accel stream |
| 6 | `06-tft-fill` | TFT SPI fill |
| **7** | **`07-intensity-ui`** | lab magnitude UI |

## Change log

- **Phase 0** — erase; no app
- **Phase 1** — added `firmware/01-hello/`
- **Phase 4** — added `firmware/04-i2c-scan/`
- **Phase 5** — added `firmware/05-accel/`
- **Phase 6** — added `firmware/06-tft-fill/`
- **Phase 7** — added `firmware/07-intensity-ui/`
