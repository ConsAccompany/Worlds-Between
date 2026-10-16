# Washington Capitol — distant West Front / Dome establishing composition v01 (QA note)

- **Status:** UNAPPROVED. This is a test-only candidate. It is not wired into the runtime, and no scene, data, test, default, meter, `docs/progress.md`, growth code or Game Bible file was edited. Science scene art stays **0/11** until the creator reviews it. Nothing was committed or pushed.
- **Run:** `wdc-dome-west-v01_20261016-014650-feb222e8` (resumed run id, see below).
- **Context:** this resumes the task held in `docs/qa/…wdc-capitol-establishing-session-limit_hold-note_unapproved-v01_20261016-023737-6e7bdc43.md`. It answers the Codex v04 audit (`docs/qa/…wdc-capitol-west-v04-codex-visual-audit_unapproved-v01_20261016-013712-a9d83f26.md`), which found that v04 never shows the dome.
- **Auth and billing:** Claude Code with claude.ai Max (firstParty). `ANTHROPIC_API_KEY` was absent. No API billing or credits and no image-generation model were used.

## 1. Partial work from the held session
- **What the held session left:** one untracked file, `tools/rpg-2-star-ocean-the-second_wdc-capitol-dome-west_establishing-scene-candidate_pixelorama-build_unapproved-v01_20261016-014650-feb222e8.py` (1,923 lines). It contained the full composition, palette, the 15 layer painters, walkability, the depth audit, `preview` and static checks. `build()`/`check()` were called from `main()` but never defined. No candidate or output files existed under that run id.
- **Scratch files outside the repo:** the held session also left `%TEMP%\wb-dome-baseline\` (git status and sha baselines from 01:46), `%TEMP%\wb-dome-chunk-foreground.py` (an older 02:02 draft of the foreground painters, superseded by the tool) and `%TEMP%\wb-dome-prev\` (02:07 previews of the same tool). They held nothing the tool lacks. They are not mine, so I left them in place.
- **Reused:** that file, under the same run id, since nothing had ever been built with it. Its first preview passed 17 of 18 static gates.
- **Added this session:**
  - `build`, the manifest, `check`, the Pixelorama gate (isolated APPDATA with a kill-switch) and the Godot gate (throwaway project in `%TEMP%`). These were adapted from the v04 tool.
  - The v04 lock (`check` re-hashes the six v04 candidate files and the v04 tool).
- **Fixed after looking at the first preview:**
  - **Paving stains:** per-tile hashes left hard axis-aligned stain rectangles across the paving. Stains now come from smooth value noise and are decided per slab, so the zones follow the joints.
  - **Meadow grass:** the grass showed a visible 12×8 checker. It now uses smooth noise with dithered thresholds, and the dry patches are organic.
  - **Cables:** a long 1-px black cable from the generator to the tripod read as a crack across the plaza. It is removed (a total station needs no mains power). The mast cable is now `k1`.
  - **Pale flecks:** there were 18 in the walkable foreground (the defect called out in the v04 audit). The causes were `d1`/`s2` leaf litter, paving texels stranded inside grass, and a slab texel trapped between a guy-rope and the tent outline. The fixes are recoloured litter, grassing over stranded paving, `fill_pinholes` on `props-low`, and a ground-only despeckle that recoloured 11 texels. **The foreground now has 0 flecks.**
  - **Path length:** the first build used the area token `wdc-capitol-dome-west`, and its candidate paths were 264–273 characters, over MAX_PATH (Pillow could not open the flat PNG). Those outputs were mine, untracked, and only minutes old, so I deleted them and rebuilt with the area token `wdc-dome-west`. Paths are now 230–257 characters. **v04's `.pxo`/`.ora` are 263 characters and have the same problem; they were left untouched.**

## 2. Files (all new, untracked)
| file | sha256 (bytes) |
|---|---|
| `game/assets/environments/candidates/wdc-dome-west-v01_20261016-014650-feb222e8/…scene-editable-15layer….pxo` | `6ab72bda203d0a68…` |
| `…/…scene-editable-15layer….ora` | `bcd2d59582ee5a7e…` |
| `…/…scene-flat-art….png` (1280×720) | `819ff113f404d806…` |
| `…/…scene-palette….gpl`, `…scene-walkability….json`, `…scene-manifest….json` | see manifest |
| `outputs/wdc-dome-west-v01_20261016-014650-feb222e8/…godot-establishing-1280x720-vista….png` | `868922fbcb890e5e…` |
| `outputs/…/…godot-cam640x360-vista-axis….png` (640×360) | `7385a8858b96e436…` |
| `outputs/…/…godot-cam640x360-tripod-behind….png` (640×360) | `1924f1fd2f8216ab…` |
| `outputs/…/…technical-check-report….json` | `7d1bc17a2ae2c13e…` |
| tool (sha256-text-lf-v1 = bytes, LF) | `9aef71e82486a9c0…` |

- **Captures:** exactly three, all written by Godot: one 1280×720 establishing still and two native 640×360 camera windows. There is no multi-view batch and no combined comparison image.
- **Layers (bottom → top), 15 total:**
  - Merged into the base: `sky`, `dome`, `west-front`, `olmsted-terrace`, `arch-ruin-survey`, `far-lawn-basin`, `groves`, `plaza-ground`, `ground-detail`, `cast-shadows`, `props-low`.
  - Y-sorted sprites: `survey-tripod-ysort` (pivot row 232) and `survey-mast-ysort` (pivot row 248).
  - Overlay: `fg-occlusion`.
  - `guides` is hidden and locked.
- **Palette:** 62 colours, 55 of them used in the flat image. That is v04's 47 colours plus 15 new haze, sky and distant-foliage colours.

## 3. Technical verification — `check --write-report`: **PASS, 35/35 gates**
- **Static:**
  - Canvas and alpha: 1280×720 on every layer, binary alpha, palette-only art layers, opaque base and flat.
  - Drained pool: no water or sky colours in the basin.
  - Dome framing: the whole dome is inside both 640×360 windows. The statue tip has 8 rows of margin in the vista view and 5 in the tripod view.
  - Dome symmetry: no silhouette row is asymmetric by more than 1 px.
  - Heroine: 48 logical px, the approved v8 south idle at 2:1. Every walkable foot keeps at least ⅓ visible (worst 0.599).
  - Depth and Y-sort: the depth audit has 0 wrong-order feet over 21 items, and the behind/front Y-sort stills are correct for the tripod and mast.
  - Walkability: nothing is walkable in the backdrop (rows < 218). Every pin is reachable from the entry with an eroded 11-px foot.
  - 0 bright flecks in rows 214–719.
- **Pixelorama 1.2.3** (headless; APPDATA redirected per run; the real `%APPDATA%\pixelorama` stayed unchanged):
  - The `.pxo` flat export is texel-exact twice and byte-identical between runs.
  - `.pxo` and `.ora` `--split-layers` give 14 PNGs, each exactly equal to its layer. The hidden guides are not exported, and the split composite equals the flat.
  - The `.ora` flat is exact, and the source copies are unchanged.
- **Godot 4.7.2** (throwaway `%TEMP%` project; nothing written to `game/` or the real user dir):
  - All 14 art layers from the `.ora` load with a matching RGBA sha256.
  - The heroine is 48 px.
  - Both stills equal the Python runtime stack (0 differing texels), and both 640×360 windows are exact.
- **Repo state:** v04 lock 7/7 unchanged, and the build is deterministic.

## 4. Composition and references
- **Layout:** top of frame is east.
  - Backdrop, rows 0–213, forced perspective at about 1.55 px/m: the dome is centred on the axis (x 605–674, statue tip at row 24) above the 354-px West Front (Senate wing, Bulfinch centre with its projecting pavilion, House wing). Below it are the Olmsted terrace with the balustrade, marble face, granite foundation and a dry exedra, then the lower lawn, the flanking groves, and the drained Capitol Reflecting Pool.
  - Walkable foreground, rows 218–719, at heroine scale: the survey camp on Union Square paving, a mown panel and an overgrown meadow, and the entry steps from the Grant Memorial platform.
- **AOC primary pages:** used as text facts only; no pixels were copied.
  - The [dome page](https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-building/capitol-dome) gives: a cast-iron dome designed by Walter; peristyle columns set on brackets; a platform widened to carry the tholos; a bronze Statue of Freedom 19 ft 6 in tall as the crowning feature; 287 ft high; restoration finished in 2016.
  - The [Olmsted terrace page](https://www.aoc.gov/explore-capitol-campus/buildings-grounds/capitol-grounds/olmsted-terrace) gives: terrace walls of Lee, Massachusetts marble on a granite rubble foundation, wrapping north, west and south; a Vermont marble centre west portion and balustrades; about 20 ft high; four Olmsted lanterns on the west side.
  - **Not verified on AOC:** the tool's 36-column peristyle count and twin stair layout are general knowledge or v04 carry-overs. The terrace page does not mention stairs or the grotto.
- **2537 fiction:**
  - Damage: a missing-plate hole with rust streaks on the south shell, two missing peristyle columns, a gutted south-wing roof corner with a self-sown tree, soot over broken windows, and a breached south balustrade with a rubble cone.
  - Vegetation: ivy on the north wing and terrace, the overgrown meadow, and a weedy drained pool.
  - Survey: a scaffold tower and beacon beside the dome, cordon and flags, a tripod total station, a telescoping mast, stake lines, paint ticks, tents, a rover, a generator, a table, crates and a light mast.

## 5. Honest visual defects (Claude's own reading of the three captures and 3–6× crops; not creator acceptance)
1. **The establishing frame is a map overview, not a cinematic shot.** In the 1280×720 capture the Capitol band fills only the top ~24% (rows 24–176), and the dome is only 70×98 px. About 60% of the frame is plaza. The 640×360 views are much stronger: the dome is unmistakable there.
2. **The paving reads like a brick wall.** It is a uniform 24×12 running bond with no foreshortening. In both 640×360 views the bottom half is just slab rows, and they read as a vertical wall face more than ground. The stain and meadow fixes reduced but did not remove the monotony.
3. **The scale seam is abrupt.** The 48-px heroine at the coping (row 220) stands right against a backdrop at about 1.55 px/m, so she looks roughly as tall as the terrace-to-roof height. Only the thin drained-pool strip (14 rows) separates the two scales. There is no mid-ground depth cue such as a haze band or a lower wall.
4. **The 2537 weathering is understated at distance.**
   - The Capitol still reads as mostly clean white marble.
   - The shell hole is the only strong damage read.
   - The two missing peristyle columns are barely readable, even at 6×.
   - There is little vegetation on the building itself.
5. **The Statue of Freedom reads as a dark spiky "pine tree"** at about 10 px rather than a figure.
6. **The Olmsted twin stairs read as a single central stair** at this scale, and the exedra is barely legible.
7. **17 bright isolated texels remain in the backdrop** (rows 0–213; not gated):
   - Deliberate: the cyan beacon lights (682,73 and 906,154), the orange flagging (550,204) and the cyan screen (545,192).
   - Not deliberate: stray cloud and sky texels (1059,1; 1037,129; 346,134; 351,140; 1041,108; 1066,167; 795,121; 507,167) and pale stone chips at the far coping and terrace (449,184; 862–871,203–205). The coping chips are the same kind of pale chip the v04 audit flagged.
8. **The foreground canopies are noisy.** The large top-corner canopies use a hashed 6×4 tone lattice, so they look noisier and less hand-directed than the grove crowns.
9. **The meadow saplings are thin "lollipop" trees,** and the generic camp props (tents, rover, crates) carry more of the survey story than the Capitol does.
10. **Geography is compressed.** The paved Union Square between the pool and the Grant Memorial is invented, since the real Union Square is mostly the pool itself. It is documented in the tool as forced perspective.

## 6. Authoring route (disclosed)
- This is **not a Pixelorama GUI paint pass.** The session had no desktop or computer-use access to the GUI.
- Route: hand-authored placement tables → Python rasteriser → native `.pxo` (pxo_version 7) and `.ora` → Pixelorama 1.2.3 headless export, compared texel by texel. The `.pxo` opens as 15 editable layers for a GUI polish pass.
- The creator still needs to decide whether this route is acceptable, as for v04.

## 7. Suggested next pass (not done)
- Crop or raise the establishing camera so the Capitol band fills at least 40% of the frame.
- Add a mid-ground haze or step band between the coping and the pool.
- Replace the running-bond field with larger, irregular, foreshortened flagstones.
- Strengthen the dome damage and vegetation.
- Redraw the statue as a figure silhouette.
- Remove the backdrop cloud and coping chips.
- Shorten v04's over-long paths in its next revision.
