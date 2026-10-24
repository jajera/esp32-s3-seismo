# Lab log

What actually passed on this bench. Detail lives in each [phase](phases/00-usb-erase.md); this page is the scoreboard.

## Bench

| Item | Value |
|------|-------|
| Host | Ubuntu 24.04 · `/dev/ttyACM0` (CH343 `1a86:55d3`) |
| Board | ESP32-S3 N16R8 · MAC `28:84:85:8C:D0:40` |
| Stack | LSM6DSO @ `0x6A` · Estardyn ST7789 |
| On chip now | [`firmware/07-intensity-ui`](firmware.md) — STA/LTA + MMI (Wald 1999) |

## Checkpoints

| # | Result | Notes |
|---|--------|-------|
| 0 | **Pass** | COM port (not USB-native). `erase-flash` OK. |
| 1 | **Pass** | `01-hello` serial + MAC. |
| 2 | **Pass** | TFT 3V3 / GND / BL. |
| 3 | **Pass** | IMU power + CS→3V3, SDO→GND. |
| 4 | **Pass** | I2C: `0x6A` (IMU). Also sees `0x7E` (ignore). Both SDA+SCL required. |
| 5 | **Pass** | Accel stream; tilt on pitch/roll, not `|a|`. |
| 6 | **Pass** | TFT SPI fill R→G→B. |
| 7 | **Pass** | HP → STA/LTA EVENT; PGA → MMI I–XII; idle MMI 0; ±8 g for XII. |

**v1 bring-up complete** (2026-10-24).

## Quirks worth remembering

- Use the **COM / UART** Type-C jack, not the other one, or nothing enumerates.
- I2C scan may show **0x7E** next to the IMU — not the LSM6DSO.
- Phase 7 warmup ~10 s (LTA fill) before EVENT is armed.
- MMI is Wald et al. 1999 on instrument PGA; plant the IMU — don’t shake the board in hand if you care about the number.
