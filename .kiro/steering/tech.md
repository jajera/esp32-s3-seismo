---
inclusion: always
---

# Tech

Demo is written for Ubuntu 24.04. Fresh machine: follow `docs/prerequisites.md` before any phase (apt → PlatformIO → `PATH`). Don’t assume `pio` exists.

Docs: Zensical + patina. Firmware: PlatformIO Arduino, env `esp32-s3-n16r8` (16MB flash, 8MB PSRAM).

Plug the **COM** port (CH343 → `/dev/ttyACM0`), not USB-OTG. Keep `ARDUINO_USB_CDC_ON_BOOT=0` so Serial hits that UART.

Pins we use:

- I2C: SDA **8**, SCL **18** (IMU at **0x6A** — CS to 3V3, SDO to GND)
- TFT SPI: SCK **12**, MOSI **11**, CS **10**, DC **9**, RST **7**, BL to 3V3 or **21**
- Don’t tie TFT SDA to IMU SDA
- Leave alone: 0, 19/20, 38/48, 45/46, and 35–37 on this Octal board

```bash
.venv/bin/zensical serve
cd firmware/01-hello && pio run -e esp32-s3-n16r8
pio run -e esp32-s3-n16r8 -t upload --upload-port /dev/ttyACM0
```

Lab board MAC: `28:84:85:8c:d0:40`.
