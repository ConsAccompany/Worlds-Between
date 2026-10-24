# Milo east static v01: style/source contract (written before authoring, UNAPPROVED)

Task `content.char.milo.static-east`. This is a production contract only. It gives no art approval, no runtime adoption and no motion claim. Base revision `1f0519de8080a6c57298838cfa8b68963b2a3bde` (south committed `8fb2c8e4`, north committed `70ac7793`). The dirty, uncommitted west work is read only: it is not imported and not modified; its stored PNG is used only as a negative control.

## Source contract (inherited unchanged from committed Milo south v01)

- Canvas 80x112. Opaque body rows 8..103 (96 source px at density 2, display scale 0.5 = 48 logical px). Pivot (40,104) inside the row-103 feet span.
- Binary alpha, transparent 1-px border, hidden `guides` layer.
- Same declared 40-entry palette as south (byte-identical `colors`), 24..48 colours used.
- Same 12 layer names/order, same per-layer outline colours, same Lin/Jiang `finish` outline pass, same male v8pair PNG/PXO/ORA serializers, all reached through the hash-pinned south author (`138a78d5…`) imported in memory. Only the direction label is rebound in memory.
- All retained south HARD gates with the same thresholds, including `face_has_eye` (a profile shows one eye), isolated texels <= 24, identity colours all visible, anchor layers case/wristband/coat/hair/face >= 12 visible texels, >= 8 genuine role layers. Added: `pxo_labels_east`.
- The committed south and north packages must stay byte-identical; the author verifies both against their pinned manifests.

## Style (Sea of Stars direction; south/north are the continuity references)

Broad flat clusters, light from the upper left on screen (on an east profile that lights the back/top edge), restrained detail, no 1-px stripe texture.

## View and attachment-side decisions (east = nose toward screen RIGHT)

Facing screen right, the character's RIGHT side faces the camera. Authored in forward coordinates with the Lin Que `P` pen (s = +1, screen x = 40 + f). This is a separate drawing, not a mirror of west: the near side carries different identity anchors from the west near side.

| anchor | character side | east choice |
|---|---|---|
| face | - | profile leading right: one green eye, brow, nose, smile corner, light stubble on the jaw, ear mid-head |
| hair | - | very short spiky dark brown, spikes up/back, cropped tapered nape, upper-left (back) sheen |
| silver patch | RIGHT temple (near) | clearly visible block at the near temple between fringe and ear: this direction's main head anchor |
| collar | - | standing white collar behind the neck, navy high zip collar at the throat front |
| coat | - | white/grey SHORT coat to mid-thigh, open front showing the navy shirt edge and zip; green chest cross is on the character's LEFT (far) chest and therefore NOT drawn; green hem accent at the front hem |
| cross-body strap | LEFT shoulder (far) -> RIGHT hip (near) | only the front branch is visible: it emerges at the chest front below the collar and runs diagonally down/back to the case handle on the near hip |
| medicine case | RIGHT hip (near) | fully presented: square white case, navy end straps and buckles, handle, green cross; it rides at the back of the hip and projects past the coat back edge |
| near (right) arm | RIGHT | rolled white sleeve, navy cuff, bare forearm, relaxed hand resting at the case's front-upper corner (no wristband) |
| far (left) arm + wristband | LEFT (far) | upper arm hidden by the torso; forearm, darker shading and hand hang slightly forward of the open coat front, bright green wristband on that wrist visible in front of the body (explicit readability choice at 48 px) |
| legs/boots | both | navy trousers; near (right) leg in front with green outer-seam piping; far leg darker, set back; boots with pale bands, green patch on the near boot, toes to screen right |

## Independent checker predicates (thresholds fixed here, before the first run)

Image-level east predicates (screen coordinates), evaluated on the real image and on negative controls:

1. `one_eye`: iris (`e2`) texels in rows 12..33 form exactly one 8-connected component.
2. `eye_in_front_half`: iris mean x > head mid x (opaque bbox of rows 8..33).
3. `face_leads_right`: in rows 18..30, the rightmost opaque texel of the row has a skin/face colour (`s1..s4`, `j1`, `m1`, `e1`, `e2`) in >= 8 of 13 rows.
4. `hair_at_back`: in rows 12..26, the leftmost opaque texel has a hair/silver colour (`h1..h4`, `a1..a3`) in >= 10 of 15 rows.
5. `silver_near_temple`: >= 16 silver (`a1..a3`) texels in rows 8..26.
6. `case_cross_behind_centre`: >= 12 green (`g1..g3`) texels in rows 64..76 at x <= 40.
7. `wristband_in_front`: green (`g1..g4`) texels in rows 58..64 exist and their mean x > 44.
8. `profile_asymmetric`: opaque-bbox mirror IoU <= 0.80 (same measure as the west checker).

The real image must pass all eight; every negative control must fail at least one. Controls: Milo south, Milo north, stored Milo west (if present, read-only), mirrored stored west (the blind-mirror shortcut), mirrored east itself, Lin Que east.

Not-a-mirror/recolour gates: opaque-colour difference vs mirrored stored west >= 35% of east opaque texels and vs Milo south >= 40%. Own-silhouette alpha-mask difference >= 400 texels (direct and mirrored) against Jiang south, Lin Que south, Lin Que east and Lin Que west. Retained controls: corrupt hash, tampered PNG, visible guides, tampered south manifest, tampered north manifest.

## Required evidence

- Author `build`/`check`: deterministic rebuild, disk equals rebuild, pins, south and north unchanged.
- Independent checker (does not import any Milo author).
- Fresh Pixelorama PXO/ORA headless exports with exact RGBA compare, sources unchanged, application diagnostics disclosed separately.
- Four EN/ZH city/ruins fit captures through the existing generic fit script and checked runner under Xvfb with Dummy audio (static overlay only, not actor integration).
