---
inclusion: always
---

# Docs

Write like a lab notebook people can follow. **Prerequisites** come first (`docs/prerequisites.md`) — this demo uses Ubuntu 24.04; assume no `pio` yet. Then one phase file, one checkpoint — don’t move on until it passes.

Overview can borrow a short **story / as-built** strip (photos + human lede) like the PICAXE project notes — keep the engine on Zensical, not Eleventy. Phase pages stay procedural.

Show the work: short mermaid or a photo when it helps. For shell steps, **always** use a `.run` block — command on top, real output underneath (`{.no-copy}`). Never a lone bash fence with no result (that’s the format we hate). Tree listings and short code excerpts are fine outside `.run`. Put failures and wins in `docs/lab-log.md`.

Every phase needs a **Firmware** blurb: which folder, changed or not. New behaviour = new `firmware/<nn>-…/` tree. Update `docs/firmware.md` too — don’t leave it only in chat.

```bash
.venv/bin/zensical serve
```

Keep `zensical.toml` nav honest about what’s done vs next.
