# QA note: female south idle v8 — lossless `.pxo` source and Pixelorama headless round-trip

- **Date:** 2026-10-15 (UTC stamp 20261015-080907, run id `2ad6d314`)
- **Scope:** user permission for the FEMALE single-direction Pixelorama pilot. South idle static only. No other direction, action or character was created.
- **Result:** **PASS.** Pixelorama 1.2.3 `--headless --export` of the new `.pxo` decodes to RGBA bytes identical to the approved v8 PNG (0 of 8,960 texels differ), on two runs.
- **Approval status:** unchanged. This is a container for the already-approved v8 static frame. It does not approve a sprite set, a direction, animation or runtime use. The manifest says `art_approved: false`. The [v8 decision doc](../character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md) is still the only approval record.
- **Auth:** Claude Code signed in through claude.ai (firstParty, Max). No `ANTHROPIC_*` environment variables were set.

## Files (all new; nothing existing was edited)

| File | Hash |
|---|---|
| [`.pxo` source](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable_m8-v08_20261015-080907-c8a1c140.pxo) | sha256-bytes `cafa4998b107ae4b884cc877b80bbc695df267f37e09fb6e69701567f08a849e` |
| [manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-editable-manifest_m8-v08_20261015-080907-270b2256.json) | sha256-text-lf-v1 `d40059be868e50f6acbea509e14dd2e8ccd6cac3b1405f39399c9fbff17e73c3` |
| [tool](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-pxo-source-roundtrip_m8-v08_20261015-080907-05c22e55.py) (`build` / `check`) | recorded in the manifest (sha256-text-lf-v1) |

Source, read only: [v8 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png), sha256-bytes `ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd`. This matches the decision-doc lock before and after every step. The tool refuses to run if it does not match.

## What the `.pxo` contains

- Format: pxo_version 7 for Pixelorama v1.2.3-stable, `color_mode` 5 (RGBA8), 80×112, 1 frame. Zip entries use fixed timestamps, so rebuilds are byte-identical (checked: `build` run twice reported `unchanged`).
- Layers, bottom to top:
  1. `v8-baseline` (visible): v8's decoded RGBA, stored unchanged. That is 2,419 opaque texels, 32 colours, binary alpha, alpha bounds (13,8)–(55,103).
  2. `guides` (hidden, locked): `#ff00ff` cell border, ticks on rows 8 and 103 (the 96-texel body), and pin (40,104). Every guide texel sits on a v8-transparent texel, so a leak would show up as a diff.
- `preview.png` inside the zip is the v8 PNG file bytes, unchanged.
- **Not done:** the per-role layer split from pipeline doc §1.3 (`hair-front`, `head-face`, …). Deciding which v8 texel belongs to which role is an art call nobody has signed off. It can be cut later from this file in the GUI, as a new uniquely named `.pxo`.

## Round-trip check (`python -I -B <tool> check`)

Python 3.12.14, Pillow 12.3.0, numpy 2.3.5. The check copies the `.pxo` into a fresh `%LOCALAPPDATA%\Temp\wb-v8pxo-*` directory, then runs this command twice:

`Pixelorama.exe --headless --quit -- --export -o <empty dir>\f.png <copy>.pxo`

| Check | Run 1 | Run 2 |
|---|---|---|
| exit code | 0 | 0 |
| PNGs exported | 1 (`protagonist-female-south-idle-selout-v8.png`) | 1 |
| mode / size | RGBA 80×112 | RGBA 80×112 |
| decoded RGBA bytes == decoded v8 RGBA | **yes** | **yes** |
| differing texels | 0 | 0 |
| hidden guide texels leaked into the export | 0 | 0 |
| temp `.pxo` copy unchanged by Pixelorama | yes | yes |
| export PNG sha256-bytes | `f62179e6…f58ad` | `f62179e6…f58ad` (byte-identical) |

Also checked:

- v8 PNG hash, `.pxo` hash and manifest hash are unchanged after the check.
- The `.pxo` on disk equals a fresh in-memory rebuild, and its `v8-baseline` blob equals v8's RGBA.

**Pixel-identical, not file-identical:** the exported PNG file is **not** byte-identical to the v8 PNG *file*, because Pixelorama's PNG encoder differs from Pillow's. The decoded RGBA bytes (all four channels, all 8,960 texels, transparent texels included as `0,0,0,0`) are identical. This is the texel-level equality the pipeline doc requires. The v8 PNG itself was never written or re-encoded.

## Pixelorama settings and side effects

- `%APPDATA%\pixelorama\config.ini` was rewritten by each CLI run (`current_dir`, as the pipeline doc says). It was backed up before the check, restored byte-for-byte with its mtime after each run, and verified: sha256 `fcdf4e58…66a0` before and after.
- Other `%APPDATA%\pixelorama` changes: Godot's own log rotation only. `logs/godot.log` was rewritten, two new timestamped logs were added, and the two oldest rotated logs were dropped. No settings, palettes, layouts or extensions changed.
- One earlier `Pixelorama.exe --headless --quit -- --version` probe (prints `v1.2.3-stable`) ran with the same backup and restore. config.ini was unchanged by it.
- **CLI naming quirk:** the exported file is named after the `.pxo`'s `export_profile.file_name`, not the `-o` basename or the `.pxo` file name. The tool picks up whatever single PNG appears in the empty directory.

## Not touched

v8 PNG and v8 manifest, run-v3 builder, tracker, readiness ledger/checklist, runtime scenes and scripts, and Git (no stage or commit). No Godot import was run, so no `.import`/`.uid` files were created for the new files. No combined images or contact sheets were made.

## Open items

- GUI-saved `.pxo` round-trip (pipeline doc §8) is still untested. This file was written by Python. Opening it in the GUI and saving a copy is the next step, and needs a person at the GUI.
- Role-layer split: needs art sign-off (see above).
