# Pixelorama .pxo Save As round-trip integrity checker v01 — QA

Date: 2026-10-18 (EDT). Worktree: `work/max0840-wdc-ruin` only. The four package files are selected for one local supporting commit after Codex review; no game, ledger or Site edit.
Scope: a **file-integrity** check only. It makes no GUI-behaviour, clean-app, rendering or art-approval claim. The art stays UNAPPROVED.

## Files (this folder)
- `…_pxo-saveas-integrity-checker_v01_…py`: the checker. Stdlib only.
- `…_pxo-saveas-integrity-negative-tests_v01_…py`: the synthetic test runner.
- `…_female-west-run_pxo-saveas-integrity-report_v01_…json`: the actual report (PASS).
- This note.

## CLI
`python -I checker.py --source <abs .pxo> --saved <abs .pxo> [--report <abs new .json>]`
- stdout is one LF JSON object. With `--report`, the same bytes are written to the report path; an existing report file is never overwritten.
- Exit codes: 0 = PASS, 1 = FAIL (mismatch), 2 = ERROR (malformed or unsupported input, bad arguments, unreadable file).
- Inputs are read in place through the `\\?\` extended-length prefix and parsed from memory. Nothing is extracted or copied.
- Output contains only SHA-256 digests, counts, numeric size/fps/duration facts, fixed error codes and difference key locations. It never contains paths, exception text, names, author fields, `user_data` or export-profile values. The keys of free-form dicts such as `metadata` are reported only at the container location.

## Contract
- **Frame/layer shape:** derived generically from `data.json`. No constants.
- **Byte-exact comparisons:** every `image_data/frames/<f>/layer_<l>` cel, every `indices_layer_<l>` payload, `mimetype`, and the full ZIP path set including directory entries.
- **Type-strict `data.json` comparison:** all fields, for example `12` ≠ `12.0`.
- **Allowed differences:**
  - `current_frame` and `current_layer`
  - `export_profile.directory_path` and `export_profile.file_name`
  - a tag colour that goes from RGB6 to the same hex plus `ff`
- **Refused tag colours:**
  - Other alpha values, changed RGB, and anything other than a 6- or 8-digit hex string are refused.
  - Missing or extra `export_profile` keys → FAIL.
- **Non-SaveAs `export_profile` fields:** still compared exactly, but a value difference is reported only at the fixed location `export_profile (non-SaveAs field value)`. Export-profile keys are never echoed, because they are input-controlled strings.
- **preview.png:** structurally validated as a PNG (signature, CRCs, IHDR, a complete IDAT zlib stream, decompressed size, legal scanline filters 0..4, IEND). The inflater must reach end-of-stream, which verifies the Adler-32 trailer, and must leave no unused, unconsumed or trailing compressed data. Decompression stays capped at 64 MiB. Its content is **excluded** from the proof.
- **Fail closed (ERROR):**
  - ZIP integrity: duplicate or unsafe ZIP paths, encrypted or corrupt entries, and size bombs (64 MiB per entry, 512 MiB total).
  - JSON: duplicate keys, NaN/Infinity, and unknown top-level, layer, frame, cel or tag keys.
  - Missing or wrongly sized cels, and ZIP entries outside the derived grammar.
  - Unsupported content: any `pxo_version` other than 7, any `color_mode` other than RGBA8 (5), non-pixel layer types, layer parents (groups), and non-empty tilesets or reference images.
  - Invalid metadata: durations, fps, opacity, booleans, tag ranges or selection.

## Actual run (source → saved, the two given absolute inputs)
Result: **PASS** (exit 0).

| | Source | Saved |
|---|---|---|
| SHA-256 | `3a162042…8c18` | `b4bff32e…6a1a` |
| ZIP entries | 3459 | 3459 |
| Directories | 128 | 128 |
| Payloads | 3331 | 3331 |

- **Shape:** 128 frames × 13 layers, 80×112 pixels, fps 70.0, all 128 durations 0.25. 1 hidden layer, 1 locked layer, 1 tag.
- **Cels:** raw 1664/1664 byte-equal; indices 1664/1664 byte-equal; `mimetype` equal; ZIP path sets equal.
- **data.json:** 0 semantic differences. Allowed differences observed: `export_profile.directory_path` and `export_profile.file_name`. One normalisation: `tags[0].color` RGB6 → RGBA8 `ff`. `current_frame`/`current_layer` happened to be equal.
- **preview.png:** the bytes differ (80×112 vs 182×256). It is a valid PNG in both files and is excluded from the proof.
- **Leak scan of the report:** none of the input string values appear in it, and neither do the input paths. One 6-letter layer name is a common English word that also occurs in the checker's fixed `proof_scope` text; that is not a value echo.
- The existing root `*_web-gui-saveas-integrity_v01_…df07c82b.json` was not read or written by this tool.
- The run supports only the file-level SaveAs/reopen data integrity. The Splash/Restore exclusive-window app error seen in the GUI session is not addressed, so this is **no clean-app claim**.

## Correction follow-up (2026-10-18, same files, same v01 names)
Codex independently reproduced two defects in the first version of this checker. Both are now fixed:
1. **Private key echo.** When `export_profile` held the same key `C:/SENTINEL_PRIVATE_PATH_7f3c/profile` in both files with values `a` and `b`, `_compare` emitted `export_profile.<key>`. That leaked the private path. It now emits only the fixed `export_profile (non-SaveAs field value)` location. The comparison is still exact (type-strict) and still FAILs.
2. **Truncated zlib accepted.** `_check_png` accepted a CRC-correct 4×3 RGBA8 PNG whose IDAT was `zlib.compress(3 rows × (1 filter + 16 bytes))[:-2]`. It returned PASS because the decompressed length was correct even though the Adler-32 trailer was missing. It now requires `eof`, empty `unused_data` and empty `unconsumed_tail`, so the result is ERROR `preview_png_invalid`.

Regressions added: `export_profile_private_key_value_no_echo_fail` (the leak scan includes the sentinel), `preview_png_truncated_zlib_error`, and `preview_png_trailing_zlib_data_error` (2 bytes appended after the stream). `export_profile_other_value_fail` now also pins its location.
- With the fix: 53/53 cases as expected.
- With both fixes reverted in a throwaway `%LOCALAPPDATA%\Temp` copy (since deleted), exactly 4 cases fail: the private-key case (leak plus location), the pinned other-value location, truncated zlib (exit 0, not 2) and trailing data (exit 0, not 2).
- **Actual pair:** rerun in place on the same two absolute inputs (source `…female-west-run_animated-source_unapproved-v01_…0817f0b2.pxo`, saved `…web-gui-saveas-reopen_v01_…df07c82b.pxo`), with stdout only and no `--report`. The result is PASS, exit 0, with empty stderr. stdout is **byte-identical** to the existing actual report, so the report is unchanged (both real previews pass the stricter zlib check). The existing root `…df07c82b.json` report was neither written nor copied.

## Synthetic tests: 54/54 as expected (exit 0)
Tiny generated projects (4×3 pixels, 3×2 frames/layers by default) are built under `%LOCALAPPDATA%\Temp\pxo-saveas-neg-<id>` and removed afterwards (`temp_root_removed: true`). Sentinel strings sit in the directory path, file names, author/license fields, layer and tag names, `user_data`, export-profile values and injected key names. No sentinel, temp root or traceback appeared in any stdout, stderr or report.

- **PASS (8 cases):**
  - baseline
  - selection plus SaveAs fields
  - opaque tag colour `1A9999FF`
  - key reorder, ZIP reorder and STORED compression
  - changed thumbnail
  - a generic 5×4 shape
  - a long Windows path (386 characters, no prefix on the CLI)
  - report file identical to stdout
- **FAIL (21 cases):**
  - a flipped raw cel byte, an index payload change, and frame or layer counts that differ between the files
  - timing: frame duration, fps, and fps int vs float
  - layer properties: hidden, lock, layer name, cel opacity
  - author and `user_data`: an author field, `user_data`
  - unexpected metadata: frame or project metadata
  - tag changes: tag alpha `80`, tag RGB, tag range
  - export profile: an unexpected export-profile key, another export-profile value, and a same private-path key with differing values (not echoed)
- **ERROR (25 cases):**
  - container: missing cel, malformed JSON, duplicate JSON key, duplicate ZIP path, not a ZIP, unexpected ZIP entry, wrong cel size, wrong mimetype
  - unsupported content: unsupported layer type, tag colour as an int, tag colour as `#hex`, colour mode, unknown top-level key
  - invalid data: negative duration, cel-count mismatch, invalid layer boolean, NaN, broken PNG, a CRC-correct PNG with truncated zlib, a CRC-correct PNG with trailing zlib data, a CRC-correct PNG with illegal filter byte 5
  - CLI: relative path, missing file, unknown argument, report already exists

## Limitations
- Only RGBA8 pixel layers are supported, with pxo v7 and the key sets observed in Pixelorama v1.2.3. Groups, tilemaps, 3D/audio layers, embedded reference images and other versions are refused (ERROR), not validated.
- Thumbnail pixels and ZIP container bytes are intentionally not compared.
- Inner keys of free-form `metadata`/`effects` dicts are reported by container location only.
- Inputs are capped at 256 MiB per file.
- The check proves data equality of two files. It does not exercise the Pixelorama GUI, and it does not prove the app reopened cleanly or that the art is approved.

## Final Codex review

Codex independently reproduced the original private export-key leak and truncated-zlib false PASS before the follow-up, then reviewed the correction. Root requested the additional bounded scanline rule: each PNG row filter must be in 0..4. A CRC-correct, complete-zlib thumbnail containing filter byte 5 was first observed to PASS, then changed to ERROR `preview_png_invalid` by the new guard and regression. The final 54-case suite (8 PASS, 21 FAIL, 25 ERROR) is the completed check set; the earlier 50/50 and 53/53 are intermediate results, not final completeness claims. No semantic/raw-cell allowances changed. This remains structural thumbnail checking, not a full image decoder, GUI exercise or art review.

Final independent Codex execution: all 54 cases passed, 386-character Windows path passed, temporary fixtures removed. The actual absolute-input invocation exited 0 with empty stderr, and stdout is byte-identical to the package actual report. Original native GUI inputs and root GUI report were not modified. Existing 378 tracked import changes remain outside the selected package.
