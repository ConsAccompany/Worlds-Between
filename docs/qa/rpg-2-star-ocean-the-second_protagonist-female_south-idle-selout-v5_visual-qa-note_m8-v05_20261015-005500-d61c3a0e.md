# Female south idle selout v5: visual QA note

M8, 2026-10-14. Scope: the static selout v5 lower-body and hair candidate, its same-run Godot captures and the separate Game Bible card that shows them. This note records technical results and an internal look at two images only. v5 is **not approved**.

**User review (correction, 2026-10-14):** the user reviewed the v5 city and dark screenshots and replied "更接近了，继续精修" (closer, keep refining). v5 is closer but remains unapproved, and further static refinement is requested. Apart from that one reply, nothing in this note is a user verdict.

## Candidate

- [selout v5 PNG](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-candidate_m8-v05_20261015-004000-8b3e5c07.png): sha256 `8ddac8acb4261cfc4e42ae9727b7cb5a4ff70791973909ab80cea33920ad7ace`, 80×112 cell, 43×96 visible body, 2,419 opaque texels, 27 colours (no new colours).
- It changes **309 texels** of selout v4: lower body and coat skirts 202, ponytail fall 56, left cuff 32, hip belt 18, left fist highlight 1. The lower body (y58–73) is restated as three-tone shapes: diagonal skirt trims, one lining strip, one thigh-strap buckle and a simplified pouch. The hip belt is one row, with a 2×1 metal mark instead of a 2×2 ring. The ponytail fall is one texel slimmer and two rows shorter; this is the only place alpha changes, so the opaque count drops from 2,443 to 2,419. The left cuff is dimmed by one value step. See the [manifest](../../game/assets/characters/pixelorama-pilots/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-manifest_m8-v05_20261015-004000-f41a7d92.json) and [edit script](../../tools/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-edit_m8-v05_20261015-004000-2d6f9a31.py). The script applies an explicit texel map over v4 with no resampling, quantizing, filtering or AI image editing.
- The manifest records these as unchanged from v4: the tuft, tie and crown (rows 8–14), the face and side lock, all teal texels, the torso apart from the cuff and one fist texel, the viewer-right forearm and glove, and everything from row 74 down.
- Measured speckle (manifest `speckle_v4_vs_v5`): lower body x21–47 y57–73 falls from 30/434 to 21/434, and the right leg from 13/118 to 3/118. It **rises** on the left leg (4/106 to 6/106) and the ponytail fall (2/147 to 4/123). The left cuff goes from 4/46 to 3/46. These are counts of isolated texels, not a quality judgement.
- v4 is the read-only source and is unchanged.

## In-engine captures

All eight images come from one run of the [isolated QA scene](../../game/tests/rpg-2-star-ocean-the-second_protagonist-female_south-idle-selout-v5-lowerbody-hair-visual-qa_m8-v05_20261015-005000-6c2a9e47.gd). The Godot harness exited 0. Each image is a separate 1280×720 capture at 48 logical px (scale 0.5, nearest filtering, no shadow). There is one v5 capture and one same-run v4 reference per scene:

| Scene | v5 | v4 reference |
| --- | --- | --- |
| Science city, beside the 32×48 placeholder | [city v5](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v5-h48_m8-v05_20261015-002513-a59b7bc1.png) | [city v4](../../outputs/rpg-2-star-ocean-the-second_city_protagonist-female-south-idle-selout-v4-reference-h48_m8-v05_20261015-002513-a59b7bc1.png) |
| Bright outskirts | [bright v5](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v5-h48_m8-v05_20261015-002513-a59b7bc1.png) | [bright v4](../../outputs/rpg-2-star-ocean-the-second_outskirts-bright_protagonist-female-south-idle-selout-v4-reference-h48_m8-v05_20261015-002513-a59b7bc1.png) |
| Dark city survey annex room 2 | [annex v5](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v5-h48_m8-v05_20261015-002513-a59b7bc1.png) | [annex v4](../../outputs/rpg-2-star-ocean-the-second_survey-annex-room2-dark_protagonist-female-south-idle-selout-v4-reference-h48_m8-v05_20261015-002513-a59b7bc1.png) |
| Dark prototype test room | [prototype room v5](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v5-h48_m8-v05_20261015-002513-a59b7bc1.png) | [prototype room v4](../../outputs/rpg-2-star-ocean-the-second_prototype-room-dark_protagonist-female-south-idle-selout-v4-reference-h48_m8-v05_20261015-002513-a59b7bc1.png) |

The [QA report](../../outputs/rpg-2-star-ocean-the-second_city-bright-dark_protagonist-female-south-idle-selout-v5-visual-qa-report_m8-v05_20261015-002513-a59b7bc1.json) uses the same stem and records, for every capture:

- a 43×96 pilot window;
- `exact_rgb_matches == opaque_texels`: 2,419/2,419 for v5 and 2,443/2,443 for the v4 reference;
- 309 changed window pixels between v5 and v4 in each scene (`matches_expected: true`), inside a 33×58 window-pixel box;
- `human_reviewed: false`, `art_approved: false`, and counters 0/52 and 0/11.

`human_reviewed: false` here is generation-time provenance, not the current review status. The report was generated before the user's reply, and the manifest value is a fixed field written by the v5 edit script. Neither file is rewritten after the fact; the current status is the user review recorded at the top of this note.

The v5 edit script was re-run with `--qa-report` after the captures, so the v5 manifest's `qa_captures` now embeds the report name, its SHA-256 (`e764aaed12238c6dfcd6127395abfe7727904186a01066b489c5ae1f262d57db`) and the SHA-256 of all eight captures. The report is also tied to the sprite through its `sources` SHA-256 values. (An earlier version of this note said `qa_captures` was `null`; that was true before the re-run.)

## Visual limitations

These are limits recorded in the manifest and report, plus Claude's own look at the 8× zoom review image (`work/rpg-2-star-ocean-the-second_protagonist-female_south-idle-v5-zoom-review_m8-v05_20261015-004500-5973ac8d.png`) and the dark-annex v5 capture during this documentation pass. They are not the user's review; the user's verdict is the single reply recorded at the top.

- **Authored blind.** The manifest says the edit map was written from texel reconstructions without Claude seeing the v5 result. The only later look on file is the one 8× zoom review image. A further revision round is likely.
- **Lower body.** At 8× the two trouser legs read as separate shapes and the right leg is cleaner. The coat skirts are still close brown-on-brown values. The coat skirt behind the viewer-right hand (x48–52, y70–75) and both lower legs from y74 (knee guard, boots) keep v4 texture. Stitching and extra straps are not drawn.
- **Hair still dominates.** The fall is slimmer and shorter, but the tuft fan, tie and crown above y15 are unchanged, so the hair is still the largest single shape in the silhouette.
- **Small at game scale.** In the full 1280×720 annex frame the figure is about 22×48 logical px. The 309 changed texels are hard to tell apart from v4 at that size. The user has since looked at the captures and judged v5 closer, but not yet right.
- **Low contrast on warm paving.** The palette is unchanged from v4, so the brown coat still sits close to the warm beige paving in the science city and bright outskirts.
- **Limited scope.** v5 is a static south idle only; it adds no walk or turn frames. Nothing is wired into the runtime, and only the default first-visit state of each area was captured. The prototype room is a test room, not a gameplay area.

## Game Bible

The production page has a separate **selout v5** card (`#idle-selout-v5`) under its own section label, after the v4 card and apart from the art-review cards. It shows the city, bright-outskirts and dark survey-annex v5 captures as separate images. The four v4 references and the dark prototype-room v5 capture are links. It shows the badge "技术候选 · 未批准 · 用户要求继续精修" (technical candidate · not approved · user asked for further refinement), a "状态：未批准" (status: not approved) line quoting the user's reply "更接近了，继续精修" and explaining that the report's and manifest's `human_reviewed: false` is generation-time provenance, the known limitations and the unchanged 0/52 and 0/11 counters. The card has no buttons or other acceptance controls. The v4 card is unchanged.

## Unchanged

v5 is not art approved (`art_approved: false`). The user has reviewed it (closer, keep refining); the files' `human_reviewed: false` is generation-time provenance, not a claim that no review happened. Historical experimental walk-frame prototypes and a rejected four-phase test loop still exist as files. No new walk frames were made after the static-frame gate, no walk animation is approved (animation acceptance 0), and walk-frame production stays paused. The manifest's `walk_frames: 0` describes the v5 candidate only, not the project. Exploration sprites stay at **0/52** and scene-quality gates at **0/11**. The 48-logical-pixel display scale is still the only approved scale decision. The project still has 51 identities and 52 variants, and play stays limited to the science region. No art, script, harness or capture file was touched by this documentation change. The asset inventory was not edited, so its hash is unchanged.

## Changed files (this change only)

- `outputs/rpg-2-star-ocean-the-second_game-bible_app_v01_20261013-195526-90e7bc24.js`: the new `#idle-selout-v5` card and its section label after the v4 card.
- `game/data/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-53da3710.json` and `docs/character-visuals/rpg-2-star-ocean-the-second_character-sprite-readiness-checklist_m8-v01_20261014-184413-5d914f92.md`: the v5 manifest was appended to the female variant's unregistered related manifests, by hand, in the build script's sorted glob order.
- `tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js`: extended with v5 file, report, checklist and Production-view assertions.
- `docs/progress.md` and this note.

## Needs independent verification

This note was written from file reads only. No commands were run. Run from the repository root:

```
node tests/game-bible-selout-v2/rpg-2-star-ocean-the-second_game-bible_selout-v2-review-card_check_m8-v02_20261014-234724-e3b7a915.js
node tests/game-bible-character-readiness/rpg-2-star-ocean-the-second_game-bible_character-readiness-view_check_m8-v01_20261014-225834-0f4cdab5.js
python -I tools/rpg-2-star-ocean-the-second_character-sprite-readiness_build-and-check_m8-v01_20261014-184413-c8e6c511.py
```

- The extended check re-hashes the v5 PNG against its literal hash and the manifest, checks that the v5 source is v4, and checks the report's source hashes and all eight captures. It asserts 27 colours, 2,419 opaque texels, 309 changed texels, 2,419/2,419 fidelity, 309 changed window pixels per scene and the checklist entry. It then renders the Production view and checks the v5 card: it follows the v4 card, has three inline v5 images, links eight captures that are served byte-identical, uses unapproved wording that records the user's "继续精修" reply (and fails on stale "尚未回复"/"待用户回复" wording), has no acceptance controls and keeps the counters unchanged. It also checks that the v5 manifest's `qa_captures` names this report, carries its current SHA-256 and matches all eight capture hashes in the report.
- If the readiness build check still reports the checklist as stale, the difference is not only the manifest list. In that case, run the script with `--write` and review the diff.
- Confirm the 27-colour count and the 309-texel diff against v4 with an independent tool.
