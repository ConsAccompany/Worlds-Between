# NYC City Hall Park — 640×360 walkable Pixelorama pilot v04 (isolated visual polish) — QA note

**Status: UNAPPROVED · NONRUNTIME.** This is a new, separate test-only candidate. It is not accepted art, and no human has reviewed it. Codex judges it before any review request.
- It is forked from the v03 tool (run `nyc-chp-v03_20261016-160059-4b2f50f6`). The v04 `check` re-hashed 16 v03 files and all are unchanged: the 7 manifest-listed candidate files, the v03 tool and manifest, the six v03 captures and the v03 report.
- Nothing is wired into the runtime, and the runtime default is unchanged. Science scene art stays **0/11**, and the meter is unchanged.
- No Game Bible, `docs/progress.md`, runtime or Git change was made.
- Run: `nyc-chp-v04_20261016-172144-eb092a52`.
- Author: Claude (Claude Code, Opus 5.5) on the signed-in claude.ai Max subscription.
  - Auth was checked before work with `claude auth status`: `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`. `ANTHROPIC_API_KEY` was not set.
  - No API billing, no image model and no paid fallback were used. No quota stop occurred.

## Inputs read

- **Review:** the Codex visual review of v03, relayed in the task (there is no separate audit file). It found the NYC civic identity clearer, and the skyline and park activity better than v02. Its defects:
  - the central promenade is a flat repeated tile strip;
  - the bright flower beds look like sticker ovals;
  - the water veil looks like a pale cylinder rather than a stone bowl;
  - several visitors are tiny generic dots beside the 48-px heroine.
- **v03 material:**
  - the v03 QA note, manifest and tool;
  - the real v03 Godot captures at 640×360 and 1280×720 (axis, behind fountain, behind tree).
- **Canon:**
  - NYC is the Science hub, and Lower Manhattan City Hall Park is the first playable area (2537). Source: creator decisions note `docs/design/…creator-decisions-2026-10-15…39efc292.md`.
  - The 48-logical-px display scale is the only approved scale. Scene quality stays 0/11 (`docs/progress.md`).
- **Naming:** global `AGENTS.md`.
- **Instructions from the task:**
  - Full-size visitors must be a separate test-only overlay, not baked background art.
  - The tiny stair figures may be removed.
  - No plot or new named-landmark decisions.

## Authoring route (disclosed)

As in v03, this is a deterministic Python tool with hand-written tables. There was no Pixelorama GUI paint pass.
- The tool writes a native `.pxo` (pxo_version 7) and an `.ora` with 24 named, editable layers, using 168 hand-picked palette colours.
- New tables cover:
  - promenade course heights, slab lengths, lane drift, edge units and sett tones;
  - bed lobes, drifts and accents;
  - the tazza profile and overflow strands;
  - visitor bodies (row-span tables per pose).
- No value noise and no hashed scatter are used. A hash only picks a slab, sett or hex-block tone or a course offset from a short hand table.

## Files

Tool, which is both the author and the check script: `tools/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-pilot-640x360_pixelorama-build_unapproved-v04_20261016-172144-eb092a52.py`
- 3,914 lines, sha256 `c7c53e350c386ff14a1fd07349940debcf62668978ddba1958b8db87372809fa`. The file is LF, so this equals its sha256-text-lf-v1.
- Usage: `python -I -B <tool> preview <tempdir> | build | check [--write-report]`.

Candidate directory: `game/assets/environments/candidates/nyc-chp-v04_20261016-172144-eb092a52/`. Every file takes the prefix `rpg-2-star-ocean-the-second_nyc-city-hall-park_` and the suffix `_unapproved-v04_20261016-172144-eb092a52`.

| file | sha256 |
|---|---|
| `scene-24layer….pxo` (source, 24 layers) | `5119170ee29be16520c9512ede6b1534ba771c597fff072464f2e987ad4ddb3d` |
| `scene-24layer….ora` | `d6ffb72374bf30c939aa669a333798da62c82b2188eebacfe662fa741e6e4cb3` |
| `scene-flat-640x360….png` (flat, art only) | `abd7a30f736b226b7bb5873989e671f5a2925b25cb9e7d98eeef96b46c10ea91` |
| `scene-palette….gpl` | `0086f5fe86cd10c465b90a110e2d5f234c96dc7fc2413299b24d7ad0295ce825` |
| `scene-walkmask….png` | `4eab4b742cfcd0eb9701867bf97742b43e7f3a42b1b4a3b86bceae93342ef2b8` |
| `scene-walkability….json` | `937829ccfc7dcfc5dff4cafc7e88acb0df2a94129bd290ffcf4d60c3cabcd70f` |
| `contact-shadow….png` (byte-identical to v03) | `ddba14ee0a49be60c49e4e5aa25d83f6ca2aedf45f610710b1a5981fdcbd0e8d` |
| `test-npc-ground….png` (**test-only overlay**: visitor contact shades, picnic blanket) | `67e9c545303e5cca80300fd6ee994b6466971778334e7289c2266c3b27dda8a8` |
| `test-npc-atlas….png` (**test-only overlay**: 7 visitors + drone, editable in Pixelorama) | `5fef46b7d36d19dc857b5e9210d8b4a58a5ca2ee3bac81f4c326511e63019ded` |
| `test-npc-overlay….json` (**test-only overlay**: atlas rects, scene positions, pivots, classes) | `06b55567f9790632bfdfc6e6812f4d246a832cbe550712948c6bbbd6d9259fa1` |
| `scene-manifest….json` | `bc9753b3625c24e3605d7f555fb01e2eb3571b24910000d1dabcf4d7e047529a` |

Output directory: `outputs/nyc-chp-v04_20261016-172144-eb092a52/`. Every capture is a separate real Godot 4.7.2 windowed capture; there are no comparison sheets.

| file | sha256 |
|---|---|
| `godot-render-1280x720-axis-test-npc….png` | `c774d58e38b6a2e00d246911063c8b06baaceece4573c377e9a938683fd7f61c` |
| `godot-render-1280x720-fountain-test-npc….png` | `8bbef791652422e843b8f1d1c0dccd5beeee8a8c0692b4fcb6bb45a3ccc60095` |
| `godot-render-1280x720-tree-test-npc….png` | `0da8ce5005593f615aee30ab2a6cc2c1e4db0ffccad1b0b07dd8ec55f83a6004` |
| `godot-render-640x360-axis-test-npc….png` | `9f61420cc4c40d214056f9a2b8a1dac38cc981f82971d6156237a7b16b43a42a` |
| `godot-render-640x360-fountain-test-npc….png` | `9d0974fecbcdde91d67430e8b6d88570ea349fd81c0ab79942327707d6cff82f` |
| `godot-render-640x360-tree-test-npc….png` | `951fa1691d9da58da1db6134192286262c329549994dd2e860edbd28e342b1dc` |
| `godot-render-640x360-axis-art-only….png` | `bc3e29f6ee0071911537376aa9e5b4e821cd27bd621104ab66a5ff38abdaccbe` |
| `godot-render-640x360-fountain-art-only….png` | `6b07e1f6fb0dce6548d378baa9b80d53a5da7868370e513c67f46c59187ee8ae` |
| `godot-render-640x360-tree-art-only….png` | `8cfc12caa01e0e820e5df05f78fbd9f72cc48b21a4fa01633418a549dc38fac1` |
| `technical-check-report….json` (test report) | `36a9cd4ff741f6dc20d332ff8fb4d58ed0a2909458e85ec24188f431d4fc74e6` |

The `-test-npc` captures include the separate test-only visitor overlay. The `-art-only` captures show the 24-layer scene art alone. The longest absolute path is 252 characters, which a gate checks.

## What changed against the v03 review

Each change was judged at gameplay size in real Godot 640×360 captures and in the 1280×720 (2×) captures.

1. **Central promenade: no longer a flat repeated strip.**
   - The walk is now bluestone flags whose courses thin toward City Hall: 10 → 5 rows, against v03's uniform 8.
   - Each course has its own slab-length offset, in running bond.
   - A warm-granite soldier-course band runs inside each curb.
   - A footfall-polished centre lane drifts course to course: slabs are one tone lighter there, with worn joints and no bevel.
   - The material also has cleft streaks, damp edge patches and rare granite replacement slabs.
   - Where the statue walk and east connector meet the axis (rows 256–281), a crossing band of warm-granite setts with border courses turns the walk into composed spaces.
   - The south plaza gets warm-granite and rare bluestone slabs.
   - Measured on the walk field against the v03 flat: 26 vs 17 distinct colours, and an 8×8 block-luma standard deviation of 15.57 vs 13.48.
2. **Flower beds: no sticker ovals.**
   - The granite ring is gone.
   - Each bed is an asymmetric union of unequal foliage lobes, lit like the tree crowns, with lumpy edges and a dark south/east edge. Mulch shows at the front lip.
   - Bloom drifts are bloom heads on a lattice: dense in the core and every other head on the rim. They use muted rose, white, lavender and yellow.
   - One end of each bed gets a low clipped-box ball or an ornamental-grass accent, and each bed casts a north-east contact shade.
   - Solidity (area ÷ convex hull) is 0.69–0.76 for the four beds; an ellipse is about 1.0.
   - The fountain-plaza hydrangea border is cut back to x 128–158 and muted, and bed 1 moves east. Behind the fountain capture, her head and shoulders now read against plain lawn instead of v03's white flower heads.
3. **Fountain: a stone bowl, not a pale cylinder.** The overflow veil and foam crown are replaced by a stone tazza:
   - a thick lit lip seen from above with water inside;
   - a gadrooned bowl body in the lip's shadow, outlined against the plaza;
   - a baluster pedestal;
   - two overflow falls that start as 2-px sheets and break into 2-texel drops, with splash rings;
   - two short drips;
   - a tiny bubbler.

   Stone outweighs water by 502 to 213 texels in the centrepiece window. At most 6 water texels per row fall below the lip; v03's veil had 12 streams per row.
4. **People removed from the art; full-size visitors in a separate test-only overlay.**
   - Removed from the art: the four 10-row stair figures and the five half-scale lawn occupants. A gate checks that the 24 art layers contain 0 skin-palette texels. The picnic blanket and the garden drone also moved out of the art.
   - Seven visitors and a drone are now in the overlay:
     - a cross-legged reader under the NW plane;
     - a commuter walking away up the NE diagonal;
     - a picnic pair on a gingham blanket under the SE plane;
     - a bench sitter reading a newspaper;
     - a gardener kneeling at the NE bed, with a bucket and trowel;
     - a vendor at the cart;
     - the 2537 garden drone hovering over the bed.
   - Their heights are measured against the 48-px heroine:

     | pose | height | gate band |
     |---|---|---|
     | standing | 47 px | 44–50 |
     | sitting on the ground | 29 px | 26–32 |
     | on a bench | 40 px | 36–42 |
     | kneeling | 32 px | 30–35 |

   - Visitors are Y-sorted with her by pivot row. They are drawn after the art sprite layers, and she is drawn last on ties.
   - No visitor box meets her box at any of the 14 pins.
5. **Science-sphere cue: restrained, ground only.**
   - A small teal wayfinding ring (13×5) is set into the crossing band, east of the axis pin so she never covers it.
   - Eight teal nozzle nodes sit on the fountain's inner tier.
   - Together they are 48 texels. City Hall has 0 teal texels, and its historic identity is unchanged.
6. **The layer `lawn-life` is renamed `shrub-borders`.** It now holds only the three shrub borders. The stack is still 24 layers.

The heroine scale (48 px), the walk network, exits, Y-sort pivots and landmarks are unchanged.

A layer-by-layer comparison of the v03 and v04 `.ora` files gives:
- **Pixel-identical to v03:** `skyline`, `city-hall`, `back-groves`, `streets`, all five tree layers, `statue`, `cart`, both lamps, `props-low` and `fg-occlusion`.
- **Differs by 2 despeckled texels:** `forecourt`.
- **Differs because of the stair-figure removal:** `forecourt-near` (104 px).
- **Changed on purpose:** `park-ground`, `ground-wear`, `ground-detail`, `fountain-basin`, `fountain-ysort` and `cast-shadows`.

## Capture pins and route (disclosed)

- **Fountain capture:** moved from (172,240) to **(184,236)**.
  - With the new low tazza, dead centre behind it put her legs ending exactly at the lip, and she read as standing *in* the bowl. Feet at (172,235) were technically walkable, with both feet hidden behind the bowl body, but still read that way.
  - At (184,236) the lip and bowl hide her west leg. Her east boot and contact shadow (22 texels visible) stand on the paving behind the fountain.
  - This is the same "partly behind" read as the tree capture.
- **Axis (320,292) and tree (398,268):** unchanged.
- **Route:** it now leaves the fountain north-about, through (184,224) → (140,224) → (140,236), instead of crossing the pocket behind the bowl. It is 1,553 one-pixel steps, with 0 blocked and 0 jumps on both the Python mask and the exported mask in Godot.

## Visual defects still visible at gameplay size

1. **Promenade colour.** The bluestone is cooler and darker than the warm plaza and the white City Hall, so at 1× it still reads as a distinct grey-blue band, though no longer a flat tile strip.
   - The 1-px joints between the field and the edge bands run the full length and read slightly like rails.
   - The polished lane is subtle at 1×.
2. **Beds may now under-read.** They read as low mixed planting rather than stickers, but at 1× the muted drifts are small, so "flower bed" is quieter than in v03.
3. **Fountain.**
   - It is a generic tazza, not the real Mould fountain form.
   - The two falls are still thin at 1×.
   - The capture is "partly behind", not fully behind.
   - 96 walk texels in a small pocket just north of the bowl (rows 227–242) are now blocked by the standing-on gate. These are the feet where only her shins would be hidden, so she would read as standing in the bowl.
4. **Test visitors are placeholders.**
   - They are simple span-built figures with 2-texel eyes and no animation.
   - The seated laps are still a little boxy.
   - Their outlines are chunkier than the heroine's selout.
   - The vendor and the bench sitter cluster near the cart.
   - The commuter and the vendor stand on walkable paving and have no collision. The overlay is review-only.
5. **The art-only frame is emptier than v03**, because every baked person was removed as instructed. Park activity now depends on the overlay or on future NPCs.
6. **The science cue is very restrained.** The ring and nozzles are just legible at 1× and could be judged too faint.
7. **Unchanged from v03:**
   - City Hall is about half heroine scale.
   - The NE elm and far-right grove still read round.
   - The skyline is shallow.
   - The statue and plaque are generic.
8. **More blocked feet.** 363 feet are blocked by the readability gate (v03: 273), mainly the tazza pocket.

## Technical gates: 60/60 PASS (`check --write-report`)

These are technical gates only, not art acceptance.

**v03 gates kept (43, all pass)**
- Raster and editability:
  - All 24 layers are 640×360 with binary alpha.
  - The base is opaque, and only palette colours are used (148 of 168 appear in the flat).
  - The build is deterministic.
  - The `.pxo` and `.ora` both list 24 named layers with the guides hidden, and the `.ora` PNGs are exact.
- Walkability:
  - 36,891 walkable texels, 30.7% of the park rows. Against v03, 96 were lost (all in the tazza pocket) and 30 were gained (24 at the SW bench where the baked bench reader's collar was removed).
  - All pins are reachable.
  - Feet stand only on paving, never in the backdrop or the basin.
- Depth and occlusion:
  - The depth audit finds 0 wrong-order feet across 23 items.
  - Worst visibility is 0.538 (floor 1/3).
  - The seven Y-sort cases are correct.
    - Behind: fountain 28/28, statue 64/64, SE tree 156/156, west lamp 73/73.
    - Front: candelabra, plaque and lamp.
  - There is no standing-on ambiguity at any walkable foot.
- Pixel clusters:
  - 0 isolated bright flecks in rows 150–359.
  - Single-texel islands are 1.70% in the park rows and 1.0% in the backdrop.
  - The despeckle pass changed 66 texels.
- Heroine and shadow: the heroine is 48 px. The contact-shadow gate passes in all three captures (49, 22 and 49 texels visible).
- Pixelorama 1.2.3 headless, 5 runs of 4.4–4.7 s:
  - The `.pxo` flat export is exact and identical across two runs.
  - The `.pxo` and `.ora` split layers are exact, and the split composite equals the flat.
  - The `.ora` flat export is exact.
  - The guides are not exported, and the sources are unchanged.
- Godot 4.7.2 (temp projects only):
  - Headless: layer hashes are exact, 273 route stills hash-match the Python stack, and the heroine is 48 px.
  - Windowed GL Compatibility renders are pixel-exact outside the alpha contact shadow and ≤1 channel unit inside it. Differing pixels, all inside the shadow:

    | render | axis | fountain | tree |
    |---|---|---|---|
    | 1280×720 with overlay | 52 | 28 | 80 |
    | 640×360 with overlay | 13 | 7 | 20 |
    | 640×360 art-only | 13 | 7 | 20 |

  - No script errors.

**New v04 gates (17, all pass)**
- `art_layers_have_no_people_skin_texels`
- `promenade_more_material_variation_than_v03`: measured against the v03 flat on disk.
- `promenade_courses_thin_with_distance`
- `beds_have_no_stone_ring`
- `beds_are_irregular_not_ovals`: solidity below 0.95.
- `fountain_stone_dominates_water`: stone at least 2× water.
- `fountain_overflow_is_strands_not_a_veil`: at most 6 water texels per row between the lip and the tier.
- `science_cue_restrained_and_off_city_hall`
- `overlay_binary_alpha_palette_only`
- `overlay_separate_from_art_stack`
- `overlay_visitor_heights_match_48px_classes`
- `overlay_visitors_clear_of_heroine_at_every_pin`
- `overlay_feet_in_park_not_basin_or_backdrop`
- `overlay_heroine_scale_unchanged_48px`
- `v03_candidate_files_unchanged`: 16 files.
- `all_written_paths_le_252_chars`
- `godot_render_640x360_art_only_equals_python_1x_exact_outside_shadow_le1_inside`

**Gate changes against v03 (disclosed)**
1. The contact-shadow gate's occluded branch no longer also requires ≥1 visible texel: a shadow fully under a front sprite now passes. The final captures don't use that branch, because all three show ≥22 texels.
2. Captures are renamed `axis` / `fountain` / `tree` with a `-test-npc` or `-art-only` suffix, to keep paths ≤252 characters.
3. The windowed render gate now runs three windows: 1280×720 and 640×360 with the overlay, and 640×360 art-only. The overlay is Y-sorted in Godot as one sprite per visitor, cut from the atlas.
4. The headless texel gate still walks the route on the **art stack only**, without the overlay.
5. The fountain pin and route changed, as described above.

## Process notes

- **Pixelorama isolation:** another session's Pixelorama GUI was open. So `check` ran with the parent `APPDATA` pointed at an empty temp dir, and each Pixelorama and Godot child got its own fake dir.
- **Real AppData snapshot:** I compared the real `%APPDATA%\pixelorama` and `%APPDATA%\Godot` before and after the run. The only changes were:
  - that GUI's `.running` heartbeat;
  - log rotation in `Godot/app_userdata/Worlds Between/logs/` (the main game project).
  - The log rotation came from another session. My Godot runs used only temp projects named `chp-*` under fake APPDATA dirs, and no `chp-*` app_userdata was created.
- **Git status:** comparing before and after, this run added only the v04 candidate dir, the v04 output dir, the v04 tool and this QA note. Entries from parallel sessions appeared in the same window and were not touched:
  - modified `game/scripts/growth_*.gd`;
  - growth stage-1-b files;
  - global-map-art v02 outputs and tools.
- **Builds and previews:** the candidate was built once, and nothing was rebuilt in place or overwritten. Previews went only to `%TEMP%\wb-chp4\` and were deleted afterwards.
- **Temp cleanup:** the gate's `rmtree(ignore_errors=True)` left one empty fake-APPDATA folder (`%TEMP%\wb-chpgodot-…\ad2_640x360-art-only`), probably still locked by the closing Godot window. It was removed by hand.

## Decisions requiring creator review

1. **People.** All baked people are removed, and full-size visitors live only in the test overlay. Should these become runtime NPC sprites with idle animation and collision? If so, which of the seven placements and poses should stay?
2. **Promenade material.** Bluestone field with warm-granite edges and setts, or an all-warm granite walk closer to the plaza? This is also a heroine-contrast question: her dark coat on mid-grey stone.
3. **Fountain form.** Generic tazza, or a lower, wider basin closer to the real Mould fountain? This is still open from v03.
4. **Behind-fountain read.** Is "partly behind" (offset pin) acceptable, or is a fully-behind read wanted? A fully-behind read needs a taller centrepiece and blocks a larger pocket of walk texels.
5. **Science cue strength.** Ring plus nozzles, or something more visible? City Hall stays untouched either way.
6. **Gates.** Should the corrected standing-on rule (v03) and the overlay gates be adopted for the other walkable pilots?

Until a creator review, v04 stays **UNAPPROVED / NONRUNTIME**, and scene art stays **0/11**.

## Zero-change closeout (2026-10-16, ledger only)

- Recorded as a **zero-change** meter closeout: 35.8% → 35.8%, no gate, counter or category change. Science scenes stay **0/11**.
- Evidence is the recorded run: technical report `result: PASS`, **60/60** gates, nine real Godot 4.7.2 windowed captures. It was not re-run or re-captured for the closeout. All 22 local files (11 candidate files, 10 outputs, the tool) were re-hashed and match the tables above.
- Codex visually inspected the 640×360 axis, fountain and tree captures. It judged the stones, plantings and fountain improved against v03, but the scene as a whole is still **below the creator's environment-quality target**, and the temporary test visitors need polish. The defects and creator decisions above remain **open**. This closeout is not a visual acceptance.
- Still **UNAPPROVED / NONRUNTIME**. Only this note is tracked. The candidate files, tool and captures stay local and are hash-pinned in `outputs/rpg-2-star-ocean-the-second_mvp-completion-ledger_map-art-v02-nyc-v04-career-s1b-closeout-evidence-index_v01_20261016-220533-2f06d687.json`.
