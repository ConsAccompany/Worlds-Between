# NYC City Hall Park — 640×360 walkable Pixelorama pilot v02 — QA note

**Status: UNAPPROVED. New, separate test-only candidate; not accepted art.** It is derived from pilot v01 (run `nyc-chp-v01_20261016-044931-92357bf2`). Every v01 file is untouched; its SHA-256 values were re-verified after this run.

- Nothing is wired into the runtime. Science scene art acceptance stays **0/11**.
- No meter, Game Bible, `docs/progress.md`, runtime or Git change was made.
- Run: `nyc-chp-v02_20261016-055120-59848a60`.
- Author: Claude (Claude Code, Opus 5.5) on the claude.ai Max subscription, firstParty only. No API key, no image model and no paid fallback were used.

## Inputs

- **Audit:** `docs/qa/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-pilot-codex-visual-audit_unapproved-v01_20261016-054107-d5cdef6f.md`.
- **v01 QA note and tool:** both read only.
- **City Hall reference:** the published description cited in that audit ([NYC DCAS City Hall page](https://www.nyc.gov/site/dcas/business/dcasmanagedbuildings/city-hall.page)), which names a central pavilion, two projecting wings, a columned entrance portico and a domed tower.
  - Bay counts, column counts and proportions are an interpretation at backdrop scale. They were **not** measured from LPC elevations.
  - No reference pixel was copied, and no generated or continuous-colour art was pasted.
- **Scale actor:** the approved v8 female south idle frame, sampled 2:1 to a **48-logical-px** heroine.

## Authoring route (disclosed)

**There was no Pixelorama GUI paint pass**: the session had no desktop or computer-use access. The deterministic tool rasterises explicit tables into 102 hand-picked palette colours across 23 named layers:
- one hand-written lobe list and trunk polylines per hero tree;
- every crack, stain, patched slab, moss box, sunken paver, worn-turf shape, litter stamp, bed, prop and pin.

Texture rules:
- Textures are hand-drawn motifs (leaf clumps, grass tufts, bed clumps) on fixed lattices with hand-written offset tables.
- No value-noise thresholds and no hashed per-texel scatter were used. A hash only picks a slab or hex-block tone from a short hand table.
- Two cleanup passes are documented in the tool: 1-px pinholes between leaf clumps are closed, and orphan texels merge into their majority neighbour.

Pixelorama 1.2.3 then re-exports the `.pxo` and `.ora` headless. The `.pxo` opens as 23 editable layers, so a GUI paint pass can start from it. **Creator decision still open:** whether a GUI paint pass is mandatory.

## Files (sha256, bytes)

Tool: `tools/rpg-2-star-ocean-the-second_nyc-city-hall-park_walkable-pilot-640x360_pixelorama-build_unapproved-v02_20261016-055120-59848a60.py`
- sha256 `81c0875d6378834af9ef3b4149fa4b20379282d23d7b6972dadb15bb4645ff89` (identical as sha256-text-lf-v1).
- Usage: `preview <tempdir> | build | check [--write-report]`, run with the runtime Python and `-I -B`.

Candidate directory: `game/assets/environments/candidates/nyc-chp-v02_20261016-055120-59848a60/`

| file (prefix `rpg-2-star-ocean-the-second_nyc-city-hall-park_`, suffix `_unapproved-v02_20261016-055120-59848a60`) | sha256 |
|---|---|
| `scene-23layer….pxo` (pxo_version 7) | `3947fec2b7e502115bd143c7e607a90c3ac964ad428d08e50cf19be7a6709f4e` |
| `scene-23layer….ora` | `7d76648b6990660173d3cc278e5d68c070c8dcf4d65edffe06f37a0f66d5dd6b` |
| `scene-flat-640x360….png` | `d83cb20832001f61244c7fc63ab393e219a56e988df8d81f85a79c4ae52c7f4b` |
| `scene-palette….gpl` (102 colours) | `cf69124f0d2efbaff85a1a43b406761c87e93254dec0f63847479661cb0f749f` |
| `scene-walkmask….png` | `c683407f31514550cf6522caf52a4ec77000e4887ff3a492fab751d446f8743b` |
| `contact-shadow….png` (17×5, black, alpha 118 / 64) | `ddba14ee0a49be60c49e4e5aa25d83f6ca2aedf45f610710b1a5981fdcbd0e8d` |
| `scene-walkability….json` | `ef1c5faf97063e55cc8be0c6f99112fdf8092b2b0f768fde29a23408c5724825` |
| `scene-manifest….json` | `67eb380540006699156ca1abc9d25db4e27d0bf0f5851bd670225ab88d2ba183` |

Output directory: `outputs/nyc-chp-v02_20261016-055120-59848a60/`. Each view is a separate file; there are no comparison sheets.

| file | sha256 |
|---|---|
| `…godot-render-1280x720-axis….png` (foot 320,292) | `2e1d00e972ca60eee8caf4e385b1317757ad87b921d1b3d51cc441c8c530070b` |
| `…godot-render-1280x720-behind-fountain….png` (foot 186,226) | `738a9aa92570a27c8d23eca62918debfbfffe8bf1306f75c9e0890d63c999145` |
| `…godot-render-1280x720-behind-tree….png` (foot 403,268) | `f4d73e958e8ea9c855308e712177932aeaffcb16e8a15a6dc4c3c21108fcd554` |
| `…technical-check-report….json` | `76116a3d606b0bf383b65cf47161f5ce755fe7d0ff30135096d4e05a0b02cedc` |

The longest absolute path is 252 characters.

## Visual changes against the v01 audit (verified in the three real Godot 1280×720 captures)

1. **Dollhouse join**
   - The central walk now ends at **hero-scale** granite gate piers. Each pier is 14 px wide and 48 rows tall, with a lantern and a teal scanner slit.
   - Hero-scale iron railings, granite end posts and box shrubs stand beside them.
   - Through the gate, the forecourt recedes:
     - landing courses thin from 5 to 2 rows and the slabs shorten;
     - stair risers grade from 4 rows at the bottom to 2 rows at the top;
     - lawns flow up to the building, with tufts shrinking from 3-row near tufts to 2-px far ticks;
     - trees recede in three sizes (hero, mid-distance, back grove).
   - The near piers overlap the far building, so it reads as distant rather than miniature.
2. **Bands broken**
   - The full-width grove, hedge and picket belt are gone.
   - Rows 0–47 hold hazed Lower Manhattan context with an irregular skyline:
     - a palazzo block on Broadway with a rooftop water tank;
     - far roofs;
     - the Tweed Courthouse roof directly behind City Hall;
     - a Municipal-Building-like tower at the upper right.
   - Separate back-grove clumps frame City Hall without hiding it.
3. **City Hall massing**
   - Projecting wings (+9 rows), with hipped roof ends, pilasters, arched ground-floor windows and pedimented upper hoods.
   - Central pavilion (+3), with quoins and Corinthian pilasters, and a projecting columned entrance portico (+7). The portico has a terrace balustrade, a dark loggia with five arched openings, a lit door, six Ionic columns and the column shadows.
   - Recessed links.
   - Sun from the south-west: the west wing and the pavilion cast shadows onto the recessed walls east of them.
   - The domed clock tower is kept. The invented green banners are removed.
4. **Foliage and wear**
   - Four hero species, each with its own clump size, ramp and lobe list:
     - a London plane with grey-olive mottled bark (NW);
     - a tall plane with a lower bough (SE);
     - an American elm in vase form;
     - a honey locust with yellow-green, see-through gaps;
     - a flowering dogwood with paired bracts.
   - A separate `ground-wear` layer holds cracks, stains, patched slabs, moss joints, sunken hex pavers, trampled turf, mulch rings and leaf or petal litter.
   - The teal centre seam is replaced by two medallions.
   - Lamp shadows are 2 px wide with a lantern blob, not hairlines.
   - Walk lamps are staggered rather than mirrored pairs. The fountain plaza has three-globe candelabra.
   - Also added: a vendor cart, pigeons and a Park Row street tree. The tram is toned down.
5. **Fountain-behind composition**
   - Low inner tier and eight arching jets are in the base layer.
   - The Y-sorted centrepiece is slim: column, bowl with solid falling sheets, bronze nozzle, and a jet with broken wet edges and a filled foam plume.
   - In the capture she stands on plaza paving north of the basin. Her contact shadow is visible, and the bowl top is 17 rows below her feet. The plume's drops fall across her left arm, which is the only overlap.
   - A new **standing-on readability gate** removes feet where a *wide* occluder (≥ 6 columns) hides at least half of her foot band but covers 10 rows or fewer above it (the v01 failure). It blocked 269 feet: behind candelabra arms, the dogwood crown, the statue pedestal top and the bottom-right fg crown.
6. **Contact shadow**
   - A 17×5 two-step alpha ellipse, nudged 1 px north-east to match the south-west sun.
   - It is drawn immediately before the actor (Godot: hero child with `show_behind_parent`).
   - Visible texels: 49 at the axis capture, 49 behind the fountain and 41 behind the tree (the trunk hides part of it).

## Technical gates: 40/40 PASS (`check --write-report`). Gates only; not art acceptance.

**Raster and editability**
- All 23 layers are 640×360 with binary alpha. The base is opaque, and only palette colours are used (99 of 102 appear in the flat).
- The build is deterministic.
- `.pxo`: the 23 named layers, guides hidden.
- `.ora`: `stack.xml` lists the 23 layers top-first with only guides hidden, and every layer PNG is byte-exact.

**Walkability**
- 36,985 walkable texels, 30.7% of rows 172–359. Feet stand only on paving: never in the backdrop or the basin.
- All 14 pins are reachable.
- The route is 1,529 one-pixel steps: 0 blocked and 0 jumps over 1 px, on both the Python mask and the exported mask in Godot.

**Occlusion and visibility**
- Depth audit: 0 wrong-order feet. Worst visibility is 0.465 at (436,258); the floor is 1/3.
- Seven Y-sort cases are correct. Behind cases (sprite covers the actor):
  - fountain: 6/6 overlapping texels;
  - statue: 64/64;
  - SE tree: 171/171;
  - west lamp: 73/73.

  Front cases (actor covers the sprite): candelabra 66, plaque 338, lamp 61.
- No walkable foot has a standing-on ambiguity.

**Pixel clusters**
- 0 isolated bright flecks in rows 150–359. The whole frame has 4, all intentional: the flag finial, two scanner LEDs and one skyline texel.
- Single-texel colour islands: **1.34%** in the park rows (v01 4.63%) and **0.98%** in the backdrop (v01 2.35%).
- The ground despeckle pass changed 110 texels.

**Pixelorama 1.2.3 headless round-trip** (`APPDATA` redirected per run; isolation held)
- 5 runs, about 4.1–4.2 s each.
- The `.pxo` flat export is exact and identical across two runs.
- `.pxo` and `.ora` `--split-layers` give 22 PNGs each, byte-exact per art layer. The split composite equals the flat image.
- The `.ora` flat export is exact. Hidden guides are not exported, and the source copies were unchanged.

**Godot 4.7.2** (temp projects only)
1. *Headless texel gate.*
   - Layer SHA-256 values are exact.
   - 269 route stills hash-match the Python stack, including the contact shadow (integer formula `c' = (c·(255−A)+127)/255`).
   - The actor is 48 px tall.
2. *Windowed GL Compatibility render.*
   - All three captures are 1280×720.
   - They are **pixel-exact outside the contact shadow**. Inside it, GPU alpha blending differs by ≤ 1 channel unit (112, 112 and 40 differing 2× pixels). The gate allows exactly that tolerance.
   - This gate pops a window for a few seconds.

## Honest open defects (why this stays UNAPPROVED)

1. **City Hall scale**
   - The building is still about half heroine scale. The gate and the graded forecourt soften the join; they do not remove the forced perspective.
   - The wing and link window rhythm is still regular within each section.
2. **Fountain**
   - The jet is stylised.
   - The behind-fountain proof is a light 6-texel overlap: the composition is resolved by keeping clear paving under her feet, not by real occlusion depth.
   - The geometry is not the actual Mould fountain.
3. **SE plane:** the 88-row bare trunk keeps the crown above the walk for visibility, so the tree still reads somewhat lollipop-like.
4. **Lower Manhattan context:** generic hazed massing in one grey value band, with regular window grids. There is no sky.
5. **Unchanged from v01:** the generic statue and plaque.
6. **Lawns**
   - The south lawns are still fairly open, and the beds read as dark blobs at 2×.
   - The grass-tuft lattice shows tile-like regularity on large lawns.
   - Back-grove crowns reuse three lobe templates; only the hero trees are unique.
7. **Gate lanterns:** they overlap the link windows. This is an intended depth cue, but it may read as clutter.
8. **Walkability:** the 269 readability-blocked feet slightly reduce the walk area; this is a design choice that needs review.
9. **Contact shadow:** subtle on dark hex pavers. Its GPU ±1 rounding needs to be accepted by the runtime.
10. **Cracks:** they are 1-px lines and could still read as linework.

## Process notes

- Godot and Pixelorama ran only in temp projects or folders. The temp dirs were removed; no Godot `app_userdata` was created, and the real `%APPDATA%\pixelorama` was untouched.
- A before/after `git status` diff shows only this run's three new entries: the candidate dir, the output dir and the tool. Other entries changed in that window belong to parallel sessions' commits and files.
- **Deleted builds.** During this session the candidate directory was twice deleted and rebuilt under the same run ID. Both were this run's own new files, and nothing from them was reviewed or used.
  - First rebuild: an early build was written before the tool was final, so its manifest would have carried a stale tool hash.
  - Second rebuild: the contact-shadow file was renamed from `actor-contact-shadow-17x5` to keep paths at 252 characters (it had reached 259).
  - The final captures are byte-identical to those from the pre-rename build.

## Requested creator decisions

1. Is the table-driven route acceptable, or is a Pixelorama GUI paint pass required?
2. Is the graded forced perspective acceptable, or should the shot be tighter on the portico at hero scale?
3. Is the restrained skyline the right level of Lower Manhattan context?
4. Should the walk mask block the 269 standing-on feet?

Until then scene art stays **0/11** and v02 is **UNAPPROVED**.
