# Female protagonist · south source-locked segmented walk · E1–E9 feasibility review · M8 it1

**Status: technical feasibility evidence only. Nothing is approved and nothing is wired into the runtime.** Only the 48 logical px display height is approved. The idle master is the LANCZOS quantized 80×112 south idle, used as a **provisional technical input**: the user has not yet chosen between Box, Lanczos and neither. If they choose otherwise, this experiment may be discarded. Acceptance is unchanged: **0/52** exploration sprites and **0/11** scene-quality gates. The progress files, the Game Bible and Git were not changed.

Plan followed: §4 of the [art pipeline decision memo](rpg-2-star-ocean-the-second_character-visuals_art-pipeline-decision-memo_m8-v01_20261014-165532-0cc81856.md) (method C). Scope: south only, 1 idle + 8 walk frames. The 90 logical px/s speed applies to this isolated test only; it is not a runtime decision, and memo R2 is still open.

## Result

**E1–E7 and E9 pass on bake iteration 1, with 0 hand-edited texels. E8 (foot contact) fails by a wide margin.** This is memo stop condition 6, so the work stopped here. No stride or speed change and no mannequin motion-reference test were started; the user must choose between them.

**Motion verdict (Claude's technical observation, not E10):** identity is locked, but **as a natural walk the motion is not plausible**. Only the boots move: rows are dropped from or duplicated in the shins, so each boot slides 3–6 texels up or down. Knees, thighs and the coat hem never move. The body bobs 0–2 texels and the viewer-right hand moves ±1 texel. At 90 px/s the feet slide across the ground. The frames should be kept only as technical evidence.

| # | Measured (iteration 1) | Result |
|---|---|---|
| E1 source lock | **9/9** frames: every visible copied texel equals its master texel under the declared transform, for example 2,553/2,553 in frame 01. No opaque texel is unaccounted for. Frame 00 is byte-equal in pixels to the master. Re-running the master's author script into a scratch folder reproduced SHA-256 `738c08c1…a643be`. | pass* |
| E2 ownership | **9/9** frames. Knee guard centroid x = 28.5, in leg_vl only, with all 28 texels visible in every frame. Scarf tail centroid x = 17.7–17.9. Both are below pin x 40. Ponytail centroid x = 29.5, left of the face centroid at 36.5. | pass |
| E3 registration | An exact-match search of the torso layer finds dx = 0 in all frames, and dy equals the declared bob (0/1/2) in all frames. | pass |
| E4 height | Idle is 96. Walk frames are 96, 94, 95, 95, 96, 94, 95, 95 (Δ −2 to 0). | pass |
| E5 alpha / palette | 0 partial-alpha texels, 0 opaque texels on the cell border, and 48 colours in every frame. 0 colours fall outside the idle palette. | pass |
| E6 hand work | **0** hand-edited texels per frame (the log is empty). Synthesized occlusion fill behind the swinging arm is visible on **12** texels in 6 of 8 frames and on 0 in the two passing frames. Counted against the 12-texel budget, that is exactly at the limit. | pass (at limit if fill counts) |
| E7 determinism | A second bake into a scratch folder gave byte-identical results for 21/21 files (PNGs and manifest). | pass |
| E8 foot contact | Godot motion run on a straight south path at 90 px/s (3 screen px per tick): stance-foot drift **max 3.0, mean 2.84 screen px/tick, with 148/148 ticks over the 1 px limit**. The analytic cross-check agrees (max 3.0, mean 2.84). Over a stance the planted foot rises only **2 texels** in the cell while the body travels 30 screen px. | **FAIL** |
| E9 display | 1 texel = 1.0 screen px. 0 fractional origins across 161 ticks. Stepping is distance-driven (phase = ⌊distance/5⌋ mod 8 + 1). **0 colour mismatches** comparing every texel of all 18 stills and 3 in-motion samples against the frame PNGs. | pass |
| E10 user review | Not done. This is the user's call alone. | open |
| E11 effort | Under 1 h of wall-clock time for tooling and the bake. | within |

\* E1, E2 and E6 come from a verifier that re-derives the placements from the declared transforms, using the same placement function as the bake, so they are close to true by construction. The measurements that are independent of the bake's own bookkeeping are E3 (search on the frame pixels), E4, E5 and E7 (raw PNGs), and E9 (Godot captures).

## Why E8 cannot pass with this method at this speed

At 90 logical px/s the body moves 3 screen px every tick. A frame is held for several ticks, and a held frame cannot move a foot inside the cell. During held ticks, drift therefore equals body speed: **3 px**. To lock a foot, the planted foot would have to climb about 40 texels per stance. Integer shin row-drops on a 96-texel figure gave 2–3 texels before the boot shaft visibly collapsed: the viewer-right shin is already down to 6 of its 12 band rows in passing-vl. This is a geometric limit of copied-texel limb posing for south-facing motion, not a tuning problem. Memo stop condition 6 now applies. The options are a stride or speed change (R2) or a motion-reference test, and the user decides between them.

## Visible defects (not hidden by the numbers)

- In the passing frames (03, 07), the swing-foot tuck leaves a 1-texel notch on the boot outline.
- The arm fill shows as a flat 1-row coat-coloured stripe above the cuff (arm down) or below the fingers (arm up).
- The knee guard is static and its contrast stays weak. These are the same losses at 96 texels already noted for the idle (memo R1).
- The viewer-left hand grips the strap and is static by design. Only one arm swings.
- The AVI is MJPEG, which is lossy. The PNGs are the colour-exact evidence.

## Files

- Bake script: `tools/rpg-2-star-ocean-the-second_protagonist-female_south-segmented-walk-bake_m8-e1e9-v01_20261014-215052-c82448bd.py`
- Isolated Godot test: `game/tests/rpg-2-star-ocean-the-second_protagonist-female_segwalk-e8e9-test_m8-it1_20261014-215052-{0151f713.gd,a9ea58a4.tscn}`
- Experiment folder: `outputs/rpg-2-star-ocean-the-second_segwalk-e1e9_m8_20261014-215052-5ab7af12/`. It holds:
  - 10 layer PNGs and 1 ownership-mask PNG;
  - 9 frame PNGs (80×112);
  - 18 Godot stills (1280×720, 9 frames × light/dark ground);
  - 1 AVI;
  - the pose table, the bake manifest (masks, offsets, row maps, fill sources, contact points, hashes, an empty edit log), the metrics JSON, and the Godot stills and motion receipts.

  All 38 PNG hashes were re-verified against the manifest and receipts.

Folder and file names were shortened so that every absolute path stays within 259 characters. Longer paths broke Python on Windows and would break Git for Windows unless `core.longpaths` is set.
