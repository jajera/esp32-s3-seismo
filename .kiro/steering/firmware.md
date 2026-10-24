---
inclusion: fileMatch
fileMatchPattern: ["firmware/**", "docs/firmware.md", "docs/phases/**"]
---

# Firmware

One directory per phase app under `firmware/<nn>-name/` (e.g. `01-hello`). That tree is a **frozen reference** — don’t rewrite it for a later phase; add a new folder instead.

Phases 2–3 keep flashing `01-hello` unchanged. Arduino / PlatformIO, env `esp32-s3-n16r8`, CDC off (COM UART).

Human tracker: `docs/firmware.md`. Phase pages: short blurb + path to the folder. Pins stay in tech steering.
