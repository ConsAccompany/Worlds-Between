# Washington Capitol west grounds — v09 collapse legibility (QA note, UNAPPROVED, NONRUNTIME)

- **Date:** 2026-10-16. **Stamp:** `20261016-210618`. **Run id:** `b1f062a8`. **Run dir:** `wdc-cw-v09_20261016-210618-b1f062a8`.
- **Author:** Claude (Claude Code, Opus 5.5), dispatch `3ec287fa` **Stream B only**.
  - Auth was verified before work: `claude auth status` showed claude.ai / firstParty / max, and `ANTHROPIC_API_KEY` was absent.
  - No API billing, credits, auto-reload, image model or paid fallback was used.
- **Status:** ONE **UNAPPROVED, NONRUNTIME, test-only** candidate. It is not accepted art and is not wired into any scene, script, data file, default or test. **Science scene art acceptance stays 0/11.** No counter or meter changed.
- **Not touched:** v08 sources and outputs (re-hashed by `check`: LOCK `match`), runtime defaults, character art, map code, the Game Bible, progress state and Git (nothing staged, committed or pushed).
  - An earlier session's untracked, never-built draft `tools/…central-decay-overgrowth…v09_20261016-180014-08377856.py` was **not** used, forked or modified. Its preview crashes in its v07-comparison step (`KeyError: 'facade-decay'`). Its paint-loss patches did not make the collapse read at 1×.

## Brief

Codex's appendices in the v08 QA note, the 11-scene audit `7359fdd2`, the transfer brief `8f6a2c10` and the Wandering Sword benchmark `714c8beb` all say the same things about v08 at 640×360:
- the dome reads, but the facade and terraces still look too intact;
- breach A is mid-grey on light marble, and its heap merges with the dark patrol walker;
- breach B is subtle at the frame edge;
- the survey cues are 1–3 px specks that share the walker's safety orange;
- the long white terrace reads as sound (it should have one failed span tied to the facade damage);
- Washington needs exposed masonry and a small temporary survey station, so it does not read like NYC's tidy park.

## Route (read first)

- **Tool:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_collapse-legibility_pixelorama-build_unapproved-v09_20261016-210618-b1f062a8.py`.
  - It is both the author script and the check script. Modes: `preview <tempdir>` | `build` | `check [--write-report]`. Run it with the runtime Python using `-I -B`.
- **Fork of the v08 builder.** The fork point is pinned: v08 tool sha256-text-lf `f34c7638…7b1c`, gate `fork_point_is_the_pinned_v08_tool`.
- **Authored by code plus a Pixelorama round-trip. NOT painted in the Pixelorama GUI.** There was no desktop or computer-use access.
  - Every collapse line, back-wall guide, window row, block, cue and outpost part is a hand-written table entry, rasterised into named palette layers. There is no continuous-colour image, no resize and no generated image.
  - The `.pxo` opens in Pixelorama as 28 named, editable layers. A GUI open/save/reopen has **not** been done.
- **No new colours.** The palette (`.gpl`) is v08's; survey teal `t0–t2` and white `fl2`/`m6` already existed.

## What changed against v08

The camera, sky, clouds, dome, central pavilion (x 306–437), patrol walker, plaza and every walkable-plane layer are unchanged. So are the pins, exits, interactions, Y-sort pivots, collision probes and the walk mask.

| | v08 | v09 |
|---|---|---|
| Breach A (south centre bays + corridor) | Cut to rows ~126–140; hazed mid-grey back walls (dm1) | Cut deeper (union with v08's cut, x 446–562, down to row 158 at its west end). The burnt-out shell is **charred dark** (sc1, soot runs sc0) with a stepped broken top and sky-lit window holes on two storeys. Party walls end-on, three surviving slabs, an Ailanthus, ivy and scrub on the lips, more scorch. |
| Spill cone A | Grey (dm1–dm4), scorch on the crest right behind the walker's back | **Pale broken marble** (dm3–dm6, dark crevices). It starts at x 478, so it pours out of the failed terrace span, and it stays behind the walker's head and hull. Crest scorch removed. |
| Terrace | Continuous | **One failed span** (new layer `terrace-breach`, x 466–501, rows 149–185) under breach A's west end. It exposes the dark granite-rubble core and soil, with a balustrade length hanging from the west stub and two pale blocks at the toe. The front above it is cut down to the terrace, so **one dark gash runs from the broken roofline to the terrace foot**. |
| Breach B (Senate-wing north corner) | Cut to row ~141; pale-ish interior; green tree like its neighbours | Cut to row ~150. Dark weathered shell (dw0) with moss clumps and sky-lit windows. The tree inside is now **yellow-green** (a different species from the hazed grounds trees). |
| Survey cues | Safety orange (X, pennants, tape, stakes, string, a hard case, the tripod LED) | **Survey teal + white** everywhere: a 7×7 teal X, teal/white pennants, prism and cordon tape; the plaza stakes, string, case and tripod LED recoloured. Same alpha; colour changes only. |
| Survey outpost | — | New layer `survey-outpost` on the non-walkable West Lawn behind the seat wall (d ≈ 34 m, ≈ 16 px/m). It has a white field shelter with a teal valance, side walls and a dark open front (console glow, rack LEDs, field table), a black-and-white quadrant target on a tripod, a whip antenna with a pennant, and teal cases. |
| Patrol | Orange hazard stripe, red eye/lights | Unchanged (walker layer byte-identical; beacon, relay and terrace sentinel keep orange and red). v08's half-buried dead walker is **dropped**. Wherever it fit on the pale cone, it touched the live walker or the dark gap and merged with them. |
| Backdrop trees | — | The broken oak moves 588 → 628 and the poplar 568 → 236; they hid breach A's corridor end and v07's House-wing bite. The magnolia moves 128 → 40; it hid breach B. |

**Layer stack (28, bottom → top):**
- `sky`, `clouds`, `capitol-dome`, `breach-interiors`, `capitol-west-front`, `facade-weathering`, `capitol-ruin`;
- `olmsted-terrace`, **`terrace-breach`** (new), `breach-rubble`, `west-lawn`, `grounds-trees`, **`survey-outpost`** (new), `patrol-walker`;
- then v08's plane, Y-sort, `fg-occlusion` and `guides` (hidden, locked).

The runtime proposal is unchanged: the base layers merge, then Y-sort with the actor, then `fg-occlusion`.

## Files (all new; no v08/v07/v06/v05t file overwritten)

**Tool:** 6,344 lines, sha256-text-lf-v1 `98b3a959f588b741b0645e045f5016eb2aa538407ccee4fcac218cb4f98eb4a4` (also recorded in the manifest).

**Candidate:** `game/assets/environments/candidates/wdc-cw-v09_20261016-210618-b1f062a8/` (sha256 of the bytes)

| purpose | sha256 |
|---|---|
| `scene-28layer.pxo` (pxo_version 7, 28 named layers) | `d4b03e100a40499448dd791f0229b04ddfec711f6c8320043cf8d833bedecdb5` |
| `scene-28layer.ora` | `8871e6ae4c7cfca6f1d7d369313abd9c5a242c15b3584295982cddd0f32e8c87` |
| `scene-flat-640x360.png` | `bd6417ce026a184d65a06cd0acf167cbbc565c1a03fc2618432bf3c1cb9f5157` |
| `scene-palette.gpl` (v08's colours; only the `Name:` line differs) | `e330b327a143bc2ba9df48c3864853be52cbde9d2e1f7be5dd8224d9c777a6fa` |
| `scene-walkmask.png` (**byte-identical to v08, v07 and v06**) | `b43cefe0e74d93d1adc1eb939d186c05d899d4b2c0cc3d3fe53878dc87f2f73a` |
| `scene-walkability.json` | `ee3df48c30503cc93d6ad3ba759e6d30898db20e011448ce5a030fb5d1d28d7c` |
| `scene-manifest.json` (includes `v09_collapse_tables`) | `21e591df1824e7dd31d02950968e2531effcc98d9394005c3864c680cfc29921` |

**Outputs:** `outputs/wdc-cw-v09_20261016-210618-b1f062a8/`. Each view is a separate file; there are no comparison sheets.
- The `godot-*` files are real windowed Godot 4.7.2 renders.
- The `zoom*` files are nearest-neighbour crops of the flat, for evidence only.

| file | heroine foot | sha256 |
|---|---|---|
| `godot-640x360-entry` | spawn (372,350) | `7aa0985107811dc471ff7f8ec80707a91004c450338c63b863006ec3a7ce33e7` |
| `godot-640x360-vista` | stair foot (372,236) | `2fc9e00c6487fdbb0d09f5f84620002372e74a064800cea9ffefcb63a3ed70e2` |
| `godot-640x360-interact` | beacon front (528,320) | `e4672f4345cc6fe27573aa09f249c46fa7a40bf89a29c2bc5075cc078392ed97` |
| `godot-640x360-occlusion` | behind the tripod (238,264) | `c3a898eaeadc1e383c04a0e90a26c31dae83f18d6536cb15507c1f21f633a2b4` |
| `godot-1280x720-entry` | spawn | `06a6cf62169275ed6053b30e3737296addc6a61720c5ca3117104c65359437ab` |
| `godot-1280x720-vista` | stair foot | `3f342ccd03132e284d1da2bb715e49600fff4b777ccf26b4035a85b4cdd243dd` |
| `godot-1280x720-interact` | beacon front | `953558f926a0551a164e796fa4b509f9e232eb6c666455510b8cf25fb7795446` |
| `godot-1280x720-occlusion` | behind the tripod | `23d9e46b950c8ca28a651a9a047182b5ad59bf9465313b7faa36cb40fe3390bf` |
| `zoom4x-breach-a-south` | — | `e9b087bdf0a5c1ae9a5a4e651935fcbf22e6e0ec6f822e0090a24ad032476181` |
| `zoom4x-breach-b-north` | — | `d4a06e22d2aa04ed8d2a53925ede08c6c94cd0a99fdb82ea3961deffa640d882` |
| `zoom4x-survey-outpost` | — | `752e6abfd0ce965b238146cc94736df370a04fffdd684e1660b6317295fb7bb9` |
| `zoom3x-west-front-north-half` | — | `7251b068bff034664ab4e140df2711000db147eefcee315978f5118cbc0b5d2e` |
| `zoom3x-west-front-south-half` | — | `609f8cc07df70a49c89bd3de56b4d321b4ba0f064cba2d994162f575645f90a6` |
| `technical-check-report.json` | 76 gates and all details | `83016ff90c1efafb68d81419027f4bd8b4453a3366cdecf26085e56d8d3fe067` |

## Technical gates: **PASS 76/76** (`check --write-report`)

These are technical gates only. Passing them is not art acceptance.

**Static (22), results unchanged from v08:**
- Heroine 48 px; worst actor visibility 0.691.
- Depth audit: 82 items, 0 wrong-order feet.
- Y-sort behind/front cases correct.
- Route 2,285 steps, fully walkable.
- All collision probes blocked; every exit and interaction zone reachable.
- 0 ground flecks on walkable ground.
- Landmark is 50.8 % of frame height; the dome above the roofline is 100 % visible; 3.81 heroine heights; facade 57 px.

**Build/lock (4):**
- `pxo_layer_stack_is_the_named_layers` and `build_deterministic`.
- `v08_v07_v06_v05t_untouched`: LOCK, all 18 entries `match`.
- `fork_point_is_the_pinned_v08_tool`.

**v09 against v08 (25).** What must not change:
- `capitol_dome_layer_identical_to_v08`.
- `central_pavilion_and_dome_columns_identical_to_v08`: flat rows 0–199, x 306–437.
- `sky_dome_lawn_walker_and_walkable_plane_layers_identical_to_v08`: 15 layers byte-identical, including `patrol-walker`, `rubble-collapse` and `fg-occlusion`.
- `cast_shadows_identical_on_the_walkable_plane`: 0 texels changed anywhere.
- `walk_contract_identical_to_v08`: pins, exits, interactions, pivots, probes, route, 8-px cells and collars.
- `walkmask_identical_to_v08`: 0 differing texels.

What may change, and only inside declared voids:
- `west_front_only_cut_inside_declared_voids`: 2,476 texels removed, 0 outside the voids, nothing repainted or added.
- `facade_weathering_only_cut_inside_declared_voids`: 165 removed.
- `olmsted_terrace_only_cut_inside_the_declared_span`: 574 removed.
- `terrace_span_fully_filled_no_see_through_hole`: 797/797 span texels filled; 0 texels outside the declared paint box.

Survey versus patrol:
- `survey_recolour_keeps_alpha_and_only_turns_orange_to_teal_white`: 167 texels in `props-low` and 1 in `survey-tripod-ysort`. The alpha is identical, every changed texel was orange before, and every one is teal or white now.
- `survey_cues_carry_no_patrol_orange_or_red_and_patrol_keeps_them`: 0 orange/red texels in any survey cue. The walker keeps 16 orange + 12 red texels, and the beacon 18 + 20.

Legibility at 1× (see the next table):
- `breach_a_dominant_dark_collapse_readable_at_640x360`, `breach_b_deeper_and_darker_than_v08`, `one_terrace_span_visibly_failed_at_640x360`.
- `walker_reads_as_a_silhouette_not_one_mass_with_the_rubble`, `survey_outpost_is_a_readable_silhouette_small_against_the_capitol`.

Composition and value guards:
- `roofline_run_not_longer_than_v08`, `backdrop_not_more_mirror_symmetric_than_v08`, `backdrop_band_repeated_windows_not_above_v08`, `no_added_pixel_noise_in_backdrop`.
- `dome_vs_sky_contrast_not_below_v08`, `focal_vs_frame_foot_contrast_not_below_v08`, `dome_still_brighter_than_the_ruin_accent`, `heroine_contrast_not_below_v08_at_every_capture_pin`.

**Other (1):** `max_path_under_260`.

**Pixelorama 1.2.3 headless (10):**
- `.pxo` flat exact ×2 (deterministic); `.pxo` split: all 27 art layers exact, and their composite equals the flat.
- `.ora` flat and split exact.
- Round trip: an `.ora` rebuilt from Pixelorama's split exports re-exports to the exact flat.
- Hidden guides are not exported; the sources are unchanged; isolation held.

**Godot 4.7.2 (11 + 3 physics):**
- All 27 art layers load texel-exact, including the two new ones.
- Route on the exported mask: walkable; probes blocked; pins walkable.
- Route stills match the Y-sort and occlusion rules.
- **The windowed captures equal the Python stack: 0 differing pixels in all 4 at 1280×720 and all 4 at 640×360.**
- Physics: 217 `RectangleShape2D`s; 90 shape queries, 0 mismatches. Sweeps: north from spawn 146.09 vs 146, east from axis_mid 251.88 vs 252, the short sweep is clear.
- Nothing was written outside temp.

**Threshold disclosure.** I set the thresholds of the new legibility gates; they are not an external standard. Three were changed after the second preview, as follows:
- Breach A: the contrast threshold went from 0.30 to 0.25 against the adjacent marble. The open sky kept above the broken back wall carries the broken skyline, and it lifts the area mean. In the same change I tightened the drop (≥ 45 rows) and the dark share (≥ 0.5).
- Terrace span: the margin went from 0.30 to 0.15 below the intact wall. I added an absolute core luma ≤ 0.35, because the intact terrace wall near the breach is itself damp-shaded (luma 0.48).
- Repetition: the gate now compares the count of repeated 16-px windows (111 vs 111) instead of the share. The dark shell has fewer qualifying windows, which moved the share's denominator (0.0104 → 0.0105).

**Isolation disclosure:**
- Another session's Pixelorama GUI (PID 50828, open since Oct 15) was not touched.
- `check` ran with the parent `APPDATA` pointed at an empty temp dir, which stayed empty. Each child gets its own fake dir.
- My before/after snapshot of the real `%APPDATA%\pixelorama` and `%APPDATA%\Godot` (244 files) changed only in `pixelorama/.running`, which is the GUI's own heartbeat.
- My `git status` delta is exactly four paths: the v09 tool, the v09 candidate dir, the v09 outputs dir and this note.
  - Changes that appeared during the run belong to other streams: Stream C staged Game Bible files, and Stream A wrote map route-inset captures.
  - No `.uid` or `.import` file appeared.

## Quantified against v08

| measure | v08 | v09 |
|---|---|---|
| Breach A: width / max roofline drop (vs the intact design) | 89 px / 34 rows | **109 px / 52 rows** |
| Breach A: visible at 1× | 99.2 % | 93.2 % (ivy, lip scrub and the prism now sit in it) |
| Breach A removed-wall area: mean luma / dark share (luma < 0.35) | 0.658 / — | **0.410 / 65.1 %** |
| Breach A area vs adjacent intact marble (0.69) | 0.03 darker | **0.28 darker** |
| What shows where A's wall was (sky / shell / trees / nearer) | 44.5 / 34.4 / 20.3 / 0.8 % | 29.7 / **61.2** / 2.3 / 6.8 % |
| Breach B: max drop / area luma / dark share | 31 rows / 0.670 / — | **41 rows / 0.519 / 44.9 %** |
| Failed terrace span: visible at 1× / core luma vs intact wall | — | 65 % / 0.289 vs 0.484 (34 px wide) |
| Walker silhouette, hull/head zone: ring luma, contrast, ring ≥ 0.20 lighter | 0.577, 0.332, 89.6 % | **0.720, 0.476, 90.1 %** |
| Walker silhouette, whole ring incl. legs on the lawn: contrast | 0.268 | 0.341 |
| Survey outpost: visible texels / height / teal+white share | — | 1,805 / 55 px (Capitol 183 px) / 37.3 % |
| Survey cues in patrol orange/red | X, pennants, tape, stakes, string, case, LED | **0** |
| Longest designed roofline run | 153 | 153 (columns lowered vs v08: 145) |
| Mirror-equal share, backdrop band | 0.302 | **0.263** |
| Repeated 16-px windows, backdrop band | 111 | 111 |
| Single-texel islands, rows 0–199 | 0.0770 | 0.0735 |
| Dome visible luma minus breach-A region | 0.086 | **0.167** (the dome stays the brightest mass with more margin) |
| Dome-box vs sky / focal vs frame foot | 0.1485 / 0.109 | 0.1485 / 0.109 |
| Heroine vs backdrop contrast (entry / vista / interact / occlusion) | 0.263 / 0.325 / 0.185 / 0.220 | identical (occlusion 0.2204) |
| Vegetation share, backdrop band | 28.6 % | **24.3 % (lower: the moved trees, and dark shell where the Ailanthus filled A)** |
| Flat texels changed | — | 5.17 % (all in the backdrop + 168 recoloured survey texels on the plane) |

## My visual read of the real Godot captures (honest; not an acceptance)

I looked at all four 640×360 captures and the 1280×720 entry and interact captures myself.

**Better than v08:**
- **The partial collapse now reads at native 640×360.** Right of the intact pavilion, the south centre range is a dark burnt-out shell. It has a broken skyline, pale window holes on two storeys, a standing tooth with the red relay, and an Ailanthus. A dark gash runs from it down through the terrace at its west end. It is the strongest value accent below the dome and is not mirrored on the left.
- **The walker no longer merges with the heap.** Its graphite hull, head and dome stand against pale broken marble pouring out of the gap. Its red eye and orange stripe are still the only warm accents.
- **Survey and patrol are separated by hue and place.** Survey is teal and white: the X, pennants, prism and cordon tape at the breach, the plaza stakes and string, and the shelter and target on the left lawn. Patrol is graphite with orange and red, on the right. The field shelter reads as a white tent with a teal valance and a glowing console. The black-and-white target reads even at 1×.
- **Breach B reads as a dark broken corner** at the left edge, with a yellow-green tree rising out of it.
- The dome, the pavilion and the 48-px heroine read exactly as in v08. Walking, occlusion and collision are unchanged.

**Remaining visual problems (not ready for creator acceptance):**
1. **The burnt shell can read as a dark block.** At 1× its broken top runs fairly level (rows ~113–130), so from a distance it can read as a dark annex or scaffold rather than a fresh collapse.
   - Its value is an artistic choice: charred stone, darker than the sunlit inner faces would really be.
   - The two-storey window holes are still fairly regular.
2. **The pale cone is smooth.** At 1× it reads partly as a white heap or snowdrift. Its stones are sparse, and the crest is a soft rounded mass.
3. **The terrace failure is narrow** (34 px; 65 % visible).
   - Right of the walker, the terrace stays hidden by the plaza rubble's Ailanthus, a `rubble-collapse` layer I kept identical.
   - Left of the twin stair (x 0–420), the long white terrace is still continuous. Codex's "one span" request is met only next to breach A.
4. **The centre and left 60 % of the West Front are still intact** and evenly fenestrated, as in v08, by design for recognisability. The transfer brief's alternative (a big break in the *left* wing, per the v03 layout guide) was **not** attempted.
5. **The survey shelter reads as a booth or kiosk**, and adds a third light mass on the left. It hides part of the terrace and left lawn behind it. No surveyor figure was added, since character art is out of scope.
6. **"Overgrown" is a little weaker on the right.** Backdrop vegetation share fell from 28.6 % to 24.3 %. v08's half-buried dead walker is gone (story loss: it read only as a dark lump in v08).
7. **Breach B is still small** (54 px) and sits at the frame edge, partly behind the far grove.
8. **Inherited from v06–v08:**
   - the compressed West Lawn (camera decision open);
   - the procedural lower third;
   - stock-looking cumulus;
   - some bubble-lobed crowns;
   - the rule-based facade rhythm;
   - the open actor contact-shadow decision.
9. **Authoring route:** code tables plus a Pixelorama round-trip, not a GUI paint pass.

## Open creator decisions

1. Is the right-hand collapse (charred shell + gash + pale spill) the right reading, or should the break move or extend to the left wing as in the transfer brief's v03 layout guide? Going further costs recognisability.
2. Should the dark charred interior stay (legible, not physical), or should the shell be lit as it would be under this sun (more physical, weaker at 1×)?
3. Survey outpost: keep it on the lawn behind the seat wall at this size? Should a surveyor figure be added later (character work)?
4. Accept dropping v08's dead walker?
5. Accept the table-driven route, or require a Pixelorama GUI polish pass from the 28-layer `.pxo`?
6. Carried over: the monument-scale camera versus lawn depth, and the actor contact shadow.

**Counter impact:** none. v09 is neither a runtime replacement nor approved scene art. Scene visuals stay 0/11, and the meter is untouched.
