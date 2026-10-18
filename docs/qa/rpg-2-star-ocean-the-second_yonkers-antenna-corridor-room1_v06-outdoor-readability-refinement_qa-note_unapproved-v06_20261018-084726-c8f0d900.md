# Yonkers antenna corridor room 1 v06 outdoor readability refinement (UNAPPROVED, NONRUNTIME, test-only)

Date: 2026-10-18. Tag `20261018-084726-c8f0d900`. Base: HEAD `160b823` (v05 `4b9d66f1` committed there).
Status: **UNAPPROVED, nonruntime, off by default. Root visual review requested.**
- Meters unchanged: 40.8%, M2 10/12, scenes 3/12, sprites 0/52, plays 0/2.
- No accepted flag, counter, ledger, Bible, Git index or commit was touched.
- `survey_annex.gd` still loads v03 (sha256 `1be0e1a1…eaea`, names no v04/v05/v06 file).
- No animation. The 51 identities, 52 variants, canon and the no-followers rule are not touched.

## What v06 answers

The creator rejected the outdoor look again after v05. The Codex 1× judgement of v05 found four problems:
- the back wall is busy and mechanical in small values, and it competes with the three antennas;
- the utility cabinets and the dish base are flat slabs;
- the composition still reads as schematic next to accepted Yonkers room 2;
- the grey repair stones read as patches.

v06 is one native 640×360 pass over the same 13 layers. The v06 author imports the v05 author unchanged (and through it v04 and v03).

| Area | v05 | v06 |
|---|---|---|
| Back wall face | Irregular ashlar in 6 value steps. Spalls, raked joints, repair stones, lime bloom, many weeps, per-pixel damp. | The face is in shade (the sun is behind the parapet), so v06 re-courses it as longer ashlar in a narrow range: two new half-step stone tones, joints one step darker instead of mortar-black, a catch-light on some blocks only, and broad value masses.<br>**Quiet zones** behind A (x 118–212), B (270–374, darker field behind the pale dish) and C (450–510) carry no marks at all.<br>Outside them only one stepped crack, two broad rain-wash runs, six short weeps and five compact damp clusters remain. Repair stones and lime bloom are gone. |
| Pilasters | 4-row stripe pattern | Lit west arris, half-lit face, turned east edge, uneven drums, damp foot. The caps are as in v05. |
| Wall boxes (3 junction boxes, west and east cabinets) | Front rectangles | Visible top face with a short lit front arris, a lid-lip shadow row, a lit west edge, a turned east edge, a kick base, and a soft half-step shadow on the wall.<br>The three junction boxes now differ: A has a hooded warning lamp, B has louvres and a steady lamp, C has a meter window with a needle. |
| Crate, dish cable trough, planter | Slabs | Top face + front face + base course. The trough has chamfered corners, sun-lit steel lids, unequal block joints and a base lip.<br>All floor fixtures get a contact row plus a short tail away from the sun. |
| Plinths A/B/C, readout cabinets, battery (antenna layers, **colour only**) | Pale slab fronts | Lit top face, crisp front arris (lit toward the sun only), cap-overhang shadow, shaded front, dark foot. The dish base B is shaded as a drum (lit west, turned east).<br>The cabinets get a lid face, a lid-lip shadow, a turned edge and a kick base. |
| Deck | A weathering blob in every slab; 12 lichen, 7 leaves, 5/4/5/5 raised/sunken/broken/lost | Patches on about a third of the slabs; 4 lichen, 4 leaves, 3/2/3/3. Same slab layout. |
| Safety paint | Dashed boxes around each pad (reads as a diagram) | Verticals removed; the front line is faded to worn paint. |
| Front parapet face, side piers | Busy v05 ashlar | Same shapes with values compressed into the shaded range. Stone pixels only; door jamb highlights, lamp, stair, plates and ivy are untouched. |

**Palette:** 77 colours. These are the 75 v05 colours (unchanged and listed first) plus `st_half_lit #8e846a` and `st_half_dk #726b55`. Native palette file: `…_native-palette_unapproved-v06_….gpl`.

**Method:**
- Alpha is binary.
- No generated, traced, resampled, blurred or palette-reduced image is used, and there are no gradients.
- The seeded rng only chooses layout among authored shapes (block widths, which blocks get a catch-light).

**Geography:** a fictional 2537 rooftop walkway in the Yonkers vicinity. It is not a landmark reconstruction.

**Pixel changes vs v05:** the flat image changes in 40,327 px. Per layer:

| Layer | Changed px |
|---|---|
| back parapet | 27,693 |
| wall kit | 892 |
| deck | 12,721 |
| deck detail | 2,872 |
| cast shadows | 2,173 |
| doors | 5,340 (stone only) |
| front parapet | 10,170 |
| antennas A / B / C | 714 / 750 / 539 (colour only) |
| sky, walkway (lane), foreground | 0 |

## Preserved (verified)

- **Antennas and foreground:** antenna and foreground alpha equal v05. Sprite boxes, anchors (163/320/477, 210) and clue ids equal the v05 manifest.
- **HUD and skyline:** antenna tops are at y 73/83/68, below the 62 px HUD. The sky is unchanged and 0 px changed above y 92.
- **Lane, doors and props:** the walkway layer (lane, grating, trench) is byte-equal to v05. The doors layer changed stone pixels to stone only. Deck-detail changes stay inside the declared crate/trough/planter rects and the paint lines. Wall-kit changes stay inside the five boxes plus their top faces.
- **Runtime layout:** clue positions, markers, collision, the walk lane and the transitions live in `survey_annex.gd`, which is untouched.

## Evidence (actually run)

**Where it ran.** Builds and Godot ran in an isolated scratch tree, `C:\Users\hkzha\AppData\Local\Temp\yk6\r`. That tree is `git archive 160b823` of:
- `game/` and `tools/`;
- the v03/v04/v05 output folders;
- the three accepted reference folders;
- plus the new v06 tools.

Nothing ran in the primary checkout, and Godot never ran in this worktree. Both Python checks were then re-run from this worktree against the copied outputs (byte-identical copy, 52 files), and both pass there.

**Prerequisite.** v05 reproduces byte-identically from HEAD (pxo, ora, flat and manifest hashes equal the committed files). So the dependency chain v06 → v05 → v04 → v03 is fully committed.

| Check | Result |
|---|---|
| Author determinism | 2 runs: all 10 output files byte-identical |
| Source check `tools/…_readability-source-check_unapproved-v06_….py` | **12/12 gates**:<br>• S1–S4: 13 layers, palette, binary alpha, manifest hashes, exports equal layers, ORA/PXO structure.<br>• G1: geometry, HUD and skyline.<br>• G2: lane, transitions and props kept.<br>• G3: v05/v04/v03 files hash as recorded; survey_annex untouched; nothing with the v06 stamp under `game/`.<br>• G4: native palette.<br>• G5: real change.<br>• G6: calmer wall.<br>• G7: fixture volume.<br>• P: Pixelorama. |
| G6 wall (plate only, visible back-wall px, mean luma step between horizontal neighbours) | whole wall 7.18 → **3.49**; quiet A 4.93 → **1.46**; quiet B 5.01 → **1.27**; quiet C 6.73 → **1.71** |
| G7 top-face minus front-face luma (≥ 12 required) | junction boxes 73/76/68; west cabinet 69; east cabinet 74; crate 28; trough 34; plinths A/B/C 38/42/38 (plinths: stone pixels only, because the antennas stand on their tops) |
| Pixelorama 1.2.3 official Windows build (`work/tooling`), headless CLI, isolated temp APPDATA | `.pxo` and `.ora` both exit 0. Split export gives 13 PNGs, all byte-exact. Flat export: 0 texels differ. The CLI left both sources unchanged. The real `%APPDATA%\pixelorama` was unchanged except one pre-existing GUI untitled autosave (folder 2026_10_16), which the check excludes. |
| Godot 4.7.2 windowed (console exe), v06 harness = mechanical rename of the v05 harness (only the header comment, file names, tags and save root differ) | exit 0, `YK1_V06_ALL_OK`, `YK1_V06_TEXTURES_IN_USE`, 0 FAIL, 0 SCRIPT ERROR |
| Clues, transitions, collision | 6/6 clues by real `interact`; next / back (555,257) / exit transitions OK; 14 held-input collision cases; slide and escape OK; lane walk; reachability; isolation |
| Parity with the v05 run | 25/25 behaviour lines identical (HUD, header, caption, depth, interaction, reachability, clue, transition, isolation, antenna); collision stops within 0.0024 px; lane walk x 578.4 vs 579.1 (frame timing) |
| Capture/replay pixel check `tools/…_godot-v06-capture-replay-pixel-check_test-only-v06_….py` | **PASS 5/5**. Of the 31,754 plate px changed vs v05 and v03 (not under an antenna or foreground texel), zh entry shows 31,432 and en entry 31,342 exactly as v06, with 0 as v05 and 0 as v03. 30 captures at 640×360, 15 kinds per language. |
| Accepted rooms 0 px | NYC room 1, NYC room 2 and Yonkers room 2 were replayed with the v06 textures overriding the v03 paths in memory: 8/8 captures equal the acceptance captures (0 px). Interactions 3/3, `ACCEPTED_REPLAY_ALL_OK`. |

## Codex-style 1× judgement (mine; not acceptance)

**Better than v05:**
- The wall now reads as one calm, shaded masonry mass. The dark lattice, the pale dish and the thin guyed whip all stand clear of it, and nothing on the wall behind them competes.
- The wall boxes and cabinets read as boxes with lids at 1×.
- The plinths read as stone blocks with a lit top and a shaded front, not pale slabs.
- The dashed pad boxes no longer draw a diagram on the deck.

**Still weaker than accepted room 2 (visible limits):**
- The layout is unchanged by constraint: three evenly spaced pads, straight conduits with L-bends and a long straight lane. It still reads more orderly or schematic than room 2.
- The deck is still mid-busy. A third of the slabs keep a weathering blob, and the joint moss and specks from v05 remain.
- There are no light pools (daylight exterior).
- The plinths are still fairly pale at 1×, and their silhouettes remain rectangles because antenna alpha is frozen.
- The wall may now read slightly flat or uniform in large areas. That is the trade-off for quiet.
- The dish trough is half hidden behind the pedestal, so its new volume shows mainly at the edges.

## Files (new, untracked; nothing staged)

**Tools** (in `tools/`):
- `rpg-2-star-ocean-the-second_yonkers-antenna-room1_outdoor-readability-author_unapproved-v06_20261018-084726-c8f0d900.py`
- `rpg-2-star-ocean-the-second_yonkers-antenna-room1_readability-source-check_unapproved-v06_20261018-084726-c8f0d900.py`
- `rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-texture-override-capture-and-check_test-only-v06_20261018-084726-c8f0d900.gd`
- `rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-accepted-rooms-replay-under-override_test-only-v06_20261018-084726-c8f0d900.gd`: extends the committed `tools/…_wdc-annex-room1_v02-review-gate-accepted-rooms-replay_check-v01_20261017-172907-03286bf3.gd`.
- `rpg-2-star-ocean-the-second_yonkers-antenna-room1_godot-v06-capture-replay-pixel-check_test-only-v06_20261018-084726-c8f0d900.py`

**Outputs** in `outputs/yonkers-room1-v06_c8f0d900/`:
- `…_readability-layers_unapproved-v06_….pxo` (sha256 `248aba423a436a4fcfe1edae8d7f94b99c602b2d25b3606bf3d94ccb6320badb`) and `.ora` (`398a22d907d0674b540f50713417ba344989675b67b324bca1fdb8b6cda2b8c2`), 13 layers each.
- `…_readability-native-640x360-flat_unapproved-v06_….png` (`a77835addd36bdc0a717d92ffc25a0f49935091c50743a09bfe4202d3edd8e8e`).
- `…_native-palette_unapproved-v06_….gpl` (`99a76833be548bb8e7bfc506b11ac88ab6fdc20dc2ef0264d7d32813684e6b45`).
- `…_readability-manifest_unapproved-v06_….json` (`d8472a32c83a71eebaba3a9b00681d5a3531ece4a9e23fe9285cafb3d0ad9247`).
- `exp/`: plate `…_corridor-plate-readability_…` (`3e95023ac608bdfd3e74c1880a2a91f85d350c846d2c88ed3f2c639d6c97419a`), foreground and the three antenna crops.
- `cap/`: 30 Godot captures (zh/en × entry, runtime-heroine entry, approach A/B/C, B from the lane, occlusion behind A/C, beside B, west stair, interact A/B/C, traversal, returned from room 2).
- `acc/`: 8 accepted-room replay captures.
- Source-check report, capture/replay pixel-check report, and the two Godot logs. The logs' capture paths are the scratch paths.

**For whoever commits (Codex):**
- The `.gpl` is hashed as LF bytes. Like v05, it needs a scoped `text eol=lf` line in `.gitattributes`, or the G4 hash fails on an autocrlf checkout. I did not edit `.gitattributes`.
- The `acc/` names exceed MAX_PATH in the primary checkout (like v05's). Both Python checks read long paths with the `\\?\` form.

**Re-run** (from a tree containing HEAD plus these files):

```
python -I tools/…_outdoor-readability-author_unapproved-v06_….py
godot --headless --path game --import            # scratch tree only: import writes .godot/.uid
godot --path game -s res://../tools/…_godot-v06-texture-override-capture-and-check_test-only-v06_….gd -- "<abs>/outputs/yonkers-room1-v06_c8f0d900/cap" 20261018-084726-c8f0d900 "<abs>/outputs/yonkers-room1-v06_c8f0d900/exp"
godot --path game -s res://../tools/…_godot-v06-accepted-rooms-replay-under-override_test-only-v06_….gd -- "<abs>/outputs/yonkers-room1-v06_c8f0d900/acc" 20261018-084726-c8f0d900 "<abs>/outputs/yonkers-room1-v06_c8f0d900/exp"
python -I tools/…_godot-v06-capture-replay-pixel-check_test-only-v06_….py
python -I tools/…_readability-source-check_unapproved-v06_….py --pixelorama <Pixelorama 1.2.3 exe>
```

**Not done:**
- No Pixelorama GUI Save As/reopen; the headless CLI cannot write `.pxo`.
- No runtime wiring.
- No creator question.
- No acceptance claim.
