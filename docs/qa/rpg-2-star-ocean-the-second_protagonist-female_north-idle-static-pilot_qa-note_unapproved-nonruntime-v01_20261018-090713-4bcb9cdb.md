# Female protagonist north idle static pilot v01: QA note

M8, 2026-10-18 (file stamps are UTC). One north-facing exploration idle **static** frame for the female protagonist, matched to the creator-approved south idle selout v8 at 48 logical px. It is one missing direction toward the four-direction set.

- **Status:** UNAPPROVED technical candidate, NONRUNTIME. It is not wired into any scene or script. Manifest: `art_approved: false`, `human_reviewed: false`, `runtime_integrated: false`.
- **Not in scope:** this is not a new south iteration, not battle art, not motion, and not a sprite-set or runtime approval.
- **Counters:** unchanged. Exploration sprites stay **0/52**. No ledger, Game Bible, index, progress or checklist file was edited, and nothing was committed.
- **No paid fallback:** no API, paid or cloud generation was used, and no quota or auth error occurred. Every texel was hand-placed in literal grids; there are no generated pixels.

## Inputs read

- **v8 approval scope:**
  - [v8 visual QA note](rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8_visual-qa-note_m8-v08_20261015-021600-c1694107.md)
  - [v8 baseline decision](../character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-idle-static-baseline-decision_m8-v08_20261015-022700-07161696.md): approves south static only, and says later facings should match its palette, materials, value structure and outline treatment.
  - [v8 `.pxo` headless round-trip note 599b83ff](rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-pxo-source_headless-roundtrip_qa-note_m8-v08_20261015-080907-599b83ff.md)
- **v8 PNG**, decoded texel by texel: 80×112 cell, rows 8–103, pin (40,104), 32 colours.
- **Identity sheet in the inventory:** the 21:9 [female character sheet](../../outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png). It is the readiness-checklist `source_art.portrait`. Its **back view** is the only direct evidence of the back.
- **Earlier work:**
  - The earlier [east/north concept review](../character-visuals/rpg-2-star-ocean-the-second_protagonist-female_east-north-city-review_m8-concept_20261014-152400-29a6d879.md), which noted the north ponytail extends to the viewer's right.
  - The male HD static pilot v02 tools, used for their `.pxo`/`.ora` and capture patterns.
- **Global `AGENTS.md`:** naming rules and the separate-images rule. The repository has no `AGENTS.md` of its own.
- **Not used:** the rejected 32×48 native body. Nothing was scaled up.

## Identity decisions

These were recorded and the work continued without asking the creator. Each is a human call at review.

1. **Arms hang relaxed.** This follows the sheet's back view. v8's hand-on-hip is treated as a front-only pose. Turning between south and north idle will therefore change the arm pose.
2. **Canister on the character's LEFT, as in v8.** In the north view that is screen-left, outside the pack. The sheet's back view shows it on the character's right. v8 is the approved baseline, so v8's side is kept for turn consistency, and the conflict is flagged.
3. **Ponytail and scarf tail fall on the character's right.** That is screen-right in the north view, the same body side as in v8 and in the sheet's back view.
4. **Bedroll's long end is past the character's left shoulder.** v8 shows that end, so in the north view it is screen-left.
5. **Light stays in the screen's upper left**, as in v8, and is not mirrored with the body. The character's left side is therefore the lit side in the north view.
6. **Collar/hood at the nape uses v8's storm-slate coat colours**, not the sheet's grey-brown hood. v8 recoloured the coat, and v8 takes precedence.
7. **Colours are a strict subset of v8's palette:** 30 of its 32 colours, exact RGB.
   - Unused: v8's mouth `#9a4634` and its lapel trim `#c07a40`. Both are front-only.
   - No new colour was added.

## Back details: direct evidence vs proposed construction

"Sheet-back" means the identity sheet's back view.

| Layer | Evidence | What is direct / what is proposed |
| --- | --- | --- |
| ponytail | sheet-back + v8 | **Direct:** high ponytail tied at the crown (sheet); plume falls on the character's right (v8). **Proposed:** exact arc, the 1–2 px gap beside the head, and the wisp tips. |
| hair | sheet-back + v8 | **Direct:** dark-brown back of head, loose locks to the collar, v8 hair ramp. **Proposed:** lock clusters, the sheen and the tie texels. |
| collar | sheet-back | **Direct:** bunched collar/hood at the nape. **Proposed:** the slate colour (see decision 6) and the 2-row height. |
| bedroll | sheet-back + v8 | **Direct:** teal roll across the top of the pack; long end on the character's left (v8). **Proposed:** the end-cap curl. |
| pack | sheet-back | **Direct:** warm pack, flap, teal community diamond, lower pocket (back view and pack panel). **Proposed:** the 17×18 texel proportions. v8 shows almost none of the pack. |
| straps | sheet-back + v8 | **Direct:** two leather straps with steel buckles. |
| canister | v8 (conflicts with sheet-back) | **Direct:** steel canister (v8). Its side is decision 2. |
| arm-left / arm-right | sheet-back + v8 | **Direct:** slate sleeve, rolled cream cuff, bare forearm, fingerless glove. **Proposed:** relaxed straight hang (decision 1). |
| scarf-tail | sheet-back + v8 | **Direct:** teal tail on the character's right below the pack. **Proposed:** the flare under the hand. |
| coat | sheet-back + v8 | **Direct:** coat skirt to mid-thigh with a centre back vent; v8 slate ramp. **Proposed:** folds. The belt stubs beside the pack are inferred from v8's front belt rows. |
| legs | sheet-back + v8 | **Direct:** spruce trousers (v8); knee strap on the character's right leg (sheet; v8's knee pad is on the same leg). **Proposed:** knee creases. |
| boots | sheet-back + v8 | **Direct:** warm leather boots with a turned cuff and an ankle strap with a buckle, seen from the heel. **Proposed:** heel blocks and the slight toe-out. |

**Deliberately absent:** face, eyes, shirt front, laces, knee pad, chest emblem and lapel trims. All of these are front-only. No new gear, outfit piece, marking or backstory was invented.

## Files (all new; nothing existing edited)

| File | Hash |
| --- | --- |
| [north PNG](../../game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot_unapproved-v01_20261018-090713-6ed8d8dd.png) | sha256-bytes `bd5c8166…8e82` (2,508 bytes) |
| [editable `.pxo`](../../game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable_unapproved-v01_20261018-090713-99e861ce.pxo): 13 role layers + hidden locked guides, pxo_version 7 | sha256-bytes `7ca7dbdf…6ef9` |
| [layered `.ora`](../../game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-editable-layers_unapproved-v01_20261018-090713-fe132628.ora): same layers; mergedimage = PNG | sha256-bytes `2601128c…27ff` |
| [manifest](../../game/assets/characters/protagonist-female/north-idle-static-pilot-unapproved-v01/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-manifest_unapproved-v01_20261018-090713-04aa20a9.json): per-layer evidence, gates, reference locks | sha256-text-lf-v1 `ea3cf200…01be` |
| [build-and-check tool](../../tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py) | sha256-text-lf-v1 `7a2f9f7c…daae` |
| [test-only Godot capture harness](../../tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-godot-capture_unapproved-v01_20261018-090713-d3f837ab.gd) | sha256-text-lf-v1 `4b374ebe…1101` |

**The tool reuses existing v8 source utilities:**

- It imports the tracked [v8 `.pxo` round-trip tool](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-pxo-source-roundtrip_m8-v08_20261015-080907-05c22e55.py) for:
  - long-path I/O, hashes and the never-overwrite writer;
  - the v8 SHA-256 source gate;
  - the guide-layer layout;
  - the Pixelorama path and version.
- It refuses to import that tool unless its sha256-text-lf-v1 is `53d492fb…4f73`.
- The `.pxo`/`.ora` writers follow the male v02 pilot's format.
- The art itself lives in two literal 56×96 grids, `MAP` and `ROLE`, at cell offset (12,8).

## Gates (`python -I -B <tool> check`): PASS

Run with Python 3.12, Pillow 12.3 and numpy.

### Shape, palette and identity

- **Alpha:** binary, with no opaque texel on the cell border.
- **Body:** rows **8–103**, the same as v8, so it shows at **48.0 logical px**. Sole row 103, pin (40,104) inside the feet span.
- **Size:**
  - north: alpha bounds (22,8)–(61,103), 40×96 visible, 2,471 opaque texels;
  - v8: 43×96 visible, 2,419 opaque texels.
- **Palette:** 30 colours, all exactly in v8's palette.
- **Not a mirrored front:**
  - only 211 of 2,471 north texels (8.5%) equal v8 mirrored left-right (best of shifts −3..+3), and 173 equal v8 at the same position;
  - those matches are mostly shared outline ink and the slate/teal bases;
  - **0** skin texels sit in head rows ≤ 33 (no face).

### Files and layers

- **Rebuild:** PNG, `.pxo`, `.ora` and manifest equal a fresh rebuild. The build refuses to overwrite.
- **`.ora` structure:**
  - mimetype is stored first;
  - the only hidden layer is `guides`;
  - the 13 role layers have 0 overlapping texels and recompose exactly to the PNG;
  - mergedimage = PNG.

### Official Pixelorama 1.2.3 CLI

Each run used `--headless --quit -- --export` with `APPDATA` redirected to a fresh temp dir.

| | `.pxo` | `.ora` |
| --- | --- | --- |
| flattened run 1 / run 2 | exit 0; RGBA == PNG; binary alpha; runs byte-identical | same |
| `--split-layers` | 13 PNGs; 13/13 equal the role blobs; guides not exported | same |
| input file unchanged by CLI | yes | yes |

**Real `%APPDATA%\pixelorama`:** none of our runs changed it. The only differences were the open GUI's `.running` heartbeat and one 2026-10-16 autosave backup, both owned by the GUI.

**Untouched:** all 9 reference files are unchanged after the check. They are the v8 PNG, v8 manifest, v8 `.pxo`, `.pxo` manifest, v8 QA note, decision doc, round-trip note, round-trip tool and identity sheet.

## Real Godot captures (test-only harness)

**Setup:**

- Godot 4.7.2 windowed, with the game's native **640×360 canvas** (canvas_items, integer scale) in its default **1280×720 window**.
- Sprite scale 0.5, so 1 texel = 1 window pixel.
- The runtime placeholder hero is hidden for these frames only, so **one north character** stands at the hero spot.
- North and v8 are both placed by the foot pin at the same x and ground row, so the framing is identical.
- No outline, glow, shadow or filter was added.

**Images:** each scene and language has **two separate images**. One is the candidate alone. The other is v8 alone, with an on-screen label (zh `对照参考：已批准南向 v8（非候选）` / en `Reference: approved south v8 (not the candidate)`) at the top-left of the play area, clear of the figure and the HUD text.

**Harness gates (all passed):**

- source SHA-256 locks;
- 1280×720 frames;
- language applied;
- placeholder hidden;
- north window 40×96 and v8 window 43×96, both 1:1;
- texel fidelity 2,471/2,471 and 2,419/2,419;
- same pin and ground row for both figures;
- label clear of the figure.

| Scene / lang | North pilot (candidate) | South v8 (labelled reference) |
| --- | --- | --- |
| city bright, zh | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_north-idle-pilot-city-bright-zh-h48_unapproved-v01_20261018-091242-c971ea02.png) `822ca50a…2629` | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-v8-reference-city-bright-zh-h48_unapproved-v01_20261018-091242-c971ea02.png) `820cda66…7ee5` |
| city bright, en | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_north-idle-pilot-city-bright-en-h48_unapproved-v01_20261018-091242-c971ea02.png) `ef3c2289…8bad` | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-v8-reference-city-bright-en-h48_unapproved-v01_20261018-091242-c971ea02.png) `e62d02be…72e2` |
| annex room 2 dark, zh | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_north-idle-pilot-annex-room2-dark-zh-h48_unapproved-v01_20261018-091242-c971ea02.png) `a8f3e555…49c7` | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-v8-reference-annex-room2-dark-zh-h48_unapproved-v01_20261018-091242-c971ea02.png) `abbe0076…a2fb` |
| annex room 2 dark, en | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_north-idle-pilot-annex-room2-dark-en-h48_unapproved-v01_20261018-091242-c971ea02.png) `c75fe686…9394` | [png](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-v8-reference-annex-room2-dark-en-h48_unapproved-v01_20261018-091242-c971ea02.png) `1e19df9e…2930` |

[Capture report JSON](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_north-idle-pilot-capture-report_unapproved-v01_20261018-091242-c971ea02.json): sha256-text-lf-v1 `9f61970d…e954`.

**Discarded first run (20261018-091206):** its v8 reference label overlapped the HUD hint line, so its 9 files were deleted and the run was redone with the label moved.

**Whole-figure CIELAB ΔE76** against the 8 px ring median and against the occluded backdrop pixel. This is a proxy, not a verdict. Both languages give identical figure numbers.

| Scene | Figure | Ring mean / p10 / min | Occluded mean / p10 |
| --- | --- | --- | --- |
| City bright | north | 42.52 / 29.30 / 4.55 | 48.08 / 26.56 |
| City bright | v8 | 42.36 / 22.52 / 4.84 | 45.57 / 20.30 |
| Annex dark | north | 25.32 / 10.99 / 7.40 | 25.61 / 10.99 |
| Annex dark | v8 (zh) | 27.28 / 11.10 / 7.74 | 27.36 / 12.65 |

- **In the city,** north separates at least as well as v8.
- **In the dark annex,** north's means are about 2 ΔE lower than v8's, because the back has no cream shirt.

## Technical self-assessment (the root judges actual 1x readability)

**What reads at 1x:**

- It reads as the same person seen from behind. The strongest cues are:
  - the side-falling high ponytail with a clear gap beside the head;
  - the teal bedroll overhanging the left shoulder;
  - the pack with the teal diamond;
  - the cream cuffs;
  - the teal tail on the right;
  - the brown boots.
- Head, shoulder and foot rows line up with v8 in the same framing.

**Weaknesses:**

- The pack is a large warm rectangle that dominates the back.
- The boots are blocky.
- The arms hang straight and symmetric, so the idle reads stiffer than v8's hip-hand pose.
- The back of the head is a broad dome with vertical lock texture.
- The collar shows only 2 rows.
- Overall the figure is darker and cooler than v8's front, because there is no shirt or face.
- The canister side and the arm pose are open identity calls (decisions 1–2).

## Limitations

- **Coverage:**
  - static north idle only, one position per scene, first-visit default state;
  - the scene's `_process` was disabled for capture;
  - no 1920×1080 sampling.
- **Shared working tree:** captures ran against it. `scifi_exploration_area.gd` and `survey_annex.gd` carry other sessions' uncommitted edits, which were read only and not modified. The `scifi.city` destination currently renders as Lower Manhattan · City Hall Park.
- **GUI save untested:** the `.pxo`/`.ora` were written by Python and verified through the official Pixelorama CLI. A GUI open-and-save round trip was not done.

## Not touched

- **Other workstreams:** the v8 PNG, manifest and `.pxo` sources; south run v07, Yonkers and Washington work; other sessions' dirty runtime scripts and scenes; battle files.
- **Shared tracking:** the Game Bible, ledger, readiness checklist and index; `docs/progress.md`.
- **Project side effects:** no Godot `--import` was run, so no `.import`/`.uid` files were created, and no game/ scene or script was changed.
- **Git and memory:** no git stage or commit; no personal memory writes.

## Reproduce

```
python -I -B tools/rpg-2-star-ocean-the-second_protagonist-female_north-idle-static-pilot-build-and-check_unapproved-v01_20261018-090713-9af15df7.py check
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game -s <absolute path of the capture .gd>
```
