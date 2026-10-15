# Female south idle selout v7: visual QA note

M8, 2026-10-14. This covers the static selout v7 slate-coat candidate, made in response to the user's reply to v6: "明亮场景对比度仍不足" (contrast in bright scenes is still insufficient). This note records technical results only. v7 is **not approved**, and nothing in it is a user verdict.

## Inputs inspected first

- The original 21:9 female character sheet ([sheet](../../outputs/rpg-2-star-ocean-the-second_protagonist_character-sheet_female_20261013-153316-8fa4d0c3.png)). Its coat is a desaturated grey-brown taupe (sampled `#574a43`, `#4a443c`, `#615448`), which is cooler and greyer than v6's red-brown `#634739`/`#533b32`.
- The v6 PNG, manifest, edit script and [v6 QA note](rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6_visual-qa-note_m8-v06_20261015-013000-7c4e1a92.md).
- The v6 Godot captures for the city, bright outskirts and dark annex.

**Diagnosis.** v6 changed the coat's value but not its hue. Its coat was still red-brown (about 20°, HSV saturation about 0.38), the same hue family as the warm beige outskirts paving (about 40°, saturation 0.47) and its brown grout. The figure was held mainly by its 1-texel ink line.

## Candidate

- [selout v7 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-candidate_m8-v07_20261015-015010-05615df5.png): sha256 `4ada7df785a2a6fd19dea74b199f28d9d2101bfe75f306529412d17a4d5bb295`, 3,795 bytes.
  - 80×112 cell, 43×96 visible body, 2,419 opaque texels.
  - Binary alpha, foot anchor (row 103, x 40), all the same as v6.
  - 31 colours: v6's 27 plus 4 new.
- [Manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-manifest_m8-v07_20261015-015010-ed510f85.json). It lists all 369 changed texels with their x, y, op, role and before/after hex.
- [Edit tool](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-edit_m8-v07_20261015-015010-b6d45ce8.py) (sha256 `14dc7c50dad2d64de34c9152aa8aca3c814ff47d7f3bca640e71b3175d45ceab`).
  - It is source-locked to the v6 PNG. Before and after writing, it checks the v5 PNG and the v6 manifest against fixed SHA-256 values.
  - It only recolours individual texels. It does no resampling, quantizing, filtering, dithering or generative editing, and no shape or leg redraw.
  - The output is a plain RGBA PNG that Pixelorama can open for manual texel edits. Pixelorama was **not** launched in this pass.
- Determinism: a second run into a temp folder produced identical bytes.

### New colours

| Role | Hex | Luma | Use |
| --- | --- | --- | --- |
| P1 | `#625c61` | 94.4 | coat lit (taupe-leaning slate) |
| P2 | `#46424a` | 68.1 | coat base (cool slate-taupe) |
| P3 | `#2d2c34` | 45.2 | coat shadow / edge cluster |
| P4 | `#c07a40` | — | warm copper lapel trim |

### Texel changes (369 total)

**1. `coat_slate` (346 texels).** This recolours v6's coat area: the same 7 coat boxes and 3 exclusions as v6, roles `m`/`n`/`b` only.
- `m` → P1: 77 texels.
- `n` → P2: 137 texels.
- `b` → P3: 132 texels.

The value order is the same as v6 (lit > base > shadow), so the folds keep their structure. The tonal range widens from v6's 52.5/65.1/77.8 to 45.2/68.1/94.4.

**2. `trim_warm` (14 texels).** The two diagonal lapel trims go from `r` to P4:
- Left lapel: (27,35) (28,36) (28,37) (29,38) (29,39) (29,40) (29,41).
- Right lapel: (43,35) (42,36) (41,37) (41,38) (40,39) (40,40) (39,41).

In a first preview the skirt front edges were also copper, but they read as long orange stripes, so they keep v6's `r`.

**3. `edge_cluster` (9 hand-placed texels).** The tool checks each texel's v6 role before changing it.
- `lower_left_sleeve_rim_to_base`: (22,42) (22,43) (21,44) (20,45) (19,46) (20,46) go from `m` to P2. The lit rim now stops at the shoulder (rows 34–41), so the highlight becomes a short shoulder cluster. The lower sleeve becomes a darker mass on bright ground.
- `right_skirt_hem_to_shadow`: (44,73) (45,73) (46,73) go from `b` to P3. These were the warm hem row outside v6's coat boxes; they now close the slate coat's hem.

**Protected invariants (all true).**
- Alpha is identical everywhere.
- Rows 8–33 (hair, ponytail, face) and rows 80 and below (boots) are identical.
- Every texel outside the coat/trim boxes and the 9 cluster texels is identical.
- All ink, teal, skin, metal, cream, shirt and leather texels are identical.
- Changes come only from v6 roles `m`/`n`/`b`/`r`.

**Coat metrics** (manifest `coat_metrics_v6_vs_v7`, same 352 coat texels):

| Metric | v6 | v7 |
| --- | --- | --- |
| Mean luma | 63.85 | 66.17 |
| Mean HSV saturation | 0.383 | 0.113 |
| Share of coat texels in the warm paving hue family | 0.645 | 0.0 |

### First iteration replaced

A first v7 build used a rule-based edge op. A check of its manifest showed that 16 of its 17 texels were already that colour after `coat_slate`, so it added almost nothing. Its PNG, manifest, captures and report were all files created in this pass. They were deleted and replaced by the hand-placed clusters above, and only the final build is on disk. No pre-existing file was overwritten.

## In-engine captures (Godot 4.7.2, real windowed run)

The [isolated QA scene](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-visual-qa_m8-v07_20261015-015010-a4ea0661.gd) is adapted from the v6 harness, which was not modified. In one run it captures v7 and v6 at the identical position, as separate 1280×720 PNGs. Settings: 48 logical px, scale 0.5, nearest filtering, no shadow.

| Scene | v7 | v6 reference |
| --- | --- | --- |
| Science city (bright) | [city v7](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v7-h48_m8-v07_20261015-015737-6abf6f01.png) | [city v6](../../outputs/rpg-2-star-ocean-the-second_city-bright_protagonist-female-south-idle-selout-v6-reference-h48_m8-v07_20261015-015737-6abf6f01.png) |
| Outskirts (bright) | [outskirts v7](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v7-h48_m8-v07_20261015-015737-6abf6f01.png) | [outskirts v6](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v6-reference-h48_m8-v07_20261015-015737-6abf6f01.png) |
| Survey annex room 2 (dark) | [annex v7](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v7-h48_m8-v07_20261015-015737-6abf6f01.png) | [annex v6](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v6-reference-h48_m8-v07_20261015-015737-6abf6f01.png) |

[QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v7-visual-qa-report_m8-v07_20261015-015737-6abf6f01.json): sha256 `0700370afda4b160c328d540912f6f34d9d20c159596a5dea7c9964a7618efba`. The manifest's `qa_captures` names this report and carries its hash and all six capture hashes.

**Gates.** The run exits 1 if any gate fails. All passed, and the run exited 0:
- source SHA-256 locks;
- 1280×720 captures;
- a 43×96 diff window at 1 texel = 1 window px;
- texel fidelity 2,419/2,419 for both variants in every scene;
- v7 and v6 on the identical window rect in each scene: (731,412), (71,426), (225,428);
- v7 vs v6 changed window pixels = 369 in every scene, matching the manifest.

The v6 reference captures were byte-identical across the two runs made in this pass.

**Contrast measurement** (reported, not gated). This is CIELAB ΔE76 between the captured coat-slate texel positions and the median colour of an 8 px background ring. v6 is measured at the same positions.

| Scene (ring median) | v6 mean / min | v7 mean / min |
| --- | --- | --- |
| City (157,140,120) | 33.40 / 27.29 | 36.09 / 24.59 |
| Outskirts (223,175,107) | 57.56 / 50.27 | 65.69 / 55.81 |
| Annex dark (111,92,75) | 15.02 / 9.15 | 22.08 / 14.78 |

## Assessment and limitations

- **Bright outskirts.** Contrast improves measurably (mean ΔE +8.1, minimum +5.5). In the captures, the coat reads as a cool grey-slate block against warm beige instead of brown-on-brown.
- **City: smaller gain, and one regression.** The mean rises by +2.7, but the minimum falls from 27.3 to 24.6. The city's ring is a greyer, less saturated tone, so the light P1 coat tone sits a little closer to it than v6's lit brown did.
- **Dark annex.** The coat is easier to tell apart from the warm floor (mean +7.1). The P1/P2/P3 steps are all visible, so the coat does not read as a black slab.
- **Lower body unchanged.** Only the coat changed hue. The trousers, hair and boots keep v6's warm browns, so from the waist down the figure still sits in the paving's hue family. At full 1280×720 the improvement is mostly in the upper body. A matching trouser pass was out of scope.
- **Edge work is limited.** Only 9 texels are new hand-placed clusters. The rest of the edge keeps v6's structure, recoloured: a lit P1 rim on the shoulder, and 2–3 texel P3/q/K clusters on the shadow side. The outer line is still v6's uniform `K` ink.
- **Hue and palette.** The slate is cooler and greyer than the concept's taupe-brown coat; this is a deliberate shift toward contrast, and identity is a matter for human review. The copper trim colour is new, not taken from the concept palette. The palette grows from 27 to 31 colours (limit 32).
- **Measurement limits.** The ΔE ring median is one colour per scene. Local grout, grass and inlays behind the figure are not modelled.
- **Scope.** Static south idle only: no walk or turn frames, nothing wired into the runtime, first-visit default area state only.

## Unchanged

- v7 is not art approved (`art_approved: false`, `human_reviewed: false` at generation time).
- No acceptance flag, counter, Game Bible file, `docs/progress.md`, readiness checklist, runtime scene/script, or v5/v6 asset/manifest/harness/capture was edited.
  - Counters stay at 0/52 exploration sprites, 0/11 scene gates and 0/2 timed playtests.
  - v6 PNG sha256 is still `f606afeb…283b`, and v5 is still `8ddac8ac…ace`.
- No Git commit was made.

## Changed files (this change only, all new)

- `game/assets/characters/pixelorama-pilots/…selout-v7-slate-coat-candidate_m8-v07_20261015-015010-05615df5.png`
- `game/assets/characters/pixelorama-pilots/…selout-v7-slate-coat-manifest_m8-v07_20261015-015010-ed510f85.json`
- `tools/…selout-v7-slate-coat-edit_m8-v07_20261015-015010-b6d45ce8.py`
- `game/tests/…selout-v7-slate-coat-visual-qa_m8-v07_20261015-015010-a4ea0661.gd` and `.tscn`
- `outputs/…_m8-v07_20261015-015737-6abf6f01.*`: six capture PNGs and one report JSON
- this note

## Reproduce

From the repository root (Codex-runtime Python 3.12, Pillow 12.3.0, NumPy 2.3.5):

```
python -I tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-edit_m8-v07_20261015-015010-b6d45ce8.py --out-dir <temp dir>
work/tooling/godot-4-7-2/Godot_v4.7.2-stable_win64_console.exe --path game res://tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v7-slate-coat-visual-qa_m8-v07_20261015-015010-a4ea0661.tscn
```

The first command reproduces the PNG byte-for-byte; running it without `--out-dir` refuses to change the existing PNG's bytes. The second writes a new set of captures and a report with a fresh timestamp and ID.
