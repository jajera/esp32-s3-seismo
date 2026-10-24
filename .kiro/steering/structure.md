---
inclusion: always
---

# Structure

```text
docs/           walkthrough site (phases, hardware, firmware story, lab log)
firmware/       one folder per phase app (01-hello, …) — frozen snapshots
scripts/        setup-linux-usb.sh + PlatformIO udev rules
zensical.toml   site nav
.kiro/steering/ agent guidance
.cursor/rules/  same for Cursor
.github/        pages + markdown-lint + commitmsg-conform
```

Docs decide the order of work. New firmware behaviour = new `firmware/<nn>-…/` directory, not edits to an old phase folder.
