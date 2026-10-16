# Selective Git transfer: Washington Capitol west v08 + NYC City Hall Park v03 (UNAPPROVED / NONRUNTIME)

- Date: 2026-10-16 16:56 (local). Run id of this note: `88f04014`.
- Purpose: cross-computer continuity only. Nothing here is accepted art. Nothing is wired into the runtime.
- Science scene visuals stay **0/11**. The MVP meter and all completion counters are unchanged. No runtime default, site source, battle code or progress state is touched by this transfer.
- The creator has **not** accepted either candidate.

## Visual status (Codex review of real Godot 640x360 captures)

- Washington Capitol west v08 (`wdc-cw-v08_20261016-155827-6cf49486`): technically verified 67/67, but still a moderate ruin read. The survey cues merge with the patrol walker.
- NYC City Hall Park v03 (`nyc-chp-v03_20261016-160059-4b2f50f6`): technically verified 43/43 and richer than v02. The central walkway is still flat, the flowers look like stickers, and the fountain occlusion is busy.

## Dependency audit

| Candidate | Tool (sha256-text-lf-v1) | Reads / hash-locks | Tracked before this commit? |
|---|---|---|---|
| WDC v08 | `f34c7638…` | v06 run, tool, notes, audits (tracked); **v07 run** (both run dirs + tool + QA note, mandatory LOCK); v05t (optional-if-absent); heroine v8 sprite (tracked) | v07: **no** |
| WDC v07 (parent) | `ddaf8213…` (= v08's pinned `V07_TOOL_SHA_TEXT`) | v06 (tracked); v05t (optional-if-absent) | — |
| NYC v03 | `d8c40162…` | heroine v8 sprite, v02 tool name, v02 Codex audit, v03 visual-direction reference (all tracked; only named, not hash-locked) | yes |

- v08 `check` hashes the whole v07 candidate dir and the whole v07 outputs dir. So the minimal parent set is all 21 v07 files: 7 candidate, 12 outputs, the tool and the QA note.
- Before staging, v07 was verified on its own: `check` gave PASS 60/60, with v05t present locally.
- v05t is not transferred. It is optional-if-absent in both v07 and v08, so on a clean clone `lock_optional_absent` lists its 4 entries.

## Clean-clone verification

- Method: `git clone` of local `d69871e` into `C:\wb\…` with `core.longpaths=true`. The 60 run files were committed in the clone, deleted, and checked out again, so line endings come from Git. The gitignored Godot 4.7.2 exe was copied into `work/tooling/`. Pixelorama 1.2.3 is at its installed path.

| check | autocrlf=false | autocrlf=true |
|---|---|---|
| WDC v07 | PASS 60/60 | PASS 60/60 |
| WDC v08 | PASS 67/67 | PASS 67/67 |
| NYC v03 | PASS 43/43 | **FAIL**: `…scene-palette_unapproved-v03_….gpl on disk differs from a fresh rebuild` |

- The NYC v03 failure is a line-ending defect only. The v03 `check` byte-compares the `.gpl` text palette against its LF rebuild, and an autocrlf=true checkout writes CRLF. (The Washington v06 builder had the same defect, fixed in 2567a2c.)
- The v03 tool and run files are hash-pinned, so they were not edited in this transfer.
- **Status: NYC v03 is clean-clone-buildable only with `core.autocrlf=false`.** On an autocrlf=true clone it is review-only until a later v04 tool compares text files with sha256-text-lf-v1.
- Workaround on the other computer:
  1. `git config core.autocrlf false`
  2. Delete the one `.gpl` file.
  3. `git checkout -- <that path>`
- In the working tree all three checks pass (v07 60/60, v08 67/67, v03 43/43).

## Transferred files (61 including this note)

- WDC v08: 7 candidate files (.pxo, .ora, flat 640x360 PNG, manifest, palette, walkability, walkmask) and 13 outputs (4×1280x720 + 4×640x360 Godot captures, technical-check report, 4 zoom crops). Plus the tool and the QA note: 22 files.
- WDC v07 parent: 7 candidate files and 12 outputs, plus the tool and the QA note: 21 files.
- NYC v03: 8 candidate files (adds the contact-shadow sprite) and 7 outputs (3×1280x720 + 3×640x360 Godot captures, technical-check report), plus the tool and the QA note: 17 files.
- Manifest flags were read in all three manifests: `art_approved: false`, `runtime_integrated: false`, `counters_changed: false`. WDC v07 and v08 also have `nonruntime: true`.

## Not transferred

- v05t, other untracked candidates, `tmp/` prompt and response files, site source, battle code, old art, game visuals and progress state.
