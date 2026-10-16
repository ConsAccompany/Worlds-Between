# Washington Capitol west grounds — v08 ruin-state legibility (QA note, UNAPPROVED, NONRUNTIME)

- **Date:** 2026-10-16. **Stamp:** `20261016-155827`. **Run id:** `6cf49486`. **Run dir:** `wdc-cw-v08_20261016-155827-6cf49486`.
- **Author:** Claude (Claude Code, Opus 5.5), Environment art Workstream B.
  - Auth was verified before work: `claude auth status` showed claude.ai / firstParty / max, and `ANTHROPIC_API_KEY` was absent.
  - No API billing, credits, auto-reload, image model or paid fallback was used.
- **Status:** ONE **UNAPPROVED, NONRUNTIME, test-only** candidate. It is not accepted art and is not wired into any scene, script, data file, default or test. **Science scene art acceptance stays 0/11.**
- **Untouched:** runtime, the MVP meter, the Game Bible (state, app, builder), `docs/progress.md` and Git (nothing staged, committed or pushed).
  - Other sessions' female-walk and NYC City Hall files were not touched.
  - v07 (and v06/v05t) are re-hashed by `check`: LOCK, all `match`.
  - The Washington walkable range text ("v01–v06") in the Game Bible and progress state still needs its later sync (see the v07 note). That is out of scope here.

## Brief

Codex judged v07 at 640×360:
- the dome and layout read, and the ground is improved;
- but the building still feels overly intact and repetitive for the creator's direction.

The approved canon says: the whole of D.C. is abandoned; the Capitol grounds are recognisable, partially collapsed and overgrown; an active science survey outpost and patrol automata operate there.

v08 therefore keeps v07's composition, camera, plaza and walkability exactly. It changes only the Capitol backdrop, to make the ruin state visible at gameplay size.

## Route (read first)

- **Tool:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_ruin-state-legibility_pixelorama-build_unapproved-v08_20261016-155827-6cf49486.py`.
  - 5,748 lines; sha256-text-lf-v1 `f34c76389f730774b4857b003e6fe1832392e89a2b4e5a04cc1ae40327847b1c`.
  - It is both the author script and the check script. Modes: `preview <tempdir>` | `build` | `check [--write-report]`.
  - Run it with the runtime Python using `-I -B`.
- **Fork of the v07 builder.** The fork point is pinned: v07 tool sha256-text-lf `ddaf8213…0ee6`, gate `fork_point_is_the_pinned_v07_tool`.
- **Authored by code plus a Pixelorama round-trip. NOT painted in the Pixelorama GUI.** There was no desktop or computer-use access.
  - Every collapse, wall run, fragment, tree and story cue is a hand-written table entry, rasterised into named palette layers. There is no continuous-colour image, no resize and no generated image.
  - Pixelorama 1.2.3 was used headless only. Its `.pxo`/`.ora` flat and split-layer exports are texel-exact, and an `.ora` rebuilt from its own split exports re-exports to the exact flat.
  - A GUI open/save/reopen has **not** been done.
- **Clean-clone limitation:** v07 is untracked. v08's `check` reads v07's flat, `.ora`, walkmask and walkability JSON, so it needs v07 on disk and cannot run on a clean clone until v07 is committed.

## What changed against v07 (backdrop only)

Two **specific, differently-told** collapses. Neither is the mirror (x' = 743 − x) of the other, or of v07's House-wing bite.

| | A — south breach (x 466–562) | B — north end (x 65–121) |
|---|---|---|
| What fell | The outer five bays of the south centre section and the whole south connecting corridor are gutted down to the principal floor. The section-end pier is left standing as a "tooth". | The outer corner of the Senate wing fell long ago, down to the principal floor. A broken corner pier remains. |
| Through the gap | Pieces of the back (east) wall stand with empty windows showing sky. There are two party walls seen end-on, three broken floor slabs with shadow beneath, and a self-sown Ailanthus inside. | One standing back-wall fragment with a sky window. A mature tree grows up through the shell above the roofline. |
| Below | A fresh grey rubble cone buries the ground-floor arcade and the terrace balustrade (the **blocked arcade**). It holds recognisable pieces: a 9 m cornice length, a fallen wall piece with its window and sill, a balustrade length, column drums and blocks. | An old spill over the terrace, grassed over into a calm mound. A few dressed blocks still show, with scrub. |
| Weathering / vegetation | Scorch tongues at the breach edges (blasted, not just decayed), scorch on the cone crest, weeds and scrub on the lower slopes. | Ivy re-hung from the broken lip in four curtains. |
| Story | **Patrol:** the v07 walker now stands guard in front of the breach. A patrol relay with a red light is bolted to the tooth. A long-dead walker lies half buried in the cone.<br>**Survey:** an orange spray X on the intact wall at the breach edge, two safety-orange pennant stakes and a cyan prism pole on the cone, and striped safety tape on posts along the terrace foot. | Nature's side: no machines, no survey marks. |

Also:
- Three small balustrade losses (sky notches at x 148–156, 284–292 and 446–451) and an ivy curtain on the north centre section. The roofline is no longer one intact run.
- Broken masonry is drawn as stepped courses: lit treads, lit left-facing risers, shaded right-facing risers. A smooth 1-px lit diagonal read as a garland in the first preview, so it was replaced.
- Two grounds trees moved right so they no longer hide breach A: the broken oak (548 → 588) and the poplar (492 → 568).
- **Unchanged on purpose:** the dome, the central pavilion (x 306–437), sky, clouds, West Lawn, patrol walker, terrace, every walkable-plane layer, Y-sort sprites and foreground.

**Layer stack (26, bottom → top):**
- `sky`, `clouds`, `capitol-dome`, **`breach-interiors`** (new, below the front), `capitol-west-front`, `facade-weathering`, `capitol-ruin` (adds the lips, blown windows, scorch, ivy, X and relay);
- `olmsted-terrace`, **`breach-rubble`** (new: both cones, fragments, survey and patrol cues), `west-lawn`, `grounds-trees`, `patrol-walker`;
- then v07's plane, Y-sort, `fg-occlusion` and `guides` (hidden, locked).

The runtime proposal is unchanged: the base layers merge, then Y-sort with the actor, then `fg-occlusion`.

## Files (all new; no v07/v06/v05t file overwritten)

**Candidate:** `game/assets/environments/candidates/wdc-cw-v08_20261016-155827-6cf49486/` (sha256 of the bytes)

| purpose | sha256 |
|---|---|
| `scene-26layer.pxo` (pxo_version 7, 26 named layers) | `11b67b5f617e633afe4585d1a4a72ef88392ae9db0a149c8b5ed46d623357317` |
| `scene-26layer.ora` | `0770387fa3fa971654c748bffbefd60a1e6498a6e286e3f29a6da83b8e4580e1` |
| `scene-flat-640x360.png` | `b8f007d23da24834a7274ea836def70340071e4225764ca0cddc8d29b1f4d681` |
| `scene-palette.gpl` (v07's palette, no new colours) | `e57a81969c484431f694872ea333e96420507c67e4e312c51e6c9b56b91ee2e5` |
| `scene-walkmask.png` (**byte-identical to v07 and v06**) | `b43cefe0e74d93d1adc1eb939d186c05d899d4b2c0cc3d3fe53878dc87f2f73a` |
| `scene-walkability.json` | `91252f132a8ef8ccbc15110277b0ef108022d3522a9094d60174dd5886cdc21f` |
| `scene-manifest.json` (includes the `v08_ruin_tables`) | `2dc9515ddddd32f27a435bbcd5c4c0aa2264a90be817c6cd77d579cc442e1636` |

**Outputs:** `outputs/wdc-cw-v08_20261016-155827-6cf49486/`. Each view is a separate file; there are no comparison sheets.
- The `godot-*` files are real windowed Godot 4.7.2 renders.
- The `zoom*` files are nearest-neighbour crops of the flat, for evidence only.

| file | heroine foot | sha256 |
|---|---|---|
| `godot-640x360-entry` | spawn (372,350) | `b566a88a4c666c81d5f3b5cea33956685e966c2dbbd1ffa3ad4fa9b4f3c3deab` |
| `godot-640x360-vista` | stair foot (372,236) | `049dbcf3be245f4277cd116057fd7cf3eeef71d38f31399d46677ec249423af6` |
| `godot-640x360-interact` | beacon front (528,320) | `01dafc195923b74b3c0ad1f65f1379f1854a445994cd44fb5f6d006ea0c924e6` |
| `godot-640x360-occlusion` | behind the tripod (238,264) | `b331a65f352bde3b95d27886cba464f0394f260024d348ac2dd074d570d36f23` |
| `godot-1280x720-entry` | spawn | `df64a3c61e9d54f5ffb5d8fba1434fbc47adc33d444a7874072e50c9127787c7` |
| `godot-1280x720-vista` | stair foot | `be41c490bf4a84f70243b4e4c735ab3eac757c4214cc40aae2f106ec64b9f21e` |
| `godot-1280x720-interact` | beacon front | `ef9d4f8b33841de8e481f89ccf1c9bb7199f5543243ef15a3a05831853375158` |
| `godot-1280x720-occlusion` | behind the tripod | `7f7704b3c04d90bf9baf781dfee22dedd35791cff1240987e72781beb9a6df0d` |
| `zoom4x-breach-a-south` | — | `322447e03d518086919256cfa20ffa7343d13b3e7befa8e2bd3edd030b64033a` |
| `zoom4x-breach-b-north` | — | `73c00141985bf984a8e9ba2f83b679e5c0d791b5ae14889d59f88b808109c091` |
| `zoom3x-west-front-north-half` | — | `f3336c9283879634dfae74275c8a49ff2e7ed481e0aedf1f9d4a1be072ae2cca` |
| `zoom3x-west-front-south-half` | — | `25671d3686d4eef4083310d524e7eba5c4acd6095ff5f59e0162985bc8bead4f` |
| `technical-check-report.json` | 67 gates and all details | `8cb55c2d0d8056489bfc329ae222d2443111f662a9350da4cfd08ebdfa9de3c6` |

## Technical gates: **PASS 67/67** (`check --write-report`)

Technical gates only; passing them is not art acceptance.

**Static (22), unchanged results from v07:**
- Heroine 48 px; worst actor visibility 0.691.
- Depth audit: 82 items, 0 wrong-order feet.
- Y-sort behind/front cases correct; route 2,285 steps; all collision probes blocked; exits and interactions OK.
- 0 ground flecks on walkable ground.
- Landmark 50.8 % of frame height; dome above the roofline 100 % visible; 3.81 heroine heights; facade 57 px.

**v08 against v07 (16):**
- `v07_v06_v05t_untouched`: LOCK, all `match`.
- `fork_point_is_the_pinned_v07_tool`.
- `capitol_dome_layer_identical_to_v07`.
- `central_pavilion_and_dome_columns_identical_to_v07`: flat rows 0–199, x 306–437.
- `west_front_only_cut_inside_declared_voids`: 2,487 texels removed, 0 outside the voids; no texel repainted or added. `facade_weathering_only_cut_inside_declared_voids`: 96 removed.
- `sky_dome_lawn_walker_and_every_walkable_plane_layer_identical_to_v07`: 18 layers, byte-identical.
- `walk_contract_identical_to_v07`: pins, exits, interactions, pivots, probes, route, the 8-px cell map and collar counts. `walkmask_identical_to_v07`: 0 differing texels.
- `two_specific_breaches_readable_at_640x360` (details below).
- `roofline_no_longer_one_continuous_run`, `backdrop_less_mirror_symmetric_than_v07`, `backdrop_band_repetition_not_above_v07`, `no_added_pixel_noise_in_backdrop`.
- `dome_vs_sky_contrast_not_below_v07`, `focal_vs_frame_foot_contrast_not_below_v07`, `dome_still_brighter_than_new_ruin_accent`, `heroine_contrast_not_below_v07_at_every_capture_pin`.

**Other (3):** `pxo_layer_stack_is_the_named_layers`, `build_deterministic`, `max_path_under_260`.

**Pixelorama 1.2.3 headless (10):**
- `.pxo` flat exact ×2 (deterministic); `.pxo` split: all 25 art layers exact, and their composite equals the flat.
- `.ora` flat and split exact.
- Round trip: an `.ora` rebuilt from Pixelorama's split exports re-exports to the exact flat.
- Hidden guides are not exported; the sources are unchanged; isolation held (guard never fired).

**Godot 4.7.2 (13 + 3 physics):**
- All 25 layers load texel-exact; 400 runtime-stack stills, 0 mismatched.
- Route on the exported mask: 0 blocked, 0 jumps; probes blocked; pins walkable.
- **Windowed captures equal the Python stack: 0 differing pixels in all 4 at 1280×720 and all 4 at 640×360.**
- Physics: 217 `RectangleShape2D`s; 90 shape queries, 0 mismatches. Sweeps: north from spawn 146.09 vs 146, east from axis_mid 251.88 vs 252, the short sweep is clear.
- Nothing was written outside temp.

**Isolation disclosure:**
- Another session's Pixelorama GUI (PID 50828) was open and was not touched.
- `check` ran with the parent `APPDATA` pointed at an empty temp dir. Each child gets its own fake dir.
- My before/after snapshot of the real `%APPDATA%\pixelorama` and `%APPDATA%\Godot` (240 files) changed only in `pixelorama/.running`, the GUI's own heartbeat.
- My `git status` delta is only the v08 candidate dir, the v08 outputs dir, the v08 tool and this note. Other untracked files that appeared during the run (Yonkers outskirts, NYC City Hall v03 tool, female south locomotion v02 tool) belong to other sessions. No `.uid` or `.import` file appeared.

## Quantified against v07

| measure | v07 | v08 |
|---|---|---|
| Longest unbroken designed roofline run (px; v07's House bite counts as broken) | 499 | **153** |
| Roofline columns lowered | — | 162 |
| Breach A: removed wall / visible at 1× / width / max drop | — | 1,419 texels / **99.2 %** / 89 px / 34 rows |
| What shows where A's wall was (sky / gutted stone / inner tree / nearer layers) | — | 44.5 / 34.4 / 20.3 / 0.8 % |
| Breach B: removed wall / visible at 1× / width / max drop | — | 996 texels / **100 %** / 54 px / 31 rows |
| What shows where B's wall was | — | 65.0 / 16.0 / 19.1 / 0 % |
| v07 House-wing bite visible at 1× | 60.3 % | **51.7 % (regression: the moved trees now stand in front of it)** |
| Mirror-equal share, backdrop band rows 95–185, x 104–371 vs 743 − x | 0.369 | **0.309** |
| 16-px exact-repeat share, backdrop band (rows 95–185) | 1.19 % | 1.04 % |
| 16-px exact-repeat share, v07's facade band (rows 95–170) | 1.45 % | 1.27 % |
| Vegetation share in the backdrop band | 26.9 % | 28.6 % |
| Single-texel colour islands, rows 0–199 (noise) | 0.0787 | 0.0770 |
| Dome-box vs sky contrast | 0.1485 | 0.1485 |
| Visible dome luma minus breach-A region luma | 0.106 | 0.102 (dome still clearly the brightest mass, slightly less margin) |
| Focal vs frame-foot contrast | 0.109 | 0.109 |
| Heroine vs backdrop contrast (entry / vista / interact / occlusion) | 0.263 / 0.325 / 0.185 / 0.220 | identical |
| Flat texels changed | — | 3.69 % (all in the backdrop: front −2,487, weathering −96, ruin overlay 1,697, grounds trees 3,367, plus the two new layers) |

## My visual read of the real Godot 640×360 captures (honest; not an acceptance)

**Better than v07:**
- The right third now reads as a ruin at 1×: a stepped break in the roofline, a dark gutted shell with sky-lit back windows, a standing pier with a red light, and a grey heap at the patrol walker's feet.
- The north end of the Senate wing has a broken corner with a tree above the roofline.
- The roofline is broken in five places instead of one, and the backdrop is measurably less mirror-symmetric.
- The dome, the central pavilion and the 48-px heroine read exactly as in v07.

**Remaining visual defects (not ready for creator acceptance):**
1. **The ruin read is still moderate at 640×360.**
   - Breach A is mid-grey against light marble. Most of its heap sits behind the dark patrol walker, so walker and heap merge into one dark-grey mass at 1×.
   - The centre 60 % of the West Front is still intact and evenly fenestrated. This was kept on purpose for recognisability, so "repetitive" is only partly answered.
2. **Breach B is subtle at 1×.** It is at the frame edge, its lower part behind v07's left grove masses, and its tree blends with the other greens. It reads only on a close look (see the zoom4x file).
3. **Survey cues are 1–3 px specks at 1×.** The X, pennants and tape share safety orange with the walker's hazard stripe, so at gameplay size the survey-versus-patrol contrast is ambiguous. The dormant walker in the cone reads only as a dark lump.
4. **Cone A** has a light crest rim that traces the mound outline, and its stones sit on a jittered grid that can look laid at 4×. Cone B's grass mound is calm but a little smooth.
5. **The interior lighting is an artistic choice, not physical.** The back walls' inner faces would be sunlit under this light; they are drawn as hazed mid-darks so the shell reads.
6. **Regression:** v07's House-wing bite is now 51.7 % visible (was 60.3 %), because the broken oak and poplar moved in front of it.
7. **Inherited from v06/v07:** compressed West Lawn (camera decision open), procedural lower third, stock-looking cumulus, some bubble-lobed grounds-tree crowns, rule-based facade rhythm, and the open actor contact-shadow decision.
8. **Authoring route:** code tables plus a Pixelorama round-trip, not a GUI paint pass.

## Open creator decisions

1. Is this level of collapse right, or should the ruin go further into the centre? Going further trades Capitol recognisability for ruin. v08 keeps the dome and central pavilion intact by design.
2. Accept the table-driven route, or require a Pixelorama GUI polish pass from the 26-layer `.pxo`?
3. Should the survey cues get a distinct accent (for example teal tape or a larger marker board) so they don't share orange with the patrol walker?
4. Carried over: the monument-scale camera versus lawn depth, and the actor contact shadow.

**Counter impact:** none. v08 is neither a runtime replacement nor approved scene art.
