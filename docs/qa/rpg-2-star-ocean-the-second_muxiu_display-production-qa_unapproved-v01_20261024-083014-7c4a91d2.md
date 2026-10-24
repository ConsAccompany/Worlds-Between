# Muxiu in-game display image — production QA (art unapproved)

Task: `content.char.muxiu.display`. Producer/sole development writer: DeepSeek through the authorized adapter; Hermes coordinates the audited transition. Tested base: `aff980c1eb77d547e24af5aa82523300e17e0d5c`. Run id: `20261024-083014-7c4a91d2`. Only the existing two-point criterion is eligible: the in-game display image is committed and shown in the UI. No runtime-integration, motion, default-adoption, visual-review, creator-approval or human-playtest credit is claimed. The canonical ledger/Bible/operating registry, Git index, commits, pushes and scores were not changed by the producer.

## Deliverable and source

The display image is derived from the already-completed, committed native south static; no concept sheet, repaint, generated pixels or new colour values are used. The source is the 80x112 RGBA static with pivot (40,104), body rows 8..103 and display scale 0.5. The display asset is an exact integer 2x nearest-neighbour pixel replication (160x224): every output 2x2 block repeats one source texel. Transparency is preserved.

| Item | Raw SHA-256 (no normalization) |
| --- | --- |
| Native south static source `game/assets/characters/muxiu-native-v01/south/rpg-2-star-ocean-the-second_muxiu_south-static_unapproved-v01_20261024-071500-ca23fad5.png` | `e14d5c50890d7fcd0c75eb362d2b08fd1d4ac02c9c33e04fc4861b5a7d7a26fe` |
| Source raw RGBA (80x112) | `02cbb1d00a22eb4268bc40eddbfb5179b106f703645150c8f096bd06f50b5faa` |
| Source manifest `…_muxiu_south-manifest_unapproved-v01_20261024-071500-dd478113.json` | `24c751575fe02a4857628dbfb8b379cd1d42344167062ae8ddbb033024e114de` |
| Display PNG `game/assets/portraits/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-portrait_v01_20261024-083014-7c4a91d2.png` | `b1c35d8367941d0cf90d6484b990dd7a92e53c8a05cf80c703dfa1aab84c0a08` |
| Display raw RGBA (160x224) | `c5de9401f9f10901061082e342bd1130dddd22e0c8f453f66aae0fcd165663b0` |
| Display manifest `game/assets/portraits/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-portrait-manifest_v01_20261024-083014-7c4a91d2.json` | recorded in the JSON receipt |

The manifest declares `transform.method = nearest-neighbor-integer-upscale`, `factor = 2`, `resampled = true`, `pixel_replication_only = true`, `repainted = false`, `ai_generated_new_pixels = false`, `new_colour_values = false`, `alpha_preserved = true`, and pins the source, source manifest, output file hash and output raw RGBA hash.

## UI selection

The proper existing display path is the standalone bilingual character display preview used by the credited Jiang Lan display40 and Lin Que display64 tasks. Muxiu is **not** in the ordinary MVP party (`AppState.MEMBER_DEFS` has hero/liang-xu/zhao-ling/ji-cheng), so adding it to the five-variant growth-screen/dialogue kit would change party/dialogue behaviour and is out of scope. Instead the new opt-in scene reuses the same card layout, pinned-manifest texture loading, nearest filtering, fallback label and probe pattern. It is not linked to ordinary gameplay, story, recruitment, save or defaults. It shows the display image at native 160x224 inside the 180x250 frame (no further scaling) and the same committed south static at the native 0.5 display scale on the stage, using the exploration pilot's documented sprite offset/scale math. There is no idle/walk or motion claim.

Scene: `game/scenes/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-preview_standalone-v01_20261024-083014-7c4a91d2.tscn`
Script: `game/scripts/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-preview_standalone-v01_20261024-083014-7c4a91d2.gd`

## Checks and exact results

All Python runs use `../tooling/venv/bin/python -X utf8 -I` (the actual virtual-environment path, not a symlink to system Python). All Godot runs use the checked runner `tools/rpg-2-star-ocean-the-second_godot_checked-runner_v01_20261018-203400-f74ac6d1.py` with finite timeouts and `--audio-driver Dummy`; windowed runs use `xvfb-run -a -s "-screen 0 640x360x24"` with `XDG_*` and `TMPDIR` under `outputs/mdisplay91/hermes91/` (fresh writable profiles) and `--rendering-driver opengl3 --resolution 640x360 --path game`.

1. Build and deterministic re-derivation:
   `… _muxiu_display-build_v01_20261024-083014-7c4a91d2.py build` → exit 0, `MDISPLAY91_BUILD OK c5de9401…` (writes PNG + manifest once; `write_safe` refuses differing bytes).
   Final `… build … check` → exit 0, `MDISPLAY91_BUILD OK c5de9401…`; every display byte and pixel matches the re-derivation.
2. Independent contract checker:
   `… _muxiu_display-contract-check_v01_20261024-083014-7c4a91d2.py --root . --manifest game/assets/portraits/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-portrait-manifest_v01_20261024-083014-7c4a91d2.json --out outputs/mdisplay91/hermes91-final/contract` → exit 0, `PASS`, **36/36 checks**, zero failures. The three built-in negative fixtures (wrong output hash, wrong actor, wrong factor) are refused. Source and output bytes are unchanged before/after. Report: `outputs/mdisplay91/hermes91-final/contract/rpg-2-star-ocean-the-second_muxiu_display-contract-report_v01_20261024-083014-7c4a91d2.json`.
3. Malformed-input gate:
   `… _muxiu_display-malformed-check_v01_20261024-083014-7c4a91d2.py --out outputs/mdisplay91/hermes91-final/malformed` → exit 0, **11/11 cases**, `MDISPLAY91_MALFORMED_OK`. It covers the real manifest, wrong factor, other actor, wrong source hash, truncated JSON, the foreign Lin Que manifest, an absent manifest (`PENDING`), one-pixel tampered display, and unchanged real display bytes. Report: `outputs/mdisplay91/hermes91-final/malformed/rpg-2-star-ocean-the-second_muxiu_display-malformed-report_v01_20261024-083014-7c4a91d2.json`.
4. Checked Godot import: first attempt with the host `XDG` profile was stopped by the checked runner on `ERROR: Cannot save file '…/.config/godot/editor_settings-4.7.tres'` (exit 1; retained `outputs/mdisplay91/hermes91/import.runner.log`). Retry with fresh writable `XDG_CONFIG_HOME/XDG_DATA_HOME/XDG_CACHE_HOME` → `CHECKED_RUN PASS`, exit 0 (`outputs/mdisplay91/hermes91/import2.runner.log`).
5. EN rendered probe: `--lang=en --out=…/cap-en` → exit 0, `MDISPLAY91_CHECKS 55 FAILS 0`, `CAPTURES true`, `MDISPLAY91_PROBE_OK`. Actual 640x360 captures: `…_standalone-en-south-static_…png`, `…_fallback-missing-portrait-en_…png`.
6. ZH rendered probe: `--lang=zh --out=…/cap-zh` → exit 0, `MDISPLAY91_CHECKS 55 FAILS 0`, `CAPTURES true`, `MDISPLAY91_PROBE_OK`. Actual 640x360 captures: `…_standalone-zh-south-static_…png`, `…_fallback-missing-portrait-zh_…png`.
   The probes check the manifest pins, portrait texture size/rect/filter/aspect, label localisation, portrait-clear-of-text geometry, display/actor raw pixels, exact 2x relation, visible UI-texture equality, actor stage bounds and real rendered pixels, transparent empty stage control, and the localized missing-portrait fallback with the static source still bound.
7. Bounded normal-entry smoke: `--timeout 60 --expect M1_SMOKE_OK --log outputs/mdisplay91/hermes91/m1-smoke.runner.log -- … --headless --audio-driver Dummy --path game --script res://tests/m1_smoke.gd` → exit 0, `M1_SMOKE_OK`, no diagnostics.

The checked runner's only windowed diagnostic was the environment's `WARNING: Could not set V-Sync mode…`; it is not a `SCRIPT ERROR`/`ERROR:` marker and the runner reported PASS.

## Visual observation — not creator approval

Hermes viewed the actual EN and ZH standalone captures and the committed display PNG through native image input. The portrait shows Muxiu's head, moss-green cape, screen-left braid, cream whistle and wrist bracelet; the identity block reads clearly and does not overlap the portrait or stage; `Art pending` / `美术待定` is explicit; the stage shows the same native south static at 0.5. This is display verification only, not artistic acceptance, motion quality or canon approval.

## Failed attempts retained

- `xvfb-run` initially failed before starting Godot: `mktemp: failed to create directory via template '/home/kel/.hermes/cache/scratch/xvfb-run.XXXXXX': Permission denied` (host `TMPDIR`). Retried with a writable local `TMPDIR`.
- Godot import attempt 1: checked-runner diagnostic on the editor-settings save error described above (`outputs/mdisplay91/hermes91/import.runner.log`), exit 1.
- EN probe attempt 1: `MDISPLAY91_CHECKS 53 FAILS 2` on `portrait pixels == display raw hash` and `display pixels are exact 2x…`. Cause: Godot's importer sanitizes RGB values under fully transparent texels (`fix_alpha_border`) while alpha/visible pixels are unchanged. The probe was corrected to validate the committed file bytes from disk and alpha-aware visible equality; the failed log and capture remain in `outputs/mdisplay91/hermes91/probe-en-failed1.runner.log` and `outputs/mdisplay91/hermes91/cap-en-failed1/`. No threshold was lowered and no asset was altered.
- Malformed check attempt 1: one failure `linque-manifest.refused` with a `KeyError: 'transform'` from a fixture mutator applied to the foreign manifest. The checker now guards missing blocks; the failed report is retained in `outputs/mdisplay91/hermes91/malformed-failed1/`. The passing rerun has 11/11 cases.
- The first contract report under `outputs/mdisplay91/hermes91/contract/` predates the checker's missing-block guard (logic unchanged for valid input); the final report is the `hermes91-final` one above.

## Limits

- The displayed texture is loaded through Godot's importer; transparent RGB values are sanitised by the engine. The committed PNG raw bytes are independently exact, and all visible (alpha>0) UI pixels match the committed image exactly. The `.import` sidecar is engine-generated and not committed.
- Static south only: no idle/walk/stop, no motion, no continuous gameplay, no runtime/default/party/exploration/battle integration, no save/recruitment/story changes.
- One 640x360 opt-in scene is not a full character-select or campaign UI. It is not linked to ordinary gameplay.
- Existing source is UNAPPROVED; human artistic acceptance, full-sprite/motion review and both human playtests remain open. The display task's source is the already-completed `content.char.muxiu.static-south`; this task does not re-credit it.
- Producer commit is pending coordinator integration. "Produced" and "shown in UI" are evidenced here; "committed" is not claimed by the producer.

## Progress and next action

Starting canonical values supplied for this batch: production **62.0%**, inspection **21.6%**, creator approval **7.8%**. This producer made no ledger/scoring change; final before/after values and the audited task transition are coordinator-owned. Only the existing `content.char.muxiu.display` two-point task is eligible. Next: coordinator verifies/stages the committed bytes and records the audited transition; do not infer default adoption, motion credit or art approval.

## Reproduction

From the repository root:

```sh
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_muxiu_display-build_v01_20261024-083014-7c4a91d2.py check
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_muxiu_display-contract-check_v01_20261024-083014-7c4a91d2.py --root . --manifest game/assets/portraits/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-portrait-manifest_v01_20261024-083014-7c4a91d2.json --out <new scoped output>
../tooling/venv/bin/python -X utf8 -I tools/rpg-2-star-ocean-the-second_muxiu_display-malformed-check_v01_20261024-083014-7c4a91d2.py --out <new scoped output>
```

Then the checked-runner probe from the note above with `--lang=en|zh`, `--audio-driver Dummy`, `--rendering-driver opengl3 --resolution 640x360 --path game`, requiring `MDISPLAY91_PROBE_OK` and `CAPTURES true` with no diagnostics. Full command arrays and hashes are in `outputs/mdisplay91/rpg-2-star-ocean-the-second_muxiu_display-production-receipt_unapproved-v01_20261024-083014-7c4a91d2.json`.
