# Female protagonist battle static v06: v05 lock dependency closure (QA note)

Status: UNAPPROVED, test-only. No runtime integration. No game/scripts, game/scenes or game/data change. No animation.

## Problem

Commit `33ee09b` added the v06 author tool `tools/…battle-idle-right-native-0p65-author_unapproved-v06_20261016-065106-7ac0f8e3.py`. Its `check` and `build` modes hash-lock three v05 files through `V05_LOCKS` (gate `v05_unchanged`, sha256-bytes). Those three files were still untracked. A clean clone could not run `check`: `read_bytes` raised on the first missing file.

## Fix: only the three locked files are tracked

All three are binary and are compared byte for byte, so line endings play no part.

| File (`game/assets/characters/combat-sideview-pilots/`) | sha256 (matches `V05_LOCKS`) |
|---|---|
| `…static-native0p65_unapproved-v05_20261016-054620-8e5e4656.png` (1,767 B) | `8165cee30f53fb598766410b066c0e3cfa4f4daa67cef19183261149badf38bf` |
| `…static-native0p65_editable-layers_unapproved-v05_20261016-054620-ad13c0b8.pxo` (9,388 B) | `9e28644f58430772ec9ae795d409081333fb4543480ea8a36ef3327b21f2240b` |
| `…static-native0p65_editable-layers_unapproved-v05_20261016-054620-f29f9ba1.ora` (9,601 B) | `eedd45dbfed96cc96cd8dca4bb3a2d9ac1f71755d7b0d462264201da9b2097ef` |

These are baseline reference files only. They stay unapproved and are not referenced by runtime code.

## Deliberately left untracked

- **v05 author tool** (`…author_unapproved-v05_20261016-054620-c5a1f05e.py`). It hash-locks v04 files that are themselves untracked. Tracking it would open a new broken dependency, and v06 does not need it.
- **v05 QA note** (`…visual-qa-note_unapproved-v05_20261016-054620-e782a2c8.md`). It links to the untracked v04 QA note and lists the untracked v05 tool, capture script and captures. In a clone those links would point nowhere.
- **v05 manifest, capture script and the two party captures.** No v06 gate reads them.

Already tracked before this change and not modified: the Codex v05 visual audit (`…battle-static-v05-codex-visual-audit_unapproved-v01_20261016-023737-c64e85a2.md`) and the Codex v05 identity/readability audit (`…battle-static-v05-identity-readability-audit_unapproved-v01_20261016-064516-5c1f320e.md`). The v8 south reference PNG that v06 also reads was already tracked.

## v06 `check` after staging

- **Working tree, with `APPDATA` redirected to a fresh temp dir for the whole run:** `PASS`, 19/19 gates, `v05_unchanged: true` before and after.
- **Same run, with the real `APPDATA`:** 18/19. Only `pixelorama_roundtrips` failed, on its sub-check `real_appdata_pixelorama_untouched_except_heartbeat`. The user's open Pixelorama GUI (PID 50828, started 2026-10-15 13:56) autosaved `backups/2026_10_15_13_56_34/(untitled backup)…` while the check was running. The tool's own headless exports already use a redirected `APPDATA`, and every round-trip export matched. The failure is caused by that environment, not by the v05 dependency. The GUI was left open.
- **Clean clone** (`git clone -c core.longpaths=true` into `C:\wb\v06c`; only the gitignored Pixelorama folder was copied in): `git ls-files` lists all three v05 files and their `sha256sum` values match `V05_LOCKS`. `check` with a redirected `APPDATA` gave `PASS`, 19/19, `v05_unchanged: true`.

Pixelorama 1.2.3 itself is still a local, gitignored tool (`work/tooling/…`). The pixel/manifest gates need only Python, NumPy and Pillow. The round-trip gates need that executable.

## Completion meter

Zero-change closeout. Stays at 35.0%: sprites 0/52, scenes 0/11, human playtests 0/2.
