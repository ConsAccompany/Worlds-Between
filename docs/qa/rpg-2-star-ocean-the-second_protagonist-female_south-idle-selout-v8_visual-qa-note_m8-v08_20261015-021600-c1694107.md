# Female south idle selout v8: visual QA note

M8, 2026-10-14 (file stamps are UTC, 2026-10-15). This covers the static selout v8 cloth/leather candidate. It responds to Codex's visual review of the v7 1280×720 city and outskirts captures:

- the upper-coat palette shift is subtle at full scale;
- the lower body still merges with the warm paving;
- the v7 note shows the city's minimum coat contrast fell below v6.

This note records technical results only. v8 is **not approved**, and nothing in it is a user verdict.

## Inputs inspected first

- **v7 PNG, manifest, edit script and [v7 QA note](rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7_visual-qa-note_m8-v07_20261015-015010-5176192d.md).**
- **The v7 run's v6/v7 Godot captures** for city, outskirts and annex, each cropped 1:1 and enlarged ×3.
- **The 21:9 female character sheet** ([sheet](../../outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png)). Sampled medians:
  - trousers `#6f6051` (HSV saturation 0.27);
  - boots `#4d4038` (0.27), dark;
  - coat front `#35362f`;
  - palette swatch 6 `#547b76`, a muted teal-grey.

**Diagnosis.**

- **Lower body.** v7's trousers (`w` `#7e5f4a`, `m` `#634739`, saturation ≈0.41) and boots (`l` `#845436`, 0.59) are *more* saturated and warmer than the concept's. Measured over the recoloured lower-body texels, 82% of them sit in the warm paving hue family.
- **Coat.** v7's coat is almost neutral (mean saturation 0.11). Its lit tone `#625c61` is the weakest colour against the city's grey-warm stone, which explains the city minimum regression.
- **Shadow side.** v7's right sleeve keeps a 2-texel lit fold down its full length, as bright as the lit shoulder. As a result the shadow side has no shadow mass.

**Constraint found while choosing colours.** These numbers come from scoring candidate colours against every background pixel around the v7 window.

- In the city, the legs stand on the blue-grey compass rose, so cool mid-value trousers merge there.
- In the outskirts, warm trousers merge with the paving.
- No low-chroma mid tone separates from both. A grid search over all sRGB colours with CIELAB chroma ≤ 12 tops out at a 5th-percentile ΔE of about 13–14 in the city for L\* 36–44.
- So the lower body has to separate by value *and* hue: a deeper, cool, low-chroma base with only small lit clusters.

## Candidate

- [selout v8 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png): sha256 `ccf9d2a293e7f1b9c706b4d2f1bf9c00b3c7714ec4e9b8bddf023e166f68b6fd`, 3,816 bytes.
  - Same as v7: 80×112 cell, 43×96 visible body (48 logical px in game), 2,419 opaque texels, binary alpha, foot anchor (row 103, x 40).
  - 32 colours (v7 had 31; see the palette section).
- [Manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json) (sha256 `0fa7937d…5992`).
  - It lists all 793 changed texels with their x, y, op, v7 role, v8 role and before/after hex.
  - It also lists the coat, trouser and boot region texels, the v7-vs-v8 region metrics, and the QA report and capture hashes.
- [Edit tool](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-edit_m8-v08_20261015-021600-3b1f3a90.py) (sha256 `2063335f…85ce`).
  - It is source-locked to the v7 PNG. Before and after writing, it also checks the v6 PNG and the v7 manifest against fixed SHA-256 values.
  - It only recolours individual native texels. It does no resampling, quantizing, filtering, dithering or AI redraw, and no alpha or shape change.
  - The output is a plain RGBA PNG that Pixelorama 1.2.3 can open for manual texel edits. Pixelorama was **not** launched in this pass.
- Determinism: a second run into a temp folder produced identical bytes. Running without `--out-dir` refuses to change existing PNG bytes.

### Material rule: cloth is cool, leather is warm

| Group | v8 treatment | Colours |
| --- | --- | --- |
| Coat (storm slate) | the strongest-chroma dark mass; lit / base / shadow ramp widened and moved toward blue | C1 `#5e6e8c` (luma 108.6), C2 `#3a4560` (68.8), C3 `#222839` (40.1) |
| Trousers (spruce-grey) | deep, cool, low-chroma: a darker cut of the concept's own swatch `#547b76`; lit only on each leg's lit (left) side | T1 `#4a625c`, T2 `#324542`, shadow = C3, the shared cloth deep |
| Boots | stay warm leather, one step down v7's own ramp (closer to the concept's dark boots), with 2×2 toe highlights kept in v7's lit `l` | existing `L`/`n`/`b`/`q`/`l` |
| Belt, straps, glove, lapel and front trims, hair | warm, unchanged | — |
| Face, shirt, cuffs, laces, teal scarf/cape, metal | unchanged | — |

### Texel changes (793 total)

1. **`coat_storm_slate` (330 texels).** Every texel that has a v7 coat colour (roles 1/2/3) gets the new C1/C2/C3. The value order is kept, so v6's fold structure survives.
2. **`coat_cluster` (25 hand-placed texels).** The tool checks each texel's v7 role before changing it.
   - `right_forearm_fold_to_base`, 22 texels:
     - rows 42–46 at x 46–47, and rows 47–52 at x 47–48, go from `1` to `2`;
     - the right sleeve becomes one base/shadow group;
     - its lit shoulder cap (rows 37–41) is kept.
   - `left_shoulder_lit_widen`, 3 texels: (26,37), (24,40) and (24,41) go from `2` to `1`. The lit shoulder becomes a consistent 2-texel band at rows 35–41.
3. **`trousers_spruce` (288 texels).** Inside the thigh, outer-thigh and shin boxes, minus the glove box, only v7 roles `w`/`m`/`b`/`n` change:
   - `w` → T1, `m` → T2, `b`/`n` → C3;
   - on the right leg, `w` at x ≥ 40 (rows 61–73) or x ≥ 43 (rows 74–84) becomes T2.
4. **`boots_umber` (143 texels).** Rows 85–102, both feet: `l`→`L`, `L`→`n`, `n`→`b`, `b`→`q`, `m`→`n`. The toe texels (27–28, 95–96) and (49–50, 98–99) keep v7's `l`.
5. **`palette_merge` (7 texels).** The flask's `y` `#4a4749` becomes `g` `#474b54` (ΔE76 ≈ 4), which frees a palette slot.

### Palette

The palette goes from 31 to 32 colours, within the 32-colour limit:

- v7's P1–P3 slots are **repurposed** for C1–C3;
- T1 and T2 are **new**;
- `y` is **retired** (merged into `g`).

### Protected invariants (all true)

- Alpha is identical everywhere.
- Rows 8–33 (hair, ponytail, face) are identical.
- Every ink, teal, skin, metal, cream, shirt, strap and trim texel is identical.
- Changes come only from the declared roles.
- No texel changes outside the coat roles, the trouser/boot boxes and the flask.

There are no isolated texels or pinholes.

### Region metrics (manifest `region_metrics_v7_vs_v8`)

| Region | Metric | v7 | v8 |
| --- | --- | --- | --- |
| Coat (355 texels) | mean luma | 65.99 | 65.64 (value kept, **not** darkened) |
| | luma steps | 45 / 68 / 94 | 40 / 69 / 109 |
| | mean saturation | 0.114 | 0.386 |
| Recoloured lower body (431 texels) | mean luma | 79.2 | 62.3 |
| | share in warm paving hue family | 0.824 | 0.135 |

## In-engine captures (Godot 4.7.2, real windowed run)

The [isolated QA scene](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-visual-qa_m8-v08_20261015-021600-97a4fea2.gd) ([.tscn](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-visual-qa_m8-v08_20261015-021600-97a4fea2.tscn)) is adapted from the v7 harness, which was not modified. It uses the same scenes, offsets and placement code. In one run it captures v8 and v7 at the identical position, as separate 1280×720 PNGs. Settings: 48 logical px, scale 0.5, nearest filtering, no shadow.

| Scene | v8 | v7 reference |
| --- | --- | --- |
| Science city (bright) | [city v8](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png) | [city v7](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v7-reference-h48_m8-v08_20261015-022215-e2203167.png) |
| Outskirts (bright) | [outskirts v8](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png) | [outskirts v7](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v7-reference-h48_m8-v08_20261015-022215-e2203167.png) |
| Survey annex room 2 (dark) | [annex v8](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v8-h48_m8-v08_20261015-022215-e2203167.png) | [annex v7](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v7-reference-h48_m8-v08_20261015-022215-e2203167.png) |

[QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v8-visual-qa-report_m8-v08_20261015-022215-e2203167.json): sha256 `513ab6595fd3bedee02d8477e9a2646c7d98b40f19de8791d147e746e3ea631a`. The manifest's `qa_captures` names this report and carries its hash and all six capture hashes.

**Gates.** The run exits 1 if any gate fails. All passed, and the run exited 0:
- source SHA-256 locks;
- 1280×720 captures;
- a 43×96 diff window at 1 texel = 1 window px;
- texel fidelity 2,419/2,419 for both variants in every scene;
- v8 and v7 on the identical window rect in each scene: (731,412), (71,426), (225,428);
- v8 vs v7 changed window pixels = 793 in every scene, matching the manifest.

**Reproducibility.**
- An earlier identical run (deleted when the files were renamed from a wrong timezone stamp to the correct UTC one) produced byte-identical captures.
- The v7 reference captures here are **byte-identical** to the v7 run's own v7 captures (`f1dd087e…`, `c5bc061d…`, `07b2c81d…`), so the placement is exactly the one in v7's QA.

### Contrast (reported, not gated)

All figures are CIELAB ΔE76 between the captured texels and the background. v7 is measured at the same window-relative positions. Three measures:

- **ring**: against the median of an 8 px background ring (the v7 note's method);
- **row-local**: against the median of the ring pixels within ±6 rows, so the legs are compared with the paving beside the legs;
- **occluded**: against the pilot-free baseline pixel directly behind the texel.

Each cell is v7 → v8.

**Bright city** (ring median 157,140,120):

| Region | Ring mean / min | Row-local mean / p10 / min | Occluded mean / p10 / min |
| --- | --- | --- | --- |
| Coat | 36.09 / 24.59 → **43.56 / 34.03** | 44.34 / 32.31 / 23.67 → **51.65 / 41.02 / 31.37** | 43.14 / 22.78 / 11.65 → **50.35 / 35.20 / 24.14** |
| Trousers | 25.67 / 17.98 → **37.20 / 26.96** | 40.83 / 28.64 / 20.53 → **57.54 / 43.36 / 34.40** | 38.56 / 21.40 / 5.80 → **53.35 / 29.79 / 12.60** |
| Boots | 31.71 / 26.42 → **36.53 / 28.83** | 32.92 / 26.23 / 22.24 → **37.31 / 27.92 / 25.83** | 34.82 / 19.90 / 11.22 → **38.51 / 22.45 / 12.74** |

**Bright outskirts** (ring median 223,175,107):

| Region | Ring mean / min | Row-local mean / p10 / min | Occluded mean / p10 / min |
| --- | --- | --- | --- |
| Coat | 65.69 / 55.81 → **74.58 / 66.50** | 66.16 / 56.11 / 54.69 → **74.88 / 66.64 / 65.12** | 65.78 / 55.53 / 34.37 → **74.36 / 65.19 / 46.50** |
| Trousers | 48.61 / 39.86 → **66.64 / 57.27** | 48.55 / 39.84 / 37.26 → **66.14 / 57.18 / 53.54** | 43.04 / 26.51 / 13.12 → **60.07 / 42.49 / 32.47** |
| Boots | 51.94 / 38.15 → **59.32 / 45.15** | 45.18 / 32.50 / 28.31 → **51.92 / 38.63 / 34.42** | 44.09 / 30.58 / 20.95 → **50.02 / 34.88 / 26.86** |

**Dark annex** (ring median 111,92,75):

| Region | Ring mean / min | Row-local mean / p10 / min | Occluded mean / p10 / min |
| --- | --- | --- | --- |
| Coat | 22.08 / 14.78 → **32.89 / 31.77** | 23.82 / 16.65 / 14.99 → **34.50 / 32.43 / 31.77** | 23.20 / 15.70 / 12.53 → **34.00 / 30.39 / 23.85** |
| Trousers | 10.22 / 6.74 → **24.72 / 19.61** | 9.75 / 5.56 / 5.03 → **24.78 / 20.41 / 18.41** | 11.02 / 4.26 / 2.87 → **25.69 / 19.56 / 16.08** |
| Boots | 16.22 / 9.15 → **19.42 / 14.16** | 15.64 / 12.01 / 8.20 → **18.04 / 12.85 / 11.94** | 15.56 / 10.79 / 5.95 → **18.26 / 13.23 / 10.77** |

**Whole figure, mean ring / row-local / occluded:**

| Scene | v7 | v8 |
| --- | --- | --- |
| City | 35.79 / 41.41 / 41.18 | 38.55 / 44.74 / 44.21 |
| Outskirts | 57.61 / 57.41 / 55.96 | 61.50 / 61.19 / 59.61 |
| Annex | 25.51 / 25.86 / 26.13 | 29.02 / 29.37 / 29.63 |

**Regression check.** No region has a lower mean, p10 or minimum than v7 in any scene, on any measure.

- **City.** The coat's ring minimum is now 34.03. That is above both v7 (24.59) and v6 (27.29, the v7 note's v6 figure measured at the same positions), so the v7 city regression is reversed.
- **Whole-figure minimum.** It is unchanged (city 2.38, outskirts 8.57, annex 4.78 row-local). It comes from untouched texels: face, shirt, cream laces and ink.

## Assessment and limitations

- **Visual change is material, not negligible.** In the 1:1 captures:
  - the coat reads as a blue storm-slate garment rather than neutral grey;
  - in the outskirts the legs read as a dark cool block against the beige paving, no longer brown on brown.

  The internal rejection test did not trigger: the change is 793 texels, every region measure improves, and the hue shift is visible at full 1280×720.
- **Clusters.**
  - The coat now has a lit shoulder band on the light side and a base/shadow right sleeve.
  - The trousers keep a lit stripe on each leg's left side, a base, and a shared cool deep between the legs.
  - The lower shins (rows 80–84) still carry some 1-texel alternation inherited from v7's folds.
- **Not "darken everything".**
  - The coat's mean luma is unchanged, and its lit tone is *lighter* than v7's (luma 109 vs 94).
  - The lower body's mean luma does drop (79 → 62), mostly from the hue move to a deeper base and from the boots stepping one value down. This is a real darkening of the legs and boots, reported as such.
  - No outline was added or thickened. The silhouette is still v7's uniform 1-texel `K` ink.
- **Identity risk (human call).**
  - The concept's coat and trousers are warm grey-brown taupe. In v8 both are cool: slate is not a concept colour, while spruce-grey is a darker cut of the concept's own swatch `#547b76`.
  - Face, hairstyle silhouette, scarf, cream shirt, brown leathers and boots keep the concept's read. The figure as a whole is now cooler than the sheet.
  - At 1:1 the spruce trousers sit near the teal cape's hue family (lower chroma, darker). That kinship may read as intended or as muddy, and should be reviewed.
- **City palette kinship.** The city uses teal/blue for banners, glass and the compass rose. The figure separates by value there, and by measure it does better than v7, but its hue is now closer to those accents than to the stone.
- **Boots.** The boots gain the least (city row-local min +3.6, annex +3.7). Their warmth is kept on purpose as the leather accent.
- **Measurement limits.** ΔE76 is a proxy. It does not model the shared ink outline or perceptual grouping. Only first-visit default area state is captured, at one position per scene.
- **Scope.** Static south idle only: no walk or turn frames, nothing wired into the runtime. The palette is at the 32-colour limit, so a future edit that needs a colour must retire one.

## Unchanged

- v8 is not art approved (`art_approved: false`, `human_reviewed: false`).
- No acceptance flag, counter, Game Bible file, `docs/progress.md`, readiness checklist, runtime scene/script, battle file, or v5/v6/v7 asset/manifest/harness/capture/note was edited.
  - Counters stay at 0/52 exploration sprites, 0/11 scene gates and 0/2 timed playtests.
  - v7 PNG sha256 is still `4ada7df7…b295`, v7 manifest `fbfd0be0…ee5f`, v6 PNG `f606afeb…283b`.
- No Git commit was made.

## Changed files (this change only, all new)

- `game/assets/characters/pixelorama-pilots/…selout-v8-cloth-leather-candidate_m8-v08_20261015-021600-157a5ea0.png`
- `game/assets/characters/pixelorama-pilots/…selout-v8-cloth-leather-manifest_m8-v08_20261015-021600-2d6c5eff.json`
- `tools/…selout-v8-cloth-leather-edit_m8-v08_20261015-021600-3b1f3a90.py`
- `game/tests/…selout-v8-cloth-leather-visual-qa_m8-v08_20261015-021600-97a4fea2.gd` and `.tscn`
- `outputs/…_m8-v08_20261015-022215-e2203167.*`: six capture PNGs and one report JSON
- this note

## Reproduce

From the repository root (Codex-runtime Python 3.12.14, Pillow 12.3.0, NumPy 2.3.5):

```
python -I tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-edit_m8-v08_20261015-021600-3b1f3a90.py --out-dir <temp dir>
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v8-cloth-leather-visual-qa_m8-v08_20261015-021600-97a4fea2.tscn
```

The first command reproduces the PNG byte-for-byte. The second writes a new set of captures and a report with a fresh timestamp and ID. `--preview <png>` renders v7 beside v8, enlarged, as a review aid.
