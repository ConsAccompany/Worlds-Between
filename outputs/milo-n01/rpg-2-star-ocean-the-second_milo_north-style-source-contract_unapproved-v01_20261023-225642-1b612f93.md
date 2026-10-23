# Milo north static v01: style/source contract (written before authoring, UNAPPROVED)

Task `content.char.milo.static-north`. This is a production contract only. It gives no art approval, no runtime adoption and no motion claim. Base revision `9c2fc393399db331f15799eea3be5e4e4e9c96b2` (south committed in `8fb2c8e4`, credited in `9c2fc393`). The dirty, uncommitted west work is not a dependency and is not imported.

## Source contract (inherited unchanged from committed Milo south v01)

- Canvas 80x112. Opaque body rows 8..103 (96 source px at density 2, display scale 0.5 = 48 logical px). Pivot (40,104) inside the row-103 feet span.
- Binary alpha, transparent 1-px border, hidden `guides` layer.
- Same declared 40-entry palette as south (byte-identical `colors`), 24..48 colours used.
- Same 12 layer names/order, same per-layer outline colours, same Lin/Jiang `finish` outline pass, same male v8pair PNG/PXO/ORA serializers, all reached through the hash-pinned south author (`138a78d5…`) imported in memory. Only the direction label is rebound in memory.
- Retained south HARD gates with the same thresholds (isolated texels <= 24, identity colours all visible, anchor layers case/wristband/coat/hair/face >= 12 visible texels, >= 8 genuine role layers, all role layers non-empty, etc.).
- Direction-appropriate gate swap, taken from the reused Lin Que author's own north rule (not invented here): south's `face_has_eye` is replaced for north by Lin's `north_face_no_eyes_or_mouth` (face layer must contain no eye-white, iris or mouth colour). Added: `pxo_labels_north`.
- The committed south package must stay byte-identical; the author verifies it against the pinned south manifest (`913d3070…`).

## Style (Sea of Stars direction; south is the continuity reference)

Broad flat clusters, light from the upper left on screen, restrained detail, no 1-px stripe texture.

## View and attachment-side decisions (north = back to camera)

Seen from behind, the character's RIGHT side is on screen RIGHT and LEFT is on screen LEFT (the reverse of south). Reauthored as a back view; not a recolour or mirror of south.

| anchor | character side | north choice |
|---|---|---|
| face | - | not visible: back of head is hair; only ears at the sides and a nape strip of skin. No eyes, mouth, brows or stubble. |
| hair | - | very short spiky dark brown: spike tips on top, cropped tapered nape, darker right (shadow) plane, upper-left sheen, short vertical tier breaks |
| silver patch | RIGHT temple | screen RIGHT side of the head, at the temple edge |
| collar | - | coat standing collar wraps the back of the neck; navy high shirt collar shows just above it (approved sheet back view) |
| coat | - | closed white/grey back, mid-thigh hem (Bible short coat), centre back seam, small green tab at upper centre back and back half-belt (sheet back view), short centre vent at the hem, green hem accents |
| belt layer | - | carries the coat's back half-belt (leather palette); the front belt is not visible from behind |
| cross-body strap | LEFT shoulder -> RIGHT hip | runs from screen-left shoulder diagonally across the back to the case at screen-right hip; flat 3-px band, no stripe shading |
| medicine case | RIGHT hip | screen RIGHT; square white case with navy straps, buckles, handle and its green cross placed where the hanging right hand does not cover it |
| green wristband | LEFT wrist | screen LEFT wrist, fully visible |
| arms | both | rolled white sleeves, navy cuffs, bare forearms, backs of relaxed hands (no knuckle line) |
| legs/boots | both | navy trousers with green outer-seam piping, back-knee folds; boots with pale bands, heel counters and green back tabs |

Recorded sheet inconsistency (no pixels sampled from the sheet): the approved sheet's front/portrait views place the silver patch on the character's right temple, while its back view shows it on the head's screen-left side. The committed south canon (character's right) is kept, which puts it on screen right from behind.

## Independent checker predicates (thresholds fixed here, before the first run)

Image-level north predicates, evaluated on the real image and on negative controls (south, mirrored south, mirrored north):

1. `no_face_features`: zero opaque texels in rows 8..40 with eye-white, iris or mouth colour (`e1`, `e2`, `m1`).
2. `head_hair_cover`: in rows 10..26, hair/silver colours (`h1..h4`, `a1..a3`) are >= 75% of opaque texels.
3. `wristband_screen_left`: green (`g1..g4`) texels in rows 58..64 exist and their mean x < 40.
4. `case_screen_right`: in rows 63..76, >= 40 opaque texels at x >= 58 and < 10 at x <= 22.
5. `silver_screen_right`: silver (`a1..a3`) texels exist and their mean x > head mid x (rows 8..34 bbox).
6. `no_front_opening`: in x 38..42, rows 40..56, at most 5 texels of shirt/zip colours (`n2`, `n3`, `x2`).

The real image must pass all six; every control must fail at least one. Also: opaque-colour difference vs Milo south and vs mirrored Milo south each >= 40% of north opaque texels (not a mirror/recolour). Own-silhouette mask difference >= 400 texels (direct and mirrored) against Jiang south, Lin Que south and Lin Que north. Milo south is deliberately excluded from the silhouette gate: a back view of the same body legitimately approximates the mirrored front outline, so the colour-content gate is used for it instead. Plus retained controls: corrupt hash, tampered PNG, visible guides, tampered south manifest.

## Required evidence

- Author `build`/`check`: deterministic rebuild, disk equals rebuild, pins, south unchanged.
- Independent checker (does not import any Milo author).
- Fresh Pixelorama PXO/ORA exports with exact RGBA compare, sources unchanged, application diagnostics disclosed separately.
- Four EN/ZH city/ruins fit captures through the existing generic fit script and checked runner under Xvfb (static overlay only, not actor integration or dark-context evidence).
