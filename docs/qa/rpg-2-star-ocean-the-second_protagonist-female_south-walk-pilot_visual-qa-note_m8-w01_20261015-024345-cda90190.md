# Female south walk pilot w01: visual QA note

M8, 2026-10-14 (file stamps are UTC, 2026-10-15). This is an isolated, reviewable **south-facing walk pilot** for the female protagonist, built from the user-approved **static** selout v8 idle. The user approved v8 only as a static 48-logical-px visual baseline.

**Status: technical pilot for human review. It is not approved.**
- It is not wired into the runtime.
- No acceptance gate or counter changed: 0/52 exploration sprites and 0/11 scene gates.
- Nothing here is a user verdict. Every judgement below is Claude's technical observation.

## 1. Why earlier walk attempts failed (inspected first)

| Attempt | What went wrong (from its review doc and frames) |
| --- | --- |
| Generated 4-phase concept frames | The knee guard switched legs and the torso jumped about 4.3 logical px sideways between phases. |
| Whole-sprite procedural slide | Boots and arms never changed shape, so she slid like a rigid cut-out. |
| Segmented rig, auto masks | Rigid legs rotated about the hips: hard seams at the coat hem, static arms, feet still sliding. |
| it1 copied-texel bake | Only the boots moved, by dropping shin rows. The knee band changed **0 texels** in every frame. The contact pose was just the idle stance plus a bob, and stride separation equalled the idle stagger (3 rows). The arm fill showed as stripes. E8 slip: max 3.0, mean 2.84 px/tick. |
| E8 audit (RC1/RC3) | In a discrete flipbook the planted foot slides by the body speed on every held tick. The legs (about 32–35 rows) are too short to climb the 30–40 rows a fully planted foot would need. |

This pilot targets the art failures: knee motion, a distinct contact pose, real stride, foot shape changes, identity lock, no knee-guard swap, no lateral torso jump, and arm and cloth motion. It does **not** claim to beat the RC1 slip limit (see §5).

## 2. Method

[Build tool](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-build_m8-w01_20261015-024345-a2d747a5.py), Python 3.12.14 / Pillow 12.3.0 / NumPy 2.3.5, run with `-I`.

- **Source lock.** The tool refuses to run unless v8 hashes to `ccf9d2a2…68b6fd`.
- **Lossless layer split.** v8 is split into five layers by explicit texel-ownership rules:
  - torso: head, hair, face, coat, scarf/cape, teal flask, belt;
  - right forearm;
  - left fist;
  - viewer-left leg (with the knee guard);
  - viewer-right leg.

  A gate checks that re-stacking the untouched layers reproduces v8 texel-for-texel.
- **Hidden fills.** 25 torso texels and 11 leg texels were authored underneath the forearm, fist and hand, so a swing never opens a hole. They are covered in the idle stack, which the gate above proves.
- **Per-frame poses** use integer placements only:
  - the torso moves only by the bob (0/+1);
  - the thighs ride the hips;
  - the knee, shin and boot are ground-relative. The knee lifts over the thigh (foreshortening), rows are repeated or overlapped as whole rows, and the swing knee tucks 1 texel inward.
- **Boots.** v8's two boots are reused. Four foot poses were redrawn as palette-letter texel text: left forward, left heel-up, right set-back and right heel-up.
- **Arms and cloth.** The right forearm and the left fist swing opposite the legs. The cape tip lags by ±1 texel.
- **No shortcuts.** There is no resampling, filtering, generative redraw, flip or mirror. Every colour is one of v8's 32.

### Loop (8 frames, 10 fps review rate; vl = viewer-left leg with the knee guard)

| # | Frame | Bob | vl sole row | vr sole row | Intent |
| --- | --- | --- | --- | --- | --- |
| 1 | f01-contact-vr | +1 | 99 (heel-up) | **104** | vr heel-strike forward; vl pushes off; fist forward, right forearm back |
| 2 | f02-down-vr | +1 | 98 | 103 | weight on vr; vl toe-off, knee bends and tucks |
| 3 | f03-passing-vr | 0 | 99 (lifted) | 103 | vr straight; vl knee lifted 2, tucked 1 |
| 4 | f04-up-vr | 0 | 103 | 102 | vr late stance; vl reaching forward |
| 5 | f05-contact-vl | +1 | **104** | 98 (heel-up) | mirror *pose*, redrawn, not flipped |
| 6 | f06-down-vl | +1 | 103 | 98 | |
| 7 | f07-passing-vl | 0 | 103 | 99 (lifted) | |
| 8 | f08-up-vl | 0 | 102 | 103 | |

**Ground anchor.** One cell pin, (40,104), is used for every frame; the ground line is row 103.
- Contact frames step the front foot 1 row toward the camera (row 104).
- The pin itself never moves per frame.

## 3. Files (all new)

**Frames, 80×112 RGBA, one PNG each**, in `game/assets/characters/walk-pilots/`. The folder has a `.gdignore`, so Godot never imports these files and creates no `.import` entries.

| Frame | File |
| --- | --- |
| f01 | `…south-walk-pilot-f01-contact-vr_m8-w01_20261015-024345-6f8a0aba.png` |
| f02 | `…-f02-down-vr_…-dd9c8254.png` |
| f03 | `…-f03-passing-vr_…-946d8b8b.png` |
| f04 | `…-f04-up-vr_…-609ca364.png` |
| f05 | `…-f05-contact-vl_…-81795ce8.png` |
| f06 | `…-f06-down-vl_…-556ea1f8.png` |
| f07 | `…-f07-passing-vl_…-918cf8be.png` |
| f08 | `…-f08-up-vl_…-00984cc2.png` |

**Same folder:**
- [manifest](../../game/assets/characters/walk-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-manifest_m8-w01_20261015-024345-e80ccf73.json) (`c07853b7…`). It records poses, declared soles, SHA-256 values and the added-files list.
- editable [Pixelorama project](../../game/assets/characters/walk-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-editable_m8-w01_20261015-024345-47dd9eba.pxo) (`2bb379cf…`): `pxo_version 7`, 8 frames × 5 layers (`leg-vl`, `leg-vr`, `torso`, `arm-right-forearm`, `arm-left-fist`).

**Godot harness** (isolated): [`.gd`](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-capture_m8-w01_20261015-024345-12396bd7.gd) and [`.tscn`](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-capture_m8-w01_20261015-024345-cc39963c.tscn).

**Media and slip tool:** [`…review-media-and-slip…-eb55a880.py`](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-review-media-and-slip_m8-w01_20261015-024345-eb55a880.py).

**Review evidence in `outputs/`.** Godot run `20261015-025033-37461356`, plus the checks file `…-446c4431`:
- **Stills, 18 separate 1280×720 PNGs:** for both `city-bright` and `outskirts-bright`, each frame f01–f08 plus a `v8-idle-reference` at the identical pin. For example, [city f05](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-walk-pilot-f05-contact-vl-h48_m8-w01_20261015-025033-37461356.png) and [outskirts f01](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-walk-pilot-f01-contact-vr-h48_m8-w01_20261015-025033-37461356.png).
- **Motion stills:** 6 PNGs from the walking run, at ticks 24, 48 and 72 per area.
- **Motion clips:**
  - [city MP4](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-walk-pilot-motion-video_m8-w01_20261015-025033-37461356.mp4) and [outskirts MP4](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-walk-pilot-motion-video_m8-w01_20261015-025033-37461356.mp4): 60 fps, a 2× nearest crop, with the walk played 3×;
  - [city motion GIF](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-walk-pilot-motion-gif_m8-w01_20261015-025033-37461356.gif) and [outskirts motion GIF](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-walk-pilot-motion-gif_m8-w01_20261015-025033-37461356.gif), in real time;
  - [in-place loop GIF](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-walk-pilot-in-place-loop-gif_m8-w01_20261015-025033-37461356.gif): the 8 city stills at 3× and 10 fps, for judging the cycle alone.
- **Reports:**
  - [capture receipt](../../outputs/rpg-2-star-ocean-the-second_city-outskirts_protagonist-female-south-walk-pilot-capture-receipt_m8-w01_20261015-025033-37461356.json) (`d217b308…`);
  - [slip and media report](../../outputs/rpg-2-star-ocean-the-second_city-outskirts_protagonist-female-south-walk-pilot-slip-and-media_m8-w01_20261015-025033-37461356.json) (`399d4bdd…`);
  - [frame checks](../../outputs/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-frame-checks_m8-w01_20261015-024345-446c4431.json) (`bd75f42c…`).

GIF and MP4 are lossy review aids. The PNGs are the colour-exact evidence.

## 4. Test results

**Build gates.**
- The v8 SHA-256 lock passed.
- The lossless layer re-stack equals v8 for all 2,419 texels.
- The leg layers overlap in no frame, so the fixed `.pxo` layer order is exact.
- **Determinism:** two builds into separate scratch folders were byte-identical for 10/10 files.

**PNG-level checks.** These read only the PNGs on disk.

| Check | Result (all 8 frames) |
| --- | --- |
| Cell, alpha | 80×112; alpha ∈ {0, 255}; 0 opaque texels on the border |
| Palette | 32 colours; **0** outside v8's palette |
| Identity lock | Bob found by exact search of the head rows 8–33: +1/0 as declared. Locked upper body (rows 8–52, minus the forearm and fist boxes) vs v8 + bob: **0** mismatched texels |
| Height / anchor | Visible height 95–96 (v8: 96); lowest row 103, or 104 on the two contact frames |
| Knee guard | 36 guard-colour texels, centroid x < 40, on the viewer-left leg in **8/8** (no leg swap) |
| Cape / scarf tail | Centroid x 17.9–18.6, always viewer-left |
| Knee-band motion (rows 73–83 vs bob-shifted idle) | **49–100 changed texels** per frame (it1: 0) |
| Stride separation, contact | **5** (f01) and **6** (f05) rows (it1 and idle: 3) |
| Leg gap (rows 80–100) | 21/21 in every frame |
| Uniqueness | 8 unique frames; none equals v8 |

**Godot 4.7.2, real windowed run.** The scenes are the science city and the outskirts, in default first-visit state: 640×360 canvas_items at 1280×720, scale 0.5, nearest filtering, no shadow. The harness uses v8's placement, but with one fixed pin for every frame.
- **Fidelity:** every opaque texel was shown with exact RGB at the expected window pixel:
  - all 8 frames in both areas, plus the v8 reference;
  - every 12th motion tick.
- The run exited 0.

**Pixelorama 1.2.3 round trip.** The staged free Windows build's own CLI exporter (`--headless … --export`) opened the `.pxo` and reported 80×112, 8 frames. Its 8 exported PNGs match the frame PNGs: alpha masks are equal, opaque RGB is equal, and there is 0 partial alpha. The project was **not** opened in the Pixelorama GUI.

## 5. Known flaws (honest)

1. **The feet still slide. This is not solved.**
   - The motion run walks straight south at 60 logical px/s, with frames chosen by distance: 6 px per frame, a 48 px cycle, 2.5 steps/s.
   - Over each declared stance, the planted foot rises only 2 texels in the cell while the body travels 46 screen px, so it slides about **44 screen px per stance**.
   - E8-style per-tick drift: max 2.0, mean 1.91, with **84/92** compared ticks over 1 px.
   - This is the RC1/RC3 flipbook limit. Alternating steps make it read as walking, not gliding, but a planted foot is not achieved. It was not tested at the runtime's 140 px/s time-driven stepping, where it would be worse.
2. **Upper thighs barely move.** Thigh motion is limited to bob, overlap and 1–2 row stretches. The right leg keeps v8's outward splay in every frame, so the gait looks slightly wide.
3. **Some stretching is mechanical.** Shin and thigh length changes are whole-row repeats or overlaps of v8 texels, so stripe shading repeats over 1–2 rows.
4. **The redrawn boots are rough.** They were authored by Claude as texel text, not by a human pixel artist. The left forward boot (19 rows) is visibly larger than v8's left boot (16 rows); this is meant as a toward-camera foot, but it may read as a size change.
5. **The arm motion is minimal.**
   - The fist moves only ±1 row.
   - The right forearm moves −2…+1 rows, plus 1 px inward.
   - There is no elbow bend and no redrawn forearm foreshortening.
6. **The cloth motion is partial.**
   - The cape tip shifts ±1 texel on rows 67–74, which leaves a 1-px jog in the outline at row 66/67.
   - The right coat flap and the left coat hem do not react.
7. **f04/f08 look like "feet together".** Both soles are within 1 row of each other.
8. **36 hidden fill texels are invented content** (sleeve, flask bottom, cape, outer thigh). They are visible only during swings.
9. **Limited scope:**
   - south only;
   - one walk speed;
   - first-visit area state;
   - no shadow;
   - the dark annex was not captured.

## 6. Unchanged

- **v8:** the PNG is still `ccf9d2a2…68b6fd`, the manifest still `0fa7937d…`, and no tracked file in `pixelorama-pilots/` has a diff.
- **Runtime:** 0 references to the pilot in `game/scripts` or `game/scenes`; no `.import` files and no `.godot/imported` entries for the pilot.
- **Docs and data:** the Game Bible, `docs/progress.md`, the readiness checklist (md, json and script) and `battle_arena.gd` were not edited by this work.
- **Concurrent edits.** Another session modified several of those tracked files during this work and committed `ff8acd8`; those changes are not part of this pilot.
- **Outside the repo:** running the Pixelorama CLI may have written its own settings under the user's AppData.
- No acceptance flag or counter changed. No Git commit or push was made.

## 7. Reproduce (repository root)

```
python -I tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-build_m8-w01_20261015-024345-a2d747a5.py --out-dir <scratch>
python -I tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-build_m8-w01_20261015-024345-a2d747a5.py --check game/assets/characters/walk-pilots
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-capture_m8-w01_20261015-024345-cc39963c.tscn -- --motion-dir=<abs scratch dir>
python -I tools/rpg-2-star-ocean-the-second_protagonist-female_south-walk-pilot-review-media-and-slip_m8-w01_20261015-024345-eb55a880.py --receipt outputs/<receipt>.json --motion-dir <abs scratch dir>
```

- `--out-dir` reproduces the frames, `.pxo` and manifest byte-for-byte.
- `--write` refuses to overwrite different bytes.
- Each Godot run writes new captures with a fresh stamp and ID.

**Rollback.** Delete these and nothing else:
- the folder `game/assets/characters/walk-pilots/`;
- the two `game/tests/…south-walk-pilot-capture…` files;
- the two `tools/…south-walk-pilot…` scripts;
- this note;
- the `outputs/` files stamped `20261015-025033-37461356` (31 files) and `…-446c4431`.
