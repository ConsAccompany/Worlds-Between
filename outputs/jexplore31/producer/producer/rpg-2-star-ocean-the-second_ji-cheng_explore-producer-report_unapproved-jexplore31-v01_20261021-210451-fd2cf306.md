# Ji Cheng (纪澄) four-direction exploration source — jexplore31 producer report

Status: **UNAPPROVED technical source**. Art is not approved, nothing is runtime-integrated, no default is changed. The work stops at the source and native-export boundary. Root handles actual input captures and integration; DeepSeek owns the independent checker.

- Base and tested revision: `d23d66397e69ff736bdfbedf8c7bd8d42a5d7167` (branch `codex/jexplore31`, worktree `work/needle31/cl-jexplore`). Nothing is committed or staged.
- Producer: Claude. Run `b2782add`, stamp `20261021-210451`.
- Text hashes use `sha256-text-lf-v1` (CRLF→LF, nothing else). PNG, PXO and ORA hashes are raw `sha256-bytes`.

## New files (the only writes)

| Path | Content |
| --- | --- |
| `tools/rpg-2-star-ocean-the-second_ji-cheng_explore-source-author_unapproved-jexplore31-v01_20261021-210451-b2782add.py` | build / check / preview author. Final text-lf sha256 `722be8dcbe08327781f29b528edd7737ba93a39498b3ac68c1d3d637a6f404a8` (also recorded in the manifest) |
| `outputs/jexplore31/png/` (164 PNG) | 4 statics, 16 idle, 48 walk, 96 stop-bridge frames, 80x112 |
| `outputs/jexplore31/*-{south,west,north,east}-editable_*.pxo` | 4 editable Pixelorama sources, 41 frames each, role layers + hidden locked guides, tags idle / walk / stop-pNN |
| `outputs/jexplore31/*-{dir}-static-layers_*.ora` | 4 layered ORA files (static role layers + hidden guides) |
| `outputs/jexplore31/*-source-manifest_*-6ebd469a.json` | sha256 `ed652103a252f97fa7f86dfd04e0119e99e6798dd176d8578191af535758a832`: provenance, per-frame hashes and poses, contact/stop/speed reports, weaknesses |
| `outputs/jexplore31/*-check-result_*-4cb32e67.json` | sha256 `a86d92fc247f3428755d45f9e165353f2d2b2b3eec2e48157d7dbae194c0f842` (written by `check`) |
| `outputs/jexplore31/*-loader-ready_*-99641fa3.json` | registry and set pointers + hashes |
| `game/data/jexplore31/*-sprite-set-runtime_*-58d91a02.json` | sha256 `8999aad32aeb7057014a76030df4eb3ea1004f10fe0fdc298531d0c68568107d`. Schema `worlds-between.exploration-sprite-set.v1`, actor `ji-cheng`, idle/walk × 4 directions, relative `png/` paths |
| `game/data/jexplore31/*-stop-transition-supplemental_*-4c66ed97.json` | sha256 `80f177bf4c10b4e60d28fa15c5c218afe1f0608d89400f55fab16a667d9fd3b5`. 12 phase bridges per direction, `runtime_default: false` |
| `game/data/jexplore31/*-sprite-set-registry_*-9469bb52.json` | sha256 `e5b8fbef32718b9754460f2eddcf886900758ef7a8ef3510ee86fb04f3c38293`. Lists **only** `ji-cheng` |
| `game/data/jexplore31/png/` (164 PNG) | runtime copies, byte-identical to `outputs/jexplore31/png` (checked) |

Godot was not run, so no `.import` sidecars exist. Root's `--import` will create them.

## Inputs and provenance (read-only, unchanged)

- South source PNG `game/assets/characters/ji-cheng-hd/..._south-idle-static_unapproved-v01_20261018-132812-1920ff13.png`, sha256 `58c92f51…a32a1d`. Its PXO `...-d4b5aa5e.pxo` has sha256 `ce9c1fab…b69c`. Both are asserted on every run.
- 13 role layers come from the literal MAP/ROLE grids in `tools/..._ji-cheng_south-idle-static-pilot-build-and-check_unapproved-v01_20261018-132812-0d31a6f9.py` (text-lf `18ef5efc…61b8`). They are imported, not edited, and assert-recompose to the source PNG exactly.
- Generic helpers come from `tools/..._protagonist-male_explore-4dir-source-author_unapproved-mexplore23-v01_20261021-162551-6e3b1a7d.py` (text-lf `93a349ee…c1f2`): raster primitives, pose tables, PXO/ORA writers, guides, `sole_points`, contact/stop reports and Pixelorama export.
- The structure follows `tools/..._liang-xu_explore-source-author_unapproved-lexplore28-v01_20261021-194350-3acdbd6e.py` (text-lf `94cbe7c1…4944`, recorded, not imported).
- Identity cues were read from the Ji Cheng **CONCEPT** character sheet `outputs/rpg-2-star-ocean-the-second_ji-cheng_character-sheet_v01_20261013-190436-dcea1a37.png`. It is absent in this sparse checkout, so it was viewed read-only from `work/max0840-sentry-sync`, not copied and not sampled. It is not approved art.
- The old 32x48 prototype was not read or used. Liang and male pixels and palettes were not used: everything is Ji's own declared palette.
- `git diff HEAD` is empty, so all existing tools and source bytes are unchanged.

## Method per direction (contract: 80x112 cell, density 2, pivot 40/104, 96-texel body, 48 logical px)

- **south**: exact source role layers. Static and idle f00 **are the source PNG bytes** (sha `58c92f51…`). Walk and stop work as follows:
  - layer offsets;
  - per-leg column split at x=40, so shin and buckled boot (rows ≥ 84) rise;
  - 1-texel coat-hem sway;
  - the magnifier arm moves at half the arm offset;
  - the book settles 1 texel.
- **north**: south silhouettes mirrored x'=80−x and refilled as back surfaces:
  - closed coat back with seam and vent;
  - crossed back harness straps, belt, satchel with brass buckle and a rolled cream scroll (from the concept back view);
  - black collar and back-of-head bob.

  Shaved scalp, earring and silver-tip texels are kept from the source. The shaved scalp ends up viewer-left (x 32–34) against south viewer-right (x 45–48): her left in both views (checked).
- **west** (her left side): authored puppet showing:
  - shaved temple with razor lines, ear, rectangular brass drop earring;
  - short silver-tipped lock, far curtain behind the neck;
  - book in the near hand, magnifier raised forward in the far hand;
  - short cream panel under the cut-away hem.
- **east** (her right side): authored puppet showing:
  - long silver-tipped curtain over the ear;
  - magnifier raised in the near hand;
  - two hip vials, thigh strap with pouch;
  - long patterned cream panel and long hem point;
  - book in the far hand.

  It is then mirrored, and it is not a mirror of west (checked).
- **Every direction** has 1 static, 4 idle (700/200/400/200 ms), a 12-phase walk (40 ms reference) and 12 phase-aware stop bridges. Each bridge is [walk p exact, s1, s2, idle f00 exact], so it has 2 new frames, with a 120 ms inclusive settle.

## Commands and results

Python runs as `C:/Users/hkzha/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8 -I <tool> ...`.

1. `build`: `WROTE 341 files`, exit 0.
2. `check --pixelorama C:/.../pixelorama-1-2-3/Pixelorama-Windows-64bit/Pixelorama.exe` (300 s timeout per export): exit 0, `RESULT PASS`.
   - **REBUILD 341/341**: deterministic, byte-identical to the written files.
   - **SOURCE 52/52**: frame format and palette, body heights, counts, distinct idle frames, lower-body change across walk phases, ORA recompose, PXO cels recompose for all 41 frames, exact south source bytes, unchanged source PXO, pairwise distinct statics, east ≠ mirror(west), north ≠ mirror(south), identity cues, shaved-side handedness, package schema and lossless copies, stop supplemental, ji-cheng-only registry, no `.gdignore`, no 32x48 input, side sole grounding.
   - **Native Pixelorama 1.2.3 headless export**: south, west, north and east each gave exit 0, 41/41 frames exported and 41/41 pixel-equal, with no `SCRIPT ERROR`.
   - **Diagnostics, reported separately and not clean**: every direction printed 4 `ERROR: Condition "!actions.custom_samplers.has(function->arguments[j].tex_builtin)" is true. Continuing.` shader lines. This is a CLI export result only. No GUI save/reopen was performed, so no clean-GUI claim is made.

### Check-definition change (disclosed)

The first full check failed 3 of 50 source checks. Two fixes followed, and the final run is the 52/52 above.

1. **East idle had only 2 distinct frames.** The book settle was hidden behind her body on that side. Fixed in the art: the magnifier now settles 1 texel too. This also adds a 1-texel magnifier bob during walk.
2. **South and north walk frames did not have their lowest row at 103.** The rule inherited from Liang is lowest row == 103 in every frame. In Ji's original south source her right foot (viewer-left) is set back, with its sole outline on row 102, while the other foot sits on 103.
   - When the 103 foot lifts, the frame's lowest row is legitimately 102.
   - For south and north walk/stop frames only, the gate is replaced by a **stricter per-foot rule**:
     - every unlifted foot keeps its exact source sole row (south L/R 102/103, north 103/102);
     - every lifted foot must be above that row.
   - That rule has 0 failures.
   - The inherited rule still fails on 15 south and 15 north walk/stop frames; that count is recorded in the check JSON.
   - Statics, idle and side views still gate on 103.

## Contact, stop and speed reports (measured, not fluidity claims)

- **Side planted heel against declared movement** (4 source texels per phase): max slip **0** in west and east, in source-cycle terms only.
- **Side IK overreach**: max **1.965** source texels in both west and east. At the extremes of the 24-texel stance the shin stretches, which reads as a straight leg at contact.
- **Stop bridges**:
  - south and north: planted drift 0;
  - west and east: max planted-heel drift 15 source texels over a bridge, max 5 per step. The foot visibly slides back to neutral during the 120 ms settle; **no world foot-lock is claimed**.
- **Normal speed**: at 140 logical px/s with a fixed 40 ms phase clock, the planted side foot slides 3.6 logical px per phase. A pure distance driver needs 70 phases/s, so 60 fps skips phases. Front and back walks are in place (not world-locked). No fluidity or world-footlock claim.

## Limitations and open items

- Side views and the north refill are new puppet and refill geometry, below the hand-placed south texel quality.
- Face, hair and props at 48 px were only previewed on grey, bright and dark flat colours at ×3 (temp, outside the repo). No in-game inspection was done.
- East light becomes upper-right after the mirror.
- The magnifier is a 3/4 oval in side views and stays raised while walking. Only the book arm swings.
- The front/back walk is an in-place shin/boot lift with a 1-texel hem sway; there is no foreshortened stride.
- North back details (straps, satchel, scroll) follow the concept sheet, which is CONCEPT only.
- The north hair outline makes a dark band over the collar. The north earring is mostly covered by the hair.
- Not done (outside this scope): Godot import, actual-input captures, runtime hooks, combat, ledger/Bible/registry updates.

## Next bounded action (root)

1. Run the independent checker (DeepSeek) on `game/data/jexplore31` plus the manifest.
2. Godot `--import` in an isolated copy.
3. Actual input captures, bright and dark, through a test-only entry for start/walk/stop/re-press/reversal at normal speed.
4. Creator visual review of the four statics.
