# Yonkers antenna corridor room 1 v05 scene-quality refinement (UNAPPROVED, NONRUNTIME)

Date: 2026-10-18. Tag `20261018-043851-4b9d66f1`. Status: **UNAPPROVED, nonruntime, off by default.**
- Scenes stay **3/12**.
- No accepted flag, counter, ledger, Bible, Git index or commit was touched.
- `survey_annex.gd` still loads v03.

## What v05 answers

Root viewed actual v04 in the official Pixelorama GUI:
- dish concavity was legible and the antennas fit under the HUD;
- but the wall, deck and grating were still rigid repeated bands with weak material relief;
- the slabs were homogeneous next to accepted Yonkers room 2.

v05 is one coherent native 640×360 pass over the same 13 layers. It is not a recolour microversion. It re-authors the surfaces.

| Surface | v04 | v05 |
|---|---|---|
| Coping (back and front) | one continuous lit band | individual stones: own top tone, open dark joints, chipped far arris (notches show sky), chipped lower face edge, shaded front face, per-stone drip shadow (deeper where a stone sags) |
| Back wall face | fixed 9 px courses, every block bevelled the same | irregular ashlar per bay: unequal courses, two-course jumper stones, crisp/eroded/spalled arris variants, flush and raked bed joints that break the mortar lines, three cooler repair stones, two stepped cracks, lime bloom under three leaking joints, five broad rain-wash runs, biofilm only where conduits shed water |
| Pilasters | brightest stone in the scene | toned down, uneven drums, corner chips, lichen on the two in the open |
| Wall fittings | flat on the wall | contact occlusion under every box, cabinet, tray, pipe and ivy clump; the tray opens in two places (teal/brass cables); one cable loop sags out; rust weeps under most brackets; brass pipe dulled with verdigris at the flanges |
| Deck | equal-width slabs per row, flat tone | re-laid flagstones: unequal widths, jogged joints, chipped corners, 5 raised slabs (front face plus cast shadow), 4 sunken slabs, 5 broken slabs, 5 lost corners (soil plus grass), a weathering patch inside each slab, joint moss and 12 lichen rosettes only where nobody walks, oil/grime under the drum, crate and dish, leaf litter in the corners |
| Grating lane | horizontal stripes with scattered single-pixel glints | bar-grating cells (bearing bars across the lane plus lower cross rods); each panel has its own age; polish only on the walking line; 6 small glint clusters on lit bar tops; rust blooms on the old panels; litter in panel corners; dirt against the lower nosing; trench lids of three ages |
| Brass | bright full-width nosing and railing lines | working finish with short worn highlights; fewer, duller conduit clamps; rust blooms at riser feet and guy anchors |
| Side piers, east block | horizontal lines every 11 px | re-coursed ashlar (stone pixels only) |
| Plinths A/B/C | | colour-only chips, rust weeps under bolts, moss at the foot |

The palette has 75 colours. The 65 v03 colours are unchanged and listed first. There are 10 named additions:
- cool repair stone ×2;
- damp stone;
- lichen ×2;
- soil;
- leaf ×2;
- oil stain;
- grating depth.

Native palette file: `…_native-palette_unapproved-v05_….gpl`.

Alpha is binary. No generated, traced, resampled, blurred or palette-quantized image was used, and there are no gradients. A seeded rng chooses only layout among the authored shapes, for example block widths and the arris variant. Wear and stains are cluster shapes or hand-drawn stamps at listed coordinates, not per-pixel noise.

**Geography:** the scene is a fictional 2537 rooftop survey walkway in the Yonkers vicinity, built from generic masonry and utility hardware. It does not reconstruct any Yonkers landmark.

## Preserved (verified)

- **Antennas and foreground:** antenna and foreground layer alpha are equal to v04, so A/B/C identities, sprite boxes, anchors (163/320/477, 210) and clue ids are unchanged.
- **HUD:** the antenna top rows are 73/83/68, below the 62 px HUD.
- **Skyline:** the sky layer and every pixel above y 92 are unchanged.
- **Doors layer:** only stone pixels changed. The door opening, threshold, lamp, stair, exit plate and ivy are v04 pixels.
- **Deck-detail layer:** only the conduit clamps and the rust blooms changed (218 px).
- **Runtime layout:** clue positions, markers, collision rects, the walk lane and the transition anchors live in `survey_annex.gd`, which is not touched (sha256 `d3a09593…` in the scratch tree of 7553581).

The flat image differs from v04 in 66,820 px. Per layer:

| Layer | Changed px |
|---|---|
| back parapet | 23,436 |
| wall kit | 427 |
| deck | 61,849 |
| walkway | 15,992 |
| deck detail | 218 |
| cast shadows | 5,755 |
| doors | 3,966 |
| front parapet | 10,714 |
| antennas | 28 / 32 / 24 |
| sky | 0 |
| foreground | 0 |

## Evidence (all actually run on this machine)

All runs used the scratch tree `C:\Users\hkzha\AppData\Local\Temp\yk5\r`, which is `git archive 7553581` of `game/`, `tools/`, the v03/v04 output folders and the three accepted reference folders. Nothing was run in `work/iv5v13` or in the primary `game/`.

| Check | Result |
|---|---|
| Author determinism | 2 runs: pxo, ora and all exports byte-identical |
| Source check `…_scene-quality-source-check_unapproved-v05_….py` | **GATES 10/10**: S1–S4 (13 layers, palette, binary alpha, manifest hashes, exports equal layers, ORA/PXO structure), G1 geometry/HUD/skyline, G2 transitions and props kept, G3 v04/v03 originals hash as recorded and survey_annex untouched, G4 native palette, G5 real change, P Pixelorama |
| Pixelorama 1.2.3 (official Windows build, `work/tooling`), headless CLI, isolated temp APPDATA | `.pxo` and `.ora` each exit 0. Split export gives 13 PNGs, all byte-exact. Flat export is exact (0 texels differ). The CLI left both sources unchanged. The real `%APPDATA%\pixelorama` was unchanged except one pre-existing GUI untitled autosave, which the check excludes. |
| Godot 4.7.2 windowed (GL Compatibility, NVIDIA), v05 harness (mechanical rename of the v04 test-only override harness) | exit 0, `YK1_V05_ALL_OK`, `YK1_V05_TEXTURES_IN_USE`, 0 FAIL, 0 SCRIPT ERROR |
| Six clues, three transitions | 3×3 approaches (marker, side, behind) plus 5 no-false-positive spots; 6/6 clues after room 2; next → room 2, back → east door (555,257), exit → surface; isolation in 4 other rooms OK |
| Collision, depth, reachability | 14 held-input collision cases; slide and escape OK; depth hidden 192 (A) and 270 (C), front 480/480, lane 480/480, stair shrub 469/480; reachability 56,083 cells, all targets |
| Parity with the v04 run | 27 behaviour lines identical; collision/slide/escape stops within 0.0064 px; lane walk x 579.1 vs 580.0 (frame timing) |
| Capture/replay pixel check `…_godot-v05-capture-replay-pixel-check_test-only-v05_….py` | **PASS 5/5**. Of the plate pixels v05 changed (not under an antenna or foreground texel), zh entry shows 57,541 and en entry 57,158 exactly as v05, with 0 as v04 and 0 as v03. 30 captures, 640×360, 15 kinds per language. |
| Accepted rooms 0 px | NYC room 1, NYC room 2 and Yonkers room 2 were replayed with the v05 textures already overriding the v03 paths in memory. 8/8 captures equal the acceptance captures (0 px). The 3 interaction sets pass and `ACCEPTED_REPLAY_ALL_OK`. |

**Captures**, in `outputs/yonkers-room1-v05_4b9d66f1/cap/` (zh and en):
- entry (review idle and runtime heroine);
- approach A/B/C;
- B dish from the lane;
- occlusion behind A and C;
- beside B;
- west stair;
- interact A/B/C;
- traversal;
- returned from room 2.

**Replay captures:** `acc/`.

## Codex 1× judgement (not acceptance)

- **Better:** at 1× the wall, deck and lane no longer read as repeated bands. The masonry reads as weathered coursed stone, the deck as worn flagstones with contact depth, and the lane as a recessed steel grate. The heroine is clearly separated from the darker lane. Brass and teal are now accents.
- **Still weaker than accepted room 2:**
  - the back wall is busier in small values than room 2's calmer masses;
  - the machinery boxes are still simple slabs;
  - there are no light pools (daylight exterior);
  - the long structural lines (trench, nosing, railing, coping) remain straight by nature;
  - the grey repair stones may read as patches.

Root will inspect the actual gameplay at 1×. v05 asks the creator nothing and claims no acceptance.

## Files (new, untracked; nothing staged)

**Tools:**
- `tools/…_scene-quality-refinement-author_unapproved-v05_….py`: imports the v04 author unchanged, which imports the v03 author.
- `tools/…_scene-quality-source-check_unapproved-v05_….py`: reuses the v03 checker's `source_checks` / `pixelorama_checks`.
- `tools/…_godot-v05-texture-override-capture-and-check_test-only-v05_….gd`
- `tools/…_godot-v05-accepted-rooms-replay-under-override_test-only-v05_….gd`: extends the existing untracked replay `tools/…_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd`, sha256 `a6552f03…22ef0`, used byte-identical.
- `tools/…_godot-v05-capture-replay-pixel-check_test-only-v05_….py`

**Outputs** in `outputs/yonkers-room1-v05_4b9d66f1/`:
- `.pxo` (Pixelorama pxo v7) and `.ora`, 13 layers;
- flat 640×360 PNG;
- `.gpl` palette;
- manifest with sha256 values;
- the two reports and the two Godot logs (their capture paths are the scratch paths);
- `nonruntime-exports/`: plate, foreground, three antennas;
- `cap/` (30) and `acc/` (8).

Key hashes (sha256-bytes):

| File | sha256 |
|---|---|
| `.pxo` | `f06528fc918936333f0bcbb38527286f39b71bc55ff1d94f19016608393a255a` |
| `.ora` | `cc3c75991c134af66b957669b56a10a662c059efb22fb332fae040cf0019d25d` |
| flat PNG | `33498bab753f587098ed739c5bdcbc408b99da6f7dab8480344f3bbe8178de70` |
| plate export | `02c080d9ff9c062c640d45d3ee2841691543a3bf8fa3f2be84de67d399d1f515` |
| manifest | `97cd7e55fbc75cdea7a8056bfafa355e8a4d02b77177cb14bb9a205adc177a88` |

**Dependency note:** the v04 author, manifest, exports and log exist only at upstream 7553581 (`work/iv5v13`, read-only here). They are not copied into the primary tree. So the v05 tools run only in a tree that contains 7553581 plus these files. The scratch tree is that tree.

**Re-run** (from such a tree):

```
python -I tools/…_scene-quality-refinement-author_unapproved-v05_….py
godot --headless --path game --import
godot --path game -s res://../tools/…_godot-v05-texture-override-capture-and-check_test-only-v05_….gd -- "$PWD/outputs/yonkers-room1-v05_4b9d66f1/cap" 20261018-043851-4b9d66f1 "$PWD/outputs/yonkers-room1-v05_4b9d66f1/nonruntime-exports"
godot --path game -s res://../tools/…_godot-v05-accepted-rooms-replay-under-override_test-only-v05_….gd -- "$PWD/outputs/yonkers-room1-v05_4b9d66f1/acc" 20261018-043851-4b9d66f1 "$PWD/outputs/yonkers-room1-v05_4b9d66f1/nonruntime-exports"
python -I tools/…_godot-v05-capture-replay-pixel-check_test-only-v05_….py
python -I tools/…_scene-quality-source-check_unapproved-v05_….py --pixelorama <Pixelorama 1.2.3 exe>
```

**Not done:**
- No Pixelorama GUI Save As/reopen; the headless CLI cannot write `.pxo`.
- No wiring into the runtime.
- No creator question.
