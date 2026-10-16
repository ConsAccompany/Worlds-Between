# Washington Capitol west grounds — walkable 640×360 camera candidate v05 (QA note, unapproved)

- **Date:** 2026-10-16. **Stamp:** `20261016-055159`. **Run id:** `ca6ec5f1`. **Run dir:** `wdc-cw-v05_20261016-055159-ca6ec5f1` (shortened so every path stays ≤ 250 characters).
- **Author:** Claude (Claude Code, Opus 5.5), signed-in claude.ai Max, firstParty only. No API key, no API billing, no image model, no paid fallback.
- **Status:** ONE **unapproved, test-only** candidate. It is not accepted art, it is not wired into any runtime scene, and it is not a creator acceptance. **Science scene art stays 0/11.**
- **Untouched:** runtime scenes/scripts/data/tests, the meter, the Game Bible, `docs/progress.md`, Git (nothing staged, committed or pushed), the City Hall workstream, v01–v04 and the cinematic vista v02.

## What this candidate is

One 640×360 logical gameplay camera, the size of `game/project.godot`'s viewport, shown by Godot at 1280×720 (integer 2×). The approved v8 female south idle is sampled 2:1 to the approved **48-logical-px** heroine. Top of frame = east (the Capitol); bottom = west (toward Union Square).

**Backdrop (not walkable).** The Capitol is inside the same camera the heroine walks in:
- the dome with the Statue of Freedom, tholos, ribbed cast-iron shell, attic drum, peristyle and stylobate;
- the West Front: central colonnaded pavilion over a rusticated arcade, centre blocks, corridors, and Senate/House wing porticoes;
- the Olmsted lower west terrace: balustrade with piers and urns, twin frontal stairs with bronze-lantern cheeks, the central shaded recess with its grotto arch and a dry planted fountain;
- the West Lawn rising toward the terrace foot, groves at both ends and mid-distance trees.

**Walkable plaza (rows ~203–359).** At the foot of the lawn:
- a curved Olmsted granite seat wall with a marble coping, and a three-step flight between two cheek piers (exit north);
- one collapsed bay of the wall with a rubble mound and a self-sown tree of heaven;
- a sett forecourt and a broken flagstone axis walk (exit south), plus worn desire paths (exits west and east);
- meadow turf, an old elm framing the top-left, the survey station, and the patrol cues listed below.

## Response to the v04 Codex audit

| v04 finding (`…wdc-capitol-west-v04-codex-visual-audit…a9d83f26.md`) | v05 |
|---|---|
| Entry view has no Capitol; the portico view is cut off and anonymous | All of these sit in the one walkable camera: <br>• the whole West Front, 168–575 px wide; <br>• the dome, fully in frame, with the statue tip at row 6; <br>• the terrace. <br>The Capitol spans rows 6–163 (**43.9 % of the frame height**); `dome_visible_share` is 0.98. The entry still (heroine at the bottom spawn) shows the full landmark. |
| Weak Capitol landmark / reads as a generic neoclassical ruin | The identity cues come from the official forms: the dome silhouette (peristyle, attic, ribbed shell, tholos, statue), the West Front central colonnade and wing porticoes, and the Olmsted terrace balustrade with twin stairs and a central recess. <br>References are the AOC [dome page](https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-building/capitol-dome) and [Olmsted Terrace page](https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-grounds/olmsted-terrace), both cited in the prior QA. They were used for forms only; nothing was copied. |
| Generic even paving and lawn | • **Forecourt:** setts in courses concentric with the curved wall; lengths of 9–13 px per course, staggered, mostly mid-tone joints. <br>• **Axis walk:** large flags in staggered courses. <br>• **Desire paths:** worn soil with a paler centre and grass creeping over the edges. <br>• Root heave from the elm, missing setts, turf invasion, a sinkhole near the collapse. <br>• **Meadow:** hand-placed tall-grass and goldenrod/aster clumps; dappled canopy shade from the elm and from trees behind the camera. <br>• **West Lawn:** world-space tufts that shrink with distance, darker tall-grass swaths, and a trampled patrol trail. |
| Repeated props | Every prop is a single hand-placed instance: <br>• survey mast, tripod lidar, field terminal on its crate, solar panel and two cases; <br>• the patrol beacon; <br>• a fallen Olmsted lamp standard, a fallen lantern head, a fallen elm limb; <br>• the balustrade fragment and the ivy block. <br>16×16 repetition share is **0.68 %** (v04: 0.84 %, same metric). |
| Pale chips read as noise | `no_isolated_bright_flecks_on_walkable_ground` passes (0 on the ground layers). There are 15 deliberate prop highlights near the walk: terminal screen, beacon bolts and lens, balustrade, fallen-lamp collar. They are reported separately, not hidden. |

## Depth: why the heroine and the building can share one camera

The scene is stated as **two projections joined at a hidden seam**. It does not claim a single perspective.

**Walkable plaza:** the game's 3/4 plane at 28 px/m (48 px = 1.7 m). That is the backdrop camera's scale at d ≈ 20 m, i.e. the plaza's far edge. Nearer ground is not enlarged (JRPG convention).

**Backdrop:** one pinhole, F = 552 logical px, eye 1.0 m, horizon row 178.4. The lawn rises 7 m from the wall (d = 20 m) to the terrace foot (d = 230 m). Ground at distance d sits at row `HZ + (EYE − e(d))·F/d`.

| element | distance | px/m | rows |
|---|---|---|---|
| seat wall, steps, cheek lanterns | 20 m | 27.6 | 192–238 |
| near lawn shrubs behind the wall | 20–30 m | 18–28 | 170–236 |
| mid trees | 45–110 m | 5–12 | 24–181 |
| patrol walker (2.2 m) | 70 m | 7.9 | 157–174 |
| Olmsted lower west terrace | 230 m | 2.4 | 137–163 |
| West Front | 310 m | 1.78 | 92–140 |
| dome (≈56 m behind the facade, so its drum is hidden behind the pavilion as seen from the lawn) | 366 m | 1.51 | 6–92 |

- Rows are hand-set within about ±10 % of this mapping. The dome is about 9 % taller than the mapping gives.
- The seam is covered by the seat wall and the shrubs behind it. Several cues carry depth: haze on the far lawn and terrace, cooler hazed groves, tree crowns that shrink from the near elm to the mid trees to the far groves, a 17-px walker, and the trail converging on the terrace recess.
- No v02 vista pixel is used. The v02 vista is a 1280×720 telephoto (F = 2800) from the Reflecting Pool; this camera is nearer, and every cluster here was placed for this camera.

## Files (all new; AGENTS naming, `rpg-2-star-ocean-the-second_wdc-capitol-west_<purpose>_unapproved-v05_20261016-055159-ca6ec5f1.<ext>`)

**Tool:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-camera-640x360_pixelorama-build_unapproved-v05_20261016-055159-ca6ec5f1.py`
- 3,579 lines, sha256-text-lf-v1 `bc4b6bb9e0e2d34941cbaf153423cb1ae4f481cd9d83aa7fa146f0d5dd7b0d58`.
- Modes: `preview <tempdir>` | `build` | `check [--write-report]`. Run with the runtime Python and `-I -B`.

**Candidate directory:** `game/assets/environments/candidates/wdc-cw-v05_20261016-055159-ca6ec5f1/` (sha256 of the bytes):

| purpose | what | sha256 |
|---|---|---|
| `scene-21layer.pxo` | native pxo_version 7: 1 frame, 21 named layers, `guides` hidden and locked | `37e55b6a5bf451cca480a6ce440c1077c7c19524dd2d52ac9f51fd74197822a7` |
| `scene-21layer.ora` | OpenRaster copy, `guides` hidden | `6bac83656f9c1d5430d3b3add1a37a5c8aeeb9c456e51dfb97ea629561d332ce` |
| `scene-flat-640x360.png` | flattened art layers | `8b9ab610f06e96a9a55c7b98c36ab0afa2dea75d7f38393de6f8d576665b75bb` |
| `scene-palette.gpl` | 119 hand-picked colours (116 used) | `6285dd9a161bd0b1608852d269b198b4dea439991a737b2726fdfa17385ee4a6` |
| `scene-walkmask.png` | collision mask: opaque = walkable foot texel | `f1c2696d2f861b9b53a0007d80723289dfc8d83a525d0704811a6607baf52b0d` |
| `scene-walkability.json` | 8-px cell grid, pins, 4 exits, 7 interactions, Y-sort pivots, collars, collision probes, route rule | `a15304c60d94129a469aa89c7665688dcbc6c0d4f5b972156c11c60d7100c45b` |
| `scene-manifest.json` | depth model and table, layers, palette, LOCK, static checks, file hashes | `5985851edf7742d26d20fcd941740b244ece71a2e0b1eec5a827667e1fd3b318` |

**Output directory:** `outputs/wdc-cw-v05_20261016-055159-ca6ec5f1/`. Every view is a separate file; there are no comparison sheets.

| capture (real windowed Godot 4.7.2) | heroine foot | sha256 |
|---|---|---|
| `godot-1280x720-entry` | spawn (372,350) | `7b667ffa464a5c5096a6357621216c197758e18724955c228e9f5780b244d9f4` |
| `godot-1280x720-vista` | stair foot (372,236) | `3d2e4883bb31e342a356a0b81aa2698559ef3c2b585a5a057c7fd3c606ac4814` |
| `godot-1280x720-survey-behind` | behind the tripod (238,264) | `991a3c41779dcaf2a192e560cd4ad4f65786cc6fd3bf3d4d892980c381ad5011` |
| `godot-1280x720-beacon-front` | in front of the beacon (528,320) | `d3504b3e03f663ecdbc407fc12b5b9a075f0e45cb7ce72094ec0cc138d3c0d93` |
| `godot-640x360-entry` | spawn | `492ed48efbcf06d339538f1c65038a9f889bde07a465549e9d549a98d9e8dabc` |
| `godot-640x360-vista` | stair foot | `ac6bd5f4c0012603d3fca65f7f72b838294eab495731bc2d22dabe9e1b5f46e1` |
| `godot-640x360-survey-behind` | behind the tripod | `90f68d75d73e908388cf4fc03f4c8e63ed45d663c458fac31350112d3382b1f1` |
| `godot-640x360-beacon-front` | in front of the beacon | `f7cb829cadaaf657a3990656166a237551f31328b8631ac3b5ffa8084105aebf` |
| `technical-check-report.json` | 46 gates and all details | `7418d18116a415b338af714a88343b6da8567724a572ac61f2c0a0b17a69df01` |

## Layer stack (bottom → top) and the proposed runtime draw order

1. **Base layers 1–15, merged into one base at runtime:**
   1. `sky` (opaque)
   2. `clouds`
   3. `capitol-dome`
   4. `capitol-west-front`
   5. `capitol-ruin`
   6. `olmsted-terrace`
   7. `west-lawn`
   8. `grounds-trees`
   9. `lawn-edge-planting`
   10. `seat-wall-steps`
   11. `plaza-ground`
   12. `ground-detail`
   13. `cast-shadows`
   14. `rubble-collapse`
   15. `props-low`
2. **Actor contact shadow.** This is a *proposal*, not approved art. It is a 9×2.6-px ellipse of ground texels drawn in their own SHADE colour, two steps darker in the core, with no semi-alpha.
3. **Y-sort layers 16–19, sorted together with the actor by pivot row** (the actor is drawn last on ties):
   - `survey-mast-ysort`, pivot 256
   - `survey-tripod-ysort`, pivot 276
   - `beacon-ysort`, pivot 306
   - `elm-ysort`, pivot 282
4. **Layer 20 `fg-occlusion`**, drawn over the actor: the balustrade fragment, the ivy block and the edge grass.
5. **Layer 21 `guides`:** hidden and locked, never exported.

## Walkability, collision, interactions

- **Walk mask:** 62,671 walkable texels, only on plaza ground and the steps; nothing at row 202 or above. Every art item that could cover the actor has a derived collar, plus footprint collars for Y-sort and fg objects.
- **Exits** (all reachable from spawn): `exit_north_steps` (the steps' top, to the lower west terrace), `exit_south` (the axis), `exit_west` (the First Street walk) and `exit_east` (the Maryland Avenue walk).
- **Interactions** (each pin lies inside its zone and is reachable):
  - `vista_point`
  - `survey_terminal`
  - `survey_scanner`
  - `patrol_beacon`
  - `collapse_cut_block` (the laser-cut granite)
  - `fallen_lantern`
  - `olmsted_plaque`
- **Collision probes:** 17 points must be blocked, and all are blocked in both the Python mask and the exported PNG loaded in Godot. They cover:
  - the seat-wall face, the lawn beyond the wall, both cheeks;
  - the rubble cone and a front block, the elm trunk;
  - the crate, the panel, the tripod feet, the mast foot, the beacon base, the lantern head;
  - both fg pieces, the terrace backdrop and the dome.
- **Heroine route:** 2,287 one-pixel steps through 52 waypoints: spawn, the steps and exit north, the plaque, behind the tripod and mast, the terminal, the elm, exit west, the beacon front and behind, the collapse, the lantern, exit east, and exit south.
  - Straight segments are used where clear. **8 segments use a local 8-connected detour** around collars; the rule is recorded in the JSON.
  - Godot re-walks every step on the exported mask: 0 blocked, 0 jumps over 1 px.

## Technical gates: **46 / 46 PASS** (`check --write-report`)

These are technical gates only. Passing them is not art acceptance.

**Static checks:**
- 640×360 in every layer; opaque base; binary alpha everywhere; palette only; the flat image is opaque and a subset of the palette.
- Heroine is 48 px; every walkable foot keeps ≥ 1/3 of the actor visible (worst 0.691).
- **Depth audit:** 82 registered items, 54,110 overlapping walkable feet, **0 wrong-order feet**.
- **Y-sort cases.** Behind (sprite drawn over her): tripod 140/140, mast 160/160, beacon 125/125, elm 45/45. Front (she is drawn over the sprite): tripod, beacon and elm.
- All pins reachable; route walkable; probes blocked; exits and interactions OK; 0 ground flecks; landmark ≥ 40 % of the frame height; dome and statue in frame.
- Deterministic double build; the `.pxo` stack is the 21 named layers; longest path < 260.

**LOCK:** read-only predecessors re-hashed: the v04 candidate and its 94 outputs, the v04 tool, QA note and Codex audit, the vista v02 candidate, outputs, tool, QA note and Codex audit, and the City Hall v01 candidate.

**Pixelorama 1.2.3 headless** (exe `6412014e…`; APPDATA redirected to temp for each run; kill-switch armed):
- `.pxo` flat ×2: exact and byte-identical.
- `.pxo --split-layers`: all 20 art layers byte-exact, and their composite equals the flat image.
- `.ora`: flat and split both exact.
- **Round trip:** an `.ora` rebuilt from Pixelorama's *own* split exports of the `.pxo`, then exported again by Pixelorama, equals the flat image.
- The hidden guides are never exported. The creator's open Pixelorama GUI (PID 50828) was never touched.

**Godot 4.7.2** (throwaway projects in `%LOCALAPPDATA%\Temp`, APPDATA redirected):
- All 20 layers load texel-exact.
- 401 runtime-stack stills (route samples plus pins) hash-equal the Python stack, including the shadow, the Y-sort and the fg overlay.
- Collision probes and pins pass on the exported mask.
- The **real windowed renders** (GL Compatibility, nearest, integer stretch) are pixel-exact against the Python stack:
  - at **1280×720**, 0 differing pixels in each of 4 captures;
  - at **640×360**, 0 differing pixels in each of 4 captures.
- Nothing was written to `%APPDATA%\Godot`, and no `.uid` or `.import` file appeared in the repo.

**Baseline / side effects:**
- 251 of the 252 Capitol, vista and City Hall files hashed before work still match.
- The one mismatch is `tools/…nyc-city-hall-park…_unapproved-v02_20261016-055120-59848a60.py`. Another session created it at 05:51:20 (City Hall workstream) and is still writing it; this run never opened it.
- The `git status` delta from this run is only the new tool, the candidate directory, the output directory and this note.

## My visual read (honest; not an acceptance)

**Stronger than v04:**
- At 1× the frame reads as *the U.S. Capitol's West Front seen from the foot of the West Lawn*. The dome silhouette, the colonnaded pavilion and the terrace stairs are recognisable in every camera position, because the camera never moves.
- The foreground tells the 2537 story without hiding the landmark:
  - collapsed seat-wall bay;
  - survey station aimed at the dome;
  - active beacon with scorch and claw prints;
  - fallen lamp;
  - meadow reclaiming the paving.
- The near elm, mid trees, hazed groves and the small walker give real depth layers.

**Still short of the target (逸剑风云决-level hand-painted finish). Not ready for creator acceptance:**
1. **Scale relation:** the West Front facade is about 48 px tall, the same as the heroine; the whole Capitol is about 3.3× her height. The depth cues help, but a viewer may still read the building as a model. The documented camera (facade at 310 m) is the justification.
2. **Rule-based facade:** the windows and columns are a mirrored half plus hand-assigned bay states. Damage on the central façade is light, and the dome breach is small.
3. **Horizontal structure:** sky, facade, terrace, lawn and wall still stack as bands. The terrace is a long continuous strip, broken only by the end groves and the stairs.
4. **Lower third:** mostly open meadow, kept on purpose for movement. Its texture comes from procedural tufts, and the off-screen canopy shade is subtle at 1×.
5. **Foliage:** the mid and far trees share one jittered 13-lobe template; the elm is hand-placed. The shrubs behind the wall read as a row of similar round bushes.
6. **Rubble:** the mound reads at 1× but its blocks are schematic boxes at 3×. The fallen lantern head reads as a dark bar.
7. **Heroine:** the approved south idle faces the viewer, away from the Capitol in the vista pose. A back-facing pose would need separate art review.
8. **Shadows:** the contact shadow is a proposal that needs a runtime decision (shader or prebaked).
9. **Authoring route:** not a Pixelorama GUI paint pass (no desktop access). The tables are hand-written and the `.pxo` is Python-written. A GUI open/save/reopen has not been done.

## Open creator decisions (no question was asked during the away window)

1. Accept the table-driven route for this candidate, or require a Pixelorama GUI polish pass starting from the 21-layer `.pxo`.
2. Accept the two-projection depth model (game plane plus documented pinhole backdrop), or ask for a larger Capitol with a smaller walkable area.
3. Adopt the actor contact shadow, and choose shader or prebaked.
4. Decide whether this single camera replaces the v04 multi-window room design, or becomes the entry screen of a sequence: the north exit leads to the lower west terrace.
