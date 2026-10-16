# Washington Capitol west grounds — v07 vista + texture merge (QA note, UNAPPROVED, NONRUNTIME)

- **Date:** 2026-10-16. **Stamp:** `20261016-145408`. **Run id:** `0f854fbc`. **Run dir:** `wdc-cw-v07_20261016-145408-0f854fbc`.
- **Author:** Claude (Claude Code, Opus 5.5), signed-in claude.ai Max, firstParty only. No API key, no API billing, no credits, no image model, no paid fallback.
- **Status:** ONE **UNAPPROVED, NONRUNTIME, test-only** candidate. It is not accepted art and not wired into any scene, script, data file, default or test. **Science scene art stays 0/11.** Codex inspects the captures before any human review; acceptance is the creator's.
- **Untouched:** runtime, the meter, the Game Bible (state, app, builder), `docs/progress.md`, M2 travel, character art, the Intuition proposal, and Git (nothing staged, committed or pushed). v06 and v05t are re-hashed by `check` (LOCK, all `match`).
- **Not done on purpose:** the Washington walkable range ("v01–v06") in the Game Bible state and the MVP progress state, and the Game Bible builder's canon check 28, still say v06. A later sync that admits v07 must update all three; this task was told not to touch them.

## Brief and decision

Codex compared both branches at gameplay size:
- v06 has the strong, recognisable dome, Capitol silhouette and city depth.
- v05t has better irregular lawn/terrace material and lighting, but a cropped dome and a generic repeated facade.

v07 therefore keeps **v06's vista composition and walkability exactly**. It transfers v05t's techniques selectively and does **not** continue v05t's composition.

**Did the merge harm v06's clarity? My judgement: no**, so the candidate is published rather than stopped. Evidence:
- The dome layer is byte-identical to v06.
- The West Front outline (alpha) is identical to v06.
- The camera, horizon and depth model are v06's.
- Dome-vs-sky luminance is 0.1485 (v06: 0.1473).
- Focal-vs-frame-foot luminance is 0.109 (v06: 0.097).

The 640×360 and 1280×720 captures read the same at a glance as v06's. The changes sit in the facade detail, the weathering and the lower third. This judgement is mine and is not an acceptance; Codex should check it against the captures.

## Route (read first)

- **Tool:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_vista-texture-merge_pixelorama-build_unapproved-v07_20261016-145408-0f854fbc.py`. It has 5,149 lines; sha256-text-lf-v1 `ddaf8213bd8ce59a27e1a4c04bea3ae777de220c4a867df4944c37d6dc210ee6`.
  - Modes: `preview <tempdir>` | `build` | `check [--write-report]`.
  - Run with the runtime Python: `-I -B`.
- **Fork of the v06 builder.** The fork point is pinned: v06 tool sha256-text-lf `aa7baec9…8e66` (gate `fork_point_is_the_pinned_v06_tool`).
- **v05t is never imported or run.** Its painters were read and re-implemented against v06's geometry and palette.
- **NOT a Pixelorama GUI paint pass.** There was no desktop or computer-use access to the GUI.
  - Every placement is a hand-written table entry, rasterised into named palette layers.
  - There is no continuous-colour image, no resizing and no generated image anywhere.
  - The `.pxo` opens as 24 editable layers. A GUI open/save/reopen has **not** been done.

## What changed against v06

| area | v06 | v07 |
|---|---|---|
| **Facade rhythm** (the specific ask) | Every bay of a section drawn by one rule: same window, same head, even column pitch, and an arcade at a fixed 8/10 px pitch across the whole width. | Every opening is assigned from a **small closed variant set**, by hand, per bay (102 openings, `facade_variant_summary` in the manifest):<br>• principal-floor windows **T** triangular pediment + balustered apron, **S** segmental, **L** cornice on consoles, **A** round head + keystone, **D** door-window + balcony;<br>• attic lights **q** square, **x** blind relief panel, **o** oculus.<br>Kind strings per section, palindromic about the axis like the real building: centre `ATSTDTSTA`, corridor `AAA`, wing `LTS·STL`, wing portico `LLDLL`, pavilion upper `LALA`.<br>Also: coupled outer pavilion columns `[308, 312, 324, 336, 348, 360]`; a tall central opening on the axis under the dome; a 55-arch ground-floor arcade aligned with the bays above (one bricked, one broken); a shallow frontispiece at each centre door-window; long-short quoins at the wing corners.<br>The 2537 states (`STATE_*`) still differ between the halves. **No random choice in the facade painter.** |
| **Facade material** (v05t technique) | Hashed weathering and 13 one-pixel streaks. | New `facade-weathering` layer: 25 hand-placed runs (rain one value step down with broken tails, soot tongues over burnt openings, rust under cramps and bent iron), 18 replaced / stained / algae blocks, and rising damp with a moss line above the terrace rail. The House-wing void is cut from it. |
| **Terrace wall** | Hashed 14 % tone scatter. | 20 hand-placed replaced/weathered blocks; rising damp with an irregular top and a moss line. |
| **Plaza turf** (v05t technique) | Checker-bordered noise zones plus one stamped tuft per jittered cell. | Hand-placed relief (11 forms + 1 swale) lit by the scene's front-left key, quantised into calm tone bands; band edges cut as grass-blade teeth; materials normal / damp / dry / shade.<br>Value falls toward the frame foot and sides; the turf round the paving is lit, so the eye runs up the axis.<br>Long grass only where an authored weight says so (wall foot, paving edges, frame edges, rubble, dry knoll). Tufts are generated (no stamps). |
| **Story ground** (v05t technique) | Flat soil bands. | New `terrain-patches` layer:<br>• worn desire lines along v06's two walks (soil, lit crown, shaded bank, pebbles with contact shade, grass islands, trampled fringe), plus a short forecourt→tripod track;<br>• **handcart ruts** from the forecourt to the survey kit, with a cracked dried puddle;<br>• four survey **soil cores** with lifted plugs;<br>• leaf litter in the elm's shade;<br>• a mossy wall-foot bed. |
| **Meadow** | Stamped blades. | Tussock clumps with a shaded front band; seed heads on the dry knoll; a sparse dark-green rush hollow (deliberately not teal: a v05t defect). |
| **Paving** | — | 9 hand-placed stained / replaced slabs on the axis and forecourt. |
| **Shadows** (v05t technique) | Hand boxes and segments. | Every registered standing object's silhouette is projected from its own contact row (sun behind the viewer's left, as in v06), with a darker contact core and blade-teeth edges on grass. This covers props, rubble blocks, the Ailanthus, the cheek piers (whose shadow now falls across the stair treads), the foreground balustrade/fern block, the mast/tripod/beacon sprites and the elm trunk. v06's elm-crown and off-screen shade pools are kept. |
| **Seat-wall ivy** (v05t technique) | Vertical f2/f3 stripes. | 10 ivy masses of wandering stems and lit leaf clusters with stone between the outer stems and a 1-px shadow on the ashlar. |
| **Rubble core** | 2-px value noise ("gravel static" at 1×). | Bed of irregular broken stones (tilted Voronoi cells, lit/rim per stone, dark crevices). The dressed blocks, drums and coping on top are v06's. |
| **Misc** | Cloud bank competed with the dome (v06 audit); Ailanthus read as bubble balls. | Cumulus bank lower (tops ~row 66 vs ~58) and mostly cl1/cl2; patrol walker's near front leg raised mid-stride with clods falling (motion cue, Codex v06 audit); Ailanthus lobes clustered. |

**Unchanged on purpose:** sky, dome, capitol-ruin overlay, West Lawn band, grounds trees and lamp standards, lawn-edge planting, props, Y-sort sprites, foreground occlusion, all collars and the walk contract.

Changed texels vs the v06 flat: 22.3 %. Per layer:

| layer | texels changed |
|---|---|
| plaza-ground | 44,078 |
| ground-detail | 11,031 |
| cast-shadows | 9,279 |
| capitol-west-front | 8,529 |
| rubble-collapse | 3,519 |
| clouds | 3,312 |
| olmsted-terrace | 2,707 |
| seat-wall-steps | 1,035 |
| patrol-walker | 134 |

`facade-weathering` and `terrain-patches` are new layers.

## Files (all new; no v06 or v05t file was overwritten)

**Candidate:** `game/assets/environments/candidates/wdc-cw-v07_20261016-145408-0f854fbc/` (sha256 of the bytes)

| purpose | sha256 |
|---|---|
| `scene-24layer.pxo` (pxo_version 7, 24 named layers, `guides` hidden + locked) | `4c2fb74272f2187482f98ac05866fd29bdfccfae8c835c7b35a3b4039f513e4c` |
| `scene-24layer.ora` | `825065c65c8bcecd49d335dc6ad777536b6814dfac0f6f88cb3fd1667b1a2a23` |
| `scene-flat-640x360.png` | `18836516e7711b5a8ce1a80d1a7101e7b6861d122b3837235a06ca0f440e563d` |
| `scene-palette.gpl` (v06's 132 colours, 131 used) | `13cd28392dc458d97286c110df7d2435ff2fa94b8883523c095bce954159ef31` |
| `scene-walkmask.png` (**byte-identical to v06's**) | `b43cefe0e74d93d1adc1eb939d186c05d899d4b2c0cc3d3fe53878dc87f2f73a` |
| `scene-walkability.json` | `3d7c4c4a5f5bc251c4fcdde96287c66c4fe827c4cdff5bd69a99fd477dc1d956` |
| `scene-manifest.json` | `61dfd0dda19f6338e90f8631d959d8a6e826e0246a964e9d9c1d3763c2d1f83a` |

**Outputs:** `outputs/wdc-cw-v07_20261016-145408-0f854fbc/`. Each view is a separate file; there are no comparison sheets.
- The `godot-*` files are real windowed Godot 4.7.2 renders (GL Compatibility, nearest, integer stretch).
- The `zoom*` files are nearest-neighbour crops of the Python flat, for evidence only.

| file | heroine foot | sha256 |
|---|---|---|
| `godot-1280x720-entry` | spawn (372,350) | `b003f812de5878fb8889bbcab73b840b3cf76c9ba317b7248981cd7d66fa8f77` |
| `godot-1280x720-vista` | stair foot (372,236) | `588236025aa13689af950bacca0208bddf65fb75d60e8a66eda8b47c24b7c57e` |
| `godot-1280x720-interact` | beacon front (528,320) | `7deb8eed3bc5eb380d34fcb2fde6b2eb3538a1470e1d01f270aacc65da999394` |
| `godot-1280x720-occlusion` | behind the tripod (238,264) | `1b14d074e56e4d41173f94ddb78aa76c8e10d1f45cb21ccfc9acab8e9e0f2c5b` |
| `godot-640x360-entry` | spawn | `545fa91df604f94d0fc23dc0d2a5f1c2e62ddf55e96653df553072b6eab519b8` |
| `godot-640x360-vista` | stair foot | `67d0f8119d56de2e6067b71b43585af727db74f1778e328c91825ab073d31d72` |
| `godot-640x360-interact` | beacon front | `54b86948818bb3b7a3b176509f31115abe9b3375524e34351e7992c304e6c3d9` |
| `godot-640x360-occlusion` | behind the tripod | `81b1b584690ad68bc94f3d10a2537de16215020fbef5a3c94a9da30d0a112f61` |
| `zoom3x-west-front-north-half` | — | `a1cb5b632ecf842ff39ed8de5041272a3ceeba9584b612770473d6d7346abf78` |
| `zoom3x-west-front-south-half` | — | `7279193a75c71f0631049aa22900ec6457278efd14dc07b1833fe42b883c0367` |
| `zoom2x-plaza-lower-third` | — | `e6fe2d719a866ecf455cf594702a3836bb916d4f3b04c37e1951307f623ed7cb` |
| `technical-check-report.json` | 60 gates and all details | `9e78c451aae6819e2b9552a3bcfd765d7dcdd683767bc18f09b47bdc8148435b` |

**Layer stack, bottom → top (24):**
`sky`, `clouds`, `capitol-dome`, `capitol-west-front`, **`facade-weathering`**, `capitol-ruin`, `olmsted-terrace`, `west-lawn`, `grounds-trees`, `patrol-walker`, `lawn-edge-planting`, `seat-wall-steps`, `plaza-ground`, **`terrain-patches`**, `ground-detail`, `cast-shadows`, `rubble-collapse`, `props-low`, then the Y-sort layers (`survey-mast-ysort` 256, `survey-tripod-ysort` 276, `beacon-ysort` 306, `elm-ysort` 282), `fg-occlusion`, `guides` (hidden, locked).
- Runtime proposal as v06: layers 1–18 merge into one base, then Y-sort with the actor, then `fg-occlusion`.

## Technical gates: **PASS 60/60** (`check --write-report`)

Technical gates only; passing them is not art acceptance.

**Static (22):**
- 640×360 in every layer; opaque base; binary alpha; palette only.
- Heroine 48 px; worst actor visibility 0.691.
- Depth audit: 82 items, 53,863 overlapping feet, 0 wrong-order feet.
- Y-sort behind/front cases correct: tripod 140/140, mast 160/160, beacon 125/125, elm 45/45.
- Pins reachable; route 2,285 steps (7 local detours); 17/17 probes blocked; exits and interactions OK.
- 0 ground flecks on walkable ground (71 despeckled; 14 deliberate prop highlights reported).
- Landmark 50.8 % of height; dome above the roofline 100 % visible; statue row 3; 3.81 heroine heights; facade 57 px.

**v07 against v06 (11):**
- `v06_and_v05t_untouched`: LOCK, 11 entries, all `match`.
- `fork_point_is_the_pinned_v06_tool`.
- `capitol_dome_layer_identical_to_v06`.
- `west_front_silhouette_identical_to_v06` (8,529 interior texels repainted).
- `walk_contract_identical_to_v06`: pins, exits, interactions, pivots, probes and route waypoints.
- `walkmask_identical_to_v06`: 0 differing texels.
- `facade_band_repetition_below_v06` (16×16 exact-repeat share, rows 95–170, x 60–639): **v06 2.93 % → v07 1.45 %**.
- `facade_openings_from_closed_variant_table`: 5/5 window kinds and 3/3 attic kinds, all from the closed set.
- `plaza_turf_calmer_than_v06` (single-texel colour islands on plaza grass): **0.128 → 0.060**.
- `focal_vs_frame_foot_contrast_not_below_v06`: 0.097 → 0.109.
- `dome_vs_sky_contrast_not_below_v06`: 0.1473 → 0.1485.

**Other (3):** `pxo_layer_stack_is_the_named_layers`, `build_deterministic` (two in-process builds), `max_path_under_260`.

**Pixelorama 1.2.3 headless (10):**
- exe `6412014e…`; APPDATA redirected per run; kill-switch armed.
- `.pxo` flat ×2: exact and deterministic.
- `.pxo` split: all 23 art layers exact, and their composite equals the flat.
- `.ora` flat and split: exact.
- **Round trip:** an `.ora` rebuilt from Pixelorama's own split exports re-exports to the exact flat.
- Hidden guides are not exported; the sources are unchanged.

**Godot 4.7.2 (14):** throwaway projects in `%LOCALAPPDATA%\Temp`, APPDATA redirected.
- Layers load texel-exact.
- 400 runtime-stack stills, 0 mismatched.
- Route on the exported mask: 0 blocked, 0 jumps.
- Probes blocked; pins walkable.
- **Windowed captures equal the Python stack: 0 differing pixels in all 4 at 1280×720 and all 4 at 640×360.**
- **Physics collision probe** (ported from v05t):
  - 217 exact `RectangleShape2D`s from the blocked mask.
  - 90 shape queries with an 11×3 foot box (21 expected blocked): 0 mismatches.
  - `CharacterBody2D` sweeps:
    - north up the axis from spawn: Godot 146.09 px vs Python 146;
    - east from axis_mid: 251.88 vs 252;
    - a short north sweep does not collide.
- Nothing was written outside temp.

**Isolation disclosure:**
- Another session's Pixelorama GUI (PID 50828) was open and was not touched.
- `check` ran with the parent `APPDATA` pointed at an empty temp dir. The guard also allows the GUI's own `.running` and `backups/` (v05t rule). No step was killed, and no foreign change was seen.
- My own before/after snapshot of the real `%APPDATA%\pixelorama` and `%APPDATA%\Godot` showed only:
  - `pixelorama/.running` (the GUI heartbeat);
  - `Godot/app_userdata/Worlds Between/logs/*` and `…/test-saves/m2/auto-00000258..266.json`, timestamped 15:13–15:15. These come from another session's game/M2 runs; new `m2-v11` outputs appeared at the same time.
  - No `cw7-*` project folder exists.
- The `git status` delta from this task is only the v07 candidate dir (7 files), the v07 outputs dir (12 files) and this note. The tool was written before the "before" snapshot and is also new and untracked. No `.uid` or `.import` file appeared.

## My visual read (honest; not an acceptance)

**Better than v06:**
- **Lower third.** Calmer sward with tonal masses instead of checker-bordered noise. The axis and forecourt are the lit focus, and the frame foot and sides fall darker. The ground tells a story: worn walks with pebbles and fringes, handcart ruts to the kit, soil cores, long grass where it would grow. The rubble core reads as broken stone rather than static.
- **Facade.** At 3× (zoom files) the bays read as a designed sequence: end bays, alternating pediments, a central door-window with a frontispiece, a coupled-column pavilion, and an arcade under the bays. The measured exact-repeat share halved.
- The cloud bank no longer pulls the eye from the dome; the walker shows a stride.

**Remaining defects (not ready for creator acceptance):**
1. **Facade variants are subtle at gameplay size.** Window heads are 1–2 px at 2.67 px/m. At 640×360 the West Front still reads as an even run of window slots (largely true of the real Capitol), and most of the Senate wing is hidden behind v06's grounds trees. The repetition metric halved; the 1× visual gain is modest.
2. **Turf tone bands** can look posterised / camouflage-like at 2×, notably the dark blobs at bottom centre. This is inherited from the v05t technique.
3. **Shadows are mostly hidden.** The projected shadows are geometrically consistent, but the sun is behind the viewer, so most of each shadow lies behind its object. The visible gain is mainly the elm trunk band, the cheek wedge on the stair and the rubble.
4. **Unchanged v06 parts:** the West Lawn band is still compressed (~20 rows; the camera decision stays open) and procedural. Some grounds-tree crowns (poplar, broken oak) still read as bubble lobes, and the stock-looking cumulus remains, now calmer.
5. **Small touches are below 1× readability:** seat-wall ivy masses, soil cores and litter.
6. **Rubble:** the dressed blocks on top are v06's box facets. The heap silhouette is unchanged.
7. **Heroine:** the approved south idle faces the viewer. The actor contact shadow is still a proposal.
8. **Authoring route:** table-driven Python, not a Pixelorama GUI pass (see Route).

## Open creator decisions

1. Accept v06's monument-scale low camera (compressed lawn), or trade Capitol height for lawn depth. Unchanged from v06.
2. Accept the table-driven route, or require a Pixelorama GUI polish pass starting from the 24-layer `.pxo`.
3. Whether stronger facade differentiation is wanted, beyond what the real building's even fenestration supports at 2.67 px/m. This would mean larger bay-width or height variants, not more surface detail.
4. Actor contact shadow: adopt, and choose shader or prebaked.

**Counter impact:** none. v07 is neither a runtime replacement nor approved scene art.
