# Female south idle selout v4: visual QA note

M8, 2026-10-14. Scope: the static selout v4 structural candidate, its same-run Godot captures and the separate Game Bible card that shows them. This note records technical results and an internal look at the captures only. v4 is **not approved**, and the user has not reviewed it.

## Candidate

- [selout v4 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-candidate_m8-v04_20261015-001500-e5b81f36.png): sha256 `da8a1ce11db136f7061206a3d8f5038b7d995016e36af2fc011d0a6f0dbcf4d7`, 80×112 cell, 43×96 visible body, 2,443 opaque texels, 27 colours (no new colours).
- It changes **358 texels** of selout v3: hair tuft fan 38, upper left coat 49, upper right coat 29, chest and waist 145, canister 29, belts 46, shirt tails 22. The torso (y34–62) is redrawn as grouped value planes. The ponytail tuft (y8–12) changes from a single spike to a gathered fan, which is the only place alpha changes. Rows 13–33 (hair fall and face) and rows 63 and below are unchanged. See the [manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-manifest_m8-v04_20261015-001500-0c9d3a74.json) and [edit script](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-edit_m8-v04_20261015-001500-7a2c4e19.py). The script applies an explicit texel map with no resampling, quantizing, filtering or AI image editing.
- Measured torso speckle (x18–55, y34–62) falls from **95/983 to 49/983** opaque texels. The left coat, shirt, right coat and canister sub-boxes all fall as well (manifest `speckle_v3_vs_v4`). This is a count of isolated texels, not a judgement of quality.
- v3 is the read-only source and is unchanged.

## In-engine captures

All eight images come from one run of the [isolated QA scene](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v4-structural-visual-qa_m8-v04_20261015-003000-4f8e1b6d.gd). The Godot harness exited 0. Each image is a separate 1280×720 capture at 48 logical px (scale 0.5, nearest filtering, no shadow). There is one v4 capture and one same-run v3 reference per scene:

| Scene | v4 | v3 reference |
| --- | --- | --- |
| Science city, beside the 32×48 placeholder | [city v4](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v4-h48_m8-v04_20261015-001305-7973118b.png) | [city v3](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v3-reference-h48_m8-v04_20261015-001305-7973118b.png) |
| Bright outskirts | [bright v4](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v4-h48_m8-v04_20261015-001305-7973118b.png) | [bright v3](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v3-reference-h48_m8-v04_20261015-001305-7973118b.png) |
| Dark city survey annex room 2 | [annex v4](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v4-h48_m8-v04_20261015-001305-7973118b.png) | [annex v3](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v3-reference-h48_m8-v04_20261015-001305-7973118b.png) |
| Dark prototype test room | [prototype room v4](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v4-h48_m8-v04_20261015-001305-7973118b.png) | [prototype room v3](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v3-reference-h48_m8-v04_20261015-001305-7973118b.png) |

The [QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v4-visual-qa-report_m8-v04_20261015-001305-7973118b.json) records, for every capture:

- a 43×96 pilot window;
- `exact_rgb_matches == opaque_texels`: 2,443/2,443 for v4 and 2,433/2,433 for the v3 reference;
- 358 changed window pixels between v4 and v3 in each scene (`matches_expected: true`), inside a 36×55 window-pixel box;
- `human_reviewed: false`, `art_approved: false`, and counters 0/52 and 0/11.

The manifest's `qa_captures.report_sha256` is `08a972ff…f1e8f`.

## Visual limitations

These are limits recorded by the author and in the report, plus Claude's own look at the city and dark-annex captures. They are not a user review.

- **Limited preview rounds.** The edit map was written from texel role dumps. Codex then rendered a first 8× preview, Claude read it and revised the script, and Codex rendered a second 8× preview before the final PNG and the Godot captures. Two preview rounds are few for a structural redraw, so another revision round is likely.
- **Small at game scale.** At 48 logical px, the 358 changed texels fall within a roughly 18×28 logical-pixel area of the torso and tuft. In the full 1280×720 city frame, v4 and v3 look very similar to Claude. Whether the cleaner torso planes register at play distance needs the user's eye on the separate captures.
- **Hair mass still dominates.** The new tuft fan sits on top of the large viewer-left ponytail arc. At 48 px the overall hair shape is still the heaviest element of the silhouette.
- **Low contrast on warm beige paving.** In the science city and the bright outskirts, the brown coat sits close in value and hue to the warm beige paving, so the scarf and face carry most of the figure's readability there. The dark survey annex separates the figure better. v4 did not change the overall palette, so this is unchanged from v3.
- **Simplified details.** Extra straps, stitching and the lower hip pouch are simplified or left with v3 texture. The lower-left coat skirt and pouch block (x22–29, y59–62) and the trousers keep v3 texture.
- **Shoulder strap.** The backpack strap over the left shoulder now emerges under the lapel at y38 instead of crossing the collar.
- **Limited scope.** v4 is a static south idle only; it adds no walk or turn frames. Nothing is wired into the runtime, and only the default first-visit state of each area was captured. The prototype room is a test room, not a gameplay area.

## Game Bible

The production page has a separate **selout v4** card (`#idle-selout-v4`) under its own section label, after the selout v2 review card and apart from the art-review cards. It shows the city, bright-outskirts and dark survey-annex v4 captures as separate images. The four v3 references and the dark prototype-room v4 capture are links. It shows the badge "技术候选 · 未批准 · 未经用户审阅" (technical candidate · not approved · not reviewed by the user), a "状态：未批准" (status: not approved) line, the known limitations and the unchanged 0/52 and 0/11 counters. The v3 sentence above the v2 card now points to this card instead of saying v4 is in progress.

## Unchanged

v4 is not art approved (`art_approved: false`) and not user reviewed (`human_reviewed: false`). Historical experimental walk-frame prototypes and a rejected four-phase test loop still exist as files. No new walk frames were made after the static-frame gate, no walk animation is approved (animation acceptance 0), and walk-frame production stays paused. The manifest's `walk_frames: 0` describes the v4 candidate only, not the project. Exploration sprites stay at **0/52** and scene-quality gates at **0/11**. The 48-logical-pixel display scale is still the only approved scale decision. The project still has 51 identities and 52 variants, and play stays limited to the science region. No art, script, harness or capture file was touched by this documentation change. The asset inventory was not edited, so its hash is unchanged.

## Changed files (this change only)

- `outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js`: the new `#idle-selout-v4` card and section label, plus the updated v3 sentence.
- `game/data/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json` and `docs/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-5d914f92.md`: the v3 and v4 manifests were appended to the female variant's unregistered related manifests. The build script globs every `protagonist-female_*manifest*.json`, so these are the two entries its no-write check would otherwise report as stale. They were edited by hand because the script could not be run in this session.
- `tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js`: extended with v4 file, report, checklist and Production-view assertions, instead of a new mirror test.
- `docs/progress.md` and this note.

## Needs independent verification

This note was written from file reads only. No commands were run. Run from the repository root:

```
node tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js
node tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js
python -I tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py
```

- The extended check re-hashes the v4 PNG, the v3 source, the v4 report (against the manifest) and all eight captures. It asserts 27 colours, 358 changed texels, 2,443/2,443 fidelity, 358 changed window pixels per scene and the checklist entry. It then renders the Production view and checks the v4 card: three inline v4 images, eight capture links served byte-identical, unapproved wording and unchanged counters. It also checks that the four historical south walk prototype files still exist, that the v4 card records the two 8× preview rounds, and that neither card claims no walk frames were ever started.
- If the readiness build check still reports the checklist as stale, the difference is not only the manifest list. In that case, run the script with `--write` and review the diff.
- Confirm the 27-colour count and the 358-texel diff against v3 with an independent tool.
