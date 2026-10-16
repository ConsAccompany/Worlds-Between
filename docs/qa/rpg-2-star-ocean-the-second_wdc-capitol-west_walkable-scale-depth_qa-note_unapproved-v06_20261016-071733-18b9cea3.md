# Washington Capitol west grounds — walkable scale-depth candidate v06 (QA note, UNAPPROVED, NONRUNTIME)

- **Date:** 2026-10-16. **Stamp:** `20261016-071733`. **Run id:** `18b9cea3`. **Run dir:** `wdc-cw-v06_20261016-071733-18b9cea3`.
- **Author:** Claude (Claude Code, Opus 5.5), signed-in claude.ai Max, firstParty only. No API key, no API billing, no credits, no image model, no paid fallback.
- **Status:** ONE **UNAPPROVED, NONRUNTIME, test-only** art-prototype candidate. It is not accepted art, it is not wired into any runtime scene, and it is not a creator acceptance. **Science scene art stays 0/11.** Visual acceptance is left to root and the creator.
- **Untouched:** runtime scenes/scripts/data/tests and defaults, completion state, acceptance counters, the meter, the Game Bible, `docs/progress.md`, and Git (nothing staged, committed or pushed). v05 and every earlier Capitol candidate are re-hashed by `check` (LOCK, all OK).

## Provenance of this pass

An earlier session started the builder `tools/…walkable-scale-depth_pixelorama-build_unapproved-v06_20261016-071733-18b9cea3.py` and stopped before building. This session inspected it first instead of assuming it worked.

**Inherited from that draft:**
- the new low-eye camera, the nearer and wider West Front, and the larger dome and statue;
- hazed glass, 3-px columns and windows;
- the patrol walker moved into the seat-wall breach, and the terrace sentinel;
- the species trees (oak, cedar, magnolia, broken oak, spruce, poplar), the near planting set, and the cumulus bank.

**What this session found:**
- The draft runs (`preview` completes).
- One static gate failed: `dome_and_statue_fully_in_frame`, with a dome visible share of 0.853.
- A probe showed the only occluder is the West Front pavilion attic, at rows 100–110 (747 texels). That occlusion is intended by the low camera.
- The docstring and the manifest still described v05: eye 1.0 m, lawn rise 7 m, "layers 1-15", no NONRUNTIME label.
- Zoomed views at 4× showed several defects:
  - floating hedge clumps;
  - roof shrubs hovering above the roofline;
  - comb-like ivy strips;
  - a regular sawtooth House-wing "collapse" (a diagonal shear of the whole wing);
  - box rubble;
  - bubble-shaped sky holes in the oak crown.

**What this session changed (all in the same tool, same stamp and run id):**

| area | change |
|---|---|
| landmark gate | New gate `dome_and_statue_in_frame_above_west_front_roofline`: the statue tip must be at row ≥ 2, and ≥ 97 % of the dome **above the West Front roofline in each column** must be visible. Result: 1.000. The raw share (0.853) and the 871 texels deliberately hidden behind the attic are still reported. <br>New gate `capitol_ge_3p5_heroine_heights_and_facade_taller_than_heroine`. |
| localised collapse | `HOUSE_COLLAPSE` is now a ragged bite. The roofline holds to x 566, a notch drops to the second floor over x 578–612, and a broken end pier survives at the frame edge. <br>New `collapse_debris()`: exposed floor slabs with sagging lips, bent iron, and scrub on two slabs. It is re-applied after the void cut, so the pieces protrude into open air. |
| vegetation | `ivy_curtain()`: ragged lobed hems from two noise octaves along x, a few tendrils, and 2×2 leaf clumps lit on the upper-left (replaces vertical stripes). Used on the wing facade and the terrace. <br>`roof_scrub()`: low mats rooted one row into the parapet, with strands drooping over the cornice (replaces floating balls). <br>Wild boxwood hedge: one continuous body rooted behind the coping, with clustered lobes on its irregular top. <br>Oak sky holes removed. |
| terrace depth | `olmsted_lamp()` and `OLMSTED_LAMPS`: seven bronze lamp standards along the two lawn walks, at d 62–128 m. They are projected by the backdrop camera, so the rows shrink and converge on the terrace stairs. Two are hand-assigned 2537 states: one headless, one leaning. They are painter-sorted with the trees by distance and get distance haze. <br>`T_URNS`: hand-assigned urn states on the terrace piers (urn, tilted, stump, gone), so the pier row no longer repeats. |
| rubble / material | `block()` rewritten: three irregular facets (a skewed, corner-chipped top; a front face with a fracture and pitting; a dark side), tilted up to ±w/6, all inside the v05 footprint so the collars and walk mask barely move. <br>New `drum` kind: two fallen fluted marble column drums with elliptic broken end faces. <br>`chip` is now a five-sided shard. |
| labelling | Docstring rewritten for v06: UNAPPROVED, NONRUNTIME; true camera numbers; inherited vs added work; disclosed route. <br>Manifest: `nonruntime: true`, `predecessor` (v05, read-only), `lawn_rise_m` = 2.18, the real-site audit reference, and the base-layer count computed from the stack. <br>LOCK also covers the real-site reference audit. |

## Composition and depth (v05 → v06)

**Unchanged contract.** v06 keeps v05's walkable plaza: pins, 4 exits, 7 interactions, 4 Y-sort pivots and 17 collision probes. It is the same one 640×360 camera with an integer 2× window.

**Backdrop:** one pinhole. F = 552 px, eye **0.5 m** (seat-coping height), horizon row 192.2. The lawn rises 2.18 m from the wall (d 20 m) to the lower-terrace foot (d 150 m).

| metric | v05 | v06 |
|---|---|---|
| Capitol rows (share of frame height) | 6–163 (43.9 %) | **3–185 (50.8 %)** |
| Capitol height ÷ 48-px heroine | ≈ 3.3 | **3.81** |
| West Front visible height at the axis (roof to terrace rail) | ≈ 48 px (= heroine) | **57 px** |
| West Front width | x 168–575 inside the frame | **x 66–677, wider than the frame**; the House wing exits right |
| West Front / dome / terrace distance, px/m | 310 m 1.78 / 366 m 1.51 / 230 m 2.4 | **207 m 2.67 / 263 m 2.1 / 150 m 3.7** |
| patrol walker | 17 px at 70 m, "nearly invisible" | ~2.5 m at ~32 m, in the seat-wall breach, readable silhouette; a 9-px parked sentinel on the terrace stair |
| 16×16 repetition share (same metric) | 0.68 % | **0.61 %** |
| single-texel colour islands, plane / backdrop | 0.117 / 0.069 | 0.121 / 0.074 (slightly more fine texture; reported, not hidden) |

## Files (all new; AGENTS naming `rpg-2-star-ocean-the-second_wdc-capitol-west_<purpose>_unapproved-v06_20261016-071733-18b9cea3.<ext>`)

**Tool:** `tools/rpg-2-star-ocean-the-second_wdc-capitol-west_walkable-scale-depth_pixelorama-build_unapproved-v06_20261016-071733-18b9cea3.py`
- 4,072 lines, sha256-text-lf-v1 `d672021eab0ff7f3b0cc3386717fbf74ae90e5c37c433cfb5f4e4a239b02e8c1`.
- Modes: `preview <tempdir>` | `build` | `check [--write-report]`. Run with the runtime Python and `-I -B`.

**Candidate:** `game/assets/environments/candidates/wdc-cw-v06_20261016-071733-18b9cea3/` (sha256 of the bytes)

| purpose | what | sha256 |
|---|---|---|
| `scene-22layer.pxo` | native pxo_version 7: 1 frame, 22 named layers, `guides` hidden and locked | `40f2428f2273ae206558c6a71b89637c573e520bc816fd22fd1fa6f860c5325d` |
| `scene-22layer.ora` | OpenRaster copy | `db499f96e6ae5dad168df93d0332e790641b73899550e153cb99e817d338be0c` |
| `scene-flat-640x360.png` | flattened art layers | `53c9212a9ff1253e7e96a13356343999efd3fc1c71a06963f19b4c27637fda77` |
| `scene-palette.gpl` | 132 hand-picked colours, all used | `4946e2992e8e22117e29bfcbcf8772fda3790bac7ca5150af541d4e620cd276e` |
| `scene-walkmask.png` | collision mask (62,687 walkable texels; v05 62,671) | `b43cefe0e74d93d1adc1eb939d186c05d899d4b2c0cc3d3fe53878dc87f2f73a` |
| `scene-walkability.json` | grid, pins, exits, interactions, pivots, collars, probes, route rule | `540c54aa3640c356def84b9a0bfcb8a9fc9a2099e274d503940459313a3cc32f` |
| `scene-manifest.json` | depth model and table, layers, palette, LOCK, static checks, file hashes | `f4ad2bfa4490db3585a09d4112af86aee7b929890dd9bd75e60bf2e53ab111be` |

**Outputs:** `outputs/wdc-cw-v06_20261016-071733-18b9cea3/`. These are real windowed Godot 4.7.2 captures (GL Compatibility, nearest, integer stretch). Every view is a separate file; there are no comparison sheets.

| capture | heroine foot | sha256 |
|---|---|---|
| `godot-1280x720-entry` | spawn (372,350) | `78562a4aefcdc8c2177e3e09f4174428634e621da7b5251e0cd47775baaa7010` |
| `godot-1280x720-vista` | stair foot (372,236) | `2151f84ecfc4cf2b24295e053931d86596d320eb575a30f588f5880b7771357b` |
| `godot-1280x720-interact` | beacon front (528,320) | `df4ecf728f0650382788dbc0e863cc69f0093ad3605499b7c017dfe3525c302b` |
| `godot-1280x720-occlusion` | behind the tripod (238,264) | `44fa561aa27d79791d273a48badb531f384729ef9674a98bad70f25f52ccd6bf` |
| `godot-640x360-entry` | spawn | `608c557787330a388965034f9f660ca533938f8c6200de3fd7c8910ac386313e` |
| `godot-640x360-vista` | stair foot | `edfa5e3b67a2ce6f098ecc80d206ccfc708fe4eb5e6dbddfc1d9c9f6d40733cb` |
| `godot-640x360-interact` | beacon front | `a1f5b33c88bfd6ed34a406d7dd515a6e384ccac890f6ad2c72ae0a80d0718a5b` |
| `godot-640x360-occlusion` | behind the tripod | `80152860bbb1d98b57223dc9d71df210cbf95395385b5ebb7a33637a9c412e09` |
| `technical-check-report.json` | 48 gates and all details | `7c7ffd98f392b1a502eee33b216ba8d872f2df6797c69cc3aaea9c78a40848ab` |

## Layer stack (bottom → top)

1. **Base, 16 layers, merged into one base at runtime:**
   1. `sky`
   2. `clouds`
   3. `capitol-dome`
   4. `capitol-west-front`
   5. `capitol-ruin`
   6. `olmsted-terrace`
   7. `west-lawn`
   8. `grounds-trees` (now also holds the lamp standards)
   9. `patrol-walker` (new in v06)
   10. `lawn-edge-planting`
   11. `seat-wall-steps`
   12. `plaza-ground`
   13. `ground-detail`
   14. `cast-shadows`
   15. `rubble-collapse`
   16. `props-low`
2. **Proposed actor contact shadow:** unchanged from v05, still a proposal.
3. **Y-sort layers, sorted with the actor by pivot row:**
   - `survey-mast-ysort` 256
   - `survey-tripod-ysort` 276
   - `beacon-ysort` 306
   - `elm-ysort` 282
4. **`fg-occlusion`**, drawn over the actor.
5. **`guides`:** hidden and locked, never exported.

## Technical gates: **48 / 48 PASS** (`check --write-report`)

These are technical gates only. Passing them is not art acceptance.

**Static checks:**
- 640×360 in every layer; opaque base; binary alpha; palette only.
- Heroine is 48 px; worst actor visibility 0.691.
- **Depth audit:** 82 registered items, 53,863 overlapping walkable feet, **0 wrong-order feet**.
- **Y-sort behind cases:** tripod 140/140, mast 160/160, beacon 125/125, elm 45/45. The front cases are also correct.
- Pins reachable; route 2,285 steps (7 local detours); 17/17 probes blocked; exits and interactions OK.
- 0 ground flecks on walkable ground. 16 deliberate prop highlights are reported separately.
- Landmark ≥ 40 % of height (50.8 %); dome above the roofline 100 % visible, with the statue at row 3; Capitol 3.81 heroine heights, facade 57 px.
- Deterministic double build; the `.pxo` stack is the 22 named layers; longest path 249 < 260.

**LOCK (all OK):**
- v05: candidate dir, outputs dir, tool, QA note and Codex audit;
- the real-site reference audit;
- the v04 candidate dir and the vista v02 candidate dir.

**Pixelorama 1.2.3 headless** (exe `6412014e…`; APPDATA redirected to a fresh temp dir for each run; real dir polled with a kill-switch; isolation held):
- `.pxo` flat ×2: exact and deterministic.
- `.pxo --split-layers`: all art layers exact, and their composite equals the flat image.
- `.ora`: flat and split both exact.
- **Round trip:** an `.ora` rebuilt from the split exports equals the flat image.
- The hidden guides are never exported, and the source files are unchanged.

**Godot 4.7.2** (throwaway projects in `%LOCALAPPDATA%\Temp`):
- The layers load texel-exact.
- 400 runtime-stack stills, 0 mismatched.
- Route re-walked on the exported mask: 0 blocked, 0 jumps over 1 px.
- Probes and pins pass.
- **Windowed renders are pixel-exact against the Python stack:** 0 differing pixels in each of the 4 captures at 1280×720 and each of the 4 at 640×360.
- Godot wrote nothing outside temp.

**Side effects:** the `git status --porcelain --untracked-files=all` delta from this run is only the candidate dir (7 files), the output dir (9 files) and this note. The builder was already untracked. One other new file, `…battle-static-v06-v07_capture-clean-clone-repair_qa-note…d8df79b0.md`, belongs to another session. No `.uid` or `.import` file appeared.

## My visual read (honest; not an acceptance)

**Stronger than v05:**
- The Capitol now dominates the camera. It fills half the frame height, the West Front is taller than the heroine and runs out of the right edge, and the dome and statue stay whole. It no longer reads as a model on a table.
- The patrol machine is a readable story beat in the breach. The terrace sentinel and the survey station keep the "active science outpost in an abandoned city" canon visible.
- The damage is localised and asymmetric:
  - the House-wing bite with its slabs and beams;
  - the dome breach and the missing peristyle columns;
  - the blast hole and soot;
  - the bricked arch.
- Ivy and roof scrub now cling to the stone instead of floating. The flanking trees are distinct species rather than one template.
- Fallen column drums tell "Capitol masonry" in the rubble.

**Remaining defects (not ready for creator acceptance):**
1. **Lawn depth.** The low eye compresses the West Lawn to a ~20-row band, so the "clearer rise from west lawn to terraces" in the real-site audit is only partly met. The lamp rows add a depth ruler, but no visible rise. A real fix needs a camera decision: a taller frame budget, a smaller dome, or a separate lower-terrace screen through the north exit.
2. **Lower third unchanged from v05.** The procedural meadow, sett forecourt, flag walk and desire paths repeat. This pass did not repaint them.
3. **Rubble.** The blocks are now faceted and tilted, but at 1× the mound still reads as a heap of blocks over a noise-textured core.
4. **Facade.** It is still a mirrored, rule-based construction with hand-assigned bay states. The sky has the stock-looking cumulus bank inherited from the draft.
5. **Lamp standards** read at 2×. At 640×360 only the nearer ones register.
6. **Heroine:** the approved south idle faces the viewer, away from the Capitol in the vista pose. The actor contact shadow is still a proposal.
7. **Authoring route.** This is NOT a Pixelorama GUI paint pass (no desktop/computer-use access). Hand-written tables are rasterised by Python into a Python-written `.pxo`. The CLI round-trip is exact, but a GUI open/save/reopen has not been done.

## Open creator decisions

1. Accept the low-eye, nearer-Capitol camera (monument scale) and its compressed lawn, or trade some Capitol height for a visible lawn rise.
2. Accept the table-driven route for this candidate, or require a Pixelorama GUI polish pass from the 22-layer `.pxo`.
3. Keep the patrol walker standing in the breach as static backdrop art, or make it a runtime actor (that would need runtime work outside this task).
4. Adopt the actor contact shadow, and choose shader or prebaked.

**Counter impact:** none. v06 is neither a runtime replacement nor approved scene art.

## Integration review erratum (Task E sync worker, 2026-10-16; the body above is unchanged)

- **Gate count is 47/47, not 48/48.** The stored `technical-check-report` JSON and a fresh `check` both emit exactly 47 gate keys, all `true`; no 48th gate exists in the tool. Every "48" above is a miscount. The v05 report's 46 keys match its 46/46 claim.
- **Re-run (no `--write-report`, so no evidence file was rewritten): PASS 47/47.** With a Pixelorama 1.2.3 GUI from another session open (untitled, autosaving to the real `%APPDATA%\pixelorama\backups\…` about every 62 s), two plain `check` runs failed 4 and 2 Pixelorama gates. The tool's kill-switch correctly stopped headless runs that overlapped an autosave, and the failing gates differed between runs. The passing re-run pointed the parent process's `APPDATA` at an empty temp dir. Each headless child still got its own fake APPDATA. A separate before/after snapshot of the real `%APPDATA%\pixelorama` (excluding the GUI's `.running` and its own backup) and `%APPDATA%\Godot` showed no change. `git status` was unchanged.
- **Hashes:** all 16 candidate/output sha256 values in this note and the tool's sha256-text-lf-v1 match the files.
- **Clean-clone limit:** `check` LOCK hashes `game/assets/environments/candidates/wdc-capitol-west-v04_20261016-004457-a17af0a6/`, which is still untracked (6 files). From a clean clone, `v05_v04_and_vista_v02_untouched` therefore fails until that directory is synced by its owner. This sync did not stage it.
- Still UNAPPROVED, NONRUNTIME, not wired; science scenes stay 0/11.
