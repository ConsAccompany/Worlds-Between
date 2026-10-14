# Female protagonist · south walk · E8 contact-failure audit and hand-drawn Pixelorama pilot plan · M8 v01

**Status: read-only technical audit plus a team pilot plan. No walk frame is drawn and no art is accepted.** This audit created no art, code, tests, registry entries, manifests, progress entries or Game Bible text, and touched nothing in Git. This file is the only file it wrote in the repository. Acceptance is unchanged: **0/52** exploration sprites and **0/11** scene-quality gates. No acceptance flag, E-metric definition or counter changes here.

> **Decision update, 2026-10-14 (added after the audit; the rest of the audit text is unchanged except where it is marked "Decision update").** The user answered D1: **neither**. They rejected both female south static idle candidates, **Box** and **Lanczos**, as not polished enough, and asked the team to keep refining the **static** south idle frame first.
>
> - **Walk-frame production is paused.** The §5 hand-drawn pilot does **not** start, and no walk frame of any kind is to be made, until the user approves a new static south idle.
> - **Historical measurements are kept.** §2 and §3 measured the it1 bake and the Box/Lanczos masters. They stay as they were, as a record of what was measured. They do not describe the new idle.
> - **RC1 still applies.** It depends only on the harness display model, not on any artwork. The geometry-based figures (sole row 103, the 48-colour palette, the §5.3 zone rectangles, the knee-guard rect, the §6 "Before" column and the §8 master SHA-256 values) were measured on the rejected masters. They must be re-measured on the new approved idle before §5–§8 can be used.
> - **Nothing else changed.** No art file was edited, no walk frame was started, and acceptance stays **0/52** exploration sprites and **0/11** scene-quality gates. E8's definition is unchanged, and so are the D2–D6 team choices.

Decisions already made by the user:

- **48 logical px** display height (approved).
- A free, one-direction Pixelorama pilot, and MVP development generally (authorized; walk frames not yet started).
- **Decision update:** idle baseline D1 = **neither** (2026-10-14). Box and Lanczos are both rejected as not polished enough. The static idle is refined first, and walk frames are paused until a new static idle is approved.

Under that authorization the team makes the pilot's working choices itself: which Pixelorama build to use, the walk frame count, the harness speed, the pilot contact gate and a new isolated test (§4).

Only two things need the user's input:

- the idle baseline: **Box**, **Lanczos** or **neither**. **Decision update: answered "neither" on 2026-10-14.** The user must now approve a new static south idle before the walk pilot can start;
- final art acceptance (E10).

Not changed by this plan: the runtime walk speed (memo R2, which stays open and is not needed for the pilot) and the definition of E8.

No `AGENTS.md` exists anywhere in the repository (searched to depth 3, excluding `.git`).

Labels used below:

- **[V]** Verified: measured or read directly from repository files during this audit.
- **[D]** Derived: arithmetic or geometric deduction from [V] items.
- **[R]** Recommendation: a team plan item within the existing authorization. It needs the user's input only where §4 says so.

## 1. Inputs read

| Input | Path |
|---|---|
| Progress | `docs/progress.md` (entries "Female south-idle Pixelorama technical pilot" and "Quantized pilot cross-area check and segmented south walk experiment") |
| E1–E9 feasibility review | `docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_south-segmented-walk-feasibility-review_m8-e1e9-it1_20261014-215849-769085fe.md` |
| Bake script | `tools/rpg-2-star-ocean-the-second_protagonist-female_south-segmented-walk-bake_m8-e1e9-v01_20261014-215052-c82448bd.py` |
| Isolated E8/E9 Godot test | `game/tests/rpg-2-star-ocean-the-second_protagonist-female_segwalk-e8e9-test_m8-it1_20261014-215052-0151f713.gd` (+ `…-a9ea58a4.tscn`) |
| Art pipeline memo | `docs/character-visuals/rpg-2-star-ocean-the-second_character-visuals_art-pipeline-decision-memo_m8-v01_20261014-165532-0cc81856.md` |
| Pixelorama setup note | `docs/character-visuals/rpg-2-star-ocean-the-second_protagonist-female_pixelorama-south-pilot-setup_m8-v01_20261014-170109-dd62c262.md` |
| Intake checklist (frame-count rule) | `docs/character-visuals/rpg-2-star-ocean-the-second_character-visuals_asset-intake-checklist_m8-design_20261014-162946-c4e7a19d.md` |
| Experiment evidence (it1) | `outputs/rpg-2-star-ocean-the-second_segwalk-e1e9_m8_20261014-215052-5ab7af12/`: pose table `…south-pose-table_m8-e1e9_20261014-215052-cae11b49.json`, metrics `…south-metrics_m8-it1_20261014-215052-d8752834.json`, Godot motion receipt `…south-godot-motion-receipt_m8-it1_20261014-215052-053da815.json`, nine frame PNGs `…south-frame-0N-…png` |
| Baseline candidates | `game/assets/characters/pixelorama-pilots/…south-idle-boxquant-pilot_m8-v01_20261014-212322-7c30d48c.png` and `…south-idle-lanczosquant-pilot_m8-v01_20261014-212322-b9fd58f7.png`, with the quantized-downscale manifest `…-aa446773.json` |
| Runtime motion (read only) | `game/scripts/scifi_exploration_area.gd`, `game/scripts/survey_annex.gd`, `game/scripts/character_directional_motion.gd` |

## 2. Verified measurements

All values were read from the files above, or computed in memory from them, with the project's Codex-runtime Python (Pillow and NumPy, `-I` isolated mode). The few scratch files I wrote went to the system temp folder, outside the repository.

### 2.1 Harness parameters [V]

Source: test `.gd` lines 16–22 and 163–175, and the pose table `pilot_motion` block.

| Parameter | Value |
|---|---|
| Speed | 90 logical px/s, fixed 60 Hz physics tick |
| Scale | `Sprite2D` scale 0.5 inside a 640×360 `canvas_items` view shown at 1280×720, so **1 texel = 1 screen px** and 1 logical px = 2 screen px |
| Body travel per tick | **3.0 screen px** |
| Frame stepping | Distance-driven: phase = ⌊distance / 5⌋ mod 8 + 1. Phase advance = 5 logical px = 10 screen px, which is 3.33 ticks per frame. |
| Gait | Cycle 40 logical px, step 20 logical px |
| Sprite movement | The sprite position is updated **every tick** (`_sprite.position = MOTION_START + Vector2(0, distance)`) |
| E8 rule | Stance-foot screen displacement between consecutive ticks with the same stance leg must be ≤ 1 px. Ticks where the stance leg switches are skipped. |

### 2.2 E8 tick decomposition [V]

Source: motion receipt `tick_log`, 161 ticks, distance 0–240 logical px.

| Tick class | Count | Drift per tick (screen px) |
|---|---|---|
| Held frame (same phase as the previous tick) | **112** | **3.0 on every one** |
| Same-stance frame change 1→2, 3→4, 5→6, 7→8 | 24 | 2.0 (the stance foot rises 1 texel in the cell) |
| Same-stance frame change 2→3, 6→7 | 12 | 3.0 (the stance foot rises 0 texels) |
| Stance-leg switch 4→5, 8→1 (skipped by E8) | 12 | not compared (the foot reference jumps 5 px) |
| **Total compared** | **148** | max **3.0**, mean **2.838**; **148/148** over 1 px |

Frame holds: 32 runs of 3 ticks and 15 runs of 4 ticks. The bake's analytic cross-check (metrics JSON `e8_analytic_cross_check`) agrees: max 3.0, mean 2.84.

### 2.3 Stance foot in the cell [V]

Source: metrics `per_frame.contact_points`; the pose table. Lowest opaque row of the stance foot, contact → down → passing → up:

| Leg | Rows | Rise in cell | Lateral x midpoint |
|---|---|---|---|
| `leg_vl` | 104, 103, 103, 102 | **2 texels** | 28 in all frames |
| `leg_vr` | 104, 103, 103, 102 | **2 texels** | 52 in all frames |

- Body travel from the first to the last stance frame is **30 screen px**. Over the whole stance, including the hand-off, it is 40 screen px.
- Contact frames 01 and 05 put the stance foot's lowest row at **104**. That is one row below the idle's lowest row, **103** (= ground pin y − 1), because the body bob is applied to the stance leg too.
- Stride separation at contact (front foot row minus back foot row) is **3 texels** in both contact frames: 104 vs 101. The idle already has a 3-texel stagger: `leg_vl` 100, `leg_vr` 103.

### 2.4 Which texels actually move [V]

Comparison is against the idle shifted by each frame's declared bob. The arm redraw zone (§5.3) is excluded.

| Region | Result |
|---|---|
| Knee band: rows 73–83 (+bob), x 23–60 | **0 changed texels in all 8 walk frames.** Knees, thighs and the knee guard never move. |
| Topmost changed leg row, frames 03, 04, 06, 07 | 86–87, i.e. the shin and boot only |
| Frames 01, 02, 08 | Changes reach rows 73–75, but only where the moved `arm_vr` overlaps the leg columns (arm offset bob + `arm_vr_dy` = 2) |
| Frame 05 (contact-vr), rows ≥ 73 | **Identical** to the idle shifted down 1. That contact pose is the idle's own leg stagger. |
| Locked zone: rows < 73 outside the arm zone | 0 differing texels in frames 01–03 and 07–08. 8 in frames 04–06, all from `arm_vr` moving 1 row above its mask rect. |

### 2.5 Leg geometry of the idle masters [V]

- **Box vs Lanczos.** Both are 80×112, 48 colours, 0 partial-alpha texels, with the same opaque bounding box (13,8)–(57,103). They differ in RGBA at **2,536** texels, but their opaque masks differ at only **11** texels. The silhouette and leg geometry below therefore apply to both.
- **Leg extent (Lanczos).** The two legs first separate at row 69 (a transparent gap opens at x 36). `leg_vl` spans x 25–36 down to its sole at row 100. `leg_vr` spans x 40–55 down to its sole at row 103. That makes the visible legs **about 32–35 rows** long, from the point where they separate to the soles. The coat hem and leg mask rules start at row 73. The knee guard is 28 texels inside rect [26,75,30,81].

### 2.6 Runtime motion, for context only (no change proposed here) [V]

- `MOVE_SPEED := 140.0` logical px/s at `game/scripts/scifi_exploration_area.gd:10` and `game/scripts/survey_annex.gd:21`.
- Walk phases are **time-driven**: `floor(walk_time / 0.12) % 4 + 1` in `_process(delta)` (`scifi_exploration_area.gd:324–330`), not distance-driven. The isolated test's distance-driven stepping is therefore not what the runtime does today.

### 2.7 Readability proxies on the it1 frames ("before") [V]

- **Leg gap.** Rows 80–100 where a transparent texel separates the two legs inside x 36–44: idle **21/21**, walk frames **19–21/21**.
- **Edge contrast.** For opaque texels with at least one transparent 4-neighbour, the share whose Rec.709 luma differs from the ground by at least 40:
  - light ground RGB (185,165,136): idle **0.986**, walk **0.986**;
  - dark ground RGB (35,38,44): idle **0.092**, walk **0.093–0.103**.

  The dark-ground figure is a property of the dark outline already in the master, not of the walk. It is a proxy number, not a visual verdict.

## 3. Why E8 failed: root causes

**RC1. In this discrete-flipbook harness at 90 logical px/s, E8 as written cannot be met by any artwork. [D]**

Scope: this is a hard limit of the it1 display model, which has three properties [V §2.1]:

- a discrete flipbook with a few held frames per cycle;
- distance-driven frame stepping;
- a sprite position moved continuously, by 3 screen px every tick.

It is **not** a claim about all possible animation systems.

On a held tick, the drawn image does not change but the sprite moves 3 screen px, so the stance foot moves exactly 3 px. This holds for 112 of the 148 compared ticks [V §2.2], and **no artwork shown through this harness can change those ticks**: copied-texel, hand-drawn, or anything else.

Within this model, per-tick drift ≤ 1 px needs either:

- body travel per tick ≤ 1 screen px, which means a speed of **≤ 30 logical px/s**; or
- a new frame on every tick, which at 90 logical px/s and a 40 logical px cycle means **≥ 27 frames per cycle**.

Neither fits the R2 speed options: (a) 140 px/s or (b) 80–100 px/s. Only 90 px/s was measured; the other speeds are arithmetic.

Other display models could reduce held-tick drift. Examples are contact-locked stepped positioning (D2 option c), separately animated limbs or a skeletal rig, or many more frames. None of these was built or measured here, and each is a code or pipeline change outside this pilot.

**Consequence:** a hand-drawn 4-frame pilot measured in an equivalent harness with E8 exactly as written is **predicted to fail with max drift 3.0**, whatever its quality. Each frame is held for about 6.7 ticks, so about 5–6 of every 6–7 ticks are held at 3.0. The feasibility review's explanation ("a held frame cannot move a foot inside the cell") is correct, but it does not say that this part is independent of the art method.

**RC2. Copied-texel row drops cannot move the foot far enough. [V/D]**

The stance foot rises only 2 texels per stance [V §2.3], against 30 px of body travel. The shin band is 11–12 rows, and dropping more rows collapses the boot shaft (feasibility review). This is the art-method limit the review identified.

**RC3. In this harness, a fully planted foot is not reachable by in-cell redrawing at a 20 logical px step, even when drawn by hand. [D]**

On screen, the world moves 1:1 in y. To stay planted while the sprite moves continuously, the stance foot would have to climb about 30–40 rows in the cell during one stance. The visible legs are only about 32–35 rows long [V §2.5], so the planted sole would have to reach the coat hem.

Partial rise is therefore the realistic target for this pilot. The remaining slip per stance is about (40 − rise) screen px under this display model. This is an estimate from the it1 geometry, not a measurement of hand-drawn frames, and it does not cover the alternative display models listed under RC1.

**RC4. The motion content is thin, separately from contact. [V]**

- Only shins and boots change; the knee band changes 0 texels [V §2.4].
- Contact-vr equals the idle shifted by the bob.
- The stride separation of 3 texels equals the idle's stagger.
- Contact frames sink 1 row below the idle sole line.

**Not causes. [V/D]**

- Display: E9 passed with 1 texel = 1 px, 0 fractional origins and 0 colour mismatches.
- Registration: E3 passed.
- Baseline choice: Box and Lanczos masks differ at 11 texels, so RC1–RC3 hold for either.

## 4. Decisions for the walk pilot

### 4.1 User input needed

| # | Decision | Options | Audit position |
|---|---|---|---|
| D1 | Idle baseline | Box · Lanczos · neither | **Decision update, 2026-10-14: neither.** Box and Lanczos are both rejected as not polished enough. This walk plan does **not** start, and walk-frame production is paused. A new static idle master must be refined and approved by the user first, which is outside this plan. Still blocking. |
| E10 | Final art acceptance | User review | The user's call alone (§6). No pilot gate result counts as art acceptance. |

### 4.2 Team choices under the existing authorization

These are taken by the team and logged in the pilot manifest. They need no further user approval. The team may revise them, logging the reason.

| # | Choice | Options considered | Team choice |
|---|---|---|---|
| D2 | Pilot contact gate for south | (a) gate on E8 as written, which is predicted to fail in this harness (RC1); (b) gate on the south contact criteria K1–K5 (§6) and report E8 unchanged; (c) contact-locked stepped rendering, a code change whose body judder was not measured; (d) a speed ≤ 30 logical px/s | **(b).** K1–K5 is the practical pilot contact gate. E8 keeps its definition and its raw value is reported every run (K6). This plan does **not** change E8. |
| D3 | Harness speed for before/after | 90 logical px/s (same as it1) | **90 logical px/s**, for comparability only. It is not a runtime decision; R2 stays open. |
| D4 | Pixelorama build | v1.2.3 web build (used for the idle pilot; free) · staged Windows build (`work/tooling/pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe`, **unsigned**) | **Web build**, matching the idle pilot. |
| D5 | Walk frame count | 4 · 8 (feasibility-review pilot proposal) | **4** for this pilot. Going to 8 is a later team step, logged as a new pilot iteration (§6 F1). |
| D6 | After-test harness | Edit the it1 test · new isolated test | **New isolated test** (§7). The it1 test is left untouched. |

## 5. Recommended pilot plan for a human artist [R]

### 5.1 Scope

- Female protagonist, **south only**.
- **1 idle** (the chosen baseline, reused byte-identical) plus **4 hand-drawn walk frames**.
- No other direction, character or animation.
- No AI pixels.
- No horizontal flip or mirror of any frame or layer. The costume is asymmetric (knee guard and scarf tail on viewer-left, ponytail tuft), and mirroring is the failure mode recorded in feasibility C1.

### 5.2 Frames to draw

These describe body poses, not pixels. vl = viewer-left = the character's right, the leg with the knee guard.

| Frame | Name | Stance foot | Pose intent |
|---|---|---|---|
| W1 | contact-vl | vl | The vl foot is planted ahead, 1–3 rows below the idle sole line. The vr foot is behind and higher (≥ 4 rows above the vl sole). The vr arm swings forward and down. Body bob 0–1. |
| W2 | passing-vl | vl | The vl sole is on the idle sole line (row 103), under the body. The vr knee lifts, so the knee band visibly changes. The vr foot is raised and tucked toward the centre line. Body bob up, −1 to 0, relative to W1. |
| W3 | contact-vr | vr | Mirror the *pose* of W1 by redrawing, never by flipping: vr planted ahead, vl behind and higher. The knee guard stays on vl. The vr arm swings back. |
| W4 | passing-vr | vr | Mirror the *pose* of W2 by redrawing: the vl knee lifts, and the knee guard foreshortens but stays visible on vl. |

The idle (frame 0) is **not redrawn**.

The viewer-left hand gripping the strap may stay static, as in the master. Whether that reads well is part of E10.

### 5.3 Zones

Coordinates are in the 80×112 cell. They apply to whichever baseline the user picks in D1. **Decision update:** these rectangles were measured on the rejected Box/Lanczos masters. Re-measure them on the new approved static idle before use.

| Zone | Definition | Rule |
|---|---|---|
| **Locked zone L** | All texels with y < 73, except the arm zone | Must equal the baseline master moved by the frame's declared integer bob (dx = 0, dy ∈ {0, 1, 2}). Zero differing texels. |
| **Arm zone A** | x 45–60, y 49–76: the `arm_vr` mask rect [49,53,56,72] grown by 4 texels | May be redrawn for the arm swing. Fill exposed coat behind the arm using master colours only. |
| **Redraw zone R** | y ≥ 73, full width (legs, lower coat hem, scarf-tail tip, boots) | May be redrawn by hand. |

If the artist needs more room, enlarging A or R is a team scope change, logged in the manifest with the new rect. It is never a silent edit.

### 5.4 Pixelorama setup

These steps assume Pixelorama v1.2.3 features; the artist should confirm each one in the tool.

1. Open a **new** project of 80×112 with 5 frames (frame 0 = idle, frames 1–4 = W1–W4). Save it under a **new unique name**; never overwrite the existing `.pxo` files.
2. Build the palette from the chosen master's 48 opaque colours, and use only those colours. Use a pencil with no anti-aliasing, alpha 255 only, and no blur, smudge or soft brushes.
3. Use these layers, back to front:

   | Layer | Contents |
   |---|---|
   | `master-locked` | The baseline master with zones R and A erased. Each frame's cel is moved by its bob with arrow-key whole-texel moves. |
   | `legs` | The redrawn legs, boots, hem and scarf tip |
   | `kneeguard` | Only the knee-guard texels, in master colours |
   | `arm-vr` | The redrawn swinging arm and any coat fill behind it |
   | `notes` | Hidden; never exported |

4. Use onion skinning against frame 0 and the neighbouring frames for spacing.
5. Export each frame as a **separate PNG**: no sprite sheet, atlas or contact sheet.
6. Also export the `kneeguard` layer alone for each walk frame, as separate PNGs, so ownership can be checked without guessing colours.

### 5.5 Files and naming

The new files go in `game/assets/characters/pixelorama-pilots/`, following the idle-pilot precedent, with **no `.import` entry and no runtime reference**. Names follow the project pattern, for example:

`rpg-2-star-ocean-the-second_protagonist-female_south-walk-handdrawn-pilot-w1-contact-vl_m8-v01_<stamp>-<8hex>.png`

Files to produce:

- one `.pxo`;
- 4 walk PNGs and 4 knee-guard PNGs;
- one pilot manifest JSON with:
  - baseline path and SHA-256;
  - `frame_counts: {"idle": {"south": 1}, "walk": {"south": 4}}` (intake checklist §3);
  - cell, ground pin and scale, each declared once;
  - per-frame bob;
  - the artist's time log;
  - the list of every file the pilot added, which the rollback uses.

### 5.6 Time box

Record the actual hours. [R] Time box: **≤ 6 artist-hours** for W1–W4 plus the exports. This is an estimate scaled down from the memo's method-A range of 3.25–6.5 person-days for a whole gate character.

## 6. Objective acceptance criteria (pilot gate only, not asset acceptance) [R]

"Before" is the it1 segmented bake, measured as in §2. A pilot "pass" means only that the frames go to the user's E10 review. It does not change 0/52 or 0/11.

| ID | Criterion | How it is measured | Before (it1) | Pass |
|---|---|---|---|---|
| **F1** Frame count | Exactly 4 walk PNGs and 4 knee-guard PNGs, plus the unchanged idle. The manifest declares `walk.south = 4`. No two walk PNGs are byte-identical, and none equals the idle. | File listing, SHA-256, manifest | 8 walk frames; contact-vr legs = idle + bob | All true. Going to 8 is a new, logged pilot iteration. |
| **S1** Locked identity | Zone L equals the master moved by the declared bob | Exact per-texel comparison | 0 diffs in 5 frames, 8 in 3 (arm overflow) | **0 differing texels in all 4** |
| **S2** Palette and alpha | Opaque RGB is a subset of the master's 48 colours; alpha ∈ {0, 255}; no opaque texel on the cell border | PNG scan | Pass | 0 new colours · 0 partial alpha · 0 border texels |
| **S3** Cell and height | 80×112; visible height within idle −3…+1 (idle = 96) | Alpha bounds | 94–96 | All 4 within |
| **S4** Ownership | Every `kneeguard` export is non-empty, has 20–36 texels (idle: 28) and centroid x < 40. Every knee-guard texel is also opaque and the same colour in the composite frame. | Separate knee-guard PNGs | 28 texels on vl in 9/9 | 4/4 |
| **S5** Provenance | No AI pixels; no flip or mirror; every PNG traced to the `.pxo` in the manifest | Artist declaration, manifest, `.pxo` layer list | N/A | Declared and consistent |
| **K1** Contact plant | In each contact frame (W1, W3), the stance foot's lowest opaque row ∈ [104, 106]: ahead of the pin by 1–3 rows | Lowest row of the stance-leg span (§7 checker) | 104 | Both within |
| **K2** Passing on ground | In each passing frame (W2, W4), the stance foot's lowest row = 103 (idle sole line): no float, no sink | Same | 103 | Both exactly 103 |
| **K3** Stride separation | In each contact frame, the back foot's lowest row ≤ front foot row − 4 | Same | **3** | ≥ 4 in both |
| **K4** No lateral skate | The stance foot's x midpoint changes ≤ 1 texel from contact to passing | Same | 0 | ≤ 1 |
| **K5** Alternation | The lowest (front) foot is vl in W1 and vr in W3 | Same | Pass | Pass |
| **K6** E8 as written (raw value reported, not gated; D2 = b) | Per-tick stance drift at 90 logical px/s | Godot motion run (§7) | max 3.0, mean 2.838, 148/148 over | Reported unchanged, with its pass/fail flag. Predicted ≈ 3.0 max in this harness (RC1). |
| **R1** Knee motion | In each passing frame, ≥ 10 texels change in the knee band (rows 73–83 + bob, x 23–60, excluding zone A) compared with the bob-shifted idle | Per-texel comparison | **0 in all frames** | ≥ 10 in W2 and W4 |
| **R2** Leg separation | Rows 80–100 with a transparent texel between the legs (x 36–44) | Row scan | 19–21 / 21 | ≥ 16 / 21 in each frame |
| **R3** Edge contrast | Share of edge texels with luma difference ≥ 40 on the light and dark test grounds | §2.7 method | Light 0.986 / dark 0.093–0.103 (idle 0.986 / 0.092) | ≥ idle − 0.02 on both grounds |
| **R4** Display | 1 texel = 1 screen px; 0 fractional origins; 0 colour mismatches on all stills and motion samples | Godot (§7) | Pass (E9) | Pass |
| **E10** User review | Compare against the approved 48 px screenshot, the it1 AVI and the v02 four-phase baseline | User | Not done | User's call alone |

A note on the K thresholds: ≥ 4 rows of separation is about 12% of the visible leg length [V §2.5], and is one row more than the idle's own stagger. It is a starting point the team may tune, logging the change. It is not derived from an approved standard. K1–K5 measure contact pose in the cell; they do not measure on-screen foot slip, which E8 (K6) still reports.

## 7. The before/after test [R]

**Before (already on disk; do not regenerate):**

- Godot E8/E9 receipts: `outputs/rpg-2-star-ocean-the-second_segwalk-e1e9_m8_20261014-215052-5ab7af12/…south-godot-motion-receipt_m8-it1_…-053da815.json` and `…south-godot-stills-receipt_m8-it1_…-231c0e6d.json`.
- PNG-level values for F1, S1–S4, K1–K5 and R1–R3: the "Before" column of §6, computed from the nine it1 frame PNGs in that folder.

**After.** The existing test hardcodes the it1 manifest name and `% 8` (test `.gd` lines 11 and 168), so it cannot be pointed at a 4-frame set unchanged. The team builds a new isolated test under the existing authorization (D6) and leaves the it1 test untouched.

1. **New** isolated test files, uniquely named under `game/tests/`, copied from the it1 test with only these changes:
   - manifest = the hand-drawn pilot manifest;
   - frame count 4 (phase = ⌊distance / 10⌋ mod 4 + 1, keeping the 40 logical px cycle);
   - `MOTION_SAMPLE_TICKS` picked to land one sample in each of the 4 frames.

   Everything else stays **identical**:
   - Godot 4.7.2 (`work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe`), run windowed;
   - `--fixed-fps 60`;
   - 90 logical px/s, straight south path, 161 ticks;
   - scale 0.5, pin (40,104), nearest filter;
   - 640×360 `canvas_items` at 1280×720;
   - the same light and dark ground colours.

   Run it twice, in two separate runs: `-- --mode=stills` (10 stills: 5 frames × 2 grounds), then `--write-movie <abs .avi> -- --mode=motion`.
2. **New** Python checker, run with `python -I`, that reads only the exported PNGs, the knee-guard PNGs, the baseline master and the manifest, and writes one metrics JSON with F1, S1–S5, K1–K5 and R1–R3. It must run **unchanged against the it1 frames as well**, so the "Before" column is reproduced by the same code. Mapping for it1: contact frames are 01/05, passing frames are 03/07, and the it1 stance tags are taken from its pose table.
3. Output: a before/after table with identical field names. A pass requires every gate in §6 except K6 and E10 to pass. K6 (E8 as written) is reported with its raw values and pass/fail flag, but does not gate the pilot (D2 = b).
4. **No-regression check.** Nothing in the runtime may change. The M8 city integration, navigation and reentry checks and the M7 automated routes are re-run only if any tracked `game/` file was modified. The expected answer is none.

## 8. Rollback [R]

- Every pilot file is new and uniquely named. Nothing is overwritten: not the masters, the existing `.pxo` files, the concept PNG, the it1 outputs, the runtime, the registry or the progress files.
- **Rollback = delete exactly the files listed in the pilot manifest's "added" list.** Do not use a blanket clean: the working tree already contains unrelated untracked files, for example `.playwright-cli/` and `game/assets/characters/combat-prototypes/…`.
- Verify the rollback with all of these:
  - `git status --porcelain` matches a snapshot taken before the pilot started. A bare "no ` M`" check is not enough, because two tracked Game Bible files (`outputs/…game-bible_app_v01_…-90e7bc24.js` and `tools/…game-bible_server_v05_…-3d5b8a9f.js`) were already modified when this plan was reviewed;
  - the baseline master's SHA-256 still matches: Box `b3a2098634e564a15cc580cb9807894a12e0e1dbf31a82811c8f0d376f9006d6` / Lanczos `738c08c1f4ca967dee325dfeefe6155272366b5e1237f4822ad6a5a2daa643be`;
  - a search for the pilot file names in `game/scripts/` and `game/scenes/` returns 0 hits;
  - no `.import` file exists for any pilot PNG.

## 9. Stop conditions for the pilot [R]

Stop and report at the first of these:

- S1 is non-zero after **2** correction passes, which means identity drift.
- Any frame needs AI output, or a flip or mirror.
- The time box is exceeded by more than 1.5×.
- The user rejects the baseline in E10(i).
- The Claude subscription limit is reached. Record the stopping point; never switch to API keys, API billing, credits or auto-reload.

## 10. Unresolved items

1. **D1 baseline: Box, Lanczos or neither.** **Decision update, 2026-10-14: neither.** Both candidates are rejected as not polished enough, and the static south idle is refined first. Still blocking: walk-frame production stays paused until the user approves a new static idle.
2. **E8 for south.** In the it1 discrete-flipbook harness at 90 logical px/s, with the sprite moved every tick, E8 as written cannot be met by any artwork (RC1). By arithmetic the same holds at 80–140 logical px/s in that model; only 90 was measured. The team gates the pilot on K1–K5 and reports E8 unchanged (D2 = b). Whether E8 itself should be redefined, or a different display model tried, stays open and is not changed here.
3. **R2 walk speed.** The runtime uses 140 logical px/s with time-driven 0.12 s phases [V §2.6]. The arithmetic below is [D]; the human reference values are general biomechanics approximations, not measured here.
   - Pilot (90 logical px/s, 20 logical px step): 4.5 steps/s.
   - Runtime (140 logical px/s, 0.48 s per 4-phase cycle): 4.17 steps/s, about 33.6 logical px per step.
   - Both cadences are far above a typical human walking cadence of about 1.7–2.0 steps/s.
4. **Runtime stepping model.** The runtime is time-driven; the pilot test is distance-driven. Runtime integration is out of scope for this pilot.
5. **Pixelorama export.** Not verified in this audit: exporting each frame as a separate PNG, and exporting a single layer, in v1.2.3. Also unverified: where the web build stores its settings. The team uses the web build (D4); the staged Windows build is unsigned.
6. **Dark-ground edge contrast.** About 0.09 for the idle and all it1 frames (§2.7). This is inherited from the master; whether it matters is for E10.
7. **E10.** The user's review of everything remains open: the it1 frames, the four idle variants and any future hand-drawn frames. **Decision update, 2026-10-14:** the user has rejected the Box and Lanczos idles. Still open: review of a new static idle, and of any walk frames, which are paused until that idle is approved.

## 11. What this audit did and did not do

- **Did:** read the files in §1, parsed the it1 receipts and metrics, and measured the it1 frames and both masters in memory. It wrote a few scratch scripts and enlarged previews to the system temp folder, outside the repository, plus this one markdown file.
- **Did not:** generate or edit any art; run Godot or the bake; create or edit code, tests, registry entries, manifests, progress entries or the Game Bible; change any acceptance flag or E-metric; touch Git; use any API key, API billing, credits or paid service.
