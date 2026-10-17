# Chicago Loop arrival block (State St × Lake St): composition pass v03, QA note

**Status: UNAPPROVED and opt-in only (off by default).** It awaits Codex visual QA and creator review. Nothing here accepts scene art. Counters are unchanged:
- MVP meter **40.8%**;
- M2 **10/12**;
- science scene visuals **3/12**;
- complete character variants **0/52**;
- post-art human playtests **0/2**.

Shared progress, the Game Bible, the map, City Hall, Washington and female files were not edited. The Git index was not touched, and nothing was staged, committed or pushed. The v02 baseline is unchanged: its art, source, tools, captures and scene script are git-clean, and the default runtime still renders v02 byte-for-byte (see Tests).

Built by Claude Code (Opus 5.5) through signed-in Claude Max, firstParty. `ANTHROPIC_API_KEY` was absent and no paid fallback was used.

## Brief and what v03 answers

Codex found v02's elevated L recognizable, but the lower plaza too empty and the stone/foliage/teal density too sparse next to the existing science city. The guidance was the Codex-generated NONRUNTIME style reference `outputs/…chicago-state-lake_style-alignment-reference_nonruntime-v01_20261017-173900-4c6e2b91.png` (1672×941, sha256 `7608a64f…`, untracked).

That reference is continuous-colour generated art. It is **not** in the runtime, and nothing here calls it pixel art. v03 uses it in two ways only:
- as composition, palette and material guidance;
- as a disclosed underpainting for two backdrop bands.

**Split by material.**
- **Underpainting (disclosed): 20.2% of visible art pixels** (33,027 of 163,840 in rows 62–317). It covers two bands:
  - the lit facade north of the L (rows 62–94);
  - the storefront glass under the deck (rows 135–165).
  
  The pipeline is a numpy area average to 640×360, then row recomposition, then nearest colour in a curated 79-colour material palette (no dither, median cut, k-means or RNG). A sequential cluster merge then folds every equal-colour component of 1–3 px into its surroundings, which also collapses the reference's checker dithers. Four copy-repairs remove the reference's own lamp, columns, braces and kiosk from behind the authored ones.
- **Authored in the tool, cluster by cluster: everything else (79.8%).** Placement uses a fixed integer hash, never a random stream:
  - **L iron:**
    - the deck: open timber ties over a dark gap, two running rails and a guard rail;
    - a riveted plate girder with a sun-glinted top flange, stiffeners every 32 px, rust runs, four amber girder lamps lighting the lattice bracing, and bolted column caps;
    - two riveted columns with knee braces, batten plates, column lamps, flared shoes and rust-stained granite plinths;
    - all in a warm painted-steel ramp, kept separate from the cold-black street furniture.
  - **Storefront and sidewalk:**
    - the granite base course;
    - under-deck concrete panels with storefront light pools;
    - large-format 32×16 granite slabs with one deliberate fleck or crack cluster each;
    - sett ribbons and a teal guide strip.
  - **State St:** asphalt with aggregate clusters, a dashed lane line, stop bars, a continental crosswalk with tyre wear, a manhole, a curb with a flush ramp, a red tactile pad and four bollards.
  - **The empty-plaza fix: architecture and props.** None of it blocks the main lanes:
    - a Loop medallion: bronze ring, the five Loop line colours as rings, and a red six-pointed Chicago star with flag-blue bars;
    - two granite seats;
    - two honey locusts in iron grates, with fallen leaves;
    - a teal wayfinding pylon;
    - a five-bike share dock with terminal;
    - column-side planters;
    - a south parapet with an iron picket fence, flowering hedge and two lanterns;
    - a fountain;
    - an east terrace;
    - **the station stair up to the platform**: granite treads, iron stringers, stone newel posts with lanterns, and a glass canopy with the line colours.
  - **Under the deck:**
    - a Chicago curb lamp with a green street blade and flag banner;
    - stone and iron planters;
    - the bench;
    - a litter bin on the legacy pin;
    - a hand-drawn **teal civic kiosk** with a Loop map screen;
    - a conifer planter.
  - **Light and shadow:** the L cast shadow with lit tie slits, column shadows, warm sun streaks, lamp pools and teal light pools at the civic sites.

**Preserved:**
- the State/Lake L identity and plate, the column and stair access, and the 48 px heroine at scale 1;
- walk top 178 with head clearance under the deck (deck bottom 134);
- the arrival spawn (320,286), the kiosk point (432,214) and its pins;
- the real English street labels (E Lake St · 200 N, N State St · 0 E/W, State/Lake);
- the unchanged bilingual title, hint, badge, note and help;
- the Chicago route (the real flight from the map lands here), save/load and Esc to map.

**Interaction sites.** v02 had **one** site (the kiosk), not three. To meet "three interaction sites", v03 keeps the kiosk and adds two read-only notes with scene-local bilingual text:
- the **station stair**: up to the State/Lake platform; riding the L is not part of this demo;
- the **wayfinding pylon**: the Brown, Green, Orange, Pink and Purple lines share the elevated Loop.

None of the sites changes time, clues, surveys, recruits or battles. Each has a teal floor ring. The creator has not reviewed this wording.

## Opt-in integration (scene-specific, off by default)

- The runtime Loop scene `game/scenes/…chicago-loop_district-placeholder-scene_m2-v02_….tscn` now points its script (one line) at `game/scripts/…state-lake-scene-opt-in-selector_unapproved-v03_20261017-174431-c223d3f7.gd`.
- **Without the flag:** the selector only `extends` the unchanged v02 script and calls `super()`, so the Loop plays exactly as v02.
- **With `-- --chicago-state-lake-v03`** (or `enabled_override = 1`): it hands over to `game/scenes/…state-lake-block-scene_unapproved-v03_….tscn` before any v02 code runs. The pending resume is left for v03. Saves still record the Loop scene path, so loading a save with the flag resumes in v03.
- **To remove the opt-in:** point that one `path=` back at the v02 script.

## Hero visibility under tall and near props

Each y-sort prop is its own region sprite with its own pivot, so props never share a pivot. The pivot sits half a row above the bottom of its collision footprint, which the build checks.

Without help, the hero is too hidden in some spots. The raw worst case is **10.5% visible**, behind the kiosk at (434,188). Directly behind a column under the deck she is about 18% visible.

v03 therefore ships a scene-local **dithered reveal**, the same technique as the NYC v06 candidate:
- An authored mask marks the 2,824 walkable feet positions where y-sort props would hide more than half of her.
- There, only the props drawn *over* her open a Bayer 4×4 window around her body; props behind her never get holes.
- **With it, she is at least 50.2% visible at every one of the 64,225 walkable positions.**

The Python model of the y-sort and reveal rules equals real Godot renders **exactly** at 9 spots (raw and revealed pixel counts).

## Files (all new, except the one-line Loop `.tscn` change)

- **Runtime art** (`game/assets/environments/chicago-loop-state-lake-v03/`), each with its `.import`:
  - `ground-far` (opaque);
  - five y-sort layers with binary alpha: `underdeck-props`, `l-columns`, `station-stair-east`, `plaza-props`, `foreground`;
  - the `occlusion-reveal-mask`.
- **Scene:**
  - `game/scenes/…state-lake-block-scene_unapproved-v03_….tscn`;
  - `game/scripts/…state-lake-block-scene_unapproved-v03_….gd` (+ `.uid`);
  - the selector `.gd` (+ `.uid`).
- **Editable source** (`outputs/chicago-loop-state-lake-v03/`):
  - `…layered-source…c223d3f7.pxo` (Pixelorama, pxo_version 7) and `.ora`, holding the same 12 layers:
    - `ground-street-plaza`
    - `ground-shadow-light`
    - `backdrop-facade-north`
    - `backdrop-deck-l-girder`
    - `backdrop-underdeck-storefronts`
    - `station-plate`
    - the 5 y-sort layers
    - a hidden, locked `guides-walkmask`
  - the merged preview, walk-mask guide, 79-colour `.gpl` (named swatches);
  - the layer manifest (provenance, 26 prop regions and pivots, the visibility report, hashes);
  - the check report.
- **Tools:**
  - `tools/…state-lake-block-pixel-author_unapproved-v03_20261017-174431-c223d3f7.py`
  - `tools/…state-lake-block-godot-capture-check_v03_20261017-174431-038f0ef0.gd`
  - `tools/…state-lake-block-pixel-source-check_v03_20261017-174431-86c3e951.py`
- **Captures** (`outputs/chicago-loop-state-lake-v03/godot-runtime/…-640x360_v03_20261017-182019-3e3c762e.png`): real Godot 4.7.2 windowed renders at 640×360, plus a visible-hero counts JSON.
  - `en-default-off-v02-entry`: the flag is off, so this is v02;
  - entry: `zh-entry`, `en-entry` (the real world-map flight NYC→Chicago);
  - traversal: `zh-traverse-under-l-lane`, `en-traverse-crosswalk`, `zh-traverse-stair-foot`;
  - occlusion: `zh-occlusion-column-raw`, `en-occlusion-column-reveal`, `zh-occlusion-honey-locust`;
  - interaction, one zh and one en capture per site:
    - `zh-interact-kiosk`, `en-interact-kiosk`;
    - `zh-interact-stair`, `en-interact-stair`;
    - `zh-interact-pylon`, `en-interact-pylon`;
  - the approved selout v8 heroine at v02's reference spot and scale: `zh-approved-heroine-ref`, `en-approved-heroine-ref`.

## Test commands and results

**Build:**
```
python -I tools/…pixel-author_unapproved-v03….py
```
The build is deterministic: a rebuild into a temp dir reproduces every hash. `.gpl` uses `sha256-text-lf-v1`; PNG, ORA and PXO use `sha256-bytes`.

**Godot behaviour and capture check: `CHICAGO_LOOP_V03_OK checks=72`.**
```
Godot --path game -s <abs>/tools/…godot-capture-check_v03….gd -- <abs out> <stamp> <abs walkmask png> <abs reveal mask png> --chicago-state-lake-v03
```
It covers:
- **opt-in:**
  - the flag enables it;
  - without it the Loop is v02 (ground texture, base script);
- **actual entry:**
  - map → Chicago depart → v03, with the flight charged once;
  - spawn;
  - zh/en labels and badge unchanged;
  - real street names;
  - labels painted under the hero;
- **collision:**
  - `walkable()` equals the authored mask (64,225 px, 0 mismatches);
  - the reveal mask equals the authored mask;
  - the legacy pins;
  - 18 solid probes;
  - head clearance;
- **held-input walks:**
  - spawn → L;
  - the under-L lane stair-foot → State St crosswalk;
  - a plinth blocks a walk south;
- **occlusion:**
  - 9 spots, raw and revealed;
  - revealed ≥ 45% of the full hero where needed;
  - unchanged elsewhere;
  - the parapet always over her;
- **the three sites:**
  - each opens its zh/en note with no time or clue change;
  - E closes it;
  - E away does nothing;
  - the Loop is not counted in areas_visited;
- **saves:**
  - 10 old placeholder/v01/v02 save spots resume on walkable ground;
  - Save → back returns to v03 at the spot;
  - the manual save loads into v03 at the spot;
- **Esc** returns to the map.

**Pixel, source and Pixelorama check: `CHICAGO_LOOP_V03_PIXEL_SOURCE_CHECK 14/15`.**
```
python -I tools/…pixel-source-check_v03….py --capture-stamp 20261017-182019-3e3c762e --report …
```
Passes:
- S1–S4: hashes and exact rebuild, canvas, alpha and palette, ORA exact, PXO exact;
- G1–G3: runtime constants equal the manifest, pins and pivots, opt-in wiring with the v02 baseline git-clean and hash-identical;
- H1: hero ≥ 50% visible everywhere with the reveal;
- C1: the Godot entry equals the y-sorted layers outside hero and labels (0 of 157,482 px differ);
- C2: Godot visible-hero counts equal the model;
- C4: fewer isolated pixels than v02;
- C5: all 17 captures present;
- P1/P2: Pixelorama 1.2.3 CLI `--split-layers` is exact for both `.pxo` and `.ora`, run with an isolated temp APPDATA; the real `%APPDATA%\pixelorama` is unchanged.

**Fails C3**; see the comparison below.

S2 was redefined during the run, before the final result. My first draft required the source ground layer itself to be full-canvas. By design, the backdrop layers own the rows above the walk. It now requires the runtime ground to be opaque and the static layers to cover the canvas.

**Default runtime unchanged (v02):**
- The v02 Godot check against the runtime Loop with no flag gives `CHICAGO_LOOP_V02_OK checks=42`.
- Its 8 renders are **byte-identical** (0 px) to the original v02 captures.
- The v02 source check now gives **12/13**: only `G3_runtime_scene_wired_to_v02` fails. That is a string match for the v02 script name in the Loop `.tscn`, which now names the selector that extends it.

**Shared regressions, headless, default (no flag), all exit 0:**
- `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`
- `M2_SMOKE_OK`
- `M7_SMOKE_OK`
- `GLOBAL_TRAVEL_CORE_OK`
- `M2_WHOLE_HOUR_TRAVEL_OK checks=246`
- `EXPORT_DATA_INCLUSION_SMOKE_OK checks=24`
- `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`
- `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=111`

## Candid comparison to v02 at actual 640×360

Measured on the zh approved-heroine reference captures (same spot and scale). The plaza-level shares cover rows 178–317.

| Measure | v02 | v03 |
|---|---|---|
| Foliage share (plaza level) | 4.1% | **6.7%** |
| Teal civic light share (plaza level) | 0.53% | **1.29%** |
| Lit stone share (plaza level) | **29.0%** | 25.4% |
| Isolated single pixels (speckle) | 16.2% | **3.4%** |
| Neighbour-change density | 0.82 | 0.54 |
| Largest single-colour share | **2.9%** | 7.8% |
| Visible colours (UI included) | 785 | 600 (79 in art) |
| Y-sort occluders | 6 layer-wide pivots | 26 props, each with its own pivot |
| Hero worst-case visibility | 0% behind a column | ≥ 50.2% everywhere (with reveal) |
| Generator-derived visible pixels | most of the frame | 20.2% (facade and storefront bands) |
| Walkable area | 63,947 px | 64,225 px |

**By eye at 1×, v03 is better on the brief's complaint:**
- The plaza is built out: medallion, seats, honey locusts, pylon, dock, planters, crosswalk ramp, bollards, hedge-and-fence foreground, fountain and stair.
- Teal civic tech now recurs (kiosk, pylon, dock, canopy, guide strip, glow pools).
- Speckle became readable clusters.
- The L reads as riveted Chicago iron with an explicit structure.

**v02 still wins on:**
- warmth;
- painterly texture;
- the lighter, sunnier paving field;
- the cleaner facade above the deck. v02's came from a cleaner reference; v03's band from the new reference is busier and muddier.

C3 fails because v03's deep deck shadow and dark hedges leave less lit stone than v02. I made **one** disclosed correction inside this same pass: brighter sunlit slabs, wider sun streaks and teal light pools. It raised lit stone from 21.8% to 25.4%, still below v02. I stopped there, per the brief (no v04 loop).

## Defects and risks (candid)

1. **Underpainted bands.** The facade strip and storefront band are generator-derived (20.2%). They are cluster-cleaned, but busy at 1×, and the top-left keeps fragments of the reference's lamps and trees.
2. **Flat, cool-to-neutral fills.** The authored paving uses one tone per slab (7.8% largest colour share). A strict reviewer may read it as clean but "vector-like" next to the painterly science-city plates. The plaza is darker than the golden reference and than v02 (C3 fail).
3. **The reveal is a stylistic choice.** The dither window over columns, the kiosk and the stair is functional, but may look noisy in motion; it eases at 6/s. Raw y-sort occlusion is as low as 10.5% visible without it.
4. **Invented composition.** The medallion, stair position, terrace, fountain and pedestrian Lake St plaza are art-pilot choices, not the real State/Lake corner. The stair note implies a stair at this spot. The facades are generic. There are still no people, trains or motion.
5. **Small props.** The bike dock and kiosk are hand-drawn but small and simple. The teal glow pools can read as puddles.
6. **Stair interaction pose.** At the stair point, the hero's head overlaps the lowest treads (she is correctly in front of them).
7. **New wording.** The stair and pylon notes are scene-local bilingual strings that the creator has not reviewed. The badge and note text ("Technical placeholder · Art not accepted") were left unchanged on purpose.
8. **v02 check G3** now fails by string match (behaviour is proven unchanged; see Tests).
9. **Reference provenance.** The style reference is untracked. A clean clone cannot rebuild the underpainting without it (the hash is pinned).
10. **Toolchain.** Pillow 12.3.0 and numpy 2.3.5. No median cut or k-means is used, but the area average uses float tensordot (BLAS).

## Process notes

- **Import side effect.** Every Godot `--import` (three runs) recreated a `.import` for another session's untracked female sideview v11 PNG (`…873fe1e6.png`); it was deleted each time. Godot also wrote `.uid` files for the two new v03 scripts, which belong to this pass. No other out-of-scope file changed. A `global-map … source-check … e8b8f8af.json` appeared during the run from another session.
- **Mistake: process kill.** While stopping a slow preview of my own, I ran `taskkill /F /IM python.exe`. It terminated two Python processes: my preview (PID 57020) and PID 53908, which may have belonged to another session. If a parallel job stopped at about 17:50 local time, that is the likely cause. Afterwards I only stopped processes by explicit PID.
- **Superseded captures.** An earlier capture set (stamp `…181705-740f8870`) and its report were made before the final art correction. Both were deleted; only `…182019-3e3c762e` remains.
