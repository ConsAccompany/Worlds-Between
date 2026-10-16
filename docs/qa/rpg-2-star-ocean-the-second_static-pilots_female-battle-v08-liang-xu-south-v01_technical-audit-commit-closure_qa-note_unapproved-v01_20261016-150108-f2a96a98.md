# Static pilots female battle v08 and Liang Xu south v01: independent technical audit and commit closure (QA note)

- **Date:** 2026-10-16. Stamp 20261016-150108 is UTC; local times below are EDT.
- **Scope:** an independent technical audit and evidence package only. No art pixels, author scripts, runtime assets, Game Bible or completion meter were changed. Nothing was staged or committed in this repository.
- **Status of both pilots:** UNAPPROVED / NONRUNTIME.
  - Accepted exploration sprites stay **0/52**, and the HEAD progress state still reads 探索精灵 0/52.
  - Each pilot is one static frame; there is no animation.
  - Liang Xu is described without gendered pronouns. This note does not settle that canon.
- **Repository state:** HEAD was `4245dd2` at the start. Other sessions committed `3f97c9a` and `ec178fd` during the audit; neither touched a file listed here.

## Inputs read

- `~/.codex/AGENTS.md`, the naming rules this note and the new tool follow.
- Female battle static v08:
  - QA note `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-game-scale-defect-pass_qa-note_unapproved-v01_20261016-095054-68ec4f17.md`
  - Codex visual audit `docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-codex-visual-audit_unapproved-v01_20261016-145125-5e1b7d6c.md`
- Liang Xu south idle static pilot v01:
  - QA note `docs/qa/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_48px-identity-qa-note_unapproved-v01_20261016-140940-d01e679f.md`
  - Codex visual audit `docs/qa/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-codex-visual-audit_unapproved-v01_20261016-145125-76c4ab13.md`

## New file (this audit's only addition besides this note)

`tools/rpg-2-star-ocean-the-second_static-pilots_female-battle-v08-liang-xu-south-v01-commit-closure-check_unapproved-v01_20261016-150108-0f79c1db.py`, sha256-text-lf-v1 `f43b796ecfc5384088c16c0479ae72150b7c13ed11ef7f9faae7bbe3722ec2c0`.

It is a read-only, deterministic check: it writes nothing and runs no Pixelorama, no Godot and neither author tool. No existing check answered "does this checkout hold every file a selective commit needs, with the exact bytes the notes were made from?" It checks 11 gates:

| Gate | What it verifies |
|---|---|
| `package_files_locked` | the 28 package files below exist and match their locks: sha256-bytes for PNG/.pxo/.ora, sha256-text-lf-v1 for text, so CRLF and LF checkouts both pass |
| `dependencies_locked`, `dependencies_in_HEAD` | the 9 already-tracked files the packages read or lock |
| `v08_manifest`, `v08_captures` | internal hashes; UNAPPROVED, `animation:false` and acceptance flags; capture geometry: crown 422, sole 543, 61 logical px, 5452/5452 nearest match, 0 off-palette, gap 10 to Liang with 0 overlap, no disc |
| `liang_manifest`, `liang_capture_report` | internal hashes; tool self-hash; `art_approved`/`human_reviewed` false; 0/52; all 4 capture hashes |
| `liang_reference_drift_known` | the manifest's reference hashes may differ from the checkout **only** for `game_bible_state` (see F1); any other drift fails |
| `editables_independent` | its own decoding of each .pxo/.ora: layer names and flags, hidden locked `guides`, and a src-over composite of the visible layers equal to the PNG; also binary alpha, cell size, and Liang palette declared == used |
| `doc_paths_resolve` | every full repo path or relative link in the four docs exists |
| `liang_no_gendered_pronoun` | no he/him/his/she/her pronoun in the Liang package text, except the QA note's deliberate pronoun-inconsistency quote |

It also reports, without gating:
- the Git tracked state of each file;
- whether Pixelorama and Godot are present;
- whether `game/scripts/battle_arena.gd` is the band-capable build.

Negative control: on a bare HEAD clone it **FAILS**, finding 28 package files missing.

## Verification results

### Female battle static v08 (run 326522f8)

- **Hashes:** all match the QA note and manifest.
  - PNG `edee2924…d0adc5`
  - .pxo `bf7111a2…04544cb`
  - .ora `818e4bd4…6048e34`
  - manifest `8ec39ef6…a903814b`
  - ruins capture `2865e4d5…60f1f55d`, outskirts capture `19c5677e…60c95e56`
  - The capture manifests' `captureSha256`/`candidateSha256` agree with these files.
- **Author `check`:** PASS 19/19 in the working tree and in both clean clones (autocrlf `true` and `false`). The four Pixelorama 1.2.3 round trips (pxo/ora × flat/split) passed, with 18/18 visible layers and guides not exported. The real APPDATA was untouched.
- **Independent decode:**
  - PNG: 68×72 RGBA, alpha {0, 255}, transparent border, 29 colours, 1363 opaque texels.
  - .pxo: version 7, 19 layers, `guides` last, hidden and locked.
  - .ora: `mimetype` first and stored; stack composite == PNG; each .ora layer == the matching .pxo layer.
  - 349 texels are covered by more than one layer. That is expected: v08 layers overlap and composite src-over.
- **Godot captures, working tree:** the committed `…party-capture-clean-clone_unapproved-v07r1_20261016-085133-1c89279f.gd` was run unchanged, with output to `%TEMP%`. It reproduced both captures **byte-identically** (`CAPTURE PASS arenaMode=arena-override-band`). The no-sprite frames are byte-identical to `%TEMP%\fv07\nosprite_{ruins,outskirts}.png`. The v07r1 blob is `f813dcfd…` in HEAD, `b12576a` and the working tree.
- **Region measures:** `…v07-vs-v08-region-measure_unapproved-v08_20261016-095054-c2a29cc3.py` over those no-sprite frames reproduces every mean |ΔL| and structure figure in the v08 QA note tables. Examples: far leg outskirts 33.9 / 52.8 % under 20; blade 19 texels in 1 component; hilt 4 rows clear of the belt; stance 31 wide; boots 5 apart. It finds 0 changed pixels outside the sprite.

### Liang Xu south idle static pilot v01 (run baa30d44)

- **Hashes:** all match the QA note, manifest and capture report.
  - PNG `9fee9018…fe38ab`
  - .pxo `26024bdd…ff09ee`
  - palette (text-lf) `6d0be31c…7e9c4f`
  - manifest (text-lf) `5cd6fea9…b0bcfa`
  - build tool (text-lf) `a91cea8a…56609b`, equal to the manifest's self-hash
  - capture tool (text-lf) `b553990b…af238f`
  - ×4 preview `60215962…935b4c35`
  - 4 captures: `d2c34078…`, `bc232b41…`, `b8e6dc18…`, `72cab5f1…`
  - capture report `42919c83…434787`
- **Author `check`:** PASS in the working tree and in the autocrlf `false` clone.
  - Rebuilt PNG, .pxo and palette are equal to the files.
  - Two flat exports had 0 differing texels and were byte-identical to each other.
  - The split export matched all 9 role layers, with guides not exported.
  - In the autocrlf `true` clone the first run FAILED only on `real_appdata_pixelorama_changed`; the rerun PASSED (see F5).
- **Independent decode:**
  - PNG: 80×112 RGBA, alpha {0, 255}, 2471 opaque texels, 33 colours = the 33 declared colours.
  - .pxo: 10 layers; 9 role layers disjoint (0 shared texels) whose union == PNG; `guides` hidden and locked.
  - `.gdignore` present and empty.
- **Godot captures, clean clone:** a clean clone of HEAD `3f97c9a` with only the package added was imported, then the capture tool was run unchanged. All **4 PNGs are byte-identical** to the recorded ones. The new report equals the recorded report except for the stamped file names: same 7 gates, same regions and contrast figures.

### Documents

- All cited full paths and relative links resolve: 8 in the v08 QA note, 5 in the v08 audit, 22 in the Liang QA note, 4 in the Liang audit. Paths abbreviated with `…` are not checked.
- The Liang package text has no gendered pronoun outside the QA note's quoted inconsistency bullet. The Codex audit's request to stay gender-neutral is respected here.

## Findings (most significant first; none changes pixels)

- **F1. The Liang `build` mode is no longer idempotent at HEAD.**
  - **Cause:** the manifest locks `outputs/rpg-2-star-ocean-the-second_game-bible_state_v01_20261013-195422-b8c16d42.json` at text-lf `02f8e2c3…6c182`, which is the `ee36736` blob. `4245dd2` (10:52 EDT, after the 10:17 build) changed it to `6713ab7e…517855`.
  - **Effect:** `build` writes `.gdignore`/PNG/.pxo/palette as "unchanged", then raises `refusing to overwrite a different existing file` on the manifest. This happens in the working tree and both clones.
  - **Proof:** regenerating the manifest in memory shows that this single hash line is the only difference.
  - `check` is unaffected because it does not re-verify references. The Liang QA note's line "`build` reports `unchanged` when the files match" is stale since `4245dd2`.
  - **Not fixed here,** because author scripts are out of scope. Options for the owner: accept the manifest as a provenance record of the build-time inputs, or freeze reference locks in a later tool revision.
- **F2. Both `build` modes refuse in an autocrlf `true` checkout.** `write_new` compares raw bytes, so the CRLF checkout of LF JSON differs: the v08 tool refuses on its manifest and the Liang tool on its palette. Both `check` modes pass there because they parse or hash text line-ending-independently. Run `build` only in an LF (autocrlf `false`) checkout, or fix this in a later tool revision.
- **F3. The v08 capture evidence is not byte-reproducible from a clean clone.**
  - The band captures need the working tree's **uncommitted** `game/scripts/battle_arena.gd`, from another workstream (text-lf `be8859a8…a592acae`; HEAD is `e9737c40…5f859f02`).
  - In a clean clone, v07r1 falls back to `head-geometric-backdrop`. It reports `CAPTURE PASS`, and ruins and outskirts come out identical (`a49d46fd…`) because there is no band.
  - Sprite pixels are bit-identical to band mode in both arenas: 5452/5452 predicted, RGB hash `1ad72202bc6d739a`, equal diff masks, and 0 pixels changed outside the sprite.
  - This blocks re-deriving the committed capture PNGs, not committing them.
- **F4. The measure tool needs no-sprite frames that are not in the repository.** They are written by v07r1's 6th argument, and the working-tree run regenerates them byte-identically. Keep them out of the commit; regenerate them as in the reproduce section.
- **F5. Two open Pixelorama GUIs make the real-APPDATA gates flaky.** PIDs 50828 and 31292 were running. At 11:05:31 EDT one autosaved `%APPDATA%\pixelorama\backups\2026_10_15_13_56_34\(untitled backup)-1792087054.891-0` and failed one Liang `check` run in the clean clone; the immediate rerun passed. This is not a pilot defect.
- **F6. Godot import creates `.png.import` sidecars for the v08 PNG.** `game/assets/characters/combat-sideview-pilots/` has no `.gdignore`, so an import in a clean clone writes sidecars for v05–v08 (and other untracked-import PNGs). v05–v07 were committed without `.import` files, and none exists for v08 in the working tree. Do **not** add one. The Liang folder is protected by its `.gdignore`.
- **F7. One untracked dependency of the Liang package.** The manifest locks `docs/design/rpg-2-star-ocean-the-second_character-sprites_pixel-art-production-pipeline_unapproved-v01_20261015-040155-ffd3391d.md`, an unapproved design doc dated 2026-10-15. It is untracked, so it must travel with the Liang package. Without it, Liang `build` raises `FileNotFoundError`; `check` would still pass.

## Exact selective-commit list (30 paths, all currently untracked)

Female battle static v08 (12):
```
tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v08_20261016-095054-326522f8.py
tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-static-v07-vs-v08-region-measure_unapproved-v08_20261016-095054-c2a29cc3.py
game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_unapproved-v08_20261016-095054-a06775a0.png
game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_editable-layers_unapproved-v08_20261016-095054-2574ce1c.pxo
game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_editable-layers_unapproved-v08_20261016-095054-314d939f.ora
game/assets/characters/combat-sideview-pilots/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_manifest_unapproved-v08_20261016-095054-ab653c87.json
outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins_unapproved-v08_20261016-095054-a7962fdf.png
outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-ruins-manifest_unapproved-v08_20261016-095054-1a83eade.json
outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts_unapproved-v08_20261016-095054-d9a8abaf.png
outputs/rpg-2-star-ocean-the-second_protagonist-female_sideview-idle-right-static-native0p65_party-capture-outskirts-manifest_unapproved-v08_20261016-095054-7dee7835.json
docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-game-scale-defect-pass_qa-note_unapproved-v01_20261016-095054-68ec4f17.md
docs/qa/rpg-2-star-ocean-the-second_protagonist-female_battle-static-v08-codex-visual-audit_unapproved-v01_20261016-145125-5e1b7d6c.md
```
Liang Xu south idle static pilot v01 (16, including the F7 dependency):
```
tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py
tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-godot-capture_unapproved-v01_20261016-140940-0e7a1c55.gd
game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/.gdignore
game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_unapproved-v01_20261016-140940-46a036ed.png
game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-editable_unapproved-v01_20261016-140940-65edcfd2.pxo
game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-palette_unapproved-v01_20261016-140940-cda9b0c6.json
game/assets/characters/liang-xu/south-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-manifest_unapproved-v01_20261016-140940-74be7552.json
outputs/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-x4-nearest-preview_unapproved-v01_20261016-140940-3018cfc8.png
outputs/rpg-2-star-ocean-the-second_city-bright_liang-xu-south-idle-static-pilot-h48_unapproved-v01_20261016-141751-bd083d0a.png
outputs/rpg-2-star-ocean-the-second_city-bright_liang-xu-pilot-with-female-v8-benchmark-h48_unapproved-v01_20261016-141751-bd083d0a.png
outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_liang-xu-south-idle-static-pilot-h48_unapproved-v01_20261016-141751-bd083d0a.png
outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_liang-xu-pilot-with-female-v8-benchmark-h48_unapproved-v01_20261016-141751-bd083d0a.png
outputs/rpg-2-star-ocean-the-second_city-bright-dark_liang-xu-south-idle-static-pilot-capture-report_unapproved-v01_20261016-141751-bd083d0a.json
docs/qa/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot_48px-identity-qa-note_unapproved-v01_20261016-140940-d01e679f.md
docs/qa/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-codex-visual-audit_unapproved-v01_20261016-145125-76c4ab13.md
docs/design/rpg-2-star-ocean-the-second_character-sprites_pixel-art-production-pipeline_unapproved-v01_20261015-040155-ffd3391d.md
```
This audit (2):
```
tools/rpg-2-star-ocean-the-second_static-pilots_female-battle-v08-liang-xu-south-v01-commit-closure-check_unapproved-v01_20261016-150108-0f79c1db.py
docs/qa/rpg-2-star-ocean-the-second_static-pilots_female-battle-v08-liang-xu-south-v01_technical-audit-commit-closure_qa-note_unapproved-v01_20261016-150108-f2a96a98.md
```

**Keep out of the commit:**
- any `.png.import` or `.uid` file;
- `%TEMP%` frames and logs;
- the v05-vs-v06 combined crop sheet;
- the other untracked v03–v05 capture files;
- every other workstream's modified file, in particular `game/scripts/battle_arena.gd` (F3).

**How to stage:** use an explicit pathspec (`git add -- <the 30 paths>`) or a temporary index. Never use `git add -A`; this working tree holds about 1,180 other status lines from other sessions.

**Already in HEAD and required (9, verified byte-exact):**
- the 4 v07 locks: `…v07_20261016-070549-6711a51d.png`, `-f6ab9173.pxo`, `-c3e59c16.ora`, `-04075564.json`;
- the v07 author tool `…author_unapproved-v07_20261016-070549-0e2efcac.py`, which the measure tool imports;
- the v07 ruins/outskirts captures `-fedb99df.png` and `-129e2621.png`, which the measure tool globs;
- the v07r1 capture script;
- the approved v8 south PNG `…selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png` (`ccf9d2a2…b6fd`).

The other 6 Liang manifest references are tracked. Only `game_bible_state` drifts (F1).

**External, gitignored (`work/tooling/`):**
- Pixelorama 1.2.3 is needed by both author `check`/`build` modes.
- Godot 4.7.2 is needed by the captures.
- The closure check needs neither.

## Clean-clone status

Method:
1. A throwaway clone of HEAD `3f97c9a` got only the 29 files above that existed then; this note was written afterwards.
2. They were committed inside that throwaway clone only.
3. It was re-cloned with `core.autocrlf=true` and with `false`, using `core.longpaths=true` under `%TEMP%`.
4. All clones were deleted afterwards with `\\?\`-prefixed `rmtree`; the deletion was confirmed.

| Check | autocrlf=true | autocrlf=false |
|---|---|---|
| closure check (11 gates) | PASS | PASS |
| v08 author `check` | PASS 19/19 | PASS 19/19 |
| Liang author `check` | PASS (1st run FAIL, F5) | PASS |
| v08 `build` idempotent | **no**: manifest, F2 | yes, 4× unchanged |
| Liang `build` idempotent | **no**: palette (F2), then manifest (F1) | **no**: manifest, F1 |
| Liang 4 Godot captures byte-identical | not run | **yes** |
| v08 band captures byte-identical | not run | **no** (F3); sprite pixels identical |

**Clean-clone blockers for a selective commit:** none for the files or the `check` gates. Only evidence regeneration is limited, by F1, F2 and F3.

## Unchanged and side effects

- No PNG, .pxo, .ora, author tool, capture tool, runtime scene/script, Game Bible, tracker or progress file was edited, and nothing was staged.
- The working-tree Godot and Python runs wrote only to `%TEMP%`.
- The `git status --porcelain` diff before and after shows only this note and the closure tool from this audit. Every other changed line belongs to other sessions' concurrent work (`3f97c9a`, `ec178fd`, Game Bible builder edits).

## Reproduce (repository root, real Python 3.12 runtime, `-I -B`)

```
python -I -B tools/rpg-2-star-ocean-the-second_static-pilots_female-battle-v08-liang-xu-south-v01-commit-closure-check_unapproved-v01_20261016-150108-0f79c1db.py [--root <checkout>]
python -I -B tools/rpg-2-star-ocean-the-second_protagonist-female_sideview-battle-idle-right-native-0p65-author_unapproved-v08_20261016-095054-326522f8.py check
python -I -B tools/rpg-2-star-ocean-the-second_liang-xu_south-idle-static-pilot-build-and-check_unapproved-v01_20261016-140940-6a60848d.py check
Godot_v4.7.2-stable_win64_console.exe --path game -s <abs>/tools/…party-capture-clean-clone_unapproved-v07r1_20261016-085133-1c89279f.gd -- <abs v08 png> edee2924e1058fa2058f04ea2d507f744e97c93999c6183bf7b7730c51d0adc5 <tmp>/cap.png <tmp>/cap.json ruins|outskirts <tmp>/nosprite.png
python -I -B tools/…v07-vs-v08-region-measure_unapproved-v08_20261016-095054-c2a29cc3.py <tmp>/nosprite-ruins.png <tmp>/nosprite-outskirts.png
```

- Run the Godot capture windowed, not `--headless`.
- The Liang capture tool writes a new stamped set into `outputs/`, so run it in a throwaway clone.
- If an open Pixelorama GUI autosaves during a `check`, rerun it.
