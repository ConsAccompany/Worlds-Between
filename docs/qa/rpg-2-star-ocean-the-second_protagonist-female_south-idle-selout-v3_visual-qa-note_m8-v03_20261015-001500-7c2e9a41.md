# Female south idle selout v3: visual QA note

M8, 2026-10-14. Scope: the static selout v3 polish candidate and its same-run Godot captures. This note records an internal technical and visual review only. v3 is **not art approved** and is not a user review option.

## Candidate

- [selout v3 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-candidate_m8-v03_20261014-234700-3c9a5d27.png): sha256 `21b148cc026a70cdb173200c46cf007f83e4963cd7b7a7c71a174a7cb343cbc3`, 80×112 cell, 43×96 visible body, 27 colours (no new colours).
- It recolours **91 texels** of selout v2 and leaves alpha unchanged: face 10, right coat panel and sleeve 39, left coat strip 6, lower coat specks 5, glove 20, trousers 11 (at y63–65). Hair, ponytail, scarf, knee guard, boots, buckles and the lower legs from y66 down stay byte-identical to v2. See the [manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-manifest_m8-v03_20261014-234700-b47e2c10.json) and [edit script](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-edit_m8-v03_20261014-234700-6e1f0b93.py). Claude authored the script, which applies a deterministic, AI-authored per-texel edit map. No generative image model repainted, resampled or quantized the image.
- v2 is the read-only source and is unchanged.

## In-engine captures

All eight images come from one run of the [isolated QA scene](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v3-polish-visual-qa_m8-v03_20261015-000500-5d7e2a91.gd). The harness exited 0. Each is a separate 1280×720 capture at 48 logical px (scale 0.5, nearest filtering, no shadow), with one v3 capture and one same-run v2 reference per scene:

| Scene | v3 | v2 reference |
| --- | --- | --- |
| Science city, beside the 32×48 placeholder | [city v3](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v3-h48_m8-v03_20261014-235850-48550879.png) | [city v2](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v2-reference-h48_m8-v03_20261014-235850-48550879.png) |
| Bright outskirts | [bright v3](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v3-h48_m8-v03_20261014-235850-48550879.png) | [bright v2](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v2-reference-h48_m8-v03_20261014-235850-48550879.png) |
| Dark city survey annex room 2 | [annex v3](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v3-h48_m8-v03_20261014-235850-48550879.png) | [annex v2](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v2-reference-h48_m8-v03_20261014-235850-48550879.png) |
| Dark prototype test room | [prototype room v3](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v3-h48_m8-v03_20261014-235850-48550879.png) | [prototype room v2](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v2-reference-h48_m8-v03_20261014-235850-48550879.png) |

The [QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v3-visual-qa-report_m8-v03_20261014-235850-48550879.json) records, for every capture:

- a 43×96 pilot window;
- `exact_rgb_matches == opaque_texels` (2,433 for both v3 and v2);
- 91 changed window pixels between v3 and v2 in each scene, inside a 26×39 window-pixel box;
- `human_reviewed: false` (the user has not reviewed v3), `art_approved: false`, and counters 0/52 and 0/11.

## Visual finding

Codex and Claude reviewed the captures separately and agree on the following. This is an internal AI visual review, not a user review. The user has not reviewed v3, and `human_reviewed` stays false.

- **Technically sound.** The texel fidelity is exact, the window is correct, there are no new colours, alpha is unchanged from v2, and the protected regions are unchanged.
- **Visibly barely changed.** At 48 logical px, v3 and v2 are hard to tell apart in all four scenes. Ninety-one recoloured texels within a 2,433-texel body is too small a change to read at game scale.
- **The coat torso still reads as noisy.** The right panel clean-up did not remove the mottled look of the brown coat. The left shoulder, strap area, shirt lacing and lower coat skirts kept v2's texture by design, and they still carry most of the noise.
- **The face and glove changes are subtle.** They do not change the overall impression of the figure.

Conclusion: v3 is a valid technical step but not a meaningful visual improvement. It is **not art approved**, and it is not offered to the user as an approval choice. A structural static **v4** refinement (larger changes to coat planes and the torso, rather than texel-level recolouring) is being done in a separate session. Historical experimental walk-frame prototypes and a rejected four-phase test loop exist from earlier passes. No new walk frames were started after the static-frame gate, no walk animation is approved, and walk-frame production stays paused.

## Unchanged

Exploration sprites stay at **0/52** and scene-quality gates at **0/11**. The 48-logical-pixel display scale is still the only approved scale decision. The project still has 51 identities and 52 variants, and play stays limited to the science region. This change did not touch the readiness checklist, the asset inventory hashes or any art file.

## Needs independent verification

This note was written from file reads only. No commands were run.

- Re-hash the v3 PNG and all eight captures against the report's `pilot_source_sha256` and `capture_sha256` values.
- Confirm that the manifest's `qa_captures.report_sha256` (`a73adb87…229f0`) matches the report on disk.
- Confirm the 27-colour count and the 91-texel diff against v2 with an independent tool.
- The QA script's file name carries the timestamp `20261015-000500`, but the capture stem is `20261014-235850`. This is probably a naming artefact, but it should be checked against the run log.
