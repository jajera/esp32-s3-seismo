# ESP32-S3 seismo

A desk seismometer on Ubuntu 24.04: ESP32-S3 N16R8 + LSM6DSO + ST7789 — wire it, flash phase folders, thump the table.

Docs: [esp32-s3-seismo.johna.kiwi](https://esp32-s3-seismo.johna.kiwi/)

## Docs locally

```bash
cd ~/workspace/jajera/esp32-s3-seismo
/usr/bin/python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m zensical serve
```

Open the URL printed by the server (usually `http://127.0.0.1:8000`).

Use `python -m` (not `.venv/bin/zensical` alone) so a broken script shebang cannot bite. Prefer `/usr/bin/python3.12` — a shell alias that points `python3` at 3.14 breaks venv creation.

## Start here

1. [docs/prerequisites.md](docs/prerequisites.md) — git, Python, PlatformIO  
2. [docs/index.md](docs/index.md) — story + phases  
3. [docs/firmware.md](docs/firmware.md) — frozen `firmware/<nn>-…/` apps  

**Current:** v1 complete (Phase 7 — STA/LTA + MMI). Tune knobs in `firmware/07-intensity-ui/src/main.cpp`.
