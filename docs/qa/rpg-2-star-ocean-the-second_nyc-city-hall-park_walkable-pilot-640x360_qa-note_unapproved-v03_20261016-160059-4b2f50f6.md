# NYC City Hall Park — 640×360 walkable Pixelorama pilot v03 — QA note

**Status: UNAPPROVED · NONRUNTIME.** This is a new, separate test-only candidate, not accepted art, and no human has reviewed it.
- It is forked from the v02 tool (run `nyc-chp-v02_20261016-055120-59848a60`). All 13 v02 files were re-verified by SHA-256 after this run and are unchanged.
- Nothing is wired into the runtime. Science scene art acceptance stays **0/11**.
- No Game Bible, meter, `docs/progress.md`, runtime or Git change was made.
- Run: `nyc-chp-v03_20261016-160059-4b2f50f6`.
- Author: Claude (Claude Code, Opus 5.5) on the signed-in claude.ai Max subscription.
  - Auth was verified before work: `authMethod: claude.ai`, `apiProvider: firstParty`, `subscriptionType: max`, and `ANTHROPIC_API_KEY` was not set.
  - No API billing, no image model and no paid fallback were used.

## Inputs read

- **Audits and QA:**
  - Codex v02 visual audit `docs/qa/…walkable-v02-codex-visual-audit_unapproved-v01_20261016-064422-216b6bc3.md`
  - v02 QA note `docs/qa/…walkable-pilot-640x360_qa-note_unapproved-v02_20261016-055120-59848a60.md`
- **Real v02 Godot 1280×720 captures:** all three views.
- **Canon:**
  - NYC is the Science hub, and the first playable area is Lower Manhattan City Hall Park in 2537 (creator decisions 2026-10-15).
  - The 48-logical-pixel display scale is the only approved scale.
  - Scene quality stays 0/11 (`docs/progress.md`).
- **Naming:** the AGENTS.md rule `[project]_[area]_[purpose]_[variant]_[YYYYMMDD-HHMMSS]-[id].[ext]`.
- **Density ideas only:** the Codex concept `outputs/…visual-direction-reference_nonruntime-v03_20261016-124945-33aa88e9.png`. It is itself an UNAPPROVED generated image. None of its pixels or colours was sampled.

## Authoring route (disclosed)

There was no Pixelorama GUI paint pass in this session.
- As in v02, a deterministic tool rasterises hand-written tables into 151 hand-picked palette colours across 24 named layers.
- Pixelorama 1.2.3 re-exports the `.pxo` and `.ora` headless.
- Textures are hand motifs on fixed lattices with hand offset tables. There is no value-noise and no hashed scatter; a hash only picks a slab or hex-block tone.
- The `.pxo` opens as 24 editable layers.

## Files

Tool: `tools/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-pilot-640x360_pixelorama-build_unapproved-v03_20261016-160059-4b2f50f6.py`
- 3,343 lines.
- sha256 `d8c40162a79bcfa4f4e0446b8ab237cc91b26e5d48efbcf1d4d36f7569cf879e`, identical as sha256-text-lf-v1.
- Usage: `python -I -B <tool> preview <tempdir> | build | check [--write-report]`. One script is both the author and the check script.

Candidate directory: `game/assets/environments/candidates/nyc-chp-v03_20261016-160059-4b2f50f6/`. File names take the prefix `rpg-2-star-ocean-the-second_nyc-city-hall-park_` and the suffix `_unapproved-v03_20261016-160059-4b2f50f6`.

| file | sha256 |
|---|---|
| `scene-24layer….pxo` (pxo_version 7) | `86755d20f91cd6e22a57aa626c46e1aa193f392914cfe7c7b89981d70481f90a` |
| `scene-24layer….ora` | `15207203bd0d71f3f69b4953cc309728b2b5dde1bb501040f6eed6b9daaea685` |
| `scene-flat-640x360….png` | `086734a6a71e6ed3a53591afec882205aa748a75dbc06aecd60c38fc4afa7f0e` |
| `scene-palette….gpl` | `84253801d0e9bf984986ea053626b4ae2ab646c88b6be1bd65fac54094583cca` |
| `scene-walkmask….png` | `124ee2e476655b6a4006e3e43a3c758fe1b618ed7ae4b7b726f13128a4a2f65e` |
| `contact-shadow….png` (byte-identical to v02) | `ddba14ee0a49be60c49e4e5aa25d83f6ca2aedf45f610710b1a5981fdcbd0e8d` |
| `scene-walkability….json` | `14b9dc97460a5d4b09b3029d26a5ecd252ed6554dd2de7690c6beeab05bd4d80` |
| `scene-manifest….json` (includes the `v03_changes_vs_v02` list and the capture-pin moves) | `2ffcbe9d8c1c4db3a075b3b3b1a6f40eeb244161ad3279dde81056b06d428fd5` |

Output directory: `outputs/nyc-chp-v03_20261016-160059-4b2f50f6/`. Every view is a separate real Godot capture; there are no comparison sheets.

| file | sha256 |
|---|---|
| `…godot-render-1280x720-axis….png` | `7af861402c635d7ee1d93d302c6f822c1a2c35ba0acfa2fb02f2e762a6c19743` |
| `…godot-render-1280x720-behind-fountain….png` | `5fcc7b1957579c8bcf65ce747a96c7d90fe0092bdb40ea8acc66db9eb543a133` |
| `…godot-render-1280x720-behind-tree….png` | `60530564d7785d9b7d33195dc872fe2da47d9f816dd64f67a49eb2a909141433` |
| `…godot-render-640x360-axis….png` | `2d193c5555175af8ce93b85eabc24e4b3f015cea76cb63e5d9302509c8fa63f0` |
| `…godot-render-640x360-behind-fountain….png` | `b886dfada793a009a25a83221b768460c56979f64e96d6b2e4028e311845b637` |
| `…godot-render-640x360-behind-tree….png` | `8b2d8bbcbb9616923101edec51d744ad06b53bf38e21a11c3baf2b377164ed81` |
| `…technical-check-report….json` | `cb04eb82075ff111170ff87a8ed8a36096c3e115613c963b5ec733f419ae0dd2` |

The longest absolute path is 252 characters.

## What changed against the v02 audit

Each change was judged in the real Godot captures.

1. **Skyline: no longer uniform grey blocks.**
   - A pale sky band shows between broken rooflines.
   - There are three aerial-perspective planes:
     - far towers close to the sky value;
     - a warmer mid plane of brick, limestone, terracotta and glass blocks, each with its own window rhythm, plus water tanks;
     - the Tweed Courthouse slate hip, nearest.
   - Woolworth-like terracotta piers with pointed heads stand on Broadway (left), and a Municipal-Building-like limestone colonnade with a central arch stands on the right.
   - The 2537 identity stays subtle: one slim far "garden tower" with green terraces and a faint teal seam.
2. **City Hall: less repetitive and less model-like.**
   - A per-window state table sets blinds, low blinds, curtains, lit panes and three sky-reflection shapes. The east and west halves never share a pattern.
   - Added surface detail: a cornice shadow band, splash grime above the plinth, 17 hand-placed rain streaks, west-jamb and lintel reveal shadows, and a small gilt Justice figure on the cupola.
   - The whole building and the far stair treads are remapped to their own hazed marble, roof and glass ramps. City Hall no longer shares values with the crisp hero-scale gate piers, so it reads as distant.
   - Four door-scaled visitors (10 rows tall; the lit door is 20) on the stair and podium give the facade a human yardstick.
3. **Trees: more natural silhouettes.**
   - Hero crowns have hand-cut gaps where limbs show through, plus asymmetric lobe lists.
   - The SE London plane now forks low into a V with a low east bough, so it is no longer a lollipop.
   - The elm is vase-shaped.
   - Back-grove trees mirror their template on every second instance and each gets a spill lobe. North of row 80 they use a hazed blue-green ramp.
   - A 1-px "nook" closer prevents see-through flecks in the gaps.
4. **Lawns: occupied, not vacant.** A new editable `lawn-life` layer holds:
   - a reader sitting under the NW plane;
   - a picnic pair on a gingham blanket with a basket, in the SE plane's shade;
   - a grey-haired bench reader;
   - a kneeling gardener at a bed, with a small 2537 garden drone (teal status light);
   - three mounded shrub borders: hydrangea on the fountain plaza's north rim, hydrangea behind the NE hoop fence, and box at the SW corner.

   Seven hand-placed mown patches break the grass-tuft lattice.
5. **Flower beds that read.**
   - Each bed has a 1-px granite edging (lit to the north and west) and a mulch line.
   - Blooms are solid drifts in a shade colour with a lit cap and bloom ticks, replacing v02's dots on dark foliage.
6. **Fountain.**
   - The 2-px jet that crossed the heroine is removed.
   - The new two-tier centrepiece has a pedestal with mouldings, a wide upper bowl seen from above (rim, water, shaded body), an overflow veil (a stream on every second column, lit west / shaded east) and a low foam crown.
   - The behind-fountain pin moves from (186,226) to **(172,240)**, directly behind it.
     - Stone and falling water now hide her from the hips down (19 covered rows; she is 75% visible).
     - v02 had a 6-texel overlap of a thin jet.
7. **Tree occlusion and foot contact.**
   - The behind-tree pin moves 5 px west, from (403,268) to **(398,268)**.
   - The trunk covers her east side and the west leader crosses her torso.
   - Her far foot and the full contact shadow stay visible (49 shadow texels). In v02 the trunk hid her centre and feet.

## Visual defects still visible at gameplay size (640×360 and 1280×720 captures)

1. **Fountain read.** At 1× the veil reads as a pale blue fluted column ("water cylinder") more than an overflowing stone bowl. The stone bowl body barely shows. It is stylised and not the real Mould fountain.
2. **Behind-fountain busy-ness.** At 1× her upper body overlaps the white hydrangea heads of the plaza-rim border behind her, which makes her silhouette noisy. Only 9 contact-shadow texels show, because 81% of the footprint is correctly under the veil.
3. **City Hall** is still about half heroine scale; the haze and visitors soften this but do not remove it. The facade stays symmetrical, as the real building is. The window-state variety is visible at 2× but subtle at 1×.
4. **Flower beds and borders** now read, but the drifts are clean ovals. At 1× they look a little like stickers or rugs and need a looser, broken edge.
5. **Skyline** is only about 25–40 rows visible. The mid-plane blocks are still regular inside each block. The far plane is very flat.
6. **Trees.** The NE elm and the far-right grove trees still read as fairly round masses at 1×. Crown gaps are visible mainly on the NW and SE planes.
7. **Central walk.** It is unchanged from v02: uniform granite courses with no shade pools or polished lane, so it is the flattest large area in the frame.
8. **Lawn occupants** are hand-drawn at roughly half heroine height. Their faces are simple, and they have no idle animation. The drone is barely legible.
9. **The NE lawn** upper band (between the railing and the elm and locust) is still fairly open.
10. **Statue and plaque** are unchanged and generic. The 11 isolated bright texels in the backdrop are intentional or minor: LEDs, a skyline texel and facade accents. Rows 150–359 have 0.

## Technical gates: 43/43 PASS (`check --write-report`)

These are technical gates only, not art acceptance.

**Raster and editability**
- All 24 layers are 640×360 with binary alpha. The base is opaque and only palette colours are used (144 of 151 appear in the flat).
- The build is deterministic.
- `.pxo`: 24 named layers, guides hidden.
- `.ora`: `stack.xml` lists 24 layers with only guides hidden, and every layer PNG is byte-exact.

**Walkability and scene controls**
- 36,957 walkable texels, 30.7% of rows 172–359. v02 had 36,985.
  - 126 texels were lost: mainly the approach just north of the new fountain veil, plus the bench reader's foot collar on the south plaza.
  - 98 were gained: feet behind tall occluders that the corrected standing-on rule no longer blocks (the SE fg crown and the dogwood).
- Exits and Y-sort pivots are the same as v02. The 14 pins are the same except the two moved capture pins; the axis pin is unchanged at (320,292).
- The route is the same apart from waypoint 7, which is the moved fountain pin. It is 1,529 one-pixel steps, with 0 blocked and 0 jumps on both the Python mask and the exported mask in Godot.
- Feet stand only on paving, never in the backdrop or the basin. All pins are reachable.

**Depth and occlusion**
- Depth audit: 0 wrong-order feet, including every new occupant, the blanket, the shrub borders and the drone.
- Worst visibility is 0.538 at (438,258); the floor is 1/3.
- Seven Y-sort cases are correct.
  - Behind: fountain 151/151, statue 64/64, SE tree 156/156, west lamp 73/73.
  - Front: candelabra 66, plaque 338, lamp 61.
- There is no standing-on ambiguity at any walkable foot; 273 feet are blocked by the gate.

**Pixel clusters**
- 0 isolated bright flecks in rows 150–359.
- Single-texel islands: 1.57% in the park rows and 1.01% in the backdrop (v02: 1.34% and 0.98%).
- The ground despeckle pass changed 45 texels.

**48-px heroine and contact shadow**
- The actor is 48 px tall in Python and in Godot.
- The shadow is ≥ 12 visible texels in the axis and behind-tree captures (49 each). Behind the fountain it is 81% under the front sprite, with 9 texels visible.

**Pixelorama 1.2.3 headless** (5 runs, 4.7–5.1 s each)
- The `.pxo` flat export is exact and identical across two runs.
- `.pxo` and `.ora` split layers are byte-exact, and the split composite equals the flat image.
- The `.ora` flat export is exact. The hidden guides are not exported, and the sources are unchanged.

**Godot 4.7.2** (temp projects only)
- Headless texel gate:
  - layer hashes are exact;
  - 269 route stills hash-match the Python runtime stack;
  - the heroine is 48 px.
- Windowed GL Compatibility renders:
  - **1280×720**: all three captures are pixel-exact outside the contact shadow, with ≤ 1 channel unit inside it (112, 16 and 80 differing pixels, all in the shadow).
  - **640×360** (native 1×, new in v03): all three captures are pixel-exact outside the contact shadow, with ≤ 1 inside it (28, 4 and 20 differing pixels).
  - No `SCRIPT ERROR` lines appeared.

## Gate changes against v02 (disclosed)

1. **Standing-on rule fix.** v02 counted a covered row only when its hidden texels reached 40% of the widest lower-body row. The heroine's bottom row has 2 texels, so v02's run counter could never exceed 0: every wide foot-hiding occluder was flagged, however tall it was. v03 counts a row when ≥ 40% of that row's own texels are hidden, which matches the documented intent. The same fix is applied to the reported occlusion profile.
2. **Contact-shadow gate.** The gate is now `contact_shadow_visible_or_occluded_by_front_sprite`. The shadow needs ≥ 12 visible texels, unless ≥ 50% of its footprint lies under a sprite that is drawn over the actor. Only the behind-fountain capture uses the second branch.
3. **New render gate.** A native 640×360 windowed Godot render gate was added beside the 1280×720 one.

## Process notes

**Pixelorama isolation**
- Another session's Pixelorama GUI was open, and its autosave trips the builder's kill-switch. So `check` ran with the parent `APPDATA` pointed at an empty temp dir, as recorded in the workflow memory; each child process still got its own fake dir.
- I snapshotted the real `%APPDATA%\pixelorama` and `%APPDATA%\Godot` before and after the run. The only change was that GUI's `.running` heartbeat. No Godot `app_userdata` was created.

**Git status**
- Before/after `git status`: this run added only three entries (candidate dir, output dir, tool) plus this QA note.
- Other new entries in that window belong to parallel sessions: the Washington `wdc-cw-v08` candidate and its QA note, the female locomotion compact v02 files, and a Yonkers art-direction image. None of their files were touched.

**Builds**
- The candidate was built once; nothing was deleted or rebuilt in place. Previews went to `%TEMP%\wb-chp3\` only.

## Requested creator decisions

1. Is the two-tier overflow fountain the right read, or should it be a lower, wider basin feature closer to the real Mould fountain?
2. Are hero-scale lawn occupants wanted in the background art? Or should people be NPC sprites so they can animate?
3. Should the corrected standing-on rule be adopted for the other walkable pilots?
4. Is a GUI paint pass still required? The table-driven route is the same as in v02.

Until a creator review, v03 stays **UNAPPROVED / NONRUNTIME**, and scene art stays **0/11**.
