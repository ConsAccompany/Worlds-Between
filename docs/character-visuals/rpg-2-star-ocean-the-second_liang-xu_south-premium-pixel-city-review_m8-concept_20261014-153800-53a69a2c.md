# Liang Xu south exploration concept — city-scale review

Status: **concept only; creator art approval pending.** No gameplay sprite, character registry, or runtime scene was changed.

## Source and preview

- Identity reference: [`outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png`](../../outputs/rpg-2-star-ocean-the-second_liang-xu_character-sheet_v01_20261013-153556-c7630671.png)
- New transparent imagegen candidate: [`game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_south-exploration-premium-pixel_m8-concept_20261014-153531-4c6e2bcd.png`](../../game/assets/characters/high-fidelity-prototypes/rpg-2-star-ocean-the-second_liang-xu_south-exploration-premium-pixel_m8-concept_20261014-153531-4c6e2bcd.png)
- Actual Godot city capture, Liang alone at 48 logical px: [`outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-character-quality-h48-canvas-items_m8-v02_20261014-153547-1ca1259c.png`](../../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-character-quality-h48-canvas-items_m8-v02_20261014-153547-1ca1259c.png)
- Actual Godot city capture, male protagonist / female protagonist / Liang on the same ground line and height: [`outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-male-female-south-scale-review_m8-concept_20261014-153644-9226ceab.png`](../../outputs/rpg-2-star-ocean-the-second_scifi-city_liang-xu-male-female-south-scale-review_m8-concept_20261014-153644-9226ceab.png)
- Reproducible 3-character comparison harness: [`game/tests/rpg-2-star-ocean-the-second_scifi-city_three-character-scale-review_m8-concept_20261014-154100-a72e59c0.gd`](../../game/tests/rpg-2-star-ocean-the-second_scifi-city_three-character-scale-review_m8-concept_20261014-154100-a72e59c0.gd)

The candidate was generated with built-in imagegen in transparent-background mode, referencing Liang's character sheet for identity and the premium female south concept for rendering style only. The requested output was one south-facing, full-body idle figure, with no scenery or alternate poses. Candidate SHA-256: `747F16C2A99169682916E5482B5430A8E1B14850F6C3299788BD84E0C4B769EE`.

## Technical check

- Source PNG: 1024 × 1536 RGBA. At alpha ≥ 64, subject bounds are `(165,83)`–`(874,1486)`; no high-alpha subject pixel touches a canvas edge.
- Source-space foot anchor `(560,1486)` was placed at city `(340,253)` in the solo capture. The visible figure is 48 logical pixels high (scale `0.0342124`). The comparison uses the same 48-pixel height and ground y for all three figures.
- Project logical canvas is 640 × 360; actual capture is 1280 × 720 with `canvas_items` scaling. Character uses nearest texture filtering and a separate soft ground shadow. This is a technical review setup, not a proposed production rendering change.
- 30,325 source pixels have alpha 1–63. The visual capture does not show an obvious broad dark box, but low-alpha fringe must be checked on light and dark backgrounds before production use.

## Visual assessment

- The dark updo, wide silver side streak, charcoal coat and copper accents preserve the sheet's identity. Liang reads older and more composed than the two young protagonists in the source concept.
- At the chosen city scale, the silver streak and long coat remain legible. The folded tablet and collar ring survive as small dark/copper marks, but their exact form does not read without a close view.
- Her height and foot placement are consistent with the premium male and female south concepts. The three candidates share similar high-detail texture density against the city. Liang's darker palette gives her a quieter silhouette; the silver hair is the strongest distinguishing cue.
- The source image is a single idle south concept. It has not been checked for north/east/west turn consistency, occlusion in all city areas, or animation. Her source face may still read younger than 46 at close view, so creator review should decide whether to strengthen mature facial cues before making more directions.

## Decision

Use this candidate only for **art calibration and review**. It is not an approved game sprite. Next production gate is creator approval of the 48-pixel in-engine look, followed by direction continuity and movement frames; alpha-fringe QA remains open.
