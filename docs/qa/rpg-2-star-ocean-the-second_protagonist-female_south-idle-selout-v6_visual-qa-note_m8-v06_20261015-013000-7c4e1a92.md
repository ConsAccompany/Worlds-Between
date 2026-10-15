# Female south idle selout v6: visual QA note

M8, 2026-10-14. Scope: the static selout v6 value/separation candidate, its existing same-run Godot captures, and the separate Game Bible card that shows them. This note records technical results. v6 is **not approved**.

**User review (2026-10-14):** the user reviewed v6 and replied "明亮场景对比度仍不足" (contrast in bright scenes is still insufficient). v6 remains unapproved. Apart from that one reply, nothing in this note is a user verdict.

## Candidate

- [selout v6 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-candidate_m8-v06_20261015-010000-5a7d3f18.png): sha256 `f606afeb70e422b5f0c44373126a7112830e8ed47c22433b18255829fedd283b`. It has an 80×112 cell, a 43×96 visible body, 2,419 opaque texels and 27 colours (no new colours).
- It recolours **301 texels** of selout v5 and changes no shapes. `coat_darken` (275) moves the coat one value step darker inside seven coat boxes; the fist, left cuff and right forearm/glove are excluded. `contour_ink` (26) sets cloth texels with a transparent 4-neighbour on rows 34–79 to `K #0a0a0e`. See the [manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-manifest_m8-v06_20261015-010000-c2e9081b.json) and [edit script](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-edit_m8-v06_20261015-010000-9e4b2c71.py). The script recolours by role only. It does no resampling, quantizing, filtering or AI image editing.
- The manifest's protected invariants are all true. Alpha is identical everywhere. Rows 8–33 (hair, ponytail, face) and rows 80 and below (boots) are identical. Teal, skin, metal and slate texels are identical. Changes come only from cloth, leather and cream roles.
- Measured values (manifest `value_metrics_v5_vs_v6`): coat mean luma 76.55 → 63.70; shirt 178.55 → 178.55; legs 83.21 → 82.14. The share of the 132 silhouette-edge texels (y34–79) below luma 40 goes from 0.7955 to 0.9924. These are measurements, not a quality judgement.
- v5 is the read-only source and is unchanged; its PNG still matches the v6 manifest's source hash.

## In-engine captures

These are the existing captures; nothing was re-captured for this note. All eight come from one run of the [isolated QA scene](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v6-value-separation-visual-qa_m8-v06_20261015-011500-3f7b8d24.gd) (Godot 4.7.2). Each is a separate 1280×720 capture at 48 logical px, with scale 0.5, nearest filtering and no shadow:

| Scene | v6 | v5 reference |
| --- | --- | --- |
| Science city, beside the 32×48 placeholder | [city v6](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v6-h48_m8-v06_20261015-003321-9bfd5b9e.png) | [city v5](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v5-reference-h48_m8-v06_20261015-003321-9bfd5b9e.png) |
| Bright outskirts | [bright v6](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v6-h48_m8-v06_20261015-003321-9bfd5b9e.png) | [bright v5](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v5-reference-h48_m8-v06_20261015-003321-9bfd5b9e.png) |
| Dark city survey annex room 2 | [annex v6](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v6-h48_m8-v06_20261015-003321-9bfd5b9e.png) | [annex v5](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v5-reference-h48_m8-v06_20261015-003321-9bfd5b9e.png) |
| Dark prototype test room | [prototype room v6](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v6-h48_m8-v06_20261015-003321-9bfd5b9e.png) | [prototype room v5](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v5-reference-h48_m8-v06_20261015-003321-9bfd5b9e.png) |

The [QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v6-visual-qa-report_m8-v06_20261015-003321-9bfd5b9e.json) (sha256 `4e1bfa3d074ba1b4be9c57e32c4d54a9d51e0a5f1c7eca73653bde9bc2c9c989`) records the following for every capture:

- a 43×96 pilot window;
- `exact_rgb_matches == opaque_texels`, which is 2,419/2,419 for both v6 and the v5 reference;
- 301 changed window pixels between v6 and v5 in each scene (`matches_expected: true`);
- `human_reviewed: false`, `art_approved: false`, and counters of 0/52 and 0/11.

The v6 manifest's `qa_captures` names this report and carries its current SHA-256 and all eight capture hashes. All file hashes were re-checked against the files on disk during this pass.

`human_reviewed: false` in the report and manifest is generation-time provenance, not the current review status. Neither file is rewritten after the fact; the current status is the user review at the top of this note.

## Visual limitations

- **Bright-scene contrast (user).** The user's reply says contrast in bright scenes is still insufficient. On the bright outskirts capture the brown coat still sits close to the warm beige paving at 48 px. Darkening the coat by one step and inking the cloth edge was not enough.
- **Authored blind.** The manifest says the operations were authored without Claude seeing the v6 result.
- **Fewer coat shades.** The one-step darkening merges the coat's two darkest tones (n into b), which reduces fold detail in shadow.
- **Flat contour.** The ink edge is a uniform `K` on cloth. It is not light-direction aware and has no lighter rim on the lit side.
- **Dark rooms.** The darker coat sits closer to the hair darks at the shoulders, and the manifest notes it may read heavier in the dark annex. It was tuned for the bright city and outskirts.
- **Carried over from v5.** The shirt, legs, scarf, skin, hair and boots are unchanged, so the ponytail is still the largest single shape.
- **Limited scope.** v6 is a static south idle only, with no walk or turn frames. Nothing is wired into the runtime, and only the default first-visit state of each area was captured. The prototype room is a test room, not a gameplay area.

## Game Bible

The production page has a separate **selout v6** card (`#idle-selout-v6`) under its own section label, after the v5 card and apart from the art-review cards. It shows the city, bright-outskirts and dark survey-annex v6 captures as separate images. The four v5 references and the dark prototype-room v6 capture are links. The card shows:

- the badge "技术候选 · 未批准 · 明亮场景对比度仍不足" (technical candidate · not approved · bright-scene contrast still insufficient);
- a "状态：未批准" (status: not approved) line that quotes the user's reply and explains that `human_reviewed: false` is generation-time provenance;
- the known limitations;
- the unchanged counters 0/52, 0/11 and 0/2.

It has no buttons or other acceptance controls. The v2, v4 and v5 cards are unchanged.

## Unchanged

v6 is not art approved (`art_approved: false`). Historical experimental walk-frame prototypes and a rejected four-phase test loop still exist as files. No new walk frames were made, no walk animation is approved (animation acceptance 0), and walk-frame production stays paused. Exploration sprites stay at **0/52**, scene-quality gates at **0/11** and human timed playtests at **0/2**. The project still has 51 identities and 52 variants. No art, edit script, harness, capture, report, manifest, asset inventory, or battle/runtime scene file was touched by this change.

## Changed files (this change only)

- `outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js`: the new `#idle-selout-v6` card and its section label after the v5 card.
- `tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js`: extended with v6 file, report, checklist and Production-view assertions.
- `docs/progress.md` and this note.
- The readiness checklist (`game/data/...53da3710.json` and `docs/character-visuals/...5d914f92.md`) already listed the v6 manifest in the working tree before this pass. It was verified, not edited.

## Verification

Run from the repository root:

```
node tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js
node tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js
python -I tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py
```

On 2026-10-14 all three passed: 12 checks, 7 checks, and a checklist PASS (52 variants, 51 identities, 0 art accepted).
