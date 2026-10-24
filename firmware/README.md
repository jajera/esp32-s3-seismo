# Firmware

One folder per phase that ships an app. Older folders stay as permanent reference — don’t rewrite them for a later phase; add a new directory instead.

| Dir | Phase | Role |
|-----|-------|------|
| [`01-hello/`](01-hello/) | 1 (and 2–3, unchanged) | Serial hello |
| [`04-i2c-scan/`](04-i2c-scan/) | 4 | I2C scan @ 0x6A |
| [`05-accel/`](05-accel/) | 5 | LSM6DSO accel stream |
| [`06-tft-fill/`](06-tft-fill/) | 6 | ST7789 SPI fill |
| [`07-intensity-ui/`](07-intensity-ui/) | 7 | lab magnitude / waveform |

Docs: [docs/firmware.md](../docs/firmware.md).

```bash
cd firmware/01-hello
pio run -e esp32-s3-n16r8
pio run -e esp32-s3-n16r8 -t upload --upload-port /dev/ttyACM0
```
