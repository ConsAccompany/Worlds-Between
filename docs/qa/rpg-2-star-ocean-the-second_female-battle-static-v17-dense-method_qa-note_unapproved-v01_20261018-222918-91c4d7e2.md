# Female battle static v17: denser authored still in the actual 1280 render (UNAPPROVED, test-only)

Answers the creator's rejection of v16 (2026-10-18 22:01, verbatim): "this is just way too coarse, her face is not even recognizable". This is a method change: a new authored native 136×144 still, shown through the game's own 1280×720 canvas-items backing. It is not another boot or shadow tweak. It is not an approval, a runtime adoption, an animation or a full native package. The v14, v15 and v16 files and their recorded failures are untouched. The v16 PNG is still `ce6d294c…`, which the check verifies.

## Style/source contract

- Identity: approved female v8 and the character sheet `…character-sheet_female_20261013-153316-8fa4d0c3.png`. That means dark-brown high ponytail with side lock and bangs, brown eyes, warm skin, teal scarf, storm-slate coat, cream shirt, spruce trousers, brown boots, pack with bedroll and a quiet steel canister, and a short blade.
- The root's non-runtime reference `…art-direction-reference-nonruntime-v01_20261015-203250-88880997.png` (sha `ceaa441b…`) was viewed for face and volume readability only. No pixels came from it, and v17 keeps adult-sized eyes, not its larger anime eyes.
- Native cell 136×144 = logical 68×72. Native pin (64,136) = logical (32,68). The baked 0.65 battle proportion is not applied again. Binary alpha. 1-texel outline (`K`); the skin profile uses deep skin `k`. No halo, rim or neon.
- Palette: v16's 33 keys plus 12 disclosed keys. 44 colours are used, against a limit of 48. The new keys are `j` skin mid-light, `k` deep skin line, `r` lip, `y` eye white, `i` iris, `b` upper iris, `O` lit slate edge, `f` deep shirt fold, `N` lit leather crest, `v` lit spruce, `a` warm hair mid and `z` mid steel.
- Light comes from the upper right (front). Default background stays geometric; the outskirts band is used only through its existing opt-in flag. No manual shadow or band overlays.

## Method and outputs (`outputs/battle-static-v17/`)

The author tool is `tools/…_dense-author_unapproved-v17_20261018-220631-3c9e7a41.py` (sha `2b3b09c1…`).

How the art was made:

- The head, face, bangs, ear, hands and buckles are hand-typed ASCII rows.
- Broad cloth and leather planes are non-antialiased polygon, ellipse and line fills, followed by hand-typed fold, seam and highlight rows.
- No resampling, filtering, dithering, noise, generation or upscaling. v16 is not pixel input; it is used only as the bounding-box comparison in check.

| File | sha256 |
| --- | --- |
| Native sprite `…_dense-native136_unapproved-v17_20261018-220631-cde3a961.png` (136×144) | `3cf05f0d3e560bdba5c4910b1192f5ff6ce34c99d747f2643e974fcaeb1d07db` |
| Head native PNG `…_dense-head-native_…-64242174.png` (44×36 crop of the composite, x52–95, y12–47) | `767863fe6802df0df1f09c153f421f841ef63962651f5fdc096de115420e33e2` |
| Layered source `…_dense-layers_…-59156ff8.ora` (24 authored layers + `outline`; stacking = PNG) | `ac001715a7ed7a930f02977a3f81d38434ae0d0a429c61f7d0ac3cfd85a9245c` |
| Manifest `…_dense-manifest_…-36233c94.json` | `a4aa499970b437c69da400644cbf3c7ce5aa4b71c2b3c0f3fac69cd02c1845d5` |
| Check report `…_dense-check-report_…-c38bb78c.json` (21/21) | `6ebb04e38aca1e10b1cb1f1f77e68c8053d287dedbe3a0ae762e631226e99f0e` |
| Inspection zooms (flat grey, root viewing only): full ×4 `…-5a2a5ef1.png`, head ×8 `…-cd6188e9.png` | `3f3d4a7b…`, `43652a2f…` |

## Drawing, not upscaling (author check, 21/21)

- 897 of 1474 fully opaque logical 2×2 blocks (60.9%) contain more than one colour. A nearest-neighbour upscale has 0.
- Only 27.8% of shared opaque texels equal a nearest-upscaled v16.
- The face region has 394 native texels in 19 colours, including distinct eye white, iris, upper iris, pupil and lash, lip and deep skin keys. v16's face had 104 texels in 12 colours.
- Bounds match v16 within 0.5 logical px on every edge: v17 logical bbox 14.5, 1.5, 59.5, 67 against v16's 15, 1, 60, 67.
- Soles end on row 135, and the pin column x64 is clear between the feet.

The first build failed the pin gate: the far boot toe reached x65. The toe was pulled back to x63. The six files from that build, written minutes earlier by this session, were deleted and rebuilt.

## Actual render proof

- Source: canonical `max0840-sentry-sync`, tested revision `ec0c784969d5`. It was archived with `core.autocrlf=true` so `battle_arena.gd` keeps its working-file hash `404eabfd…` (blob `025de05…`), with project.godot at `38ed61a4…`.
- The canonical HEAD is now `b429e8e`. The commits since only touch UI audio; arena and project are unchanged. Not re-captured.
- Isolated tree in `%TEMP%`, bounded `--import`, `APPDATA` redirected for every Godot run. Afterwards all 2033 files are present. 436 tracked `.import` files were rewritten by the import; no `.gd`, `.tscn` or `.png` changed.
- The project itself declares a viewport of 640×360, a window override of 1280×720 and `stretch/mode="canvas_items"` (integer). So the 1280 canvas-items backing is the game's own default window; the earlier 640 captures forced `--resolution 640x360`.
- New harness `tools/…_ci1280-density-capture_test-only-v17_…-5a17d0c3.gd` (sha `28e5e7d5…`) is forked from root's current-main harness `9d01d796…`. It is an in-memory subclass that replaces only the hero draw with `draw_texture_rect(tex, Rect2(round(x)-32, 204, 68, 72))`, nearest filtering, no mipmaps. It asserts:
  - canvas_items mode, content scale 640×360, logical visible 640×360, stretch factor 2 (or 1 at 640);
  - normal party x 135/171/207/243;
  - 0 changed pixels outside the hero bounds;
  - identical UI control rects before and after injection;
  - the 0.1 s right-step moves 16.8 logical px.
- Each run used the checked runner (`0a3e036a…`) with a 75 s deadline, a unique log and the marker `V17_DENSITY_CAPTURE_OK`. All five runs were `CHECKED_RUN PASS`, exit 0, 2.9–3.2 s. The logs contain no SCRIPT ERROR, ERROR, WARNING, shader or leak lines. The import also had 0 ERROR or WARNING lines.
- Captures are EN and ZH 1280×720 frames, kept as separate files:
  - `k1280-def-v16/`, `k1280-def-v17/`: geometric default background;
  - `k1280-osk-v16/`, `k1280-osk-v17/`: opt-in outskirts band;
  - `n640-def-v17/`: 640×360 compatibility only.
  - Run evidence is `…_v17-capture-run-evidence_…-4b8e1f60.json`.
- The native-640 main-hero frames are byte-identical to root's earlier current-main captures (`62ea2ff7…` EN, `7a900452…` ZH, run b139dcb6).
- Measurement: `tools/…_ci1280-density-measure_test-only-v17_…-7d41e2b6.py`, report `…_v17-capture-measure-report-r2_…json`, **PASS 72/72**.
  - At 1280, every visible hero pixel equals its native texel exactly (fidelity 1.0) for both v16 and v17.
  - 110 v17 pixels and 132 v16 pixels at the blade tip (x308–326) are overdrawn by the next party member in the normal layout. They are counted and excluded, not hidden.
  - The v16 control has 0 of 1557 blocks with sub-logical detail; v17 has 886 of 1451. In the face, v16 has 0 of 104 and v17 has 78 of 95.
  - Hero colours: 32 for v16, 44 for v17.
  - Physical bounding boxes: v16 (236,410)–(311,543), v17 (235,411)–(309,543); the largest edge difference is 2 px.
  - Outside the hero union, the v16 and v17 frames are identical. UI rects are identical between v16 and v17, and between 1280 and 640.
  - Measure attempt 1 (kept, `…measure-report_test-only…`, `a7dd7044…`) failed 10 gates because it did not yet account for this overdraw.
- Separate inspection crops of the actual captures are in `inspect/` (×3 at 1280, ×6 at 640).

## Face readability and limitations

- At 1280 the face reads as an adult three-quarter profile: brow, a lashed eye with white, brown iris and pupil, the far eye, a nose with nostril shade, lips, chin, jaw, ear and side lock framing.
- The head is still small, about 30×26 physical px. On a large monitor it is a recognisable face, but not portrait detail; the expression is neutral.
- At native 640 the density method does **not** work. Nearest sampling picks one of the four texels per pixel with mixed phase: 122/10/19/1 pixels identified uniquely as phases 00/10/01/11. The face shows 95 of its 394 native texels and the eye and lines break up, which is visible in the 640 crop. This capture only discloses that loss. It is not a claim that density fixes the 640 path.
- Adoption would need one code change that was not made. The current `draw_texture()` call would draw a 136×144 file at double size; it would need `draw_texture_rect` into 68×72.
- Remaining art defects:
  - heavy block boots;
  - broad, flat coat planes;
  - compact gloved hands;
  - bangs read as vertical locks;
  - dark back-hair mass;
  - the blade tip is overlapped by Liang Xu, as in v16.

## State and next action

- Production 51.3%, coding 100%, content 18.8%, inspection 13.2%, approval 7%. These are unchanged: no new task, denominator or approval.
- Full sprites 0/52, accepted scenes 3/12, human plays 0/2.
- Nothing is committed, staged or pushed. Nothing was written to the ledger, index, Site, defaults or any `game/` tree.

**Next action:** root inspects the v17 1280 EN/ZH captures against the v16 controls and the native/head PNGs. If the face and density read is accepted, the creator is shown that single 1280 comparison. If it is rejected, the identified face defects are fixed in the same authoring source before any package or animation work.
