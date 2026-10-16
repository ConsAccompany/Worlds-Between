# NYC City Hall Park v03: clean-clone autocrlf portability repair (UNAPPROVED / NONRUNTIME)

- Date: 2026-10-16 17:00 (local). Run id of this note: `f120e4bf`.
- Scope: repository line-ending configuration only. This fixes the open defect recorded in the selective transfer note `…selective-git-transfer_qa-note-unapproved-v01_20261016-165616-88f04014.md` (commit f1489aa). That note stays as written, because it is an accurate record of the state at f1489aa.
- Art status is unchanged. NYC v03, WDC v07 and WDC v08 stay **UNAPPROVED / NONRUNTIME**. Manifest flags stay `art_approved: false`, `runtime_integrated: false`, `counters_changed: false`.
- MVP meter stays **35.8%**. Science scene visuals stay **0/11**. There is no runtime integration, and no progress state, site source or battle code is touched.

## Defect

- The v03 `check` byte-compares 6 candidate files with a fresh in-memory rebuild: `.pxo`, `.ora`, flat PNG, `.gpl`, walkmask and contact shadow (tool lines 3284–3286).
- The `.gpl` palette is the only text file in that set. Its rebuild is LF.
- The repo had no `.gitattributes`. With `core.autocrlf=true`, Git checks the palette out as CRLF, so `check` stops with `…scene-palette_unapproved-v03_….gpl on disk differs from a fresh rebuild`.
- The manifest and walkability JSON files are text too, but `check` never byte-compares them, so they do not cause the failure.

## Remedy (smallest clean-repo fix)

- Add a new root `.gitattributes` with one rule, scoped to the exact v03 palette path:

```
game/assets/environments/candidates/nyc-chp-v03_20261016-160059-4b2f50f6/rpg-2-star-ocean-the-second_nyc-city-hall-park_scene-palette_unapproved-v03_20261016-160059-4b2f50f6.gpl text eol=lf
```

- `eol=lf` overrides `core.autocrlf`, so this file is LF on checkout in every clone mode.
- The rule is scoped to one path, not `*.gpl`, so no other palette changes its checkout behaviour. The other tracked palettes were not retested here. They include NYC v01/v02, WDC dome-west v01/v02 and WDC v05/v06, and any of their tools that byte-compare `.gpl` may still have the same autocrlf=true defect. WDC v07/v08 pass either way (below).
- Nothing pinned is edited: not the v03 tool (`d8c40162…`, sha256-text-lf-v1), the manifest, the source images, the generated files, the captures or the report. The index blob of the palette is unchanged, because it was already LF (`i/lf`).
- `.gitattributes` blob: `293f3d3f5b211ab5e0a40097852df114bdaff212`.

## Verification (git 2.54.0.windows.1)

### Method

1. A scratch clone (`C:\wb\gx`, `core.longpaths=true`, `autocrlf=false`) of local `f1489aa` got the `.gitattributes` above as trial commit `ba7215a`. Its blob equals the committed blob.
2. Fresh clones were made from that scratch clone: `gf` with `autocrlf=false` and `gt` with `autocrlf=true`.
3. An unfixed control clone, `gb`, was made from `f1489aa` with `autocrlf=true`.
4. The gitignored Godot 4.7.2 exes were copied into each clone's `work/tooling/godot-4-7-2/`. Pixelorama 1.2.3 was used from its installed path.
5. Every `check` ran in full, with the Pixelorama round-trip and the Godot gates (no `--no-*` flags).

### Palette line endings after checkout (`git ls-files --eol`)

| clone | autocrlf | .gitattributes | index | working tree |
|---|---|---|---|---|
| gb | true | absent | lf | **crlf** |
| gf | false | present | lf | lf |
| gt | true | present | lf | lf |

### Check results

| check | gb (unfixed, true) | gf (fixed, false) | gt (fixed, true) |
|---|---|---|---|
| NYC v03 | **FAIL**: `.gpl on disk differs from a fresh rebuild` (reproduced) | PASS 43/43 | PASS 43/43 |
| WDC v07 | — | PASS 60/60 | PASS 60/60 |
| WDC v08 | — | PASS 67/67 | PASS 67/67 |

- WDC v07 and v08 list the 4 v05t entries under `lock_optional_absent`, as expected in a clean clone. v05t is not tracked.
- After all checks, `git status --short` was empty in both `gf` and `gt`.
- In the main working tree, the v03 palette stays `i/lf w/lf` with the new attribute. Adding the rule does not show the file as modified.

## Result

- **NYC v03 is now clean-clone-buildable with both `core.autocrlf=false` and `core.autocrlf=true`.**
- The workaround in the transfer note (set `core.autocrlf=false`, then delete and check out the `.gpl` again) is no longer needed for clones at or after this commit.
- An existing autocrlf=true clone that already holds a CRLF copy must refresh it once after pulling: delete the `.gpl` file, then run `git checkout -- <path>`.

## Carry-forward for v04

- Any v04 builder should compare text outputs with sha256-text-lf-v1 or LF-normalised bytes, not raw bytes. Then it does not depend on this per-path rule.
- Alternatively, v04 can add its own palette path to `.gitattributes`.
