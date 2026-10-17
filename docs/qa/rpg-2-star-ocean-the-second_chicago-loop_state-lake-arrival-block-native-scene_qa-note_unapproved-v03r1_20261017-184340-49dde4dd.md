# Chicago Loop arrival block (State St × Lake St): bounded correction v03r1, QA note

**Status: UNAPPROVED and opt-in only (off by default).** This is one bounded visual correction of v03, for Codex visual QA and creator review. It does not accept any scene art. The aesthetic judgment is still open; this pass stops here (no v04).

Counters are unchanged:
- MVP meter 40.8%;
- M2 10/12;
- science scene visuals 3/12;
- character variants 0/52;
- post-art playtests 0/2.

What was not touched:
- the Git index (nothing staged, committed or pushed);
- the Game Bible, shared progress, the map, City Hall and character motion;
- every v02 and v03 file.

Built by Claude Code (Opus 5.5) through signed-in Claude Max, firstParty. `ANTHROPIC_API_KEY` was absent and no paid fallback was used. No process was terminated by image name, and no process was stopped by PID either: every Godot and Python run exited on its own.

## Brief

Codex judged v03 more recognizably Chicago and more populated than v02, but:
- the plaza was too dark and flat;
- the upper building strip was busy;
- source gate C3 failed: lit plaza stone was 25.4% against v02's 29.0%.

## What v03r1 changes

The v03r1 author tool started as a copy of the v03 one; each change is marked `v03r1`.

1. **Warm sunlit paving ramp.** Four new colours, `ps0`–`ps3`. Each sits at the value of `pv4`–`pv7` but warmer. Only the authored ground uses them, never the underpainting.
2. **Slab tones.** All slabs are one step lighter. Sunlit slabs now come in running clusters of about 3×2 slabs (40% of cluster cells), each slab one of three sun values. Flecks and cracks are still one cluster per slab, so no grain was added.
3. **L cast shadow.** The shadow is −2 instead of −3. The tie slits are now warm sun instead of −1, and the long streaks are warm sun +1 instead of +1 granite. The teal glow pools also cover the sunlit slabs.
4. **Under-deck concrete** is one step lighter.
5. **Upper facade strip** (rows 62–94, the same underpainted pixels, share still 20.16%):
   - near-black components of up to 14 px are merged into their surroundings;
   - the cold iron and asphalt blacks left over are warmed to stone shadow (`st0`/`st1`).

**Unchanged, and byte-identical to v03:**
- all 26 y-sort props and their pivots;
- the five y-sort layer PNGs;
- the walk mask and the occlusion reveal mask;
- geometry, blocks and the hero-visibility report;
- the three read-only sites (kiosk, stair, pylon) and their zh/en text;
- the street labels, title, badge and help.

The scene script is the v03 script with only its header comment and art path changed; the source check proves this.

**Generated reference.** It stays out of the runtime and is used as before.

## Opt-in path

The runtime Loop `.tscn` now points at a new selector, `game/scripts/…state-lake-scene-opt-in-selector_unapproved-v03r1_20261017-183235-a00fabf3.gd`. It `extends` the unchanged v02 script:
- **no flag:** v02, byte-identical;
- **`-- --chicago-state-lake-v03r1`** (or `v03r1_override = 1`): the v03r1 scene;
- **`-- --chicago-state-lake-v03`:** still the untouched v03 scene, through the v03 selector's own rule.

To fall back, point the one `path=` in the Loop `.tscn` back at the v03 selector (v03 only) or at the v02 script (no candidates).

## Comparison at actual 640×360

All figures come from the real Godot zh approved-heroine reference capture: same spot and scale, plaza rows 178–317, facade rows 62–94. The en capture gives the same numbers.

| Measure | v02 | v03 | **v03r1** |
|---|---|---|---|
| Lit stone share (gate C3 vs v02) | 28.95% | 25.43% ✗ | **33.21% ✓** |
| Foliage share | 4.08% | 6.74% | 6.93% |
| Teal civic light share | 0.53% | 1.29% | 1.30% |
| Isolated single pixels | 16.22% | 3.38% | 3.46% |
| Neighbour-change density | 0.819 | 0.537 | 0.539 |
| Largest single-colour share | 2.88% | 7.75% | 8.07% |
| Art palette | — | 79 | 83 (+4 sun tones) |
| Facade near-black share (luma < 40) | — | 43.1% | 40.1% |
| Facade near-black specks ≤ 14 px | — | 29 | 23 |
| Facade mean r − b (warmth) | — | 27.7 | 29.7 |
| Underpainted visible share | — | 20.16% | 20.16% |

**By eye at 1×:**
- **Better than v03.** The plaza reads as warm low sun rather than a grey slab field. The sunlit slab runs give the open paving a gentle, clustered variation, close to the warm, mid-light stone of the accepted NYC public-facilities room 1 floor, and it is not noisy (isolated pixels +0.08 pp). The deck shadow still reads, but is no longer a black band, and the tie slits catch sun.
- **Still open:**
  - The facade strip is only modestly calmer. It is less pitted, but still busy and muddy, because it is generator-derived. Fixing it properly means redrawing that band by hand, which is out of scope for a bounded pass.
  - The largest single colour rose slightly (`pv3` slab interiors).
  - v02 still has the more painterly texture.
  - Every other open v03 defect from its QA note stands: invented stair, medallion and fountain; small kiosk and dock; reveal dither in motion; unreviewed note wording.

**Facade iteration, disclosed.** Within this pass I also tried a stronger facade setting: merge up to 30 px and warm all blacks to `st1`. It lowered the near-black share to 24.6%, but raised the small near-black specks from 29 to 46, because the large dark areas fragmented. A further variant reached 10.2% near-black but 67 specks. Both made the speckle worse, so I reverted to the setting above. The two superseded capture sets (`…183710-82d698b8`, `…184124-e69d22f2`) and their reports were deleted. Only `…184340-44bc6d7f` remains.

## Files (all new, except the one-line Loop `.tscn` change)

- **Author tool:** `tools/…state-lake-block-pixel-author_unapproved-v03r1_20261017-183235-a00fabf3.py`. Its manifest pins the v03 author's hash under `correction_of`.
- **Godot check:** `tools/…state-lake-block-godot-capture-check_v03r1_20261017-183235-fb585437.gd` (a copy of the v03 check, plus 2 checks for the v03 route).
- **Source check:** `tools/…state-lake-block-pixel-source-check_v03r1_20261017-183235-e920e570.py` (a copy of the v03 check; C3 is kept verbatim).
- **Runtime art:** `game/assets/environments/chicago-loop-state-lake-v03r1/` holds 7 PNGs, each with its `.import`. Import settings are identical to v03's.
- **Scene:**
  - `game/scenes/…state-lake-block-scene_unapproved-v03r1_….tscn`;
  - `game/scripts/…state-lake-block-scene_unapproved-v03r1_….gd`;
  - the selector `.gd`;
  - the `.uid` files Godot wrote for the two scripts.
- **Editable source** (`outputs/chicago-loop-state-lake-v03r1/`):
  - `…layered-source_unapproved-v03r1_….pxo` (Pixelorama pxo_version 7) and `.ora`, the same 12 layers as v03 plus the hidden, locked walk-mask guide;
  - the merged preview, walk-mask guide and 83-colour `.gpl`;
  - the layer manifest;
  - the check report `…pixel-source-check-report_v03r1_20261017-184340-e920e570.json`.
- **Captures** (`outputs/chicago-loop-state-lake-v03r1/godot-runtime/…640x360_v03r1_20261017-184340-44bc6d7f.png`), real Godot 4.7.2 windowed renders: the same 17 tags as v03, plus a visible-hero counts JSON.
  - flag off: `en-default-off-v02-entry`;
  - arrival: `zh-entry`, `en-entry` (the real NYC→Chicago flight);
  - walking: `zh-traverse-under-l-lane`, `en-traverse-crosswalk`, `zh-traverse-stair-foot`;
  - occlusion: `zh-occlusion-column-raw`, `en-occlusion-column-reveal`, `zh-occlusion-honey-locust`;
  - the three sites in zh and en;
  - the approved heroine reference in zh and en.

## Tests

- **Build:** `python -I tools/…pixel-author_unapproved-v03r1….py`. It is deterministic: the rebuild into a temp dir matched every hash (gate S1).
- **Godot:** `Godot --path game -s <abs>/tools/…godot-capture-check_v03r1….gd -- <abs out> <stamp> <abs walkmask> <abs reveal mask> --chicago-state-lake-v03r1` gives **`CHICAGO_LOOP_V03R1_OK checks=74`**. That is all 72 v03 checks retargeted at v03r1 (flag, default-off v02, map→Chicago entry, collision equal to the mask, held-input walks, 9 occlusion spots, 3 sites, saves, Esc), plus:
  - the v03 flag still reaches v03;
  - the v03 flag is off when only the v03r1 flag is given.
- **Source:** `python -I tools/…pixel-source-check_v03r1….py --capture-stamp 20261017-184340-44bc6d7f` gives **`CHICAGO_LOOP_V03R1_PIXEL_SOURCE_CHECK 18/18`**:
  - S1–S4, G1–G3, H1, C1 (Godot entry equals the y-sorted layers: 0 of 157,482 px differ), C2, **C3 (the original gate, now passing)**, C4, C5, P1/P2 (Pixelorama 1.2.3 CLI split-layers exact for `.pxo` and `.ora`, real APPDATA untouched);
  - new **R1:** a bounded correction; v03 manifest hashes and the pinned v03 code are unchanged; y-sort, reveal and walk-mask bytes equal v03's; ground changed;
  - new **C6:** not noisier than v03; isolated pixels +1 pp or less and edge density +0.05 or less, tolerances fixed before measuring;
  - new **F1:** less facade black speckle than v03, in both the zh and en captures.
- **Regressions:**
  - The v03 Godot check, run through the new selector with `--chicago-state-lake-v03`, gives **72/72**.
  - The v02 Godot check on the runtime Loop with no flag gives **42/42**.
  - All 17 v03 and 8 v02 regression renders are **0 px different** from their original captures. They were written to temp, and the originals were not overwritten.
  - Shared headless smokes, default, all exit 0: `US_SCIENCE_MIGRATION_SMOKE_OK checks=32`, `M2_SMOKE_OK`, `M7_SMOKE_OK`, `GLOBAL_TRAVEL_CORE_OK`, `M2_WHOLE_HOUR_TRAVEL_OK checks=246`, `EXPORT_DATA_INCLUSION_SMOKE_OK checks=24`, `GLOBAL_EARTH_MAP_SMOKE_OK checks=212`, `GLOBAL_MAP_TRAVEL_INTEGRATION_OK checks=114`. The v03 note reported 111 for the last one; the difference is not from this pass.
- **Known string-match failures (behaviour proven unchanged above):**
  - v03 source check **13/15**: `G3` fails only on `runtime_scene_uses_selector`, because the Loop `.tscn` names the v03r1 selector now; `C3` fails as before, since the v03 art is unchanged.
  - v02 source check **12/13**: `G3_runtime_scene_wired_to_v02` fails, as since v03.

## Process notes

- **Import side effect.** Each of the three Godot `--import` runs recreated a `.import` for another session's untracked female sideview v11 PNG (`…873fe1e6.png`), as in v03. Each time I deleted only that `.import`; the PNG was left alone. No other out-of-scope file changed: `git status` was diffed before and after the import, the checks and the regressions.
- **Scratch file.** A scratch copy of the author tool sat briefly in `tools/` (`zz-tmp-chi-variant-a00fabf3.py`) while I previewed a facade variant. It was removed at once; all other scratch work stayed under `%LOCALAPPDATA%\Temp\chi-v03r1-work`.
