# Milo south static v01: QA note and style/source contract (UNAPPROVED)

Canonical task: `content.char.milo.static-south`. Producer: Claude Code adapter session (attempt 12), sole writer. Status: **production output only**. There is no creator art approval, no runtime default or wiring, and no motion review. Ledger, Bible, registry and index were not touched, and nothing was committed.

## Outputs (sha256 of raw bytes, no normalization)

| file | sha256 |
|---|---|
| `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-static_unapproved-v01_20261023-215823-28a012bd.png` | `3822b31805729f3091a61b3e073ade723f613049db4622364dc162a5101fa473` |
| `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-aaf32a0b.pxo` | `400c634f35c8aa43cce6ddf607968ac9a8041edd7c5caf4b582083164004c51f` |
| `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-e1afaba2.ora` | `1545d66ca66296e44d37466526f262431a03740f93b8935161dd91408de56b2c` |
| `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-palette_unapproved-v01_20261023-215823-ef8896f1.json` | `cae805d053847d1c39f3c8de7801ca826c2679b5db5abb75b22238990dbac927` |
| `game/assets/characters/milo-native-v01/south/rpg-2-star-ocean-the-second_milo_south-manifest_unapproved-v01_20261023-215823-e604f893.json` | `913d3070528bfb8539c65e7570e73c5f7bedc1b45a23928ec9aa091db7324cf7` |
| `game/assets/characters/milo-native-v01/.gdignore` (empty; keeps the unapproved sources out of Godot import) | n/a |
| `outputs/milo-s01/author/rpg-2-star-ocean-the-second_milo_south-preview-x6_unapproved-v01_20261023-215823-0bd82ad9.png` (QA preview, not a source) | `987866829d069da516e6028df465528a902552ed1a1eb3419590bd2787643d02` |
| `outputs/milo-s01/author/rpg-2-star-ocean-the-second_milo_south-output-paths-rawhashes_unapproved-v01_20261023-215823-f2e132e1.json` | `1ed5561fc59f5ffda50e87d551c683bcb3c2ac90c9f2ac4b6937efd6ef6f3875` |
| `outputs/milo-s01/independent-source1/rpg-2-star-ocean-the-second_milo_independent-source-proof_v01_20261023-215823-51a12dd6.json` | `c16f85493f7dd57e76b182ac1f8a6e3b22ca3627e49172b6c9f8a91077760e36` |

Tools: author `tools/rpg-2-star-ocean-the-second_milo_south-static-author_unapproved-v01_20261023-215823-51a12dd6.py` (`138a78d5a8ec32a4cbef7037c5eb5bda8740821f5868cf0a277ad4eda613cb6d`); independent checker `tools/rpg-2-star-ocean-the-second_milo_static-source-check_v01_20261023-215823-51a12dd6.py` (`9cb5d76870917c19495fe4d671aeefa4b1286a2e7cb802d7bd4cf6de2449239c`, unmodified this session). The reused Lin Que, Jiang and male-v8pair tools are hash-pinned, and the pins verified `true`.

## Source contract

- Canvas 80x112, opaque body rows 8..103, pivot (40,104), display scale 0.5 = 48 logical px. Binary alpha, transparent border.
- Declared palette: 40 entries, 35 used. 12 layers; 11 visible role layers contribute pixels; `guides` is hidden.
- Pixels are code-authored in a declared palette. No pixels were sampled from the portrait.
- Serialization reuses the existing male v8pair PNG/PXO/ORA serializers and the Lin/Jiang `finish` outline pass, through in-memory rebinding only. No Lin, Jiang or male file was written.
- PXO `data.json` is relabelled for Milo. The checker confirms no `lin-que`, `jiang-lan` or `protagonist-male` labels remain.
- Does not modify or count the old 32x48 native-animation placeholder.
- Not a recolour: the opaque mask differs from the Jiang and Lin south statics by 400 or more texels (independent check `own_silhouette_not_recolour`).

## Style and identity contract

Style reference: `docs/design/rpg-2-star-ocean-the-second_characters_sea-of-stars-style-direction_v01_20261020-181026-f5938409.md` (broad clusters, upper-left light).

Identity reference (no pixels sampled): approved portrait sheet `outputs/rpg-2-star-ocean-the-second_milo_character-sheet_hairstyle-v02_20261013-161317-f1651dc0.png`, sha256 `79a02c53…c244f`, verified by the checker. Identity anchors drawn:

- very short spiky dark-brown hair with a silver patch at the character's right temple (screen left)
- light stubble, green eyes, gentle smile
- navy high-collar zip shirt
- white/grey **short** coat with a green chest cross
- square white medicine case with navy straps and a green cross, at the character's right hip
- bright green wristband on the character's left wrist (screen right)
- navy trousers with green piping; dark boots with pale bands and green patches

Authored simplifications (also recorded in the manifest `authored_deviations_from_sheet`):

1. Coat hem at mid-thigh, following the Bible's "short coat"; the sheet's knee length is not used.
2. Case strap drawn cross-body (left shoulder to right hip) for readability at 48 px; the sheet shows it over the right shoulder.
3. This session: strap drawn as one flat 3-px band in `n1` (lighter navy) with a `g2` panel. The previous three 1-px diagonal shade stripes were the main noise source. `n1` keeps the strap distinct from the `n2` shirt.
4. The character's right hand overlaps part of the case's green cross in the front view. The cross is still partly visible. Visual limitation noted, not fixed.

## Root-cause fixes this session (author file only; gate thresholds unchanged)

The first `check` failed one hard gate: `isolated_texels` = 97, against `isolated_texels_le_24`. A diagnostic map (`outputs/milo-s01/scratch/milo_isolated_diag.py`, log `logs/diag1`) traced about 65 texels to the 1-px diagonal strap stripes. The rest were 1-px outline staircase corners at:

- hair spike gaps
- jaw step and ear
- sleeve tops, hand bottoms and coat hem steps
- boot band and boot patch highlight
- case strap and lid line
- zip pull and temple pixel

Drawing fixes:

- flat strap band
- spike segments and gaps widened to 2 px
- straightened the jaw (rows 28..31) and sleeve top rows
- full-width hand bottom row
- squared coat hem and collar row 37
- 2-px boot highlight; boot band widened to 3 px
- case straps moved to x 14..15 and 25..26
- stubble extended to row 32
- removed the lone zip-pull and temple pixels

Result: 9 isolated texels, including the two intentional smile corners.

## Commands actually executed (from `repo/`; logs under `outputs/milo-s01/logs/<dir>/`)

`source ../tooling/worlds-between-env.sh` was refused by the shell permission layer, and so was `$?` inspection. All steps ran through `python3 -I outputs/milo-s01/rpg-2-star-ocean-the-second_milo_south-qa-orchestrate_v01_20261023-215823-51a12dd6.py <step> <dir>`. The orchestrator calls `../tooling/venv/bin/python -X utf8 -I` (venv symlink not resolved) with subprocess timeouts and logs `cmd` and `rc`.

| dir | step | rc | result |
|---|---|---|---|
| check1 | author `check` | 1 | hard failure `isolated_texels_le_24` (97); disk files absent |
| diag1/diag2/diag3 | isolated-texel map | 0 | 97 → 9 |
| check2 | author `check` | 1 | `hard_failures: []`; FAIL only because outputs were not yet on disk |
| build1 | author `build` | 0 | `MILO_SOUTH_V01_ALL_OK`, deterministic rebuild true, pins true |
| check3 | author `check` after build | 0 | `MILO_SOUTH_V01_ALL_OK`; all 5 disk files match rebuild |
| source1 | independent checker `--out outputs/milo-s01/independent-source1` | 0 | `MILO_S01_INDEPENDENT 29 / 29`, failures [] (includes corrupt-hash, tampered-PNG and visible-guides negative controls) |
| pxl1 | Pixelorama 1.2.3 `--headless --audio-driver Dummy --quit -- --export -o <abs target> <abs source>`, PXO and ORA, timeout 120 s, fresh folders | 0 / 0 | sources unchanged (sha before = after) |
| compare1 | emitted PNG vs authored PNG | 0 | `MILO_PXL_EXPORT_PIXEL_EXACT`: both 80x112 RGBA, 0 differing texels |

Pixelorama emitted file names differ from the requested `-o` target:

- PXO export wrote `export-pxo/milo-south-idle-static-v01.png` (the stored export-profile basename).
- ORA export wrote `export-ora/rpg-2-star-ocean-the-second_milo_south-edit_unapproved-v01_20261023-215823-e1afaba2.png`.

Both emitted files have sha256 `2449291595b4684100ace8eabb28360f08bc782ad8367b7d66912bea9161ef26`. That differs from the authored PNG bytes because of encoder differences, but the pixels are identical.

**Pixelorama is not application-clean.** Diagnostics are preserved in `logs/pxl1/pixelorama-{pxo,ora}.log`:

- repeated `custom_samplers` shader condition errors
- dummy-texture RID leaks
- `get_child` index out of bounds, `rp_node` null and `ensure_control_visible` ancestor errors (ORA run)
- ObjectDB and resource leaks at exit

## Batch 13 provider re-run (Claude Code, sole writer; sources unchanged)

Tested source revision: HEAD `d539a85508a471db0077a93d20ba72231b477943`. The Milo files are untracked working files on top of it. No source, author or checker edits were needed, so none were made. Raw-byte sha256 values of all 5 south files, the author `138a78d5…13cb6d`, the checker `9cb5d768…239c`, the fit script `91d9b3e0…d528` and the checked runner `0a3e036a…0bd5` were identical before and after (`PINS_UNCHANGED True`). These working-file hashes were not compared with staged Git blobs, because nothing is staged.

Everything ran through `python3 -I outputs/milo65/provider13/rpg-2-star-ocean-the-second_milo_south-provider13-qa-run_v01_20261023-215823-51a12dd6.py`, from `repo/`. Logs and outputs are in `outputs/milo65/provider13/`.

| step | rc | result |
|---|---|---|
| author `check` (`author-check.log`) | 0 | `MILO_SOUTH_V01_ALL_OK`; `hard_failures: []`; isolated_texels 9; deterministic rebuild true; pins true; all 5 disk files match the rebuild |
| independent checker `--out outputs/milo65/provider13/independent` (`independent-source.log`) | 0 | `MILO_S01_INDEPENDENT 29 / 29`, `FAILURES []` |
| Godot source fit (`fit.log`, `fit.runner.log`) | 0 | `JIANG37_SOURCE_FIT_PASS captures=4`; `CHECKED_RUN PASS None exit= 0 elapsed= 3.684 missing= []` |

Fit command:

`xvfb-run -a -s "-screen 0 640x360x24" <venv python> -I <checked runner> --timeout 110 --expect "JIANG37_SOURCE_FIT_PASS captures=4" --log …/fit.runner.log -- <Godot 4.7.2> --audio-driver Dummy --rendering-driver opengl3 --resolution 640x360 --path game --script <tools/…native-static_scene-fit-capture_test-only-v01_20261021-235007-514b9771.gd> -- <abs south static PNG> <abs outputs/milo65/provider13/fit> provider13-20261023-215823-51a12dd6 milo`

The runner deadline was 110 s, the script's own timer is 75 s, and the outer subprocess timeout was 150 s.

Fit outputs in `outputs/milo65/provider13/fit/`. Each manifest entry has `sourceSha256` = `3822b318…a473`, scale 0.5, position (400,280), `testOnly`, `runtimeAdopted:false`, `artApproved:false`.

| file | sha256 |
|---|---|
| `…_milo_source-fit-city-en_test-only-640-v01_provider13-20261023-215823-51a12dd6.png` | `2f0673df9b68d67ac38ab0515d6c6e4c32983003dc45f449a4abf08eaf3a864d` |
| `…_milo_source-fit-city-zh_test-only-640-v01_provider13-20261023-215823-51a12dd6.png` | `b1290786c6d159b056e0d9e463829c2c09155c744cf06eafe0631af417453d1b` |
| `…_milo_source-fit-ruins-en_test-only-640-v01_provider13-20261023-215823-51a12dd6.png` | `601c78c330a4aaa1feec41ee4432f356f80e7d0533332dd6e54b122ab508556b` |
| `…_milo_source-fit-ruins-zh_test-only-640-v01_provider13-20261023-215823-51a12dd6.png` | `7805936821e4acaa483417b5a23d609568b7e364ab39201da5dbb2257ce9d152` |
| `…_milo_source-fit-manifest_test-only-v01_provider13-20261023-215823-51a12dd6.json` | `714c13b4c228ca7b0fcce757df0aa800bcf9f8615a5dbe98d6b00ff889556694` |

Run summary: `outputs/milo65/provider13/rpg-2-star-ocean-the-second_milo_provider13-qa-summary_test-only-v01_20261023-215823-51a12dd6.json`.

Fit diagnostics and limits:

- Godot printed one non-fatal `WARNING: Could not set V-Sync mode` (Xvfb/llvmpipe). The runner's diagnostic pattern does not match it. No `SCRIPT ERROR` or `ERROR:` lines were printed.
- Visual read of the city-en and ruins-zh captures (the other two not viewed): the 48-logical-px Milo stands at about the same height as the in-scene heroine and NPCs in both scenes, and the bilingual labels render.
- The fit is a direct `Sprite2D` overlay on a CanvasLayer. It does not cover actor assignment, collision, y-sort/occlusion, interaction, motion or normal-input play.
- The generic script fixes the host scene to `hero_appearance="female"`.
- The success marker keeps its historical `JIANG37_` name.
- This is a fit capture, not creator art approval or runtime adoption.

## Not done / limitations

- Godot fit check is done (see batch 13 above). No other Godot or runtime check was run.
- `outputs/milo65/` (coordinator's independent baseline smoke) and `outputs/ldisplay64/` were not touched.
- South only. No other directions, no motion, no runtime wiring, no creator approval.
- Scratch diagnostics in `outputs/milo-s01/scratch/` are QA aids, not sources.
