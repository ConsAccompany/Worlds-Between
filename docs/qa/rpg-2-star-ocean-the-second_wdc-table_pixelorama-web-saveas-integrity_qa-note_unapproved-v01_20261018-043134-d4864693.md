# WDC analysis light table — Pixelorama web Save As integrity (QA, UNAPPROVED)

Date: 2026-10-18 04:31 local.

**Scope:** WDC annex room 2 analysis light table only, and the **web GUI only** (official Pixelorama web 1.2.3 via itch embed). This does **not** prove a desktop GUI save. Art stays UNAPPROVED. Scenes stay 3/12. No Git, index, shared ledger or Bible writes.

## Verdict: PASS 10/10. The Save As is lossless.

The web-saved `.pxo` holds the same 96×40 image as the original. All five raw layer blocks are byte-equal, and layer names, order and flags are unchanged. The official native CLI exports it to the same split layers and the same flat PNG. That flat image equals the runtime PNG.

## Files

| Role | Path | SHA-256 |
|---|---|---|
| Original | `outputs/wdc-rc2-v01_151fb8d0/…_analysis-light-table-pixel-fixture_unapproved-v01_20261018-001157-151fb8d0.pxo` | `b4f2f865…0d6b009` |
| GUI import copy (byte-identical) | `work/native-save-0340/…_wdc-table_native-v01_20261018-042600-2961d7ad.pxo` | `b4f2f865…0d6b009` |
| Web Save As output | `work/native-save-0340/…_wdc-table_web-saveas-v01_20261018-043000-29f180ab.pxo` | `3f14e0b2…721580ff` |
| **Packaged saved copy** | `outputs/wdc-table-web-saveas_d4864693/rpg-2-star-ocean-the-second_wdc-annex-room2_analysis-light-table_pixelorama-web-v1.2.3-saveas-copy_unapproved-v01_20261018-043134-d4864693.pxo` | `3f14e0b2…721580ff` (byte copy) |
| Runtime PNG | `game/assets/props/wdc-annex-room2/…151fb8d0.png` (= outputs `.png`) | `5ab45266…56907d9` |
| Root reopen evidence | `outputs/rpg-2-star-ocean-the-second_wdc-table_pixelorama-web-saveas-reopened-identity-v01_20261018-043200-51cb3e69.png` | `614803cf…7c06a469` |
| Checker (reusable) | `tools/rpg-2-star-ocean-the-second_pixelorama-web-saveas-pxo-integrity-check_v01_20261018-043134-d4864693.py` | `f8aab523…0e2c13f8` |
| Report | `outputs/wdc-table-web-saveas_d4864693/rpg-2-star-ocean-the-second_wdc-table_web-saveas-integrity-report_unapproved-v01_20261018-043134-d4864693.json` | `b5df2ec4…7520fa89` |

## Checks (report `checks`)

1. **zip_ok, mimetype, same_member_names:** both files are valid `application/x-pixelorama` ZIPs with the same 14 members.
2. **data_json_only_allowed_diffs:** the only differences are `export_profile.directory_path` (`""` → `"user://"`, the web virtual filesystem) and `export_profile.file_name` (→ the name of the opened import copy). The project `name` key moved position but keeps the same value. `preview.png` was regenerated (1273 → 2012 B) and is not used as evidence.
3. **size_frames_layers:** 96×40, 1 frame, 5 layers.
4. **layer_metadata_order:** layers bottom→top are `contact-shadow`, `structure`, `form-and-light`, `specimen-and-cables` and `teal-light`. In both files every layer is visible and unlocked, with opacity 1, blend 0, parent −1, no effects and no clipping.
5. **raw_layers_equal:** 5/5 raw blocks are byte-equal (15360 B each), and so are the indices. `contact-shadow` has semi-transparent alpha by design. The other four layers have binary alpha.
6. **cli_original and cli_saved:** official Pixelorama 1.2.3 (exe `6412014e…4b92f10`) ran headless with `--export`, once with `--split-layers` and once flat. Each run used its own temp `APPDATA`. Results:
   - All runs exited 0.
   - The split export gave 5 PNGs, each equal to its raw layer.
   - The flat export equals the 5-layer alpha composite (RGBA sha `2e78cbd2…0e80d8`).
7. **runtime_eq_composite:** the game runtime PNG and the outputs PNG both equal the composite pixel-for-pixel.

The real `%APPDATA%\pixelorama` folder was snapshotted before and after the checker's CLI runs. One backup file changed; nothing else did. See **Correction (2026-10-18)** below. The open web GUI was not touched.

**Checker self-test:** flipping one channel bit in `structure` gives 8/10 (`raw_layers_equal` and `cli_saved` fail). The checker also reproduces the earlier Yonkers v04 web Save As result at 10/10.

## GUI evidence (root, web only)

The root screenshot shows a `[96×40]` canvas with the table, the layers teal-light → contact-shadow in the timeline, and a File menu entry that reads `Save rpg-2-star-ocean-the-second_wdc-table_web-saveas-v01_20261018-043000-29f180ab.pxo`. That identifies the reopened project as the saved output. This QA confirms the file data; root confirmed the visible reopen.

## Reuse

```
python -I tools/…pixelorama-web-saveas-pxo-integrity-check_v01_20261018-043134-d4864693.py \
  --original <orig.pxo> --saved <saved.pxo> \
  --pixelorama work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe \
  --report <out.json> [--runtime-png <png> ...]
```

The checker exits 0 only if every check passes. It is read-only on its inputs. CLI runs go in temp folders with their own `APPDATA`.

## Correction (2026-10-18): real-APPDATA change

An earlier version of this note and the earlier hand-off both said nothing changed in the real `%APPDATA%\pixelorama`. **That was wrong.** The durable report was left exactly as written (`b5df2ec4…7520fa89`, written 04:33:55). It records:

```
"real_appdata_pixelorama_changed": [
  "backups\2026_10_16_23_14_03\(untitled backup)-1792218380.455-0"
]
```

The "nothing changed" statement came from a different checker run. Its console output listed `[]`. The final run, which wrote the report, had its console output discarded, so I never saw the change.

**What was observed:**
- The only changed path is one untitled backup file. No other file in the snapshot changed, which includes `config.ini`.
- The snapshot skips only `.running`. `config.ini` was last modified at 2026-10-16 23:14:03, before this work started.
- The backup changed again **after** the checker had finished: its last modified time is 04:35:41, later than the report's 04:33:55.
- A desktop Pixelorama v1.2.3 window titled "untitled" is running (PID 37584). It started at 2026-10-16 23:13:56, which matches the backup folder `2026_10_16_23_14_03`.

**Likely cause, not proven:** that open desktop window's periodic untitled autosave. The checker's CLI runs each used their own temp `APPDATA`. I did not trace which process wrote each file, so I can't fully rule out an effect from the CLI runs.

**What this note does and does not claim:**
- `config.ini` and every other snapshotted file were byte-unchanged.
- The note does **not** claim the user's Pixelorama data folder was fully unchanged: one backup file did change during the window.
- The 10/10 layer, metadata, CLI and runtime-pixel results are unaffected.
- Scope is unchanged: the web GUI reopen was verified by root (96×40 canvas, saved file name in the File menu); the desktop GUI was not. Art stays UNAPPROVED and scenes stay 3/12.
